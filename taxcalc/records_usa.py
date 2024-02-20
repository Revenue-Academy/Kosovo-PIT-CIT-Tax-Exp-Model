"""
Tax-Calculator tax-filing-unit Records class.
"""
# CODING-STYLE CHECKS:
# pycodestyle records.py
# pylint --disable=locally-disabled records.py

import os
import json
import numpy as np
import pandas as pd
from taxcalc.growfactors import GrowFactors
from taxcalc.utils import read_egg_csv, read_egg_json


class Records(object):
    """
    Constructor for the tax-filing-unit Records class.

    Parameters
    ----------
    data: string or Pandas DataFrame
        string describes CSV file in which records data reside;
        DataFrame already contains records data;
        default value is the string 'puf.csv'
        For details on how to use your own data with the Tax-Calculator,
        look at the test_Calculator_using_nonstd_input() function in the
        tests/test_calculate.py file.

    exact_calculations: boolean
        specifies whether or not exact tax calculations are done without
        any smoothing of "stair-step" provisions in income tax law;
        default value is false.

    gfactors: GrowFactors class instance or None
        containing record data extrapolation (or "blowup") factors.
        NOTE: the constructor should never call the _blowup() method.

    weights: string or Pandas DataFrame or None
        string describes CSV file in which weights reside;
        DataFrame already contains weights;
        None creates empty sample-weights DataFrame;
        default value is filename of the PUF weights.

    start_year: integer
        specifies calendar year of the input data;
        default value is PUFCSV_YEAR.
        Note that if specifying your own data (see above) as being a custom
        data set, be sure to explicitly set start_year to the
        custom data's calendar year.  For details on how to
        use your own data with the Tax-Calculator, read the
        DATAPREP.md file in the top-level directory and then
        look at the test_Calculator_using_nonstd_input()
        function in the taxcalc/tests/test_calculate.py file.

    Raises
    ------
    ValueError:
        if data is not the appropriate type.
        if taxpayer and spouse variables do not add up to filing-unit total.
        if dividends is less than qualified dividends.
        if gfactors is not None or a GrowFactors class instance.
        if start_year is not an integer.
        if files cannot be found.

    Returns
    -------
    class instance: Records

    Notes
    -----
    Typical usage when using PUF input data is as follows::

        recs = Records()

    which uses all the default parameters of the constructor, and
    therefore, imputed variables are generated to augment the data and
    initial-year grow factors are applied to the data.  There are
    situations in which you need to specify the values of the Record
    constructor's arguments, but be sure you know exactly what you are
    doing when attempting this.

    Use Records.cps_constructor() to get a Records object instantiated
    with CPS input data.
    """
    # suppress pylint warnings about unrecognized Records variables:
    # pylint: disable=no-member
    # suppress pylint warnings about uppercase variable names:
    # pylint: disable=invalid-name
    # suppress pylint warnings about too many class instance attributes:
    # pylint: disable=too-many-instance-attributes

    CPSCSV_YEAR = 2014

    CUR_PATH = os.path.abspath(os.path.dirname(__file__))
    CPS_WEIGHTS_FILENAME = 'cps_weights.csv.gz'
    VAR_INFO_FILENAME = 'records_variables.json'

    def __init__(self,
                 data='puf.csv',
                 exact_calculations=False,
                 gfactors=GrowFactors(),
                 weights=CPS_WEIGHTS_FILENAME,
                 start_year=2011):
        # pylint: disable=too-many-arguments,too-many-locals
        self.__data_year = start_year
        # read specified data
        self._read_data(data, exact_calculations)
        # check that three sets of split-earnings variables have valid values
        msg = 'expression "{0} == {0}p + {0}s" is not true for every record'
        tol = 0.020001  # handles "%.2f" rounding errors
        if not np.allclose(self.e00200, (self.e00200p + self.e00200s),
                           rtol=0.0, atol=tol):
            raise ValueError(msg.format('e00200'))
        if not np.allclose(self.e00900, (self.e00900p + self.e00900s),
                           rtol=0.0, atol=tol):
            raise ValueError(msg.format('e00900'))
        if not np.allclose(self.e02100, (self.e02100p + self.e02100s),
                           rtol=0.0, atol=tol):
            raise ValueError(msg.format('e02100'))
        # check that ordinary dividends are no less than qualified dividends
        other_dividends = np.maximum(0., self.e00600 - self.e00650)
        if not np.allclose(self.e00600, self.e00650 + other_dividends,
                           rtol=0.0, atol=tol):
            msg = 'expression "e00600 >= e00650" is not true for every record'
            raise ValueError(msg)
        del other_dividends
        # check that total pension income is no less than taxable pension inc
        nontaxable_pensions = np.maximum(0., self.e01500 - self.e01700)
        if not np.allclose(self.e01500, self.e01700 + nontaxable_pensions,
                           rtol=0.0, atol=tol):
            msg = 'expression "e01500 >= e01700" is not true for every record'
            raise ValueError(msg)
        del nontaxable_pensions
        # handle grow factors
        is_correct_type = isinstance(gfactors, GrowFactors)
        if gfactors is not None and not is_correct_type:
            msg = 'gfactors is neither None nor a GrowFactors instance'
            raise ValueError(msg)
        self.gfactors = gfactors
        # read sample weights
        self.WT = None
        self._read_weights(weights)
        # weights must be same size as tax record data
        if self.WT.size > 0 and self.array_length != len(self.WT.index):
            # scale-up sub-sample weights by year-specific factor
            sum_full_weights = self.WT.sum()
            self.WT = self.WT.iloc[self.__index]
            sum_sub_weights = self.WT.sum()
            factor = sum_full_weights / sum_sub_weights
            self.WT *= factor
        # specify current_year and FLPDYR values
        if isinstance(start_year, int):
            self.__current_year = start_year
            self.FLPDYR.fill(start_year)
        else:
            msg = 'start_year is not an integer'
            raise ValueError(msg)
        # construct sample weights for current_year
        if self.WT.size > 0:
            wt_colname = 'WT{}'.format(self.current_year)
            if wt_colname in self.WT.columns:
                self.weight = self.WT[wt_colname] * 0.01
        # specify that variable values do not include behavioral responses
        self.behavioral_responses_are_included = False

    @staticmethod
    def cps_constructor(data=None,
                        exact_calculations=False,
                        gfactors=GrowFactors()):
        """
        Static method returns a Records object instantiated with CPS
        input data.  This works in a analogous way to Records(), which
        returns a Records object instantiated with PUF input data.
        This is a convenience method that eliminates the need to
        specify all the details of the CPS input data just as the
        default values of the arguments of the Records class constructor
        eliminate the need to specify all the details of the PUF input
        data.
        """
        if data is None:
            data = os.path.join(Records.CUR_PATH, 'cps.csv.gz')
        return Records(data=data,
                       exact_calculations=exact_calculations,
                       gfactors=gfactors,
                       weights=Records.CPS_WEIGHTS_FILENAME,
                       start_year=Records.CPSCSV_YEAR)

    @property
    def data_year(self):
        """
        Records class original data year property.
        """
        return self.__data_year

    @property
    def current_year(self):
        """
        Records class current calendar year property.
        """
        return self.__current_year

    @property
    def array_length(self):
        """
        Length of arrays in Records class's DataFrame.
        """
        return self.__dim

    def increment_year(self):
        """
        Add one to current year.
        Also, does extrapolation, reweighting, adjusting for new current year.
        """
        # no incrementing Records object that includes behavioral responses
        assert self.behavioral_responses_are_included is False
        # move to next year
        self.__current_year += 1
        # apply variable extrapolation grow factors
        if self.gfactors is not None:
            self._blowup(self.__current_year)
        # specify current-year sample weights
        if self.WT.size > 0:
            wt_colname = 'WT{}'.format(self.__current_year)
            self.weight = self.WT[wt_colname] * 0.01

    def set_current_year(self, new_current_year):
        """
        Set current year to specified value and updates FLPDYR variable.
        Unlike increment_year method, extrapolation, reweighting, adjusting
        are skipped.
        """
        self.__current_year = new_current_year
        self.FLPDYR.fill(new_current_year)

    @staticmethod
    def read_var_info():
        """
        Read Records variables metadata from JSON file;
        returns dictionary and specifies static varname sets listed below.
        """
        var_info_path = os.path.join(Records.CUR_PATH,
                                     Records.VAR_INFO_FILENAME)
        if os.path.exists(var_info_path):
            with open(var_info_path) as vfile:
                vardict = json.load(vfile)
        else:
            # cannot call read_egg_ function in unit tests
            vardict = read_egg_json(
                Records.VAR_INFO_FILENAME)  # pragma: no cover
        Records.INTEGER_READ_VARS = set(k for k, v in vardict['read'].items()
                                        if v['type'] == 'int')
        FLOAT_READ_VARS = set(k for k, v in vardict['read'].items()
                              if v['type'] == 'float')
        Records.MUST_READ_VARS = set(k for k, v in vardict['read'].items()
                                     if v.get('required'))
        Records.USABLE_READ_VARS = Records.INTEGER_READ_VARS | FLOAT_READ_VARS
        INT_CALCULATED_VARS = set(k for k, v in vardict['calc'].items()
                                  if v['type'] == 'int')
        FLOAT_CALCULATED_VARS = set(k for k, v in vardict['calc'].items()
                                    if v['type'] == 'float')
        FIXED_CALCULATED_VARS = set(k for k, v in vardict['calc'].items()
                                    if v['type'] == 'unchanging_float')
        Records.CALCULATED_VARS = (INT_CALCULATED_VARS |
                                   FLOAT_CALCULATED_VARS |
                                   FIXED_CALCULATED_VARS)
        Records.CHANGING_CALCULATED_VARS = FLOAT_CALCULATED_VARS
        Records.INTEGER_VARS = Records.INTEGER_READ_VARS | INT_CALCULATED_VARS
        return vardict

    # specify various sets of variable names
    INTEGER_READ_VARS = None
    MUST_READ_VARS = None
    USABLE_READ_VARS = None
    CALCULATED_VARS = None
    CHANGING_CALCULATED_VARS = None
    INTEGER_VARS = None

    # ----- begin private methods of Records class -----

    def _blowup(self, year):
        """
        Apply to variables the grow factors for specified calendar year.
        """
        # pylint: disable=too-many-locals,too-many-statements
        AWAGE = self.gfactors.factor_value('AWAGE', year)
        AINTS = self.gfactors.factor_value('AINTS', year)
        ADIVS = self.gfactors.factor_value('ADIVS', year)
        ATXPY = self.gfactors.factor_value('ATXPY', year)
        ASCHCI = self.gfactors.factor_value('ASCHCI', year)
        ASCHCL = self.gfactors.factor_value('ASCHCL', year)
        ACGNS = self.gfactors.factor_value('ACGNS', year)
        ASCHEI = self.gfactors.factor_value('ASCHEI', year)
        ASCHEL = self.gfactors.factor_value('ASCHEL', year)
        ASCHF = self.gfactors.factor_value('ASCHF', year)
        AUCOMP = self.gfactors.factor_value('AUCOMP', year)
        ASOCSEC = self.gfactors.factor_value('ASOCSEC', year)
        ACPIM = self.gfactors.factor_value('ACPIM', year)
        ABOOK = self.gfactors.factor_value('ABOOK', year)
        AIPD = self.gfactors.factor_value('AIPD', year)
        self.e00200 *= AWAGE
        self.e00200p *= AWAGE
        self.e00200s *= AWAGE
        self.pencon_p *= AWAGE
        self.pencon_s *= AWAGE
        self.e00300 *= AINTS
        self.e00400 *= AINTS
        self.e00600 *= ADIVS
        self.e00650 *= ADIVS
        self.e00700 *= ATXPY
        self.e00800 *= ATXPY
        self.e00900s[:] = np.where(self.e00900s >= 0,
                                   self.e00900s * ASCHCI,
                                   self.e00900s * ASCHCL)
        self.e00900p[:] = np.where(self.e00900p >= 0,
                                   self.e00900p * ASCHCI,
                                   self.e00900p * ASCHCL)
        self.e00900[:] = self.e00900p + self.e00900s
        self.e01100 *= ACGNS
        self.e01200 *= ACGNS
        self.e01400 *= ATXPY
        self.e01500 *= ATXPY
        self.e01700 *= ATXPY
        self.e02000[:] = np.where(self.e02000 >= 0,
                                  self.e02000 * ASCHEI,
                                  self.e02000 * ASCHEL)
        self.e02100 *= ASCHF
        self.e02100p *= ASCHF
        self.e02100s *= ASCHF
        self.e02300 *= AUCOMP
        self.e02400 *= ASOCSEC
        self.e03150 *= ATXPY
        self.e03210 *= ATXPY
        self.e03220 *= ATXPY
        self.e03230 *= ATXPY
        self.e03270 *= ACPIM
        self.e03240 *= ATXPY
        self.e03290 *= ACPIM
        self.e03300 *= ATXPY
        self.e03400 *= ATXPY
        self.e03500 *= ATXPY
        self.e07240 *= ATXPY
        self.e07260 *= ATXPY
        self.e07300 *= ABOOK
        self.e07400 *= ABOOK
        self.p08000 *= ATXPY
        self.e09700 *= ATXPY
        self.e09800 *= ATXPY
        self.e09900 *= ATXPY
        self.e11200 *= ATXPY
        # ITEMIZED DEDUCTIONS
        self.e17500 *= ACPIM
        self.e18400 *= ATXPY
        self.e18500 *= ATXPY
        self.e19200 *= AIPD
        self.e19800 *= ATXPY
        self.e20100 *= ATXPY
        self.e20400 *= ATXPY
        self.g20500 *= ATXPY
        # CAPITAL GAINS
        self.p22250 *= ACGNS
        self.p23250 *= ACGNS
        self.e24515 *= ACGNS
        self.e24518 *= ACGNS
        # SCHEDULE E
        self.e26270 *= ASCHEI
        self.e27200 *= ASCHEI
        self.k1bx14p *= ASCHEI
        self.k1bx14s *= ASCHEI
        # MISCELLANOUS SCHEDULES
        self.e07600 *= ATXPY
        self.e32800 *= ATXPY
        self.e58990 *= ATXPY
        self.e62900 *= ATXPY
        self.e87530 *= ATXPY
        self.e87521 *= ATXPY
        self.cmbtp *= ATXPY
        # BENEFITS
        self.other_ben *= self.gfactors.factor_value('ABENOTHER', year)
        self.mcare_ben *= self.gfactors.factor_value('ABENMCARE', year)
        self.mcaid_ben *= self.gfactors.factor_value('ABENMCAID', year)
        self.ssi_ben *= self.gfactors.factor_value('ABENSSI', year)
        self.snap_ben *= self.gfactors.factor_value('ABENSNAP', year)
        self.wic_ben *= self.gfactors.factor_value('ABENWIC', year)
        self.housing_ben *= self.gfactors.factor_value('ABENHOUSING', year)
        self.tanf_ben *= self.gfactors.factor_value('ABENTANF', year)
        self.vet_ben *= self.gfactors.factor_value('ABENVET', year)

    def _read_data(self, data, exact_calcs):
        """
        Read Records data from file or use specified DataFrame as data.
        Specifies exact array depending on boolean value of exact_calcs.
        """
        # pylint: disable=too-many-statements,too-many-branches
        if Records.INTEGER_VARS is None:
            Records.read_var_info()
        # read specified data
        if isinstance(data, pd.DataFrame):
            taxdf = data
        elif isinstance(data, str):
            if os.path.isfile(data):
                taxdf = pd.read_csv(data)
            else:
                # cannot call read_egg_ function in unit tests
                taxdf = read_egg_csv(data)  # pragma: no cover
        else:
            msg = 'data is neither a string nor a Pandas DataFrame'
            raise ValueError(msg)
        self.__dim = len(taxdf.index)
        self.__index = taxdf.index
        # create class variables using taxdf column names
        READ_VARS = set()
        self.IGNORED_VARS = set()
        for varname in list(taxdf.columns.values):
            if varname in Records.USABLE_READ_VARS:
                READ_VARS.add(varname)
                if varname in Records.INTEGER_READ_VARS:
                    setattr(self, varname,
                            taxdf[varname].astype(np.int32).values)
                else:
                    setattr(self, varname,
                            taxdf[varname].astype(np.float64).values)
            else:
                self.IGNORED_VARS.add(varname)
        # check that MUST_READ_VARS are all present in taxdf
        if not Records.MUST_READ_VARS.issubset(READ_VARS):
            msg = 'Records data missing one or more MUST_READ_VARS'
            raise ValueError(msg)
        # delete intermediate taxdf object
        del taxdf
        # create other class variables that are set to all zeros
        UNREAD_VARS = Records.USABLE_READ_VARS - READ_VARS
        ZEROED_VARS = Records.CALCULATED_VARS | UNREAD_VARS
        for varname in ZEROED_VARS:
            if varname in Records.INTEGER_VARS:
                setattr(self, varname,
                        np.zeros(self.array_length, dtype=np.int32))
            else:
                setattr(self, varname,
                        np.zeros(self.array_length, dtype=np.float64))
        # check for valid MARS values
        if not np.all(np.logical_and(np.greater_equal(self.MARS, 1),
                                     np.less_equal(self.MARS, 5))):
            raise ValueError('not all MARS values in [1,5] range')
        # create variables derived from MARS, which is in MUST_READ_VARS
        self.num[:] = np.where(self.MARS == 2, 2, 1)
        self.sep[:] = np.where(self.MARS == 3, 2, 1)
        # check for valid EIC values
        if not np.all(np.logical_and(np.greater_equal(self.EIC, 0),
                                     np.less_equal(self.EIC, 3))):
            raise ValueError('not all EIC values in [0,3] range')
        # specify value of exact array
        self.exact[:] = np.where(exact_calcs is True, 1, 0)
        # delete intermediate variables
        del READ_VARS
        del UNREAD_VARS
        del ZEROED_VARS

    def zero_out_changing_calculated_vars(self):
        """
        Set to zero all variables in the Records.CHANGING_CALCULATED_VARS set.
        """
        for varname in Records.CHANGING_CALCULATED_VARS:
            var = getattr(self, varname)
            var.fill(0.)
        del var

    def _read_weights(self, weights):
        """
        Read Records weights from file or
        use specified DataFrame as data or
        create empty DataFrame if None.
        Assumes weights are integers equal to 100 times the real weight.
        """
        if weights is None:
            setattr(self, 'WT', pd.DataFrame({'nothing': []}))
            return
        if isinstance(weights, pd.DataFrame):
            WT = weights
        elif isinstance(weights, str):
            weights_path = os.path.join(Records.CUR_PATH, weights)
            if os.path.isfile(weights_path):
                WT = pd.read_csv(weights_path)
            else:
                # cannot call read_egg_ function in unit tests
                WT = read_egg_csv(
                    os.path.basename(weights_path))  # pragma: no cover
        else:
            msg = 'weights is not None or a string or a Pandas DataFrame'
            raise ValueError(msg)
        assert isinstance(WT, pd.DataFrame)
        setattr(self, 'WT', WT.astype(np.int32))
        del WT
