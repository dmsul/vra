/*
Requires `DCdensity` from http://eml.berkeley.edu/~jmccrary/DCdensity/
*/

clear all
cap log close

global logfile ..\out\mccrary_log.txt

global filename tmp
global year 1964


// Reset log file
log using $logfile, text replace
log close

foreach year in 1960 1964 1968 {
    use $filename, replace
    keep if year == `year'

    // Run 'official' McCrary test
    log using $logfile, text  append
    di "McCrary for `year'"
    DCdensity turnout_vap , breakpoint(.5) generate(Xj Yj r0 fhat se_fhat)
    log close

    gen lo = fhat - 1.96 * se_fhat
    gen hi = fhat + 1.96 * se_fhat

    qui summ turnout_vap
    local min = r(min)
    local max = r(max)

    twoway  (scatter Yj Xj if Xj > `min' & Xj < `max') ///
            (line fhat r0 if r0 < .5, lc(navy)) ///
            (line fhat r0 if r0 >= .5, lc(navy)) ///
            (rline hi lo r0 if r0 < .5, lc(maroon) lp(dash) lwidth(thin)) ///
            (rline hi lo r0 if r0 > .5, lc(maroon) lp(dash) lwidth(thin))  ///
            , name(mine, replace) xline(.5) xlab(.2(.1).9) legend(off)
    graph export ../out/mccrary_plot_`year'.pdf, replace
}

