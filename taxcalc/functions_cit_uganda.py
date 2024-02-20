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


@iterate_jit(nopython=True)
def Net_accounting_profit(sch1_profit_loss_before_tax, Net_accounting_profit):
    """
    Compute accounting profit from business
    """
    Net_accounting_profit = sch1_profit_loss_before_tax
    return Net_accounting_profit


@iterate_jit(nopython=True)
def Total_additions_to_GP(sch1_tot_amt_added, Total_additions_to_GP):
    """
    Compute accounting profit from business
    """
    Total_additions_to_GP = sch1_tot_amt_added
    return Total_additions_to_GP


'''
-------------------------------------------------------------------------------------
Calculation of Depreciation Allowance - Plant & M/c
-------------------------------------------------------------------------------------
'''

# @iterate_jit(nopython=True)
# def Op_wdv_pm(sch2_wdv_beg_year_class_40, sch2_wdv_beg_year_class_35, sch2_wdv_beg_year_class_30,
#               sch2_wdv_beg_year_class_20, Op_wdv_pm40, Op_wdv_pm35, Op_wdv_pm30, Op_wdv_pm20):
#     """
#     Return the opening WDV of each asset class.
#     """
#     Op_wdv_pm40 = sch2_wdv_beg_year_class_40
#     Op_wdv_pm35 = sch2_wdv_beg_year_class_35
#     Op_wdv_pm30 = sch2_wdv_beg_year_class_30
#     Op_wdv_pm20 = sch2_wdv_beg_year_class_20
#     return (Op_wdv_pm40, Op_wdv_pm35, Op_wdv_pm30, Op_wdv_pm20)


@iterate_jit(nopython=True)
def Init_allow_PM(gross_add_pm40, gross_add_pm35, gross_add_pm30, gross_add_pm20,
                  rate_init_allow_pm40, rate_init_allow_pm35, rate_init_allow_pm30, 
                  rate_init_allow_pm20, init_allow_pm40, init_allow_pm35, init_allow_pm30, 
                  init_allow_pm20, ia_allowed_pm40, ia_allowed_pm35, ia_allowed_pm30, 
                  ia_allowed_pm20, total_init_allow_pm):
    """
    Return the initial allowance for each asset class.
    """
    init_allow_pm40 = gross_add_pm40 * rate_init_allow_pm40*ia_allowed_pm40
    init_allow_pm35 = gross_add_pm35 * rate_init_allow_pm35*ia_allowed_pm35
    init_allow_pm30 = gross_add_pm30 * rate_init_allow_pm30*ia_allowed_pm30
    init_allow_pm20 = gross_add_pm20 * rate_init_allow_pm20*ia_allowed_pm20
    total_init_allow_pm = init_allow_pm20 + init_allow_pm30 + init_allow_pm35 + init_allow_pm40
    return (init_allow_pm40, init_allow_pm35, init_allow_pm30, init_allow_pm20, total_init_allow_pm)


@iterate_jit(nopython=True)
def Disposal_PM(sch2_dispsl_class_40, sch2_dispsl_class_35, sch2_dispsl_class_30,
                sch2_dispsl_class_20, disp_pm40, disp_pm35, disp_pm30, disp_pm20):
    """
    Return the disposal of each asset class.
    """
    disp_pm40 = sch2_dispsl_class_40
    disp_pm35 = sch2_dispsl_class_35
    disp_pm30 = sch2_dispsl_class_30
    disp_pm20 = sch2_dispsl_class_20
    return(disp_pm40, disp_pm35, disp_pm30, disp_pm20)
    

@iterate_jit(nopython=True)
def Depr_PM(Op_wdv_pm40, Op_wdv_pm35, Op_wdv_pm30, Op_wdv_pm20,
            sch2_addinit_during_yr_class_40, sch2_addinit_during_yr_class_35, 
            sch2_addinit_during_yr_class_30, sch2_addinit_during_yr_class_20,
            disp_pm40, disp_pm35, disp_pm30, disp_pm20,
            depr_pm40, depr_pm35, depr_pm30, depr_pm20, asset_use_ratio, 
            gross_add_pm40, gross_add_pm35, gross_add_pm30, gross_add_pm20,
            rate_depr_pm40, rate_depr_pm35, rate_depr_pm30, rate_depr_pm20, 
            ia_allowed_pm40, ia_allowed_pm35, ia_allowed_pm30, ia_allowed_pm20, total_depr_pm):
    """
    Return the depreciation for each asset class.
    """
    depr_pm40 = max((Op_wdv_pm40 + sch2_addinit_during_yr_class_40 + gross_add_pm40*(1- ia_allowed_pm40) - disp_pm40), 0)*rate_depr_pm40*asset_use_ratio
    depr_pm35 = max((Op_wdv_pm35 + sch2_addinit_during_yr_class_35 + gross_add_pm35*(1- ia_allowed_pm35) - disp_pm35), 0)*rate_depr_pm35*asset_use_ratio
    depr_pm30 = max((Op_wdv_pm30 + sch2_addinit_during_yr_class_30 + gross_add_pm30*(1 - ia_allowed_pm30) - disp_pm30), 0)*rate_depr_pm30*asset_use_ratio
    depr_pm20 = max((Op_wdv_pm20 + sch2_addinit_during_yr_class_20 + gross_add_pm20*(1 - ia_allowed_pm20) - disp_pm20), 0)*rate_depr_pm20*asset_use_ratio
    total_depr_pm = depr_pm40 + depr_pm35 + depr_pm30 + depr_pm20
    return(depr_pm40, depr_pm35, depr_pm30, depr_pm20, total_depr_pm)


@iterate_jit(nopython=True)
def Cl_WDV_PM(Op_wdv_pm40, Op_wdv_pm35, Op_wdv_pm30, Op_wdv_pm20,
              sch2_addinit_during_yr_class_40, sch2_addinit_during_yr_class_35, 
              sch2_addinit_during_yr_class_30, sch2_addinit_during_yr_class_20,
              gross_add_pm40, gross_add_pm35, gross_add_pm30, gross_add_pm20,
              disp_pm40, disp_pm35, disp_pm30, disp_pm20,
              depr_pm40, depr_pm35, depr_pm30, depr_pm20,
              Cl_wdv_pm40, Cl_wdv_pm35, Cl_wdv_pm30, Cl_wdv_pm20):
    """
    Return the closing written down value for each PM asset class.
    """
    Cl_wdv_pm40 = max(Op_wdv_pm40 + sch2_addinit_during_yr_class_40 + gross_add_pm40 - disp_pm40 - depr_pm40, 0)
    Cl_wdv_pm35 = max(Op_wdv_pm35 + sch2_addinit_during_yr_class_35 + gross_add_pm35 - disp_pm35 - depr_pm35, 0)
    Cl_wdv_pm30 = max(Op_wdv_pm30 + sch2_addinit_during_yr_class_30 + gross_add_pm30 - disp_pm30 - depr_pm30, 0)
    Cl_wdv_pm20 = max(Op_wdv_pm20 + sch2_addinit_during_yr_class_20 + gross_add_pm20 - disp_pm20 - depr_pm20, 0)
    return (Cl_wdv_pm40, Cl_wdv_pm35, Cl_wdv_pm30, Cl_wdv_pm20)



'''
-------------------------------------------------------------------------------------
Calculation of Initial Allowance and Industrial Building Deduction - Buildings
-------------------------------------------------------------------------------------
'''


@iterate_jit(nopython=True)
def Init_allow_bld(addition_bld, rate_init_allow_bld, ia_allowed_bld, init_allow_bld):
    """
    Return the initial allowance for building.
    """
    init_allow_bld = addition_bld * rate_init_allow_bld*ia_allowed_bld
    return init_allow_bld


@iterate_jit(nopython=True)
def Depr_bld(Op_bal_bld, rate_depr_bld, ia_allowed_bld, addition_bld, depr_bld):
    """
    Return the depreciation for building.
    """
    depr_bld = Op_bal_bld * rate_depr_bld  + addition_bld * rate_depr_bld*(1 - ia_allowed_bld)
    return depr_bld

@iterate_jit(nopython=True)
def Cl_bal_bld(Op_bal_bld, addition_bld, Cl_bal_bld):
    """
    Return the opening WDV of each asset class.
    """
    Cl_bal_bld = Op_bal_bld + addition_bld
    return Cl_bal_bld


'''
-------------------------------------------------------------------------------------
Calculation of profit chargeable to tax
-------------------------------------------------------------------------------------
'''

@iterate_jit(nopython=True)
def Depr_cap_deductions(total_depr_pm, depr_bld, total_init_allow_pm, init_allow_bld, 
                   sch2_startup_cost, sch2_intangible_asset, sch2_deduction_acquisition, depr_cap_allow):
    """
    Compute Schedule 2 Depreciation and Capital Allowances
    """
    depr_cap_allow = total_depr_pm + depr_bld + total_init_allow_pm + init_allow_bld + \
                     sch2_startup_cost + sch2_intangible_asset + sch2_deduction_acquisition
                     
    return depr_cap_allow


@iterate_jit(nopython=True)
def Total_subtractions_from_GP(sch1_exmpt_incm_less, sch1_insurance_incm, sch1_mining_incm, 
                               sch1_profit_depreciate_asset, sch1_research_expense,
                               sch1_unreal_forex_less, sch1_total_witheld_incm, sch1_total_othr_allow_ded,
                               depr_cap_allow,Total_subtractions_from_GP):
    """
    Compute total taxable profits afer adding back non-allowable deductions.
    """
    Total_subtractions_from_GP = sch1_exmpt_incm_less + sch1_insurance_incm + sch1_mining_incm + \
                                 sch1_profit_depreciate_asset + sch1_research_expense + \
                                 sch1_unreal_forex_less + sch1_total_witheld_incm + sch1_total_othr_allow_ded + \
                                 depr_cap_allow
    
    return Total_subtractions_from_GP


'''
-------------------------------------------------------------------------------------
Calculation of income from Capital Gains
-------------------------------------------------------------------------------------
'''

@iterate_jit(nopython=True)
def Income_Cap_Gains(sch1_incm_capital_gain, sch1_capital_losses, income_capgains):
    """
    Compute total taxable profits afer adding back non-allowable deductions.
    """
    income_capgains = sch1_incm_capital_gain - sch1_capital_losses
    return income_capgains



@iterate_jit(nopython=True)
def Taxable_profit(Net_accounting_profit, Total_additions_to_GP, Total_subtractions_from_GP, 
                   income_capgains, taxable_profit):
    """
    Compute total taxable profits afer adding back non-allowable deductions.
    """
    taxable_profit = Net_accounting_profit + Total_additions_to_GP - Total_subtractions_from_GP + income_capgains
    return taxable_profit



@iterate_jit(nopython=True)
def BF_loss(sch1_loss_prvs_year, bf_loss):
    """
    Compute net taxable profits afer allowing deductions.
    """
    bf_loss = sch1_loss_prvs_year
    return bf_loss

@iterate_jit(nopython=True)
def Taxable_profit_after_adjloss(taxable_profit, loss_cf_limit, Loss_lag1, 
                                 Loss_lag2, Loss_lag3, Loss_lag4, Loss_lag5, Loss_lag6, 
                                 Loss_lag7, Loss_lag8, Loss_lag9, Loss_lag10, Loss_lag11, Loss_lag12,
                                 Loss_lag13, Loss_lag14, Loss_lag15, newloss1, newloss2, newloss3, 
                                 newloss4, newloss5, newloss6, newloss7, newloss8, 
                                 newloss9, newloss10,  newloss11, newloss12,  newloss13, newloss14, 
                                 newloss15, Used_loss_total, taxbase_post_loss):
    
    """
    Compute net tax base afer allowing donations and losses.
    """
    BF_loss = np.array([Loss_lag1, Loss_lag2, Loss_lag3, Loss_lag4, Loss_lag5, Loss_lag6, 
                        Loss_lag7, Loss_lag8, Loss_lag9, Loss_lag10, Loss_lag11, Loss_lag12, 
                        Loss_lag13, Loss_lag14, Loss_lag15])
            
    N = int(loss_cf_limit)
    Used_loss = np.zeros(N)
    
    if N == 0:
        (newloss1, newloss2, newloss3, newloss4, newloss5, newloss6, 
         newloss7, newloss8, newloss9, newloss10, newloss11, newloss12,  newloss13, newloss14, 
         newloss15) = np.zeros(15)
        taxbase_post_loss = taxable_profit
    else:
        BF_loss = BF_loss[:N]
                
        if taxable_profit < 0:
            CYL = abs(taxable_profit)
        
        elif taxable_profit >= 0:
            CYL = 0
            Cum_used_loss = 0
            for i in range(N, 0, -1):
                GTI = taxable_profit - Cum_used_loss
                Used_loss[i-1] = min(BF_loss[i-1], GTI)
                Cum_used_loss += Used_loss[i-1]
            
        New_loss = BF_loss - Used_loss
        Used_loss_total = Used_loss.sum()
        taxbase_post_loss = taxable_profit - Used_loss_total
        newloss1 = CYL
        (newloss2, newloss3, newloss4, newloss5, newloss6, newloss7, 
         newloss8, newloss9, newloss10, newloss11, newloss12,  newloss13, newloss14, 
         newloss15) = np.append(New_loss[:-1], np.zeros(15-N))

    return (taxbase_post_loss, newloss1, newloss2, newloss3, newloss4, newloss5, newloss6, 
            newloss7, newloss8, newloss9, newloss10, newloss11, newloss12,  newloss13, newloss14, 
            newloss15, Used_loss_total)



@iterate_jit(nopython=True)
def Net_tax_base_behavior(cit_rate_std, cit_rate_std_curr_law, elasticity_cit_taxable_income_threshold,
                          elasticity_cit_taxable_income_value, taxbase_post_loss, net_tax_base_behavior):
    """
    Compute net taxable profits afer allowing deductions.
    """
    NP = taxbase_post_loss
    elasticity_taxable_income_threshold0 = elasticity_cit_taxable_income_threshold[0]
    elasticity_taxable_income_threshold1 = elasticity_cit_taxable_income_threshold[1]
    elasticity_taxable_income_threshold2 = elasticity_cit_taxable_income_threshold[2]
    elasticity_taxable_income_value0=elasticity_cit_taxable_income_value[0]
    elasticity_taxable_income_value1=elasticity_cit_taxable_income_value[1]
    elasticity_taxable_income_value2=elasticity_cit_taxable_income_value[2]
    if NP<=0:
        elasticity=0
    elif NP<elasticity_taxable_income_threshold0:
        elasticity=elasticity_taxable_income_value0
    elif NP<elasticity_taxable_income_threshold1:
        elasticity=elasticity_taxable_income_value1
    else:
        elasticity=elasticity_taxable_income_value2

    frac_change_net_of_cit_rate = ((1-cit_rate_std)-(1-cit_rate_std_curr_law))/(1-cit_rate_std_curr_law) 
    frac_change_Net_tax_base = elasticity*(frac_change_net_of_cit_rate)
    net_tax_base_behavior = NP*(1+frac_change_Net_tax_base) 
    return net_tax_base_behavior


@iterate_jit(nopython=True)
def mat_liability(mat_rate, Net_accounting_profit, MAT):
    """
    Compute tax liability given the corporate rate
    """
    # subtract TI_special_rates from TTI to get Aggregate_Income, which is
    # the portion of TTI that is taxed at normal rates
    MAT = mat_rate*Net_accounting_profit
        
    return MAT

@iterate_jit(nopython=True)
def cit_liability(sch4_sch_cntrt_gross_incm, sch5_net_charge_income, 
                  sch6_net_inc_short_bsns, net_tax_base_behavior, cit_rate_std, 
                  cit_rate_mining, cit_rate_insurance, cit_rate_ltcontract, MAT, citax):
    """
    Compute tax liability given the corporate rate
    """
    # subtract TI_special_rates from TTI to get Aggregate_Income, which is
    # the portion of TTI that is taxed at normal rates
   
    citax1 = cit_rate_std * max(net_tax_base_behavior, 0)
    citax2 = cit_rate_mining * max(sch5_net_charge_income, 0)
    citax3 = cit_rate_insurance*max(sch6_net_inc_short_bsns, 0)
    citax4 = cit_rate_ltcontract * max(sch4_sch_cntrt_gross_incm, 0)
    citax = max(citax1 + citax2 + citax3 + citax4, MAT)
    return citax

@iterate_jit(nopython=True)
def Ebdta(Net_accounting_profit, Total_additions_to_GP, Total_subtractions_from_GP, sch1_add_depreciation,
          sch1_add_strt_up_cost, depr_cap_allow, income_capgains, ebdta):
    """
    Compute total taxable profits afer adding back non-allowable deductions.
    """
    ebdta = Net_accounting_profit + (Total_additions_to_GP - sch1_add_strt_up_cost - sch1_add_depreciation) + \
            (Total_subtractions_from_GP - depr_cap_allow) + income_capgains
    return ebdta


