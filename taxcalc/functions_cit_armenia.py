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
I. PROFIT TAX CALCULATION
-------------------------------------------------------------------------------------
'''

'''
Section 1
Gross income

'''
# 41 Gross income (the sum of the income specified in points 6-40)
@iterate_jit(nopython=True)
def calc_income_fun(inc_supply, inc_product, inc_work, inc_service, inc_freight, inc_transactions,
                    inc_disposal_fixed, inc_disposal_intangible, inc_disposal_other, inc_dividends,
                    inc_interest_loans, inc_interest_borrowings, inc_interest_lease, inc_operating,
                    inc_royalties, inc_granted_funds, inc_granted_land, inc_other_granted,
                    inc_forfeited_court, inc_forfeited_other, inc_excess, inc_received_discount,
                    inc_insurance, inc_compensation, inc_penalties, inc_recalculation,
                    inc_credit_debts, inc_repayments_bad_debts, inc_accrued, inc_banks,
                    inc_not_written, inc_recognized, inc_commissions, inc_settlement,
                    inc_VAT, inc_other, calc_income):
    calc_income = inc_supply + inc_product + inc_work + inc_service + inc_freight + inc_transactions + \
                  inc_disposal_fixed + inc_disposal_intangible + inc_disposal_other + inc_dividends + \
                  inc_interest_loans + inc_interest_borrowings + inc_interest_lease + inc_operating + \
                  inc_royalties + inc_granted_funds + inc_granted_land + inc_other_granted + \
                  inc_forfeited_court + inc_forfeited_other + inc_excess + inc_received_discount + \
                  inc_insurance + inc_compensation + inc_penalties + inc_recalculation + \
                  inc_credit_debts + inc_repayments_bad_debts + inc_accrued + inc_banks + \
                  inc_not_written + inc_recognized + inc_commissions + inc_settlement + \
                  inc_VAT + inc_other
    return calc_income

'''

Deductions

'''



# 62.Total expenses (the sum of the expenses mentioned in points 42-61)
@iterate_jit(nopython=True)
def calc_exp_fun(exp_supplied_goods, exp_production_goods, exp_work, exp_service, exp_mediation,
                        exp_disposed_fixed_assets, exp_disposed_intangible_assets, exp_disposed_other,
                        exp_administrative, exp_commercial, exp_non_production, exp_fin_interest_banking,
                        exp_charity, exp_insurance_reinsurance, exp_rent_easement, exp_compensation,
                        exp_penalties, exp_non_expuctible_taxes, exp_expunction_VAT, exp_other,calc_exp):
    calc_exp = (
        exp_supplied_goods + exp_production_goods + exp_work + exp_service + exp_mediation +
        exp_disposed_fixed_assets + exp_disposed_intangible_assets + exp_disposed_other +
        exp_administrative + exp_commercial + exp_non_production + exp_fin_interest_banking +
        exp_charity + exp_insurance_reinsurance + exp_rent_easement + exp_compensation +
        exp_penalties + exp_non_expuctible_taxes + exp_expunction_VAT + exp_other
    )
    return calc_exp

'''
loses

'''

# 67.Total loses (the sum of the losses mentioned in points 63-66)
@iterate_jit(nopython=True)
def calc_loss_fun(loss_natural, loss_quality, loss_accidental, loss_other,calc_loss):
    calc_loss = (
        loss_natural + loss_quality + loss_accidental + loss_other
    )
    return calc_loss

# Calculated value of depreciation 
# New formula
@iterate_jit(nopython=True)
def calc_dep_fun(ab_tx_prop_jan1,ab_in_tx_prop,ab_tx_int_assets_jan1,ab_in_tx_int_assets,depr_prop_rate, depr_int_rate,calc_dep):
    calc_dep = -(
           ((ab_tx_prop_jan1+ab_in_tx_prop) * depr_prop_rate )
    + ((ab_tx_int_assets_jan1+ab_in_tx_int_assets) * depr_int_rate)
    )
    return calc_dep


# 77. The value of assets provided to libraries, museums, public schools, boarding houses, nursing homes, orphanages, medical institutions, as well as non-profit organizations,	o_pay_value_of_assets
# New Policy Variable
@iterate_jit(nopython=True)
def calc_o_pay_value_of_assets_fun(o_pay_value_of_assets, toggle_o_pay_value_of_assets, calc_o_pay_value_of_assets):
    calc_o_pay_value_of_assets = o_pay_value_of_assets * toggle_o_pay_value_of_assets
    return calc_o_pay_value_of_assets

# 78. 150% of the total of the calculated salary and other payments equal to it, as well as the sum of the income received from the civil law contract for each disabled person who	o_pay_150_percent

"""
150 percent of the sum of the salary and other equivalent fees, as well as of the total incomes derived from a civil law contract, calculated for each person with disabilities 
(including those employed on a concurrent basis), or who performs works based on a civil law contract;

"""

# New Policy Variable
@iterate_jit(nopython=True)
def calc_o_pay_150_percent_fun(o_pay_150_percent, toggle_o_pay, calc_o_pay_150_percent):
    calc_o_pay_150_percent = o_pay_150_percent * toggle_o_pay
    return calc_o_pay_150_percent




# 82 Calculated column

@iterate_jit(nopython=True)
def calc_o_pay_other_fun(o_pay_other, calc_dep, calc_o_pay_other):
    calc_o_pay_other = (
        o_pay_other+calc_dep
    )
    return calc_o_pay_other


# 83. Total other payments (the sum of other deductions specified in points 68-82)
@iterate_jit(nopython=True)
def calc_other_pay_fun(o_pay_invalid, o_pay_bad_debt, o_pay_bad_debt_excess, o_pay_repaying,
                        o_pay_possible_loss, o_pay_insurance_reinsurance, o_pay_technical_reserve,
                        o_pay_loss_counterfeit, o_pay_tax_loss, calc_o_pay_value_of_assets, calc_o_pay_150_percent,
                        o_pay_derivative_settlement, o_pay_resident_dividends, o_pay_voluntary_pension,
                        calc_o_pay_other,calc_other_pay):
    calc_other_pay = (
        o_pay_invalid + o_pay_bad_debt + o_pay_bad_debt_excess + o_pay_repaying +
        o_pay_possible_loss + o_pay_insurance_reinsurance + o_pay_technical_reserve +
        o_pay_loss_counterfeit + o_pay_tax_loss + calc_o_pay_value_of_assets + calc_o_pay_150_percent +
        o_pay_derivative_settlement + o_pay_resident_dividends + o_pay_voluntary_pension +
        calc_o_pay_other
    )
    return calc_other_pay

'''

Other deductions 


'''


#  84.Total deductions ([point 62] + [point 67] + [point 83])

# New Policy Variable
@iterate_jit(nopython=True)
def calc_total_ded_fun(calc_exp, calc_loss, calc_other_pay, toggle_calc_total_ded,calc_total_ded ):
    calc_total_ded = (calc_exp + calc_loss + calc_other_pay)*toggle_calc_total_ded
    return calc_total_ded



# 84. 1).  Reductions in licensing activities 	ded_total_licensing
# New Policy Variable
@iterate_jit(nopython=True)
def calc_ded_total_licensing_fun(ded_total_licensing,toggle_ded_total_licensing,calc_ded_total_licensing):
    calc_ded_total_licensing = ded_total_licensing*toggle_ded_total_licensing
    return calc_ded_total_licensing

# 84. 2). Deductions from joint activities (cooperation)	ded_total_joint_activities
# New Policy Variable (not affect other variables)
@iterate_jit(nopython=True)
def calc_ded_total_joint_activities_fun(ded_total_joint_activities, toggle_ded_total_joint_act, calc_ded_total_joint_act):
    calc_ded_total_joint_act = ded_total_joint_activities*toggle_ded_total_joint_act
    return calc_ded_total_joint_act


#84. 3). Deductions related to organization of production within the framework of economic activities carried out in border settlements included in the list approved by the GoA	ded_total_org_production_border
# New Policy Variable
@iterate_jit(nopython=True)
def calc_ded_total_org_production_border_fun(ded_total_org_production_border, toggle_ded_tot_org_prod_border, calc_ded_total_joint_act):
    calc_ded_total_org_production_border = ded_total_org_production_border*toggle_ded_tot_org_prod_border
    return calc_ded_total_org_production_border



# 85.Taxable profit or tax loss (([point 41] - [point 41 subpoint 1] - [point 41 subpoint 3]) +  ([point 84] [point 84 subpoint 1] - [point 84 subpoint 3]))
@iterate_jit(nopython=True)
def calc_taxable_profit_loss_fun(inc_total, inc_licensing, inc_border, calc_total_ded, calc_ded_total_licensing, calc_ded_total_org_production_border,calc_taxable_profit_loss):
    calc_taxable_profit_loss = (
        (inc_total - inc_licensing - inc_border) + (calc_total_ded - calc_ded_total_licensing - calc_ded_total_org_production_border)
    )
    return calc_taxable_profit_loss


# 86. Insentives/privileges for the reduction of taxable profit (including the exemption of income from payment of profit tax)	incentives_tax_reduction


# New Policy Variable
@iterate_jit(nopython=True)
def calc_incentives_tax_reduction_fun(incentives_tax_reduction, toggle_incentives_tax_reduction, calc_incentives_tax_reduction):
    calc_incentives_tax_reduction = incentives_tax_reduction*toggle_incentives_tax_reduction
    return calc_incentives_tax_reduction

# Tax base for calculation of CIT
# 86. Taxable profit considering incentives for reducing taxable profits (including  exemption from profit tax)  ([point 85] + [point 86]) if [point 85]>0 and ([point 85] + [point 86]))
# new aproach
@iterate_jit(nopython=True)
def taxable_profit_with_incentives_fun(calc_taxable_profit_loss,calc_incentives_tax_reduction,calc_taxable_profit_with_incentives):
    calc_taxable_profit_with_incentives= calc_taxable_profit_loss+calc_incentives_tax_reduction
    if calc_taxable_profit_with_incentives > 0 and calc_taxable_profit_loss > 0:
        return calc_taxable_profit_with_incentives
    else:
        calc_taxable_profit_with_incentives=0
        return (calc_taxable_profit_with_incentives)

# 87. Estimation of Taxable profit 
@iterate_jit(nopython=True)
def profit_tax_reporting_fun(calc_taxable_profit_with_incentives,cit_tax_rate,calc_profit_tax_reporting):
    calc_profit_tax_reporting = calc_taxable_profit_with_incentives*cit_tax_rate    
    return calc_profit_tax_reporting

# 89. The amount of profit tax reduced as a result of the incentives/privileges of profit tax reduction of a resident profit tax payer implementing a business project approved by the decision of the Government of the Republic of Armenia	profit_tax_reduction_projects
# New Policy Variable
@iterate_jit(nopython=True)
def calc_profit_tax_reduction_projects_fun(profit_tax_reduction_projects, toggle_profit_tax_reduction_projects, calc_profit_tax_reduction_projects):
    calc_profit_tax_reduction_projects = profit_tax_reduction_projects*toggle_profit_tax_reduction_projects
    return calc_profit_tax_reduction_projects

# 90. The amount of profit tax that can be reduced as a result of the incentive/privilege of profit tax reduction to the citizens of certain groups by law or in the cases defined by law, at discount rates established by the decision of the GoA or to a resident profit taxpayer providing free services.	profit_tax_reduction_citizens
# New Policy Variable
@iterate_jit(nopython=True)
def calc_profit_tax_reduction_citizens_fun(profit_tax_reduction_citizens, toggle_profit_tax_reduction_citizens, calc_profit_tax_reduction_citizens):
    calc_profit_tax_reduction_citizens= profit_tax_reduction_citizens*toggle_profit_tax_reduction_citizens
    return calc_profit_tax_reduction_citizens


#  91. The amount of profit tax that is reduced as a result of the total profit tax reduction benefit ([point 89] + [point 90])
@iterate_jit(nopython=True)
def calc_income_tax_ded_fun(calc_profit_tax_reduction_projects, calc_profit_tax_reduction_citizens,calc_income_tax_ded):
    calc_income_tax_ded = calc_profit_tax_reduction_projects+calc_profit_tax_reduction_citizens
    return calc_income_tax_ded


# CIT output
# 92 The amount of profit tax after deducting profit tax benefit (([point 88] + [point 91]), if ([point 88] + [point 91])>0, or 0)

#@iterate_jit(nopython=True)
# def profit_tax_after_ded_fun(calc_profit_tax_reporting,income_tax_ded):
#     calc_profit_tax_after_ded= calc_profit_tax_reporting+income_tax_ded
#     if calc_profit_tax_after_ded > 0:
#         return calc_profit_tax_after_ded
#     else:
#         calc_profit_tax_after_ded=0
#         return (calc_profit_tax_after_ded)
@iterate_jit(nopython=True)
def cit_liability(calc_profit_tax_reporting,income_tax_ded,citax):
    citax= calc_profit_tax_reporting+income_tax_ded
    if citax > 0:
        return citax
    else:
        citax=0
        return (citax)
    
   

    

# 95 The amount of profit tax charged in foreign countries or other tax calculated on profit from the profit tax of the reporting year(([point 93] + [point 94]), if ([point 93]+[point 94])<[point 92], or [point 92])**
@iterate_jit(nopython=True)
def reduced_income_foreign_profits_fun(foreign_tax_ded_previous, foreign_tax_ded_reporting, profit_tax_after_ded):
    calc_reduced_income_foreign_profits = foreign_tax_ded_previous + foreign_tax_ded_reporting

    if calc_reduced_income_foreign_profits < profit_tax_after_ded:
        return calc_reduced_income_foreign_profits
    else:
        calc_reduced_income_foreign_profits=profit_tax_after_ded
        return (calc_reduced_income_foreign_profits)


# 96 The amount of profit tax or other tax calculated on profits in foreign countries carried over to subsequent years (([point 93] + [point 94] – [point 95]), if ([point 93] + [point 94] – [point 95])<0, or 0)**
@iterate_jit(nopython=True)
def calc_tax_foreign_profits_carried_over_fun(foreign_tax_ded_previous,foreign_tax_ded_reporting, reduced_income_foreign_profits):
    calc_tax_foreign_profits_carried_over = (foreign_tax_ded_previous + foreign_tax_ded_reporting)-reduced_income_foreign_profits
    if calc_tax_foreign_profits_carried_over < 0:
        return calc_tax_foreign_profits_carried_over
    else:
        calc_tax_foreign_profits_carried_over=0
        return (calc_tax_foreign_profits_carried_over)


# 98   Profit tax amount after deductions (([point 92] + [point 95] + [point 97]), if ([point 92] + [point 95] + [point 97])>0, or 0)
@iterate_jit(nopython=True)
def profit_tax_after_deductions_fun(profit_tax_after_ded,reduced_income_foreign_profits,profit_tax_withheld_tax_agent):
    calc_profit_tax_after_deductions= profit_tax_after_ded + reduced_income_foreign_profits + profit_tax_withheld_tax_agent
    if calc_profit_tax_after_deductions > 0:
        return calc_profit_tax_after_deductions
    else:
        calc_profit_tax_after_deductions=0
        return (calc_profit_tax_after_deductions)


# 100 Total sum of profit tax ([point 98] + [point 99]) calc_total_profit_tax= (profit_tax_after_deductions+profit_tax_non_attributable )
@iterate_jit(nopython=True)
def calc_total_profit_tax_fun(profit_tax_after_deductions, profit_tax_non_attributable,calc_total_profit_tax):
    calc_total_profit_tax = profit_tax_after_deductions+profit_tax_non_attributable
    return calc_total_profit_tax


# 102 The amount of profit tax after reducing the sum of calculated advance payments of profit tax in the reporting year (([point 100] + [point 101]), if ([point 100] + [point 101])>0, or 0)
@iterate_jit(nopython=True)
def profit_tax_after_ded_adv_pay_fun(total_profit_tax,total_advance_pay):
    calc_profit_tax_after_ded_adv_pay= total_profit_tax + total_advance_pay
    if calc_profit_tax_after_ded_adv_pay > 0:
        return calc_profit_tax_after_ded_adv_pay
    else:
        calc_profit_tax_after_ded_adv_pay=0
        return (calc_profit_tax_after_ded_adv_pay)


# 104 The amount of profit tax payable # (([point 102] + [point 103]), if ([point 102] + [point 103])>0, or 0)**
@iterate_jit(nopython=True)
def profit_tax_payable_fun(profit_tax_after_ded_adv_pay,min_profit_tax_not_ded,calc_profit_tax_payable):
    calc_profit_tax_payable= profit_tax_after_ded_adv_pay + min_profit_tax_not_ded
    if calc_profit_tax_payable > 0:
        return calc_profit_tax_payable
    else:
        calc_profit_tax_payable=0
        return calc_profit_tax_payable  
# def cit_liability(profit_tax_after_ded_adv_pay,min_profit_tax_not_ded):
#     citax= profit_tax_after_ded_adv_pay + min_profit_tax_not_ded
#     if citax > 0:
#         return citax
#     else:
#         citax=0
#         return citax
    

# 105 The amount of non-offset minimum profit tax carried over to subsequent years (([point 102]+[point 103]), if ([point 102] + [point 103]<0), or 0)**
@iterate_jit(nopython=True)
def min_inc_tax_carried_over_fun(profit_tax_after_ded_adv_pay,min_profit_tax_not_ded):
    calc_min_inc_tax_carried_over= profit_tax_after_ded_adv_pay + min_profit_tax_not_ded
    if calc_min_inc_tax_carried_over < 0:
        return calc_min_inc_tax_carried_over
    else:
        calc_min_inc_tax_carried_over=0
        return (calc_min_inc_tax_carried_over)


# 106 The amount of profit tax to be reimbursed from the budget (([point 88] + [point 91] + [point 95] + [point 97] + [point 99] + [point 101]), if ([point 88] + [point 91] + [point 95] + [point 97] + [point 99] + [point 101])<0, or 0)**
@iterate_jit(nopython=True)
def profit_tax_reimbursed_budget_fun(calc_profit_tax_reporting,income_tax_ded,reduced_income_foreign_profits,profit_tax_withheld_tax_agent,profit_tax_non_attributable,total_advance_pay):
    calc_profit_tax_reimbursed_budget= calc_profit_tax_reporting+income_tax_ded+reduced_income_foreign_profits+profit_tax_withheld_tax_agent+profit_tax_non_attributable+total_advance_pay
    if calc_profit_tax_reimbursed_budget < 0:
        return calc_profit_tax_reimbursed_budget
    else:
        calc_profit_tax_reimbursed_budget=0
        return (calc_profit_tax_reimbursed_budget)


'''
           Section 2.
 
Income not attributed to the permanent establishment received by a non-resident profit taxpayers carrying out activities in the Republic of Armenia 
through a permanent establishment, who are not considered tax agents, and the amounts of profit tax calculated with respect to them

'''
@iterate_jit(nopython=True)
def calc_other_revenues_fun(inc_001_ins_ben, inc_002_reins_premiums, inc_003_rev_trans, inc_004_div,
                        inc_005_interests, inc_006_royalties, inc_007_rental_fees,
                        inc_008_inc_value_assets, inc_009_inc_value_assets_sale_securities,
                        inc_010_div_received_pan_armenian, inc_099_other_revenues_RA,calc_inc_total_0):
    calc_inc_total_0 = (
        inc_001_ins_ben + inc_002_reins_premiums + inc_003_rev_trans + inc_004_div +
        inc_005_interests + inc_006_royalties + inc_007_rental_fees +
        inc_008_inc_value_assets + inc_009_inc_value_assets_sale_securities +
        inc_010_div_received_pan_armenian + inc_099_other_revenues_RA
    )
    return calc_inc_total_0


@iterate_jit(nopython=True)
def calc_other_revenues_1_fun(inc_001_ins_ben_1, inc_002_reins_premiums_1, inc_003_rev_trans_1, inc_004_div_1,
                          inc_005_interests_1, inc_006_royalties_1, inc_007_rental_fees_1,
                          inc_008_inc_value_assets_1, inc_009_inc_value_assets_sale_securities_1,
                          inc_010_div_received_pan_armenian_bank_1, inc_099_other_revenues_RA_1,calc_inc_total_1):
    calc_inc_total_1 = (
        inc_001_ins_ben_1 + inc_002_reins_premiums_1 + inc_003_rev_trans_1 + inc_004_div_1 +
        inc_005_interests_1 + inc_006_royalties_1 + inc_007_rental_fees_1 +
        inc_008_inc_value_assets_1 + inc_009_inc_value_assets_sale_securities_1 +
        inc_010_div_received_pan_armenian_bank_1 + inc_099_other_revenues_RA_1
    )
    return calc_inc_total_1

@iterate_jit(nopython=True)
def calc_other_revenues_2_fun(inc_001_ins_ben_2, inc_002_reins_premiums_2, inc_003_rev_trans_2, inc_004_div_2,
                          inc_005_interests_2, inc_006_royalties_2, inc_007_rental_fees_2,
                          inc_008_inc_value_assets_2, inc_009_inc_value_assets_sale_securities_2,
                          inc_010_div_received_pan_armenian_bank_2, inc_099_other_revenues_RA_2,calc_inc_total_2):
    calc_inc_total_2 = (
        inc_001_ins_ben_2 + inc_002_reins_premiums_2 + inc_003_rev_trans_2 + inc_004_div_2 +
        inc_005_interests_2 + inc_006_royalties_2 + inc_007_rental_fees_2 +
        inc_008_inc_value_assets_2 + inc_009_inc_value_assets_sale_securities_2 +
        inc_010_div_received_pan_armenian_bank_2 + inc_099_other_revenues_RA_2
    )
    return calc_inc_total_2

@iterate_jit(nopython=True)
def calc_other_revenues_3_fun(inc_001_ins_ben_3, inc_002_reins_premiums_3, inc_003_rev_trans_freight_3,
                          inc_004_div_3, inc_005_interests_3, inc_006_royalties_3,
                          inc_007_rental_fees_3, inc_008_inc_value_assets_3,
                          inc_009_inc_value_assets_sale_securities_3,
                          inc_10_div_received_pan_armenian_bank_3, inc_099_other_revenues_RA_3,calc_inc_total_3):
    calc_inc_total_3 = (
        inc_001_ins_ben_3 + inc_002_reins_premiums_3 + inc_003_rev_trans_freight_3 +
        inc_004_div_3 + inc_005_interests_3 + inc_006_royalties_3 +
        inc_007_rental_fees_3 + inc_008_inc_value_assets_3 +
        inc_009_inc_value_assets_sale_securities_3 +
        inc_10_div_received_pan_armenian_bank_3 + inc_099_other_revenues_RA_3
    )
    return calc_inc_total_3


@iterate_jit(nopython=True)
def calc_total_profit_tax_amount_fun(inc_total_1, inc_total_3,calc_total_profit_tax_amount):
    calc_total_profit_tax_amount = (
        inc_total_1+inc_total_3
    )
    return calc_total_profit_tax_amount




'''
-------------------------------------------------------------------------------------
II. TURNOVER TAX CALCULATION 
-------------------------------------------------------------------------------------
'''

# 5.3. Amount of tax calculated for the reporting quarter in terms of income from commercial (purchase and sale) activities (5.3 = 5.1 x 5.2) 
@iterate_jit(nopython=True)
def calc_tax_calc_comm_q_fun(rev_comm_q,tax_rate_comm_q,calc_tax_calc_comm_q):
    calc_tax_calc_comm_q = rev_comm_q*tax_rate_comm_q    
    return calc_tax_calc_comm_q


#  5.6. Amount deducted from the amount of tax in the reporting quarter (5.6 = 5.4 x 5.5) 
@iterate_jit(nopython=True)
def calc_amount_ded_tax_q_fun(exp_purchase_q,rate_exp_ded_tax_calc,calc_amount_ded_tax_q):
    calc_amount_ded_tax_q = exp_purchase_q*rate_exp_ded_tax_calc    
    return calc_amount_ded_tax_q



# 5.8. Total amount to be deducted from the amount of tax in the reporting quarter (5.8 = 5.6 + 5.7)
@iterate_jit(nopython=True)
def calc_total_ded_tax_q_fun(amount_ded_tax_q, unded_trans_tax_prev_q,calc_total_ded_tax_q):
    calc_total_ded_tax_q = (
        amount_ded_tax_q+unded_trans_tax_prev_q
    )
    return calc_total_ded_tax_q



# 5.10. Amount of tax payable calculated for the reporting quarter (if (5.3-5.8) < 5.9, then 5.10=5.9, if (5.3-5.8)≥ 5.9, then 5.10=(5.3-5.8 ).(if (5.3-5.8) < 5.9, then 5.10=5.9, if (5.3-5.8)≥ 5.9, then 5.10=(5.3-5.8 )
@iterate_jit(nopython=True)
def calc_turnover_q_fun(tax_calc_comm_q,total_ded_tax_q,min_tax_q_1_5pct,calc_tax_payable_calc_q):
    calc1 = tax_calc_comm_q
    calc2 = total_ded_tax_q
    calc3 = min_tax_q_1_5pct
    calc4 = tax_calc_comm_q - total_ded_tax_q

    if calc4 < calc3:
        calc_tax_payable_calc_q = calc3
    else:
        calc_tax_payable_calc_q = calc4

    return calc_tax_payable_calc_q

# 5.11. Amount that cannot be deducted from the amount of tax and transferred to the next quarters in terms of the costs of purchasing goods (if (5.3-5.8)<5.9, then 5.11=[5.8-(5.3-5.9)], if (5.3-5.8) ≥ 5.9 then 5.11=0)
@iterate_jit(nopython=True)
def unded_trans_tax_next_q_purchase_fun(tax_calc_comm_q,total_ded_tax_q,min_tax_q_1_5pct,):
    calc1 = tax_calc_comm_q
    calc2 = total_ded_tax_q
    calc3 = min_tax_q_1_5pct
    calc4 = calc1 - calc2
    calc5 = calc2 - (calc1 - calc3)

    if calc4 < calc3:
        calc_unded_trans_tax_next_q_purchase = calc5
    else:
        calc_unded_trans_tax_next_q_purchase = 0

    return calc_unded_trans_tax_next_q_purchase


# 6.3. Tax amount on income from activities in the field of public catering (6.3 = 6.1 x 6.2) 
@iterate_jit(nopython=True)
def calc_tax_calc_pub_cater_q_fun(rev_pub_cater_q,tax_rate_pub_cater_q,calc_tax_calc_pub_cater_q):
    calc_tax_calc_pub_cater_q = rev_pub_cater_q*tax_rate_pub_cater_q    
    return calc_tax_calc_pub_cater_q

# 6.6. Amount deducted from the amount of tax in the reporting quarter (6.6 = 6.4 x 6.5) 
@iterate_jit(nopython=True)
def calc_amount_ded_tax_q_1_fun(rate_exp_ded_tax_calc_pub_cater,exp_activities_pub_cater_q,calc_amount_ded_tax_q_1):
    calc_amount_ded_tax_q_1 = exp_activities_pub_cater_q*rate_exp_ded_tax_calc_pub_cater
    return calc_amount_ded_tax_q_1


# 6.8 Amount of tax payable calculated for the reporting quarter  (if (6.3-6.6) < 6.7, then 6.8=6.7, if (6.3-6.6)≥ 6.7, then 6.8=(6.3-6.6 )
@iterate_jit(nopython=True)
def tax_payable_calc_q_fun(tax_calc_pub_cater_q,amount_ded_tax_q_1,min_tax_accounting_q_4pct,calc_tax_payable_calc_q_1):
    calc1 = tax_calc_pub_cater_q
    calc2 = amount_ded_tax_q_1
    calc3 = min_tax_accounting_q_4pct
    calc4 = calc1 - calc2
    calc5 = calc2 - (calc1 - calc3)

    if calc4 < calc3:
        calc_tax_payable_calc_q_1 = calc3
    else:
        calc_tax_payable_calc_q_1 = calc4

    return calc_tax_payable_calc_q_1

#  column [C] = column [A] x column [B]).
@iterate_jit(nopython=True)
def calc_to_tax_amount_fun(to_rate,to_income,calc_to_tax_amount):
    calc_to_tax_amount = to_income*to_rate
    return calc_to_tax_amount


#  Tax amount.1 Sum total of points of 7-16 of column [A]
@iterate_jit(nopython=True)
def calc_to_tax_amount_1_fun(to_rate_1,to_income_1,calc_to_tax_amount_1):
    calc_to_tax_amount_1 = to_income_1*to_rate_1
    return calc_to_tax_amount_1


#  # **Tax amount.2**
@iterate_jit(nopython=True)
def calc_to_tax_amount_2_fun(to_rate_1,to_income_2,calc_to_tax_amount_2):
    calc_to_tax_amount_2 = to_income_2*to_rate_1
    return calc_to_tax_amount_2


#  # **Tax amount.3 **
@iterate_jit(nopython=True)
def calc_to_tax_amount_3_fun(to_rate_2,to_income_3,calc_to_tax_amount_3):
    calc_to_tax_amount_3 = to_income_3*to_rate_2
    return calc_to_tax_amount_3


#  Tax amount.4
@iterate_jit(nopython=True)
def calc_to_tax_amount_4_fun(to_rate_3,to_income_4,calc_to_tax_amount_4):
    calc_to_tax_amount_4 = to_income_4*to_rate_3
    return calc_to_tax_amount_4

#  Tax amount.5
@iterate_jit(nopython=True)
def calc_to_tax_amount_5_fun(to_rate_4,to_income_5,calc_to_tax_amount_5):
    calc_to_tax_amount_5 = to_income_5*to_rate_4
    return calc_to_tax_amount_5

#  Tax amount.6
@iterate_jit(nopython=True)
def calc_to_tax_amount_6_fun(to_rate_5,to_income_6,calc_to_tax_amount_6):
    calc_to_tax_amount_6 = to_income_6*to_rate_5
    return calc_to_tax_amount_6

#  Tax amount.7
@iterate_jit(nopython=True)
def calc_to_tax_amount_7_fun(to_rate_6,to_income_7,calc_to_tax_amount_7):
    calc_to_tax_amount_7 = to_income_7*to_rate_6
    return calc_to_tax_amount_7


#  Tax amount.8
@iterate_jit(nopython=True)
def calc_to_tax_amount_8_fun(to_rate_7,to_income_8,calc_to_tax_amount_8):
    calc_to_tax_amount_8 = to_income_8*to_rate_7
    return calc_to_tax_amount_8


#  Tax amount.9
@iterate_jit(nopython=True)
def calc_to_tax_amount_9_fun(to_rate_7,to_income_9,calc_to_tax_amount_9):
    calc_to_tax_amount_9 = to_income_9*to_rate_7
    return calc_to_tax_amount_9

# Tax amount.10
@iterate_jit(nopython=True)
def calc_sales_turn_rev_all_act_fun(to_income_10,rev_articles_19_7_19_8,rev_turn_tax_priv_retail_sales_population,rev_sale_prod_org_turn_tax_priv_border_sett,rev_act_public_catering_turn_tax_priv_border_sett):
    calc_sales_turn_rev_all_act = (
       to_income_10 + rev_articles_19_7_19_8 + rev_turn_tax_priv_retail_sales_population + rev_sale_prod_org_turn_tax_priv_border_sett + rev_act_public_catering_turn_tax_priv_border_sett
    )
    return calc_sales_turn_rev_all_act



# @iterate_jit(nopython=True)
# def Net_accounting_profit(sch1_profit_loss_before_tax, Net_accounting_profit):
#     """
#     Compute accounting profit from business
#     """
#     Net_accounting_profit = sch1_profit_loss_before_tax
#     return Net_accounting_profit


# @iterate_jit(nopython=True)
# def Total_additions_to_GP(sch1_tot_amt_added, Total_additions_to_GP):
#     """
#     Compute accounting profit from business
#     """
#     Total_additions_to_GP = sch1_tot_amt_added
#     return Total_additions_to_GP


# '''
# -------------------------------------------------------------------------------------
# Calculation of Depreciation Allowance - Plant & M/c
# -------------------------------------------------------------------------------------
# '''

# # @iterate_jit(nopython=True)
# # def Op_wdv_pm(sch2_wdv_beg_year_class_40, sch2_wdv_beg_year_class_35, sch2_wdv_beg_year_class_30,
# #               sch2_wdv_beg_year_class_20, Op_wdv_pm40, Op_wdv_pm35, Op_wdv_pm30, Op_wdv_pm20):
# #     """
# #     Return the opening WDV of each asset class.
# #     """
# #     Op_wdv_pm40 = sch2_wdv_beg_year_class_40
# #     Op_wdv_pm35 = sch2_wdv_beg_year_class_35
# #     Op_wdv_pm30 = sch2_wdv_beg_year_class_30
# #     Op_wdv_pm20 = sch2_wdv_beg_year_class_20
# #     return (Op_wdv_pm40, Op_wdv_pm35, Op_wdv_pm30, Op_wdv_pm20)


# @iterate_jit(nopython=True)
# def Init_allow_PM(gross_add_pm40, gross_add_pm35, gross_add_pm30, gross_add_pm20,
#                   rate_init_allow_pm40, rate_init_allow_pm35, rate_init_allow_pm30, 
#                   rate_init_allow_pm20, init_allow_pm40, init_allow_pm35, init_allow_pm30, 
#                   init_allow_pm20, ia_allowed_pm40, ia_allowed_pm35, ia_allowed_pm30, 
#                   ia_allowed_pm20, total_init_allow_pm):
#     """
#     Return the initial allowance for each asset class.
#     """
#     init_allow_pm40 = gross_add_pm40 * rate_init_allow_pm40*ia_allowed_pm40
#     init_allow_pm35 = gross_add_pm35 * rate_init_allow_pm35*ia_allowed_pm35
#     init_allow_pm30 = gross_add_pm30 * rate_init_allow_pm30*ia_allowed_pm30
#     init_allow_pm20 = gross_add_pm20 * rate_init_allow_pm20*ia_allowed_pm20
#     total_init_allow_pm = init_allow_pm20 + init_allow_pm30 + init_allow_pm35 + init_allow_pm40
#     return (init_allow_pm40, init_allow_pm35, init_allow_pm30, init_allow_pm20, total_init_allow_pm)


# @iterate_jit(nopython=True)
# def Disposal_PM(sch2_dispsl_class_40, sch2_dispsl_class_35, sch2_dispsl_class_30,
#                 sch2_dispsl_class_20, disp_pm40, disp_pm35, disp_pm30, disp_pm20):
#     """
#     Return the disposal of each asset class.
#     """
#     disp_pm40 = sch2_dispsl_class_40
#     disp_pm35 = sch2_dispsl_class_35
#     disp_pm30 = sch2_dispsl_class_30
#     disp_pm20 = sch2_dispsl_class_20
#     return(disp_pm40, disp_pm35, disp_pm30, disp_pm20)
    

# @iterate_jit(nopython=True)
# def Depr_PM(Op_wdv_pm40, Op_wdv_pm35, Op_wdv_pm30, Op_wdv_pm20,
#             sch2_addinit_during_yr_class_40, sch2_addinit_during_yr_class_35, 
#             sch2_addinit_during_yr_class_30, sch2_addinit_during_yr_class_20,
#             disp_pm40, disp_pm35, disp_pm30, disp_pm20,
#             depr_pm40, depr_pm35, depr_pm30, depr_pm20, asset_use_ratio, 
#             gross_add_pm40, gross_add_pm35, gross_add_pm30, gross_add_pm20,
#             rate_depr_pm40, rate_depr_pm35, rate_depr_pm30, rate_depr_pm20, 
#             ia_allowed_pm40, ia_allowed_pm35, ia_allowed_pm30, ia_allowed_pm20, total_depr_pm):
#     """
#     Return the depreciation for each asset class.
#     """
#     depr_pm40 = max((Op_wdv_pm40 + sch2_addinit_during_yr_class_40 + gross_add_pm40*(1- ia_allowed_pm40) - disp_pm40), 0)*rate_depr_pm40*asset_use_ratio
#     depr_pm35 = max((Op_wdv_pm35 + sch2_addinit_during_yr_class_35 + gross_add_pm35*(1- ia_allowed_pm35) - disp_pm35), 0)*rate_depr_pm35*asset_use_ratio
#     depr_pm30 = max((Op_wdv_pm30 + sch2_addinit_during_yr_class_30 + gross_add_pm30*(1 - ia_allowed_pm30) - disp_pm30), 0)*rate_depr_pm30*asset_use_ratio
#     depr_pm20 = max((Op_wdv_pm20 + sch2_addinit_during_yr_class_20 + gross_add_pm20*(1 - ia_allowed_pm20) - disp_pm20), 0)*rate_depr_pm20*asset_use_ratio
#     total_depr_pm = depr_pm40 + depr_pm35 + depr_pm30 + depr_pm20
#     return(depr_pm40, depr_pm35, depr_pm30, depr_pm20, total_depr_pm)


# @iterate_jit(nopython=True)
# def Cl_WDV_PM(Op_wdv_pm40, Op_wdv_pm35, Op_wdv_pm30, Op_wdv_pm20,
#               sch2_addinit_during_yr_class_40, sch2_addinit_during_yr_class_35, 
#               sch2_addinit_during_yr_class_30, sch2_addinit_during_yr_class_20,
#               gross_add_pm40, gross_add_pm35, gross_add_pm30, gross_add_pm20,
#               disp_pm40, disp_pm35, disp_pm30, disp_pm20,
#               depr_pm40, depr_pm35, depr_pm30, depr_pm20,
#               Cl_wdv_pm40, Cl_wdv_pm35, Cl_wdv_pm30, Cl_wdv_pm20):
#     """
#     Return the closing written down value for each PM asset class.
#     """
#     Cl_wdv_pm40 = max(Op_wdv_pm40 + sch2_addinit_during_yr_class_40 + gross_add_pm40 - disp_pm40 - depr_pm40, 0)
#     Cl_wdv_pm35 = max(Op_wdv_pm35 + sch2_addinit_during_yr_class_35 + gross_add_pm35 - disp_pm35 - depr_pm35, 0)
#     Cl_wdv_pm30 = max(Op_wdv_pm30 + sch2_addinit_during_yr_class_30 + gross_add_pm30 - disp_pm30 - depr_pm30, 0)
#     Cl_wdv_pm20 = max(Op_wdv_pm20 + sch2_addinit_during_yr_class_20 + gross_add_pm20 - disp_pm20 - depr_pm20, 0)
#     return (Cl_wdv_pm40, Cl_wdv_pm35, Cl_wdv_pm30, Cl_wdv_pm20)



# '''
# -------------------------------------------------------------------------------------
# Calculation of Initial Allowance and Industrial Building Deduction - Buildings
# -------------------------------------------------------------------------------------
# '''


# @iterate_jit(nopython=True)
# def Init_allow_bld(addition_bld, rate_init_allow_bld, ia_allowed_bld, init_allow_bld):
#     """
#     Return the initial allowance for building.
#     """
#     init_allow_bld = addition_bld * rate_init_allow_bld*ia_allowed_bld
#     return init_allow_bld


# @iterate_jit(nopython=True)
# def Depr_bld(Op_bal_bld, rate_depr_bld, ia_allowed_bld, addition_bld, depr_bld):
#     """
#     Return the depreciation for building.
#     """
#     depr_bld = Op_bal_bld * rate_depr_bld  + addition_bld * rate_depr_bld*(1 - ia_allowed_bld)
#     return depr_bld

# @iterate_jit(nopython=True)
# def Cl_bal_bld(Op_bal_bld, addition_bld, Cl_bal_bld):
#     """
#     Return the opening WDV of each asset class.
#     """
#     Cl_bal_bld = Op_bal_bld + addition_bld
#     return Cl_bal_bld


# '''
# -------------------------------------------------------------------------------------
# Calculation of profit chargeable to tax
# -------------------------------------------------------------------------------------
# '''

# @iterate_jit(nopython=True)
# def Depr_cap_deductions(total_depr_pm, depr_bld, total_init_allow_pm, init_allow_bld, 
#                    sch2_startup_cost, sch2_intangible_asset, sch2_deduction_acquisition, depr_cap_allow):
#     """
#     Compute Schedule 2 Depreciation and Capital Allowances
#     """
#     depr_cap_allow = total_depr_pm + depr_bld + total_init_allow_pm + init_allow_bld + \
#                      sch2_startup_cost + sch2_intangible_asset + sch2_deduction_acquisition
                     
#     return depr_cap_allow


# @iterate_jit(nopython=True)
# def Total_subtractions_from_GP(sch1_exmpt_incm_less, sch1_insurance_incm, sch1_mining_incm, 
#                                sch1_profit_depreciate_asset, sch1_research_expense,
#                                sch1_unreal_forex_less, sch1_total_witheld_incm, sch1_total_othr_allow_ded,
#                                depr_cap_allow,Total_subtractions_from_GP):
#     """
#     Compute total taxable profits afer adding back non-allowable deductions.
#     """
#     Total_subtractions_from_GP = sch1_exmpt_incm_less + sch1_insurance_incm + sch1_mining_incm + \
#                                  sch1_profit_depreciate_asset + sch1_research_expense + \
#                                  sch1_unreal_forex_less + sch1_total_witheld_incm + sch1_total_othr_allow_ded + \
#                                  depr_cap_allow
    
#     return Total_subtractions_from_GP


# '''
# -------------------------------------------------------------------------------------
# Calculation of income from Capital Gains
# -------------------------------------------------------------------------------------
# '''

# @iterate_jit(nopython=True)
# def Income_Cap_Gains(sch1_incm_capital_gain, sch1_capital_losses, income_capgains):
#     """
#     Compute total taxable profits afer adding back non-allowable deductions.
#     """
#     income_capgains = sch1_incm_capital_gain - sch1_capital_losses
#     return income_capgains



# @iterate_jit(nopython=True)
# def Taxable_profit(Net_accounting_profit, Total_additions_to_GP, Total_subtractions_from_GP, 
#                    income_capgains, taxable_profit):
#     """
#     Compute total taxable profits afer adding back non-allowable deductions.
#     """
#     taxable_profit = Net_accounting_profit + Total_additions_to_GP - Total_subtractions_from_GP + income_capgains
#     return taxable_profit



# @iterate_jit(nopython=True)
# def BF_loss(sch1_loss_prvs_year, bf_loss):
#     """
#     Compute net taxable profits afer allowing deductions.
#     """
#     bf_loss = sch1_loss_prvs_year
#     return bf_loss

# @iterate_jit(nopython=True)
# def Taxable_profit_after_adjloss(taxable_profit, loss_cf_limit, Loss_lag1, 
#                                  Loss_lag2, Loss_lag3, Loss_lag4, Loss_lag5, Loss_lag6, 
#                                  Loss_lag7, Loss_lag8, Loss_lag9, Loss_lag10, Loss_lag11, Loss_lag12,
#                                  Loss_lag13, Loss_lag14, Loss_lag15, newloss1, newloss2, newloss3, 
#                                  newloss4, newloss5, newloss6, newloss7, newloss8, 
#                                  newloss9, newloss10,  newloss11, newloss12,  newloss13, newloss14, 
#                                  newloss15, Used_loss_total, taxbase_post_loss):
    
#     """
#     Compute net tax base afer allowing donations and losses.
#     """
#     BF_loss = np.array([Loss_lag1, Loss_lag2, Loss_lag3, Loss_lag4, Loss_lag5, Loss_lag6, 
#                         Loss_lag7, Loss_lag8, Loss_lag9, Loss_lag10, Loss_lag11, Loss_lag12, 
#                         Loss_lag13, Loss_lag14, Loss_lag15])
            
#     N = int(loss_cf_limit)
#     Used_loss = np.zeros(N)
    
#     if N == 0:
#         (newloss1, newloss2, newloss3, newloss4, newloss5, newloss6, 
#          newloss7, newloss8, newloss9, newloss10, newloss11, newloss12,  newloss13, newloss14, 
#          newloss15) = np.zeros(15)
#         taxbase_post_loss = taxable_profit
#     else:
#         BF_loss = BF_loss[:N]
                
#         if taxable_profit < 0:
#             CYL = abs(taxable_profit)
        
#         elif taxable_profit >= 0:
#             CYL = 0
#             Cum_used_loss = 0
#             for i in range(N, 0, -1):
#                 GTI = taxable_profit - Cum_used_loss
#                 Used_loss[i-1] = min(BF_loss[i-1], GTI)
#                 Cum_used_loss += Used_loss[i-1]
            
#         New_loss = BF_loss - Used_loss
#         Used_loss_total = Used_loss.sum()
#         taxbase_post_loss = taxable_profit - Used_loss_total
#         newloss1 = CYL
#         (newloss2, newloss3, newloss4, newloss5, newloss6, newloss7, 
#          newloss8, newloss9, newloss10, newloss11, newloss12,  newloss13, newloss14, 
#          newloss15) = np.append(New_loss[:-1], np.zeros(15-N))

#     return (taxbase_post_loss, newloss1, newloss2, newloss3, newloss4, newloss5, newloss6, 
#             newloss7, newloss8, newloss9, newloss10, newloss11, newloss12,  newloss13, newloss14, 
#             newloss15, Used_loss_total)



# @iterate_jit(nopython=True)
# def Net_tax_base_behavior(cit_rate_std, cit_rate_std_curr_law, elasticity_cit_taxable_income_threshold,
#                           elasticity_cit_taxable_income_value, taxbase_post_loss, net_tax_base_behavior):
#     """
#     Compute net taxable profits afer allowing deductions.
#     """
#     NP = taxbase_post_loss
#     elasticity_taxable_income_threshold0 = elasticity_cit_taxable_income_threshold[0]
#     elasticity_taxable_income_threshold1 = elasticity_cit_taxable_income_threshold[1]
#     elasticity_taxable_income_threshold2 = elasticity_cit_taxable_income_threshold[2]
#     elasticity_taxable_income_value0=elasticity_cit_taxable_income_value[0]
#     elasticity_taxable_income_value1=elasticity_cit_taxable_income_value[1]
#     elasticity_taxable_income_value2=elasticity_cit_taxable_income_value[2]
#     if NP<=0:
#         elasticity=0
#     elif NP<elasticity_taxable_income_threshold0:
#         elasticity=elasticity_taxable_income_value0
#     elif NP<elasticity_taxable_income_threshold1:
#         elasticity=elasticity_taxable_income_value1
#     else:
#         elasticity=elasticity_taxable_income_value2

#     frac_change_net_of_cit_rate = ((1-cit_rate_std)-(1-cit_rate_std_curr_law))/(1-cit_rate_std_curr_law) 
#     frac_change_Net_tax_base = elasticity*(frac_change_net_of_cit_rate)
#     net_tax_base_behavior = NP*(1+frac_change_Net_tax_base) 
#     return net_tax_base_behavior


# @iterate_jit(nopython=True)
# def mat_liability(mat_rate, Net_accounting_profit, MAT):
#     """
#     Compute tax liability given the corporate rate
#     """
#     # subtract TI_special_rates from TTI to get Aggregate_Income, which is
#     # the portion of TTI that is taxed at normal rates
#     MAT = mat_rate*Net_accounting_profit
        
#     return MAT

# @iterate_jit(nopython=True)
# def cit_liability(sch4_sch_cntrt_gross_incm, sch5_net_charge_income, 
#                   sch6_net_inc_short_bsns, net_tax_base_behavior, cit_rate_std, 
#                   cit_rate_mining, cit_rate_insurance, cit_rate_ltcontract, MAT, citax):
#     """
#     Compute tax liability given the corporate rate
#     """
#     # subtract TI_special_rates from TTI to get Aggregate_Income, which is
#     # the portion of TTI that is taxed at normal rates
   
#     citax1 = cit_rate_std * max(net_tax_base_behavior, 0)
#     citax2 = cit_rate_mining * max(sch5_net_charge_income, 0)
#     citax3 = cit_rate_insurance*max(sch6_net_inc_short_bsns, 0)
#     citax4 = cit_rate_ltcontract * max(sch4_sch_cntrt_gross_incm, 0)
#     citax = max(citax1 + citax2 + citax3 + citax4, MAT)
#     return citax

# @iterate_jit(nopython=True)
# def Ebdta(Net_accounting_profit, Total_additions_to_GP, Total_subtractions_from_GP, sch1_add_depreciation,
#           sch1_add_strt_up_cost, depr_cap_allow, income_capgains, ebdta):
#     """
#     Compute total taxable profits afer adding back non-allowable deductions.
#     """
#     ebdta = Net_accounting_profit + (Total_additions_to_GP - sch1_add_strt_up_cost - sch1_add_depreciation) + \
#             (Total_subtractions_from_GP - depr_cap_allow) + income_capgains
#     return ebdta