"""
Tax-Calculator abstract base parameters class.
"""
# CODING-STYLE CHECKS:
# pycodestyle parameters.py

import os
import json
import abc
import collections as collect
import numpy as np
from taxcalc.utils import read_egg_json

#from utils import read_egg_json
#print("global in parameter ")

f = open('global_vars.json')
vars = json.load(f)
verbose = vars['verbose']
        
class ParametersBase(object):
    """
    Inherit from this class for Policy, Behavior, Consumption, GrowDiff, and
    other groups of parameters that need to have a set_year method.
    Override this __init__ method and DEFAULTS_FILENAME.
    """
    __metaclass__ = abc.ABCMeta

    #DEFAULTS_FILENAME = 'current_law_policy.json'
    #DEFAULTS_FILENAME = None


    @classmethod
    def default_data(cls, metadata=False, start_year=None):
        """
        Return parameter data read from the subclass's json file.

        Parameters
        ----------
        metadata: boolean

        start_year: int or None

        Returns
        -------
        params: dictionary of data
        """
        # extract different data from DEFAULT_FILENAME depending on start_year
        if start_year is None:
            params = cls._params_dict_from_json_file()
        else:
            nyrs = start_year - cls.JSON_START_YEAR + 1
            ppo = cls(num_years=nyrs)
            ppo.set_year(start_year)
            params = getattr(ppo, '_vals')
            params = ParametersBase._revised_default_data(params, start_year,
                                                          nyrs, ppo)
        # return different data from params dict depending on metadata value
        if metadata:
            return params
        else:
            return {name: data['value'] for name, data in params.items()}
   
    def __init__(self):
        #print("Inside init of Parameters")
        pass

    def initialize(self, start_year, num_years):
        """
        Called from subclass __init__ function.
        """
        self._current_year = start_year
        self._start_year = start_year
        self._num_years = num_years
        self._end_year = start_year + num_years - 1
        self.set_default_vals()

    def inflation_rates(self):
        """
        Override this method in subclass when appropriate.
        """
        return None

    def wage_growth_rates(self):
        """
        Override this method in subclass when appropriate.
        """
        return None

    def indexing_rates(self, param_name):
        """
        Return appropriate indexing rates for specified param_name.
        """
        if param_name == '_SS_Earnings_c':
            return self.wage_growth_rates()
        else:
            return self.inflation_rates()

    def set_default_vals(self, known_years=999999):
        """
        Called by initialize method and from some subclass methods.
        """
        if hasattr(self, '_vals'):
            for name, data in self._vals.items():
                intg_val = data.get('integer_value')
                bool_val = data.get('boolean_value')
                values = data.get('value')
                if values:
                    cpi_inflated = data.get('cpi_inflated', False)
                    if cpi_inflated:
                        index_rates = self.indexing_rates(name)
                        if name != '_SS_Earnings_c':
                            values = values[:known_years]
                    else:
                        index_rates = None
                    setattr(self, name,
                            self._expand_array(values, intg_val, bool_val,
                                               inflate=cpi_inflated,
                                               inflation_rates=index_rates,
                                               num_years=self._num_years))
        self.set_year(self._start_year)

    @property
    def num_years(self):
        """
        ParametersBase class number of parameter years property.
        """
        return self._num_years

    @property
    def current_year(self):
        """
        ParametersBase class current assessment year property.
        """
        return self._current_year

    @property
    def start_year(self):
        """
        ParametersBase class first parameter year property.
        """
        return self._start_year

    @property
    def end_year(self):
        """
        ParametersBase class lasst parameter year property.
        """
        #print("inside end_year in parameters ")
        return self._end_year

    def set_year(self, year):
        """
        Set parameters to their values for the specified assessment year.

        Parameters
        ----------
        year: int
            assessment year for which to current_year and parameter values

        Raises
        ------
        ValueError:
            if year is not in [start_year, end_year] range.

        Returns
        -------
        nothing: void

        Notes
        -----
        To increment the current year, use the following statement::

            behavior.set_year(behavior.current_year + 1)

        where, in this example, behavior is a Behavior object.
        """
        if year < self.start_year or year > self.end_year:
            msg = 'year {} passed to set_year() must be in [{},{}] range.'
            if verbose:
                print(msg.format(year, self.start_year, self.end_year))
            raise ValueError(msg.format(year, self.start_year, self.end_year))
        self._current_year = year
        year_zero_indexed = year - self._start_year
        if hasattr(self, '_vals'):
            for name in self._vals:
                if isinstance(name, str):
                    arr = getattr(self, name)
                    setattr(self, name[1:], arr[year_zero_indexed])
                    #print(self._tbrk3, year)
    # ----- begin private methods of ParametersBase class -----

    @staticmethod
    def _revised_default_data(params, start_year, nyrs, ppo):
        """
        Return revised default parameter data.

        Parameters
        ----------
        params: dictionary of NAME:DATA pairs for each parameter
            as defined in calling default_data staticmethod.

        start_year: int
            as defined in calling default_data staticmethod.

        nyrs: int
            as defined in calling default_data staticmethod.

        ppo: Policy object
            as defined in calling default_data staticmethod.

        Returns
        -------
        params: dictionary of revised parameter data

        Notes
        -----
        This staticmethod is called from default_data staticmethod in
        order to reduce the complexity of the default_data staticmethod.
        """
        start_year_str = '{}'.format(start_year)
        for name, data in params.items():
            data['start_year'] = start_year
            values = data['value']
            num_values = len(values)
            if num_values <= nyrs:
                # val should be the single start_year value
                rawval = getattr(ppo, name[1:])
                if isinstance(rawval, np.ndarray):
                    val = rawval.tolist()
                else:
                    val = rawval
                data['value'] = [val]
                data['row_label'] = [start_year_str]
            else:  # if num_values > nyrs
                # val should extend beyond the start_year value
                data['value'] = data['value'][(nyrs - 1):]
                data['row_label'] = data['row_label'][(nyrs - 1):]
        return params

    @classmethod
    def _params_dict_from_json_file(cls, DEFAULTS_FILENAME=None):
        """
        Read DEFAULTS_FILENAME file and return complete dictionary.

        Parameters
        ----------
        nothing: void

        Returns
        -------
        params: dictionary
            containing complete contents of DEFAULTS_FILENAME file.
        """

        if cls.DEFAULTS_FILENAME is None:
            msg = 'DEFAULTS_FILENAME must be overridden by inheriting class'
            raise NotImplementedError(msg)
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                            cls.DEFAULTS_FILENAME)
        if os.path.exists(path):
            with open(path) as pfile:
                params_dict = json.load(pfile,
                                        object_pairs_hook=collect.OrderedDict)
        else:
            # cannot call read_egg_ function in unit tests
            params_dict = read_egg_json(
                cls.DEFAULTS_FILENAME)  # pragma: no cover
        return params_dict

    def _update(self, year_mods):
        """
        Private method used by public implement_reform and update_* methods
        in inheriting classes.

        Parameters
        ----------
        year_mods: dictionary containing a single YEAR:MODS pair
            see Notes below for details on dictionary structure.

        Raises
        ------
        ValueError:
            if year_mods is not a dictionary of the expected structure.

        Returns
        -------
        nothing: void

        Notes
        -----
        This is a private method that should **never** be used by clients
        of the inheriting classes.  Instead, always use the public
        implement_reform or update_behavior methods.
        This is a private method that helps the public methods work.

        This method implements a policy reform or behavior modification,
        the provisions of which are specified in the year_mods dictionary,
        that changes the values of some policy parameters in objects of
        inheriting classes.  This year_mods dictionary contains exactly one
        YEAR:MODS pair, where the integer YEAR key indicates the
        assessment year for which the reform provisions in the MODS
        dictionary are implemented.  The MODS dictionary contains
        PARAM:VALUE pairs in which the PARAM is a string specifying
        the policy parameter (as used in the DEFAULTS_FILENAME default
        parameter file) and the VALUE is a Python list of post-reform
        values for that PARAM in that YEAR.  Beginning in the year
        following the implementation of a reform provision, the
        parameter whose value has been changed by the reform continues
        to be inflation indexed, if relevant, or not be inflation indexed
        according to that parameter's cpi_inflated value loaded from
        DEFAULTS_FILENAME.  For a cpi-related parameter, a reform can change
        the indexing status of a parameter by including in the MODS dictionary
        a term that is a PARAM_cpi:BOOLEAN pair specifying the post-reform
        indexing status of the parameter.

        So, for example, to raise the OASDI (i.e., Old-Age, Survivors,
        and Disability Insurance) maximum taxable earnings beginning
        in 2018 to $500,000 and to continue indexing it in subsequent
        years as in current-law policy, the YEAR:MODS dictionary would
        be as follows::

            {2018: {"_SS_Earnings_c":[500000]}}

        But to raise the maximum taxable earnings in 2018 to $500,000
        without any indexing in subsequent years, the YEAR:MODS
        dictionary would be as follows::

            {2018: {"_SS_Earnings_c":[500000], "_SS_Earnings_c_cpi":False}}

        And to raise in 2019 the starting AGI for EITC phaseout for
        married filing jointly filing status (which is a two-dimensional
        policy parameter that varies by the number of children from zero
        to three or more and is inflation indexed), the YEAR:MODS dictionary
        would be as follows::

            {2019: {"_EITC_ps_MarriedJ":[[8000, 8500, 9000, 9500]]}}

        Notice the pair of double square brackets around the four values
        for 2019.  The one-dimensional parameters above require only a pair
        of single square brackets.

        To model a change in behavior substitution effect, a year_mods dict
        example would be::

            {2014: {'_BE_sub': [0.2, 0.3]}}
        """
        # check YEAR value in the single YEAR:MODS dictionary parameter
        if not isinstance(year_mods, dict):
            msg = 'year_mods is not a dictionary'
            raise ValueError(msg)
        if len(year_mods.keys()) != 1:
            msg = 'year_mods dictionary must contain a single YEAR:MODS pair'
            raise ValueError(msg)
        year = list(year_mods.keys())[0]
        if year != self.current_year:
            msg = 'YEAR={} in year_mods is not equal to current_year={}'
            raise ValueError(msg.format(year, self.current_year))
        # check that MODS is a dictionary
        if not isinstance(year_mods[year], dict):
            msg = 'mods in year_mods is not a dictionary'
            raise ValueError(msg)
        # implement reform provisions included in the single YEAR:MODS pair
        num_years_to_expand = (self.start_year + self.num_years) - year
        all_names = set(year_mods[year].keys())  # no duplicate keys in a dict
        used_names = set()  # set of used parameter names in MODS dict
        for name, values in year_mods[year].items():
            # determine indexing status of parameter with name for year
            if name.endswith('_cpi'):
                continue  # handle elsewhere in this method
            vals_indexed = self._vals[name].get('cpi_inflated', False)
            intg_val = self._vals[name].get('integer_value')
            bool_val = self._vals[name].get('boolean_value')
            name_plus_cpi = name + '_cpi'
            if name_plus_cpi in year_mods[year].keys():
                used_names.add(name_plus_cpi)
                indexed = year_mods[year].get(name_plus_cpi)
                self._vals[name]['cpi_inflated'] = indexed  # remember status
            else:
                indexed = vals_indexed
            # set post-reform values of parameter with name
            used_names.add(name)
            cval = getattr(self, name, None)
            index_rates = self._indexing_rates_for_update(name, year,
                                                          num_years_to_expand)
            nval = self._expand_array(values, intg_val, bool_val,
                                      inflate=indexed,
                                      inflation_rates=index_rates,
                                      num_years=num_years_to_expand)
            cval[(year - self.start_year):] = nval
        # handle unused parameter names, all of which end in _cpi, but some
        # parameter names ending in _cpi were handled above
        unused_names = all_names - used_names
        for name in unused_names:
            used_names.add(name)
            pname = name[:-4]  # root parameter name
            pindexed = year_mods[year][name]
            self._vals[pname]['cpi_inflated'] = pindexed  # remember status
            cval = getattr(self, pname, None)
            pvalues = [cval[year - self.start_year]]
            index_rates = self._indexing_rates_for_update(name, year,
                                                          num_years_to_expand)
            intg_val = self._vals[pname].get('integer_value')
            bool_val = self._vals[pname].get('boolean_value')
            nval = self._expand_array(pvalues, intg_val, bool_val,
                                      inflate=pindexed,
                                      inflation_rates=index_rates,
                                      num_years=num_years_to_expand)
            cval[(year - self.start_year):] = nval
        # confirm that all names have been used
        assert len(used_names) == len(all_names)
        # implement updated parameters for year
        self.set_year(year)

    @staticmethod
    def _expand_array(x, x_int, x_bool, inflate, inflation_rates, num_years):
        """
        Private method called only within this abstract base class.
        Dispatch to either _expand_1D or _expand_2D given dimension of x.

        Parameters
        ----------
        x : value to expand
            x must be either a scalar list or a 1D numpy array, or
            x must be either a list of scalar lists or a 2D numpy array

        x_int : boolean
            True implies x has dtype=np.int8;
            False implies x has dtype=np.float64 or dtype=np.bool_

        x_bool : boolean
            True implies x has dtype=np.bool_;
            False implies x has dtype=np.float64 or dtype=np.int8

        inflate: boolean
            As we expand, inflate values if this is True, otherwise, just copy

        inflation_rates: list of inflation rates
            Annual decimal inflation rates

        num_years: int
            Number of budget years to expand

        Returns
        -------
        expanded numpy array with specified dtype
        """
        assert not (x_int and x_bool)
        if not isinstance(x, list) and not isinstance(x, np.ndarray):
            msg = '_expand_array expects x to be a list or numpy array'
            raise ValueError(msg)
        if isinstance(x, list):
            if x_int:
                x = np.array(x, np.int8)
            elif x_bool:
                x = np.array(x, np.bool_)
            else:
                x = np.array(x, np.float64)
        if len(x.shape) == 1:
            return ParametersBase._expand_1D(x, inflate, inflation_rates,
                                             num_years)
        elif len(x.shape) == 2:
            return ParametersBase._expand_2D(x, inflate, inflation_rates,
                                             num_years)
        else:
            raise ValueError('_expand_array expects a 1D or 2D array')

    @staticmethod
    def _expand_1D(x, inflate, inflation_rates, num_years):
        """
        Private method called only from _expand_array method.
        Expand the given data x to account for given number of budget years.
        If necessary, pad out additional years by increasing the last given
        year using the given inflation_rates list.
        """
        if not isinstance(x, np.ndarray):
            raise ValueError('_expand_1D expects x to be a numpy array')
        if len(x) >= num_years:
            return x
        else:
            ans = np.zeros(num_years, dtype=x.dtype)
            ans[:len(x)] = x
            if inflate:
                extra = []
                cur = x[-1]
                for i in range(0, num_years - len(x)):
                    cur *= (1. + inflation_rates[i + len(x) - 1])
                    cur = round(cur, 2) if cur < 9e99 else 9e99
                    extra.append(cur)
            else:
                extra = [float(x[-1]) for i in
                         range(1, num_years - len(x) + 1)]
            ans[len(x):] = extra
            return ans

    @staticmethod
    def _expand_2D(x, inflate, inflation_rates, num_years):
        """
        Private method called only from _expand_array method.
        Expand the given data to account for the given number of budget years.
        For 2D arrays, we expand out the number of rows until we have num_years
        number of rows. For each expanded row, we inflate using the given
        inflation rates list.
        """
        if not isinstance(x, np.ndarray):
            raise ValueError('_expand_2D expects x to be a numpy array')
        if x.shape[0] >= num_years:
            return x
        else:
            ans = np.zeros((num_years, x.shape[1]), dtype=x.dtype)
            ans[:len(x), :] = x
            for i in range(x.shape[0], ans.shape[0]):
                for j in range(ans.shape[1]):
                    if inflate:
                        cur = (ans[i - 1, j] *
                               (1. + inflation_rates[i - 1]))
                        cur = round(cur, 2) if cur < 9e99 else 9e99
                        ans[i, j] = cur
                    else:
                        ans[i, j] = ans[i - 1, j]
            return ans

    def _indexing_rates_for_update(self, param_name,
                                   calyear, num_years_to_expand):
        """
        Private method called only in the _update method.
        """
        if param_name == '_SS_Earnings_c':
            rates = self.wage_growth_rates()
        else:
            rates = self.inflation_rates()
        if rates:
            expanded_rates = [rates[(calyear - self.start_year) + i]
                              for i in range(0, num_years_to_expand)]
            return expanded_rates
        else:
            return None
