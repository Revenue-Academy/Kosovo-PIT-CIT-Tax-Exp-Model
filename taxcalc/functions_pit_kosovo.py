"""
Functions that calculate personal income tax liability.
"""
# CODING-STYLE CHECKS:
# pycodestyle functions.py
# pylint --disable=locally-disabled functions.py

import math
import copy
import numpy as np
from taxcalc.decorators import iterate_jit


'''
-------------------------------------------------------------------------------------
I. PERSONAL INCOME TAX CALCULATION
-------------------------------------------------------------------------------------
'''

'''
Income
'''

# D19	Total Income (add 8 to 18)
@iterate_jit(nopython=True)
def total_inc_fun(gross_wage,net_income_business,net_income_partnership,gross_rents,
                  gross_i_interest_pen_pay,gross_i_interest,gross_i_inta_prop,capital_gain,
                  foreign_s_inc,other_inc_gifts,calc_total_inc):
    calc_total_inc =  gross_wage+net_income_business+net_income_partnership+gross_rents + \
                      gross_i_interest_pen_pay+gross_i_interest+gross_i_inta_prop+capital_gain + \
                      foreign_s_inc + other_inc_gifts
    return calc_total_inc

'''Deductions'''
# D24	Total deductions (add 20 to 23)
@iterate_jit(nopython=True)
def total_ded_fun(rate_ded_rent, ded_rents_expen_rents10pct,ded_pen_cont, ded_exp_int_prop, gross_rents, 
                  other_allowed_ded,calc_total_ded):
    calc_total_ded =  max(ded_rents_expen_rents10pct, rate_ded_rent * gross_rents) + \
                          ded_pen_cont + ded_exp_int_prop + other_allowed_ded
    return calc_total_ded


# D25	Taxable amount (19-24)
@iterate_jit(nopython=True)
def taxable_amount_fun(calc_total_inc,calc_total_ded,calc_gti):
    calc_gti =  calc_total_inc-calc_total_ded
    return calc_gti

# D27 Deduction for Charitable Contributions (max 5% of taxable amount).not claimed on FS
@iterate_jit(nopython=True)
def charity_contribution_fun(rate_ded_charitable, dis_charity_contribution, calc_gti, calc_charity_contribution):
    calc_charity_contribution = min(dis_charity_contribution, max(calc_gti * rate_ded_charitable, 0))
    return calc_charity_contribution


# D28	Total Additional Deductions (26+27)
@iterate_jit(nopython=True)
def tot_additional_ded_fun(calc_charity_contribution,loss_carried_for,calc_tot_additional_ded):
    calc_tot_additional_ded =  calc_charity_contribution+loss_carried_for
    return calc_tot_additional_ded


# D29 Taxable Income before tax [25]-[28] (if negative put the amount in brackets)
@iterate_jit(nopython=True)
def taxable_inc_before_tax_fun(calc_gti,calc_tot_additional_ded,calc_taxable_inc_before_tax):
    calc_taxable_inc_before_tax =  calc_gti - calc_tot_additional_ded
    return calc_taxable_inc_before_tax


# D30 Tax on Taxable Income as per tax brackets 
@iterate_jit(nopython=True)
def tax_on_tax_inc_bracket_fun(calc_taxable_inc_before_tax, rate1, rate2, rate3, rate4, tbrk1, tbrk2, tbrk3,pitax):
    pitax = (rate1 * min(calc_taxable_inc_before_tax, tbrk1) +
                    rate2 * min(tbrk2 - tbrk1, max(0., calc_taxable_inc_before_tax - tbrk1)) +
                    rate3 * min(tbrk3 - tbrk2, max(0., calc_taxable_inc_before_tax - tbrk2)) +
                    rate4 * max(0., calc_taxable_inc_before_tax - tbrk3))
    return (pitax)

