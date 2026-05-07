*******************************************************
* RUN_AGG_figs_FINAL.do
* Purpose: Re-create clean rehospitalization figures for resubmission
* Inputs (in E:\AGG by default):
*   - panel_rehosp_main_plus_sens.dta
*   - nhats_with_traj_km4.dta   (or traj_only_km4.dta)
* Outputs:
*   - output\figs\Fig_rehosp_overall.(png/tif)
*   - output\figs\Fig_rehosp_by_traj.(png/tif)
*   - output\rehosp_overall_by_year.csv
*   - output\rehosp_by_traj_by_year.csv
*******************************************************

version 17.0
clear all
set more off

* =========================
* 0) USER SETTINGS
* =========================
global ROOT "E:\AGG"
cd "$ROOT"

local PANEL   "panel_rehosp_main_plus_sens.dta"
local TRAJSRC "nhats_with_traj_km4.dta"
local TRAJMAP "traj_only_km4.dta"

capture mkdir "output"
capture mkdir "output\figs"

* =========================
* 1) BUILD (pid -> traj_group) MAP IF NEEDED
* =========================
capture confirm file "`TRAJMAP'"
if _rc {
    di as txt ">> `TRAJMAP' not found. Creating from `TRAJSRC' ..."

    capture confirm file "`TRAJSRC'"
    if _rc {
        di as err "ERROR: Cannot find `TRAJSRC' in $ROOT = $ROOT"
        exit 601
    }

    use "`TRAJSRC'", clear

    * --- ID variable: pid (preferred) or aid
    capture confirm variable pid
    if _rc {
        capture confirm variable aid
        if !_rc rename aid pid
        else {
            di as err "ERROR: ID variable not found in `TRAJSRC' (need pid or aid)."
            exit 198
        }
    }

    * --- Trajectory variable: traj_group (preferred) or km4
    local tvar ""
    capture confirm variable traj_group
    if !_rc local tvar "traj_group"
    if "`tvar'"=="" {
        capture confirm variable km4
        if !_rc local tvar "km4"
    }
    if "`tvar'"=="" {
        di as err "ERROR: trajectory variable not found in `TRAJSRC' (need traj_group or km4)."
        exit 198
    }

    keep pid `tvar'
    drop if missing(pid)
    drop if missing(`tvar')

    * Keep one record per person (trajectory membership is person-level)
    bysort pid: keep if _n==1

    rename `tvar' traj_group
    label variable traj_group "Trajectory group (km4)"
    compress

    save "`TRAJMAP'", replace
}

* =========================
* 2) LOAD PANEL + STANDARDIZE VARIABLES
* =========================
capture confirm file "`PANEL'"
if _rc {
    di as err "ERROR: Cannot find `PANEL' in $ROOT = $ROOT"
    exit 601
}

use "`PANEL'", clear

* --- ID variable: pid (preferred) or aid
capture confirm variable pid
if _rc {
    capture confirm variable aid
    if !_rc rename aid pid
    else {
        di as err "ERROR: ID variable not found in `PANEL' (need pid or aid)."
        exit 198
    }
}

* --- Year variable: fyear (preferred) or year
capture confirm variable fyear
if _rc {
    capture confirm variable year
    if !_rc rename year fyear
    else {
        di as err "ERROR: year variable not found in `PANEL' (need fyear or year)."
        exit 198
    }
}

* If fyear is coded as years-since-1960 (0-120), convert to calendar year
capture confirm numeric variable fyear
if _rc {
    destring fyear, replace force
}
quietly summarize fyear, meanonly
if (r(min) >= 0 & r(max) <= 120) {
    replace fyear = fyear + 1960
}

* --- Rehospitalization variable:
* In your current dataset, rehosp_any appears coded as 1 or missing(.).
* We create a clean 0/1 indicator rehosp_any01 where missing => 0.
local yvar ""
capture confirm variable rehosp_any
if !_rc local yvar "rehosp_any"
if "`yvar'"=="" {
    capture confirm variable rehosp_any_ext
    if !_rc local yvar "rehosp_any_ext"
}
if "`yvar'"=="" {
    di as err "ERROR: rehospitalization variable not found (need rehosp_any or rehosp_any_ext)."
    exit 198
}

gen byte rehosp_any01 = (`yvar' == 1)
replace rehosp_any01 = 0 if missing(rehosp_any01)
label variable rehosp_any01 "Rehospitalization (any) 0/1 (1=yes, 0=no; source stores 0 as missing)"

* =========================
* 3) MERGE TRAJECTORY GROUP INTO PANEL
* =========================
merge m:1 pid using "`TRAJMAP'", nogen keep(master match)

* -------------------------
* DIAGNOSTIC: trajectory sample balance
* (If group-specific N is constant by year, it can be by design because the trajectory sample
*  includes only participants with complete 2015–2023 LSM data.)
preserve
    keep if traj_group>0
    bys pid: gen nyears=_N
    bys pid: keep if _n==1
    tab nyears
    assert nyears==9
restore
* -------------------------

* =========================
* 4) FIGURE: OVERALL REHOSP RATE BY YEAR (WITH 95% CI)
* =========================
preserve
    keep fyear rehosp_any01
    drop if missing(fyear)

    collapse (count) n=rehosp_any01 (mean) rate=rehosp_any01, by(fyear)

    gen double se    = sqrt(rate*(1-rate)/n)
    gen double ci_lo = max(0, rate - 1.96*se)
    gen double ci_hi = min(1, rate + 1.96*se)

    sort fyear
    export delimited using "output\rehosp_overall_by_year.csv", replace

    twoway ///
        (rcap ci_lo ci_hi fyear, lwidth(thin)) ///
        (connected rate fyear, msize(medlarge)) ///
        , ///
        title("Annual rehospitalization rate (overall)") ///
        ytitle("Rehospitalization rate") ///
        xtitle("Year") ///
        xlabel(2015(1)2023, angle(45)) ///
        legend(off)

    graph export "output\figs\Fig_rehosp_overall.png", replace width(2400)
    graph export "output\figs\Fig_rehosp_overall.tif", replace
restore

* =========================
* 5) FIGURE: REHOSP RATE BY TRAJECTORY GROUP (BY YEAR)
* =========================
preserve
    keep fyear traj_group rehosp_any01
    drop if missing(fyear)
    drop if missing(traj_group)

    collapse (count) n=rehosp_any01 (mean) rate=rehosp_any01, by(fyear traj_group)
    sort traj_group fyear
    export delimited using "output\rehosp_by_traj_by_year.csv", replace

    twoway ///
        (connected rate fyear if traj_group==1, msize(medlarge)) ///
        (connected rate fyear if traj_group==2, msize(medlarge)) ///
        (connected rate fyear if traj_group==3, msize(medlarge)) ///
        (connected rate fyear if traj_group==4, msize(medlarge)) ///
        , ///
        title("Annual rehospitalization rate by trajectory group") ///
        ytitle("Rehospitalization rate") ///
        xtitle("Year") ///
        xlabel(2015(1)2023, angle(45)) ///
        legend(order(1 "Group 1" 2 "Group 2" 3 "Group 3" 4 "Group 4") rows(1) position(6))

    graph export "output\figs\Fig_rehosp_by_traj.png", replace width(2400)
    graph export "output\figs\Fig_rehosp_by_traj.tif", replace
restore

di as result "DONE. Figures and CSVs saved under: $ROOT\output\"
