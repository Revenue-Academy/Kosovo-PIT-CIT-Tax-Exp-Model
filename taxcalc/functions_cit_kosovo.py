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
1.Adustments to Income
'''

# [16] Total adjustment to income (add lines [11] to [15])
@iterate_jit(nopython=True)
def calc_totadjinc_l11_l15_fun(forsourceincsch_a,recbaddebts_sch_b,capgain_sch_c,div_sch_d,otherincgain_sch_e,calc_totadjinc_l11_l15):
    calc_totadjinc_l11_l15 =  forsourceincsch_a + recbaddebts_sch_b+capgain_sch_c+div_sch_d+otherincgain_sch_e
    return calc_totadjinc_l11_l15

# 17 [Profit (loss) after adjustment to income (line [10] + line [16])
@iterate_jit(nopython=True)
def calc_profitloss_afteradjinc_fun(netprofit_fd,calc_totadjinc_l11_l15,calc_profitloss_afteradjinc):
    calc_profitloss_afteradjinc =  netprofit_fd + calc_totadjinc_l11_l15
    return calc_profitloss_afteradjinc


'''
2. Adjustments to Expenses (mostly negative numbers shown in brackets - except line 24)
'''
# 27. Total adjustment to expenses (add lines [18] to [26]).
@iterate_jit(nopython=True)
def calc_totadjexp_l18_l26_fun(disallowedexp_sch_f,repcosts_sch_g,reservefunds_sch_h,paymrelper_sch_i,
        amort_sch_j,dep_sch_k,specallownewassets_sch_l,caploss_sch_c,otherexp_sch_m,calc_totadjexp_l18_l26):    
    calc_totadjexp_l18_l26 =  disallowedexp_sch_f+repcosts_sch_g+reservefunds_sch_h+paymrelper_sch_i+amort_sch_j+dep_sch_k+specallownewassets_sch_l+caploss_sch_c+otherexp_sch_m
    return calc_totadjexp_l18_l26

# [28] Profit (loss) of business after adjustment to expenses (line [17]- line [27]), (When line 27 is in brackets add the whole numbers)

@iterate_jit(nopython=True)
def calc_proflossaftadjexp_l17_l27_fun(calc_profitloss_afteradjinc,calc_totadjexp_l18_l26):
    #calc_proflossaftadjexp_l17_l27 =   calc_totadjexp_l18_l26 - calc_profitloss_afteradjinc
    calc_proflossaftadjexp_l17_l27 =   calc_profitloss_afteradjinc-calc_totadjexp_l18_l26
    return calc_proflossaftadjexp_l17_l27

# 29. Charitable contributions (attach receipts), (limit of 5% of line 28)
@iterate_jit(nopython=True)
def calc_charitycontrib_box28_fun(charitycontrib_box28, toggle_charitable,calc_charitycontrib_box28):
    calc_charitycontrib_box28 = charitycontrib_box28 * toggle_charitable
    return calc_charitycontrib_box28

# 31.Add lines [29] and [30]
@iterate_jit(nopython=True)
def calc_add_l29_l30_fun(calc_charitycontrib_box28,losscarryforward,calc_add_l29_l30):
    calc_add_l29_l30 =  calc_charitycontrib_box28 + losscarryforward
    return calc_add_l29_l30

# 32. Adjusted profit (line [28]- line [31])
@iterate_jit(nopython=True)
def calc_adjprofit_l28_l31_fun(calc_proflossaftadjexp_l17_l27,calc_add_l29_l30,calc_adjprofit_l28_l31):
    calc_adjprofit_l28_l31 =  calc_proflossaftadjexp_l17_l27 - calc_add_l29_l30
    return calc_adjprofit_l28_l31

# 33.Corporate income tax (If line 32 is a profit, multiply by 10%. If line [32] is a loss, enter 0)
@iterate_jit(nopython=True)
def calc_corpinctax_l32_fun(calc_adjprofit_l28_l31,cit_rate,calc_corpinctax_l32):
    calc_corpinctax_l32 =  calc_adjprofit_l28_l31 * cit_rate
    return calc_corpinctax_l32

"""  For Insurance Companies only"""

# [35] Corporate Income Tax for Insurance Companies ( [34] * 5%)
# Double check this amount again
@iterate_jit(nopython=True)
def corpinctax_insurcomp_fun(gross_prem,cit_rate_ins,calc_corpinctax_insurcomp):
    calc_corpinctax_insurcomp =  gross_prem * cit_rate_ins
    return calc_corpinctax_insurcomp


"""
Refund or Amount Due

"""

# 36.Corporate Income Tax (add the amounts in the line [33] and [35] according to your situation)
@iterate_jit(nopython=True)
def calc_corpinctax_total_fun(calc_corpinctax_l32,calc_corpinctax_insurcomp,calc_corpinctax_total):
    calc_corpinctax_total =  calc_corpinctax_l32 + calc_corpinctax_insurcomp
    return calc_corpinctax_total


#  [39] Total Credits for the period [37] +[38]
@iterate_jit(nopython=True)
def calc_totcredits_l37_l38_fun(forstattaxcredit_sch_o,taxwithheld_sch_p,calc_totcredits_l37_l38):
    calc_totcredits_l37_l38 =  forstattaxcredit_sch_o + taxwithheld_sch_p
    return calc_totcredits_l37_l38

#  [40] Line [36] less [39]
@iterate_jit(nopython=True)
def calc_l36_minus_l39_fun(calc_corpinctax_total, calc_totcredits_l37_l38,calc_l36_minus_l39):    
    if calc_corpinctax_total == 0:
        #return 0
        return calc_corpinctax_total
    else:
        calc_l36_minus_l39 = calc_corpinctax_total - calc_totcredits_l37_l38
        return calc_l36_minus_l39
    
    
# [43] Discounts for sponsorship in the field of sports (max.30% of the box [42]
@iterate_jit(nopython=True)
def calc_sportspodisc_fun(sportspodisc_max30pct_box42, toggle_sport,calc_sportspodisc_max30pct_box42):
    calc_sportspodisc_max30pct_box42 = sportspodisc_max30pct_box42 * toggle_sport
    return calc_sportspodisc_max30pct_box42


#	44 Discounts for sponsorship in the field of Culture and Youth (Max. 20% of Box [42]
@iterate_jit(nopython=True)
def calc_cul_youths_disc_fun(culyouthspodisc_max20pct_box42, toggle_culture_youth,calc_culyouthspodisc_max20pct_box42):
    calc_culyouthspodisc_max20pct_box42= culyouthspodisc_max20pct_box42 * toggle_culture_youth
    return calc_culyouthspodisc_max20pct_box42


# D45	Total discounts for sponsorships ([43]+[44], max.30% of box [42]
@iterate_jit(nopython=True)
def calc_total_sponsorship_fun(calc_sportspodisc_max30pct_box42, calc_culyouthspodisc_max20pct_box42,calc_totalspodisc_max30pct_box42):
    calc_totalspodisc_max30pct_box42= calc_sportspodisc_max30pct_box42 + calc_culyouthspodisc_max20pct_box42
    return calc_totalspodisc_max30pct_box42

# D46	Tax for payment with this form ([36]-[39]-[41]-[45])
# Double check this again !

@iterate_jit(nopython=True)
def calc_taxpaywithform_fun(calc_corpinctax_total, calc_totcredits_l37_l38, installmentspaid_sch_q, calc_totalspodisc_max30pct_box42,calc_taxpaywithform):    
    calc = (calc_corpinctax_total - calc_totcredits_l37_l38 - installmentspaid_sch_q - calc_totalspodisc_max30pct_box42)
    if calc <= 0:
        calc_taxpaywithform = 0
    else:
        calc_taxpaywithform = calc_corpinctax_total
    return calc_taxpaywithform


 # D63	Total ([61] + [62])
@iterate_jit(nopython=True)
def calc_total_l61_l62_fun(openinginv,costofprod,calc_total_l61_l62):
    calc_total_l61_l62 =  openinginv + costofprod
    return calc_total_l61_l62


# D65	Cost of goods sold ([63]-[64])
@iterate_jit(nopython=True)
def calc_costofgoodssold_l63_l64_fun(calc_total_l61_l62,endinginventory,calc_costofgoodssold_l63_l64):
    calc_costofgoodssold_l63_l64 =  calc_total_l61_l62 - endinginventory
    return calc_costofgoodssold_l63_l64


# [66] Gross profit ([60]-[65])
@iterate_jit(nopython=True)
def calc_grossprofit_l60_l65_fun(grossinc,costofgoodssold_l63_l64,calc_grossprofit_l60_l65):
    calc_grossprofit_l60_l65 =  grossinc - costofgoodssold_l63_l64
    return calc_grossprofit_l60_l65


# [73] Total operating expenses (Add [67] through [72])
@iterate_jit(nopython=True)
def calc_totalopexp_l67_l72_fun(grosswages,depamortexp_notincost,sellingexp,genadminexp_notincost,rnd_costs,otheropexp,calc_totalopexp_l67_l72):
    calc_totalopexp_l67_l72 =  grosswages+depamortexp_notincost+sellingexp+genadminexp_notincost+rnd_costs+otheropexp
    return calc_totalopexp_l67_l72

# D74	PROFIT/LOSS FROM OPERATIONS ([66] - [73])
@iterate_jit(nopython=True)
def calc_profitloss_oper_l66_l73_fun(calc_grossprofit_l60_l65,calc_totalopexp_l67_l72,calc_profitloss_oper_l66_l73):
    calc_profitloss_oper_l66_l73 = calc_grossprofit_l60_l65-calc_totalopexp_l67_l72
    return calc_profitloss_oper_l66_l73

# D77	PROFIT/LOSS FROM NON-OPERATING ACTIVITIES ([75] - [76])
@iterate_jit(nopython=True)
def calc_profitloss_nonopact_l75_l76_fun(otherrevgains,otherexploss,calc_profitloss_nonopact_l75_l76):
    calc_profitloss_nonopact_l75_l76 = otherrevgains-otherexploss
    return calc_profitloss_nonopact_l75_l76

# D78	Net profit (Loss) ([74] + [77])
@iterate_jit(nopython=True)
def calc_netprofitloss_l74_l77_fun(calc_profitloss_oper_l66_l73,calc_profitloss_nonopact_l75_l76):
    calc_netprofitloss_l74_l77 = calc_profitloss_oper_l66_l73+calc_profitloss_nonopact_l75_l76
    return calc_netprofitloss_l74_l77


'''
---------------------------------------------------------------------------------------------------------------
                                           Small_Corporations 2022

                                  Quarterly payments of tax on gross receipts 
----------------------------------------------------------------------------------------------------------------
'''

# Tax on quarterly income [10] = [8] x 3%	
# 3% of gross income received from trade, transport, agricultural, or similar activities 
@iterate_jit(nopython=True)
def calc_tqi_3pct_fun(g_inc_spcel,rate_small_trans_ag,calc_tqi_3pct):
    calc_tqi_3pct = g_inc_spcel*rate_small_trans_ag
    return calc_tqi_3pct


# Tax on quarterly income [11]=[9] x 9%
# 9% of gross income for the quarter from services, professional, vocational, entertainment, or similar activities
@iterate_jit(nopython=True)
def calc_tqi_9pct_fun(g_inc_q,rate_small_service_prof,calc_tqi_9pct):
    calc_tqi_9pct = g_inc_q*rate_small_service_prof
    return calc_tqi_9pct


#  [12] Amount for payment in this statement [10]+[11] , but not less than 37.50 euro

@iterate_jit(nopython=True)
def calc_tot_amount_3pct_9pct_fun(calc_tqi_3pct,calc_tqi_9pct,min_payment,calc_tot_amount_3pct_9pct):
    calc_tot_amount_3pct_9pct= calc_tqi_3pct + calc_tqi_9pct
    
    if calc_tot_amount_3pct_9pct  <=  min_payment:
        calc_tot_amount_3pct_9pct = min_payment
        return calc_tot_amount_3pct_9pct
    else:
        calc_tot_amount_3pct_9pct=calc_tot_amount_3pct_9pct
        return (calc_tot_amount_3pct_9pct)

"""
Total tax large plus micro

"""
@iterate_jit(nopython=True)
def cit_liability(calc_taxpaywithform,calc_tot_amount_3pct_9pct,citax):
    citax = calc_taxpaywithform+calc_tot_amount_3pct_9pct
    return citax


# Test
# @iterate_jit(nopython=True)
# # Only for testing purposes
# def Tax_base_CF_losses(
#     Loss_lag1, Loss_lag2, Loss_lag3, Loss_lag4, Loss_lag5, Loss_lag6, Loss_lag7, Loss_lag8,
#     newloss1, newloss2, newloss3, newloss4, newloss5, newloss6, newloss7, newloss8,newloss9, newloss10 ):
    
#     """
#     Compute net tax base afer allowing donations and losses.
#     """
#     # BF_loss = np.array([Loss_lag1, Loss_lag2, Loss_lag3, Loss_lag4, Loss_lag5, Loss_lag6, Loss_lag7, Loss_lag8])
    
#     # Gross_Tax_base = min(Net_taxable_profit, max((Net_taxable_profit - Donations_allowed), 0))

#     # if BF_loss.sum() == 0:
#     #     BF_loss[0] = CF_losses

#     # N = int(Loss_CFLimit)
#     # if N == 0:
#     #     (newloss1, newloss2, newloss3, newloss4, newloss5, newloss6, newloss7, newloss8) = np.zeros(8)
#     #     Used_loss_total = 0
#     #     Tax_base = Gross_Tax_base
        
#     # else:
#     #     BF_loss = BF_loss[:N]
                
#     #     if Gross_Tax_base < 0:
#     #         CYL = abs(Gross_Tax_base)
#     #         Used_loss = np.zeros(N)
#     #     elif Gross_Tax_base >0:
#     #         CYL = 0
#     #         Cum_used_loss = 0
#     #         Used_loss = np.zeros(N)
#     #         for i in range(N, 0, -1):
#     #             GTI = Gross_Tax_base - Cum_used_loss
#     #             Used_loss[i-1] = min(BF_loss[i-1], GTI)
#     #             Cum_used_loss += Used_loss[i-1]
#     #     elif Gross_Tax_base == 0:
#     #         CYL=0
#     #         Used_loss = np.zeros(N)
    
#     #     New_loss = BF_loss - Used_loss
#     #     Tax_base = Gross_Tax_base - Used_loss.sum()
#     #     newloss1 = CYL
#     #     Used_loss_total = Used_loss.sum()
#     #     (newloss2, newloss3, newloss4, newloss5, newloss6, newloss7, newloss8) = np.append(New_loss[:-1], np.zeros(8-N))
#     newloss1=0
#     newloss2=0
#     newloss3=0
#     newloss4=0
#     newloss5=0
#     newloss6=0
#     newloss7=0
#     newloss8=0
#     newloss9=0
#     newloss10=0
    
    
#     return (newloss1, newloss2, newloss3, newloss4, newloss5, newloss6, newloss7, newloss8,newloss9,newloss10)








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