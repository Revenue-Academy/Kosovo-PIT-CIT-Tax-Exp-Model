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
def calc_totadjinc_l11_l15_fun(forsourceincsch_a,recbaddebts_sch_b,capgain_sch_c,div_sch_d,otherincgain_sch_e, totadjinc_l11_l15, calc_totadjinc_l11_l15):
    calc_totadjinc_l11_l15 =  forsourceincsch_a + recbaddebts_sch_b + capgain_sch_c + div_sch_d+otherincgain_sch_e
    calc_totadjinc_l11_l15 = totadjinc_l11_l15
    return calc_totadjinc_l11_l15

# # 17 [Profit (loss) after adjustment to income (line [10] + line [16])
# @iterate_jit(nopython=True)
# def calc_profitloss_afteradjinc_fun(netprofit_fd,calc_totadjinc_l11_l15, profitloss_afteradjinc, calc_profitloss_afteradjinc):
#     calc_profitloss_afteradjinc =  netprofit_fd + calc_totadjinc_l11_l15
#     calc_profitloss_afteradjinc = profitloss_afteradjinc
#     return calc_profitloss_afteradjinc

# 17 [Profit (loss) after adjustment to income (line [10] + line [16])
@iterate_jit(nopython=True)
def calc_profitloss_afteradjinc_fun(profitloss_afteradjinc, calc_profitloss_afteradjinc):
    calc_profitloss_afteradjinc = profitloss_afteradjinc
    return calc_profitloss_afteradjinc

'''
2. Adjustments to Expenses (mostly negative numbers shown in brackets - except line 24)
'''
# 27. Total adjustment to expenses (add lines [18] to [26]).
@iterate_jit(nopython=True)
def calc_totadjexp_l18_l26_fun(rate_spl_all, disallowedexp_sch_f,repcosts_sch_g,reservefunds_sch_h,paymrelper_sch_i,
        amort_sch_j,dep_sch_k,specallownewassets_sch_l,caploss_sch_c,otherexp_sch_m,calc_totadjexp_l18_l26):    
    calc_totadjexp_l18_l26 =  disallowedexp_sch_f + repcosts_sch_g + reservefunds_sch_h + paymrelper_sch_i + amort_sch_j + \
                              dep_sch_k + specallownewassets_sch_l * rate_spl_all + caploss_sch_c + otherexp_sch_m
    return calc_totadjexp_l18_l26

# [28] Profit (loss) of business after adjustment to expenses (line [17]- line [27]), (When line 27 is in brackets add the whole numbers)

@iterate_jit(nopython=True)
def calc_proflossaftadjexp_l17_l27_fun(calc_profitloss_afteradjinc, calc_totadjexp_l18_l26, calc_grossinc):
    #calc_proflossaftadjexp_l17_l27 =   calc_totadjexp_l18_l26 - calc_profitloss_afteradjinc
    calc_grossinc =   calc_profitloss_afteradjinc - calc_totadjexp_l18_l26
    return calc_grossinc


# 29. Charitable contributions (attach receipts), (limit of 5% of line 28)
@iterate_jit(nopython=True)
def calc_charitycontrib_box28_fun(rate_max_charitable_ded,  calc_grossinc, charitycontrib_box28, calc_charitycontrib_box28):
    calc_charitycontrib_box28 = min(charitycontrib_box28, max(rate_max_charitable_ded*calc_grossinc, 0))
    return calc_charitycontrib_box28

@iterate_jit(nopython=True)
def calc_gti_fun(calc_grossinc, calc_charitycontrib_box28, calc_gti):
    calc_gti =   calc_grossinc - calc_charitycontrib_box28
    return calc_gti

# 31.Add lines [29] and [30]
@iterate_jit(nopython=True)
def calc_loss_adj_fun(calc_gti,Loss_lag1, newloss1, calc_nti):
    if calc_gti < 0:
            newloss1 = Loss_lag1 + calc_gti
            calc_nti = 0
    else:
            used_loss = min(abs(Loss_lag1), calc_gti)
            newloss1 = Loss_lag1 - used_loss
            calc_nti = calc_gti - used_loss
    return (calc_nti, newloss1)
    # BF_loss = np.array([Loss_lag1])
    # Gross_Tax_base = calc_gti
    # N = int(Loss_CFLimit)
    # if N == 0:
    #     newloss1 = np.zeros(0)
    #     calc_nti = calc_gti
        
    # else:
    #     BF_loss = BF_loss[:N]
    #     if Gross_Tax_base < 0:
    #         CYL = abs(Gross_Tax_base)
    #         Used_loss = np.zeros(N)
    #     elif Gross_Tax_base >= 0:
    #         CYL = 0
    #         Cum_used_loss = 0
    #         Used_loss = np.zeros(N)
    #         for i in range(N, 0, -1):
    #             GTI = Gross_Tax_base - Cum_used_loss
    #             Used_loss[i-1] = min(BF_loss[i-1], GTI)
    #             Cum_used_loss += Used_loss[i-1]
    #     newloss1 = BF_loss - Used_loss
    #     calc_nti = Gross_Tax_base - Used_loss.sum()
            
    


# 33.Corporate income tax (If line 32 is a profit, multiply by 10%. If line [32] is a loss, enter 0)
@iterate_jit(nopython=True)
def calc_citax_non_insurance_fun(calc_nti, cit_rate, citax_non_insurance):
    citax_non_insurance =  max(calc_nti * cit_rate, 0)
    return citax_non_insurance

"""  For Insurance Companies only"""

# [35] Corporate Income Tax for Insurance Companies ( [34] * 5%)
# Double check this amount again
@iterate_jit(nopython=True)
def corpinctax_insurcomp_fun(gross_prem,cit_rate_ins,citax_insurance):
    citax_insurance =  max(gross_prem * cit_rate_ins, 0)
    return citax_insurance

@iterate_jit(nopython=True)
def calc_citax_large_fun(citax_non_insurance, citax_insurance, citax_large):
    citax_large =  citax_non_insurance + citax_insurance
    return citax_large

"""
Refund or Amount Due

"""

#  [39] Total Credits for the period [37] +[38]
@iterate_jit(nopython=True)
def calc_totcredits_l37_l38_fun(forstattaxcredit_sch_o,taxwithheld_sch_p,calc_totcredits_l37_l38):
    calc_totcredits_l37_l38 =  forstattaxcredit_sch_o + taxwithheld_sch_p
    return calc_totcredits_l37_l38

#  [40] Line [36] less [39]
@iterate_jit(nopython=True)
def calc_l36_minus_l39_fun(citax_large, calc_totcredits_l37_l38,calc_l36_minus_l39):    
    calc_l36_minus_l39 = max(0, citax_large - calc_totcredits_l37_l38)
    return calc_l36_minus_l39
    
    
# [43] Discounts for sponsorship in the field of sports (max.30% of the box [42]
@iterate_jit(nopython=True)
def calc_sportspodisc_fun(rate_ded_sponsorship, citax_large, sportspodisc_max30pct_box42, calc_sportspodisc_max30pct_box42):
    calc_sportspodisc_max30pct_box42 = min(sportspodisc_max30pct_box42, rate_ded_sponsorship * citax_large)
    #calc_sportspodisc_max30pct_box42 = sportspodisc_max30pct_box42 * rate_ded_sponsorship
    return calc_sportspodisc_max30pct_box42

#	44 Discounts for sponsorship in the field of Culture and Youth (Max. 20% of Box [42]
@iterate_jit(nopython=True)
def calc_cul_youths_disc_fun(rate_ded_culture_youth, citax_large, culyouthspodisc_max20pct_box42,calc_culyouthspodisc_max20pct_box42):
    calc_culyouthspodisc_max20pct_box42= min(culyouthspodisc_max20pct_box42, rate_ded_culture_youth * citax_large)
    return calc_culyouthspodisc_max20pct_box42


# D45	Total discounts for sponsorships ([43]+[44], max.30% of box [42]
@iterate_jit(nopython=True)
def calc_total_sponsorship_fun(calc_sportspodisc_max30pct_box42, calc_culyouthspodisc_max20pct_box42,calc_totalspodisc_max30pct_box42):
    calc_totalspodisc_max30pct_box42= calc_sportspodisc_max30pct_box42 + calc_culyouthspodisc_max20pct_box42
    return calc_totalspodisc_max30pct_box42

# D46	Tax for payment with this form ([36]-[39]-[41]-[45])
# Double check this again !

@iterate_jit(nopython=True)
def calc_citax_fun(citax_large, calc_totalspodisc_max30pct_box42, citax):    
    citax = max(citax_large - calc_totalspodisc_max30pct_box42, 0)
    return citax


#  # D63	Total ([61] + [62])
# @iterate_jit(nopython=True)
# def calc_total_l61_l62_fun(openinginv,costofprod,calc_total_l61_l62):
#     calc_total_l61_l62 =  openinginv + costofprod
#     return calc_total_l61_l62


# # D65	Cost of goods sold ([63]-[64])
# @iterate_jit(nopython=True)
# def calc_costofgoodssold_l63_l64_fun(calc_total_l61_l62,endinginventory,calc_costofgoodssold_l63_l64):
#     calc_costofgoodssold_l63_l64 =  calc_total_l61_l62 - endinginventory
#     return calc_costofgoodssold_l63_l64


# # [66] Gross profit ([60]-[65])
# @iterate_jit(nopython=True)
# def calc_grossprofit_l60_l65_fun(grossinc,costofgoodssold_l63_l64,calc_grossprofit_l60_l65):
#     calc_grossprofit_l60_l65 =  grossinc - costofgoodssold_l63_l64
#     return calc_grossprofit_l60_l65


# # [73] Total operating expenses (Add [67] through [72])
# @iterate_jit(nopython=True)
# def calc_totalopexp_l67_l72_fun(grosswages,depamortexp_notincost,sellingexp,genadminexp_notincost,rnd_costs,otheropexp,calc_totalopexp_l67_l72):
#     calc_totalopexp_l67_l72 =  grosswages+depamortexp_notincost+sellingexp+genadminexp_notincost+rnd_costs+otheropexp
#     return calc_totalopexp_l67_l72

# # D74	PROFIT/LOSS FROM OPERATIONS ([66] - [73])
# @iterate_jit(nopython=True)
# def calc_profitloss_oper_l66_l73_fun(calc_grossprofit_l60_l65,calc_totalopexp_l67_l72,calc_profitloss_oper_l66_l73):
#     calc_profitloss_oper_l66_l73 = calc_grossprofit_l60_l65-calc_totalopexp_l67_l72
#     return calc_profitloss_oper_l66_l73

# # D77	PROFIT/LOSS FROM NON-OPERATING ACTIVITIES ([75] - [76])
# @iterate_jit(nopython=True)
# def calc_profitloss_nonopact_l75_l76_fun(otherrevgains,otherexploss,calc_profitloss_nonopact_l75_l76):
#     calc_profitloss_nonopact_l75_l76 = otherrevgains-otherexploss
#     return calc_profitloss_nonopact_l75_l76

# # D78	Net profit (Loss) ([74] + [77])
# @iterate_jit(nopython=True)
# def calc_netprofitloss_l74_l77_fun(calc_profitloss_oper_l66_l73,calc_profitloss_nonopact_l75_l76):
#     calc_netprofitloss_l74_l77 = calc_profitloss_oper_l66_l73+calc_profitloss_nonopact_l75_l76
#     return calc_netprofitloss_l74_l77


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
def calc_tot_amount_3pct_9pct_fun(calc_tqi_3pct,calc_tqi_9pct,min_payment_small,calc_tot_amount_3pct_9pct):
    calc_tot_amount_3pct_9pct= calc_tqi_3pct + calc_tqi_9pct
    calc_tot_amount_3pct_9pct = max(min_payment_small, max(calc_tot_amount_3pct_9pct, 0))
    return (calc_tot_amount_3pct_9pct)


#  [16] Amount for payment in this statement [14] - [15]

@iterate_jit(nopython=True)
def calc_rental_inc_fun(gross_inc_rent, rate_tax_rent, rent_tax_held_oth, calc_rent_tax):
    calc_rent_tax = max(gross_inc_rent * rate_tax_rent - rent_tax_held_oth, 0)
    return (calc_rent_tax)

#  [17] Total tax Small Corporate

@iterate_jit(nopython=True)
def calc_citax_small_fun(calc_rent_tax,calc_tot_amount_3pct_9pct,totax):
    totax = (calc_tot_amount_3pct_9pct + calc_rent_tax)*4
    return totax


@iterate_jit(nopython=True)
def calc_turnover_small_fun(g_inc_q,g_inc_spcel, calc_turnover_small):
    calc_turnover_small = (g_inc_q + g_inc_spcel)*4
    return calc_turnover_small

"""
Total tax large plus micro

# """
# @iterate_jit(nopython=True)
# def calc_citax_fun(calc_citax_large_net,citax_small, citax):
#     citax = calc_citax_large_net + citax_small
#     return citax

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