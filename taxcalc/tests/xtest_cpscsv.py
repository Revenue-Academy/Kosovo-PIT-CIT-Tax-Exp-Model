"""
Tests of Tax-Calculator using cps.csv input.

Note that the CPS-related files that are required to run this program
have been constructed by the Tax-Calculator development team from publicly
available Census data files.  Hence, the CPS-related files are freely
available and are part of the Tax-Calculator repository.

Read Tax-Calculator/TESTING.md for details.
"""
# CODING-STYLE CHECKS:
# pycodestyle test_cpscsv.py
# pylint --disable=locally-disabled test_cpscsv.py

import os
import json
import numpy as np
import pandas as pd
# pylint: disable=import-error
from taxcalc import Policy, Records, Calculator, nonsmall_diffs


def test_agg(tests_path, cps_fullsample):
    """
    Test current-law aggregate taxes using cps.csv file.
    """
    # pylint: disable=too-many-statements,too-many-locals
    nyrs = 10
    # create a baseline Policy object containing current law policy parameters
    baseline_policy = Policy()
    # create a Records object (rec) containing all cps.csv input records
    recs = Records.cps_constructor(data=cps_fullsample)
    # create a Calculator object using baseline policy and cps records
    calc = Calculator(policy=baseline_policy, records=recs)
    calc_start_year = calc.current_year
    # create aggregate diagnostic table (adt) as a Pandas DataFrame object
    adt = calc.diagnostic_table(nyrs)
    taxes_fullsample = adt.loc["Combined Liability ($b)"]
    # convert adt to a string with a trailing EOL character
    actual_results = adt.to_string() + '\n'
    # read expected results from file
    aggres_path = os.path.join(tests_path, 'cpscsv_agg_expect.txt')
    with open(aggres_path, 'r') as expected_file:
        txt = expected_file.read()
    expected_results = txt.rstrip('\n\t ') + '\n'  # cleanup end of file txt
    # ensure actual and expected results have no nonsmall differences
    diffs = nonsmall_diffs(actual_results.splitlines(True),
                           expected_results.splitlines(True))
    if diffs:
        new_filename = '{}{}'.format(aggres_path[:-10], 'actual.txt')
        with open(new_filename, 'w') as new_file:
            new_file.write(actual_results)
        msg = 'CPSCSV AGG RESULTS DIFFER\n'
        msg += '-------------------------------------------------\n'
        msg += '--- NEW RESULTS IN cpscsv_agg_actual.txt FILE ---\n'
        msg += '--- if new OK, copy cpscsv_agg_actual.txt to  ---\n'
        msg += '---                 cpscsv_agg_expect.txt     ---\n'
        msg += '---            and rerun test.                ---\n'
        msg += '-------------------------------------------------\n'
        raise ValueError(msg)
    # create aggregate diagnostic table using unweighted sub-sample of records
    rn_seed = 180  # to ensure sub-sample is always the same
    subfrac = 0.03  # sub-sample fraction
    subsample = cps_fullsample.sample(frac=subfrac, random_state=rn_seed)
    recs_subsample = Records.cps_constructor(data=subsample)
    calc_subsample = Calculator(policy=baseline_policy, records=recs_subsample)
    adt_subsample = calc_subsample.diagnostic_table(nyrs)
    # compare combined tax liability from full and sub samples for each year
    taxes_subsample = adt_subsample.loc["Combined Liability ($b)"]
    msg = ''
    for cyr in range(calc_start_year, calc_start_year + nyrs):
        if cyr == calc_start_year:
            reltol = 0.014
        else:
            reltol = 0.006
        if not np.allclose(taxes_subsample[cyr], taxes_fullsample[cyr],
                           atol=0.0, rtol=reltol):
            reldiff = (taxes_subsample[cyr] / taxes_fullsample[cyr]) - 1.
            line1 = '\nCPSCSV AGG SUB-vs-FULL RESULTS DIFFER IN {}'
            line2 = '\n  when subfrac={:.3f}, rtol={:.4f}, seed={}'
            line3 = '\n  with sub={:.3f}, full={:.3f}, rdiff={:.4f}'
            msg += line1.format(cyr)
            msg += line2.format(subfrac, reltol, rn_seed)
            msg += line3.format(taxes_subsample[cyr],
                                taxes_fullsample[cyr],
                                reldiff)
    if msg:
        raise ValueError(msg)


def test_cps_availability(tests_path, cps_path):
    """
    Cross-check records_variables.json data with variables in cps.csv file.
    """
    cpsdf = pd.read_csv(cps_path)
    cpsvars = set(list(cpsdf))
    # make set of variable names that are marked as cps.csv available
    rvpath = os.path.join(tests_path, '..', 'records_variables.json')
    with open(rvpath, 'r') as rvfile:
        rvdict = json.load(rvfile)
    recvars = set()
    for vname, vdict in rvdict['read'].items():
        if 'taxdata_cps' in vdict.get('availability', ''):
            recvars.add(vname)
    # check that cpsvars and recvars sets are the same
    assert (cpsvars - recvars) == set()
    assert (recvars - cpsvars) == set()
