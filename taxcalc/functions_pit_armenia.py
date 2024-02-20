"""
pitaxcalc-demo functions that calculate personal income tax liability.
"""
# CODING-STYLE CHECKS:
# pycodestyle functions.py
# pylint --disable=locally-disabled functions.py

import math
import copy
import numpy as np
from taxcalc.decorators import iterate_jit


'I. CALCULATION OF TAX BASE FOR LABOR INCOME '

"Calculation of annual maximum limit for social payment at low rate"
@iterate_jit(nopython=True)
def cal_max_annual_income_lowssc(max_income_pm_low_ssc, max_annual_income_low_ssc):
   max_annual_income_low_ssc = max_income_pm_low_ssc*12
   return (max_annual_income_low_ssc)

"Calculation of monthly cap for social payment - (15 times the minimum wage per pm)"
@iterate_jit(nopython=True)
def cal_max_annual_income_ssc(min_wage_pm, max_annual_income_ssc):
   max_annual_income_ssc = (min_wage_pm*15)*12
   return (max_annual_income_ssc)



"Calculation of Social payments"
@iterate_jit(nopython=True)
def cal_ssc_fun(social_fee, base_social, min_income_for_ssc,max_annual_income_low_ssc,max_annual_income_ssc,rate_sp_1,rate_sp_2, sstax):    
    """ Note:  
            Hint: Please note, that the social security scheme is mandatory for all the taxpayers born after 1974, and it is voluntary for others born before 1974.
            
             1.Base for social payment :
              
              The base for calculation of the social payment is the basic income, 
              which is salary and other payments equal thereto which are subject 
              to taxation by income tax.
              The Employer, as a tax agent, is obliged to withhold the amount of 
              social payment as well as submit monthly personalized reports to the 
              tax authorities on calculated income, amounts of tax and social payments withheld from individuals within the terms established by the RA Tax Code.
              
              The social payment rates are as follows:
                  
                     Basic monthly Income*             Social payment
             2021   Up to AMD 500,000                   3.5 %
                    More than AMD 500,000              10 % on income above 500000
                     
             2022  Up to AMD 500,000                     4.5 %
                   More than AMD 500,000                10 % on income above 500000     
                     
             2023  Up to AMD 500,000                     5 %
                   More than AMD 500,000                10 % on income above 500000            
                     
              Starting 01.07.2020 the maximum monthly threshold of the calculation 
              basis for social payment is AMD 1,020,000. This means that the maximum 
              amount of the Social Payment in 2021 will be capped at AMD.69,500. 
              (Source https://home.kpmg/xx/en/home/insights/2021/07/armenia-thinking-beyond-borders.html)
                
              
              2.Rule for calculation Social security contributions for 2021 :
               
              Individuals born after 1 January 1974 must make social security payments 
              at a rate of 3.5 % on their salary and equivalent income and income 
              from the provision of services, in a case where the income is less 
              than or equal to AMD 500,000. 
              If the salary and equivalent income or income from the provision of 
              services is between AMD 500,000 and AMD 1,020,000 (the latter amount 
              is calculated as 15 times the minimum monthly salary (AMD 68,000)), 
              the social security contribution is calculated as 10% on the gross 
              income minus AMD 32,500. Where the relevant income is equal to or 
              exceeds AMD 1,020,000, the social security contribution is calculated 
              as 10% on AMD 1,020,000 minus AMD 32,500. Individuals have the right 
              to waive the maximum threshold for social security payments.
              (Source:https://www2.deloitte.com/content/dam/Deloitte/global/Documents/Tax/dttl-tax-armeniahighlights-2021.pdf)
    
    """
    
    if social_fee ==0 and base_social> 1:
        sstax = 0
    elif base_social <= min_income_for_ssc:
        sstax = 0.
    elif (base_social >=min_income_for_ssc) and (base_social <= max_annual_income_low_ssc):
       sstax = base_social * rate_sp_1  #policy is to pay ssc on entire base if it exceeds threshold
    #elif (base_social >=min_income_for_ssc) and (base_social <= max_annual_income_low_ssc):
        #sstax = (base_social - min_income_for_ssc)  * rate_sp_1  #policy is to pay ssc on portion above min threshold 
    elif (base_social >=max_annual_income_low_ssc) and (base_social <=max_annual_income_ssc): 
       sstax =  (max_annual_income_low_ssc * rate_sp_1) +  max(0., (base_social - max_annual_income_low_ssc)*rate_sp_2)
    elif base_social > max_annual_income_ssc:
       sstax = (max_annual_income_low_ssc * rate_sp_1) +  max(0., (max_annual_income_ssc - max_annual_income_low_ssc)*rate_sp_2)
    return  (sstax)



"Calculation for tax base for income from wages"
@iterate_jit(nopython=True)
def cal_tti_wage(percent_ssc_deductible, sstax, salary, civil_contract,other_income,deduction,tti_wages):
    tti_wages=(salary + civil_contract + other_income) - deduction
    allowed_ssc = sstax*percent_ssc_deductible
    if tti_wages>=allowed_ssc:
        tti_wages = tti_wages-allowed_ssc
    else:
        tti_wages=0
    return (tti_wages)


'II. CALCULATION OF TAX BASE FOR PASSIVE INCOME '

'''
Type of income	Code	Rate	Income code	Rate
	RA resident		Non-Resident	
1. Royalty	1	10%	101	10%
2. Interest	2	10%	102	10%
3․ Gaining/wining/	3	Standard rate*	103	Standard rate*
4. Prize	4	Standard rate*	104	Standard rate*
5. Donation	5	Standard rate*	105	Standard rate*
6. Insurance compensation / Income from the alienation of a person's share in the ownership of industrial, other commercial, and public property, including buildings, structures (including unfinished (semi-constructed), industrial, use of subsoil, and other land or property of industrial significance) 	6	20%	106	20%
Income (107) from alienation of property (except for what is indicated in lines 6 and 8 of this table) 	7	10%	107	 10%
8. Additional increase in the value of the property / Income received from the alienation of the building, its apartments or other premises by a developer who is not a sole entrepreneur (108)	8	20%	108	20%
9. Rent	9	10%	109	10%
10. Dividends	10	5%	110	10%
11.Insurance premium for physical persons	11	Standard rate*	111	Standard rate*
12. Voluntary pensions	12	10%	112	10%
14. Unpaid passive income during the 12-month period following the year in which the reduction was made	14	20%	114	20%
15. Income calculated for the performance of work under the employment contract of a foreign citizen or a stateless person who does not have residence status in the Republic of Armenia	na	na	115	Standard rate*
16. Other income	99	Standard rate*	199	Standard rate*

'''

'1. Royalty'

"Calculation for tax base for income from royalty_resident"
@iterate_jit(nopython=True)
def cal_tti_royalty_resident(royalty_resident, tti_royalty_resident):
    tti_royalty_resident=royalty_resident
    return (tti_royalty_resident)

"Calculation for tax base for income from royalty_non_resident"
@iterate_jit(nopython=True)
def cal_tti_royalty_non_resident(royalty_non_resident, tti_royalty_non_resident):
    tti_royalty_non_resident=royalty_non_resident
    return (tti_royalty_non_resident)

'2. Interest'

"Calculation for tax base for income from interest_resident"
@iterate_jit(nopython=True)
def cal_tti_interest_resident(interest_resident, tti_interest_resident):
    tti_interest_resident=interest_resident
    return (tti_interest_resident)

"Calculation for tax base for income from interest_resident"
@iterate_jit(nopython=True)
def cal_tti_interest_non_resident(interest_non_resident, tti_interest_non_resident):
    tti_interest_non_resident=interest_non_resident
    return (tti_interest_non_resident)

'3.Gaining/wining/'
"Calculation for tax base for income from gaining_resident"	
@iterate_jit(nopython=True)
def cal_tti_gaining_resident(gaining_resident, tti_gaining_resident):
    tti_gaining_resident=gaining_resident
    return (tti_gaining_resident)

"Calculation for tax base for income from gaining_non_resident"	
@iterate_jit(nopython=True)
def cal_tti_gaining_non_resident(gaining_non_resident, tti_gaining_non_resident):
    tti_gaining_non_resident=gaining_non_resident
    return (tti_gaining_non_resident)

'4. Prize'
"Calculation for tax base for income from prize_resident"	
@iterate_jit(nopython=True)
def cal_tti_prize_resident(prize_resident, tti_prize_resident):
    tti_prize_resident=prize_resident
    return (tti_prize_resident)

"Calculation for tax base for income from prize_non_resident"	
@iterate_jit(nopython=True)
def cal_tti_prize_non_resident(prize_non_resident, tti_prize_non_resident):
    tti_prize_non_resident=prize_non_resident
    return (tti_prize_non_resident)

'5. Donation'
"Calculation for tax base for income from donation_resident"	
@iterate_jit(nopython=True)
def cal_tti_donation_resident(donation_resident, tti_donation_resident):
    tti_donation_resident=donation_resident
    return (tti_donation_resident)

"Calculation for tax base for income from donation_non_resident"	
@iterate_jit(nopython=True)
def cal_tti_donation_non_resident(donation_non_resident, tti_donation_non_resident):
    tti_donation_non_resident=donation_non_resident
    return (tti_donation_non_resident)

'''6. Income from the alienation of a persons share in the ownership of industrial, other commercial, 
     and public property, including buildings, structures (including unfinished (semi-constructed), industrial, use of subsoil, and other land or property of industrial significance) 
'''


"Calculation for tax base for income from alienation_property_dev_resident"	
@iterate_jit(nopython=True)
def cal_tti_alienation_property_dev_resident(alienation_property_dev_resident, tti_alienation_property_dev_resident):
    tti_alienation_property_dev_resident=alienation_property_dev_resident
    return (tti_alienation_property_dev_resident)

"Calculation for tax base for income from alienation_property_dev_non_resident"	
@iterate_jit(nopython=True)
def cal_tti_alienation_property_dev_non_resident(alienation_property_dev_non_resident, tti_alienation_property_dev_non_resident):
    tti_alienation_property_dev_non_resident=alienation_property_dev_non_resident
    return (tti_alienation_property_dev_non_resident)




'7.Income (107) from alienation of property (except for what is indicated in lines 6 and 8 of this table) '

"Calculation for tax base for income from alienation_prop_resident"	
@iterate_jit(nopython=True)
def cal_tti_alienation_prop_resident(alienation_prop_resident, tti_alienation_prop_resident):
    tti_alienation_prop_resident=alienation_prop_resident
    return (tti_alienation_prop_resident)

"Calculation for tax base for income from alienation_prop_non_resident"	
@iterate_jit(nopython=True)
def cal_tti_alienation_prop_non_resident(alienation_prop_non_resident, tti_alienation_prop_non_resident):
    tti_alienation_prop_non_resident=alienation_prop_non_resident
    return (tti_alienation_prop_non_resident)
	

''' 8. Additional increase in the value of the property / Income received from the alienation of the building, its apartments or other premises by a developer who is not a sole entrepreneur (108)
'''
"Calculation for tax base for income from additional_value_prop_resident"	
@iterate_jit(nopython=True)
def cal_tti_additional_value_prop_resident(additional_value_prop_resident, tti_additional_value_prop_resident):
    tti_additional_value_prop_resident=additional_value_prop_resident
    return (tti_additional_value_prop_resident)

"Calculation for tax base for income from additional_value_prop_non_resident"	
@iterate_jit(nopython=True)
def cal_tti_additional_value_prop_non_resident(additional_value_prop_non_resident, tti_additional_value_prop_non_resident):
    tti_additional_value_prop_non_resident=additional_value_prop_non_resident
    return (tti_additional_value_prop_non_resident)

'9. Rent'
"Calculation for tax base for income from rent"
@iterate_jit(nopython=True)
def cal_tti_rent_resident(rent_resident, tti_rent_resident):
    tti_rent_resident=rent_resident
    return (tti_rent_resident)	

"Calculation for tax base for income from rent_non_resident"
@iterate_jit(nopython=True)
def cal_tti_rent_non_resident(rent_non_resident, tti_rent_non_resident):
    tti_rent_non_resident=rent_non_resident
    return (tti_rent_non_resident)	

'10. Dividends'

"Calculation for tax base for income from dividends_resident"
@iterate_jit(nopython=True)
def cal_tti_dividends_resident(dividends_resident, tti_dividends_resident):
    tti_dividends_resident=dividends_resident
    return (tti_dividends_resident)	

"Calculation for tax base for income from dividends_non_resident"	
@iterate_jit(nopython=True)
def cal_tti_dividends_non_resident(dividends_non_resident, tti_dividends_non_resident):
    tti_dividends_non_resident=dividends_non_resident
    return (tti_dividends_non_resident)	

'11.Insurance premium for physical persons'

"Calculation for tax base for income from insurance_premium_resident"
@iterate_jit(nopython=True)
def cal_tti_insurance_premium_resident(insurance_premium_resident, tti_insurance_premium_resident):
    tti_insurance_premium_resident=insurance_premium_resident
    return (tti_insurance_premium_resident)	

"Calculation for tax base for income from insurance_premium_non_resident"
@iterate_jit(nopython=True)
def cal_tti_insurance_premium_non_resident(insurance_premium_non_resident, tti_insurance_premium_non_resident):
    tti_insurance_premium_non_resident=insurance_premium_non_resident
    return (tti_insurance_premium_non_resident)	

'12. Voluntary pensions'

"Calculation for tax base for income from voluntary_pensions_resident"
@iterate_jit(nopython=True)
def cal_tti_voluntary_pensions_resident(voluntary_pensions_resident, tti_voluntary_pensions_resident):
    tti_voluntary_pensions_resident=voluntary_pensions_resident
    return (tti_voluntary_pensions_resident)	
	
"Calculation for tax base for income from voluntary_pensions_non_resident"
@iterate_jit(nopython=True)
def cal_tti_voluntary_pensions_non_resident(voluntary_pensions_non_resident, tti_voluntary_pensions_non_resident):
    tti_voluntary_pensions_non_resident=voluntary_pensions_non_resident
    return (tti_voluntary_pensions_non_resident)	


'14. Unpaid passive income during the 12-month period following the year in which the reduction was made'


"Calculation for tax base for income from unpaid_passive_12_month_resident"
@iterate_jit(nopython=True)
def cal_tti_unpaid_passive_12_month_resident(unpaid_passive_12_month_resident, tti_unpaid_passive_12_month_resident):
    tti_unpaid_passive_12_month_resident=unpaid_passive_12_month_resident
    return (tti_unpaid_passive_12_month_resident)	

"Calculation for tax base for income from unpaid_passive_12_month_non_resident"
@iterate_jit(nopython=True)
def cal_tti_unpaid_passive_12_month_non_resident(unpaid_passive_12_month_non_resident, tti_unpaid_passive_12_month_non_resident):
    tti_unpaid_passive_12_month_non_resident=unpaid_passive_12_month_non_resident
    return (tti_unpaid_passive_12_month_non_resident)



'''15. Income calculated for the performance of work under the employment contract of a foreign citizen or a stateless person 
       who does not have residence status in the Republic of Armenia'
'''

"Calculation for tax base for income from foreign_citizen_stateless_person_resident"
@iterate_jit(nopython=True)
def cal_tti_foreign_citizen_stateless_person_resident(foreign_citizen_stateless_person_resident, tti_foreign_citizen_stateless_person_resident):
    tti_foreign_citizen_stateless_person_resident=foreign_citizen_stateless_person_resident
    return (tti_foreign_citizen_stateless_person_resident)	


"Calculation for tax base for income from foreign_citizen_stateless_person_non_resident"
@iterate_jit(nopython=True)
def cal_tti_foreign_citizen_stateless_person_non_resident(foreign_citizen_stateless_person_non_resident, tti_foreign_citizen_stateless_person_non_resident):
    tti_foreign_citizen_stateless_person_non_resident=foreign_citizen_stateless_person_non_resident
    return (tti_foreign_citizen_stateless_person_non_resident)	


'16. Other income'

"Calculation for tax base for income from other_income_passive_resident"
@iterate_jit(nopython=True)
def cal_tti_other_income_passive_resident(other_income_passive_resident, tti_other_income_passive_resident):
    tti_other_income_passive_resident=other_income_passive_resident
    return (tti_other_income_passive_resident)	

"Calculation for tax base for income from other_income_passive_non_resident"
@iterate_jit(nopython=True)
def cal_tti_other_income_passive_non_resident(other_income_passive_non_resident, tti_other_income_passive_non_resident):
    tti_other_income_passive_non_resident=other_income_passive_non_resident
    return (tti_other_income_passive_non_resident)	


'17. Other passive income - OLD'

"Calculation for tax base for income from rent higher than AMD 60 mn"
@iterate_jit(nopython=True)
def cal_tti_rent_high(rent_high, tti_rent_high):
    tti_rent_high=rent_high
    return (tti_rent_high)

"Calculation for tax base for income from sale of securities"
@iterate_jit(nopython=True)
def cal_tti_stocks(stocks, tti_stocks):
    tti_stocks=stocks
    return (tti_stocks)


'III. Grouping of tax bases'
    
"Calculation for total tax base from all income sources ("
@iterate_jit(nopython=True)
def cal_tti_all(tti_wages, cap_allowance, tti_royalty_resident,tti_royalty_non_resident,tti_interest_resident,tti_interest_non_resident,tti_gaining_resident,tti_gaining_non_resident,
                tti_prize_resident,tti_prize_non_resident,tti_donation_resident,tti_donation_non_resident,tti_alienation_property_dev_resident,
                tti_alienation_property_dev_non_resident,tti_alienation_prop_resident,tti_alienation_prop_non_resident,tti_additional_value_prop_resident,
                tti_additional_value_prop_non_resident,tti_rent_resident,tti_rent_non_resident,tti_dividends_resident,
                tti_dividends_non_resident,tti_insurance_premium_resident,tti_insurance_premium_non_resident,
                tti_voluntary_pensions_resident,tti_voluntary_pensions_non_resident,tti_unpaid_passive_12_month_resident,tti_unpaid_passive_12_month_non_resident,
                tti_foreign_citizen_stateless_person_resident,tti_foreign_citizen_stateless_person_non_resident,tti_other_income_passive_resident,tti_other_income_passive_non_resident,tti_rent_high,
                tti_stocks,tti_all):
    tti_cap=tti_royalty_resident+tti_royalty_non_resident+tti_interest_resident+tti_interest_non_resident+tti_gaining_resident+tti_gaining_non_resident+tti_prize_resident+tti_prize_non_resident+tti_donation_resident+tti_donation_non_resident+tti_alienation_property_dev_resident+tti_alienation_property_dev_non_resident+tti_alienation_prop_resident+tti_alienation_prop_non_resident+tti_additional_value_prop_resident+tti_additional_value_prop_non_resident+tti_rent_resident+tti_rent_non_resident+tti_dividends_resident+tti_dividends_non_resident+tti_insurance_premium_resident+tti_insurance_premium_non_resident+tti_voluntary_pensions_resident+tti_voluntary_pensions_non_resident+tti_unpaid_passive_12_month_resident+tti_unpaid_passive_12_month_non_resident+tti_foreign_citizen_stateless_person_resident+tti_foreign_citizen_stateless_person_non_resident+tti_other_income_passive_resident+tti_other_income_passive_non_resident+tti_rent_high+tti_stocks
    if tti_cap <= cap_allowance:
        tti_cap = 0
    else:
        tti_cap = tti_cap
    tti_all=tti_wages+tti_cap
    return (tti_all)


    

'IV. Grouping of total gross income' 

"Calculation for gross total income from all income sources before deductions"
@iterate_jit(nopython=True)
def cal_tot_gross_inc(tti_wages,tti_royalty_resident,tti_royalty_non_resident,tti_interest_resident,tti_interest_non_resident,tti_gaining_resident,tti_gaining_non_resident,
                tti_prize_resident,tti_prize_non_resident,tti_donation_resident,tti_donation_non_resident,tti_alienation_property_dev_resident,
                tti_alienation_property_dev_non_resident,tti_alienation_prop_resident,tti_alienation_prop_non_resident,tti_additional_value_prop_resident,
                tti_additional_value_prop_non_resident,tti_rent_resident,tti_rent_non_resident,tti_dividends_resident,
                tti_dividends_non_resident,tti_insurance_premium_resident,tti_insurance_premium_non_resident,
                tti_voluntary_pensions_resident,tti_voluntary_pensions_non_resident,tti_unpaid_passive_12_month_resident,tti_unpaid_passive_12_month_non_resident,
                tti_foreign_citizen_stateless_person_resident,tti_foreign_citizen_stateless_person_non_resident,tti_other_income_passive_resident,tti_other_income_passive_non_resident,tti_rent_high,
                tti_stocks,deduction,total_gross_income):
    total_gross_income=tti_wages+tti_royalty_resident+tti_royalty_non_resident+tti_interest_resident+tti_interest_non_resident+tti_gaining_resident+tti_gaining_non_resident+tti_prize_resident+tti_prize_non_resident+tti_donation_resident+tti_donation_non_resident+tti_alienation_property_dev_resident+tti_alienation_property_dev_non_resident+tti_alienation_prop_resident+tti_alienation_prop_non_resident+tti_additional_value_prop_resident+tti_additional_value_prop_non_resident+tti_rent_resident+tti_rent_non_resident+tti_dividends_resident+tti_dividends_non_resident+tti_insurance_premium_resident+tti_insurance_premium_non_resident+tti_voluntary_pensions_resident+tti_voluntary_pensions_non_resident+tti_unpaid_passive_12_month_resident+tti_unpaid_passive_12_month_non_resident+tti_foreign_citizen_stateless_person_resident+tti_foreign_citizen_stateless_person_non_resident+tti_other_income_passive_resident+tti_other_income_passive_non_resident+tti_rent_high+tti_stocks+deduction
    return (total_gross_income)



'V.Calculation PIT' 

"5.1 Calculation for PIT from salaires,civil contracts, other income"
@iterate_jit(nopython=True)
def cal_pit_wages(tti_wages,rate1,rate2,rate3,rate4,tbrk1,tbrk2,tbrk3,pit_wages):
    """
        Note: 
             From 1 January 2020, a FLAT RATE of income tax on salaries was established, which will gradually decrease to 20 percent by 2023: 
      
             Period                                                         Income tax rate
          From 1 January 2020                                                    23 %
          From 1 January 2021                                                    22 %
          From 1 January 2022                                                    21%
          From 1 January 2023                                                    20 %
        
        (Source https://home.kpmg/xx/en/home/insights/2021/07/armenia-thinking-beyond-borders.html)
        
            
    """   
    
    pit_wages = (rate1 * min(tti_wages, tbrk1) +
                            rate2 * min(tbrk2 - tbrk1, max(0., tti_wages - tbrk1)) +
                            rate3 * min(tbrk3 - tbrk2, max(0., tti_wages - tbrk2)) +
                            rate4 * max(0., tti_wages - tbrk3))
    
        
    return (pit_wages)
    

'5.1 Royalty'                      
"Calculation for total tax from royalty "
@iterate_jit(nopython=True)
def cal_pit_royalty(tti_royalty_resident,tti_royalty_non_resident,rate_royalty_resident,rate_royalty_non_resident,pit_royalty):
    pit_royalty_resident = tti_royalty_resident*rate_royalty_resident
    pit_royalty_non_resident = tti_royalty_non_resident*rate_royalty_non_resident
    pit_royalty = pit_royalty_resident+pit_royalty_non_resident
    return (pit_royalty)

'5.2 Interest'   
"Calculation for total tax from interest "
@iterate_jit(nopython=True)
def cal_pit_interest(tti_interest_resident,tti_interest_non_resident,rate_interest_resident,rate_interest_non_resident,pit_interest):
    pit_interest_resident = tti_interest_resident*rate_interest_resident
    pit_interest_non_resident = tti_interest_non_resident*rate_interest_non_resident
    pit_interest = pit_interest_resident+pit_interest_non_resident
    return (pit_interest)

'5.3 Gaining'   
"Calculation for total tax from gaining "
@iterate_jit(nopython=True)
def cal_pit_gaining(tti_gaining_resident,tti_gaining_non_resident,rate1,pit_gaining):
    pit_gaining_resident = tti_gaining_resident*rate1
    pit_gaining_non_resident = tti_gaining_non_resident*rate1
    pit_gaining = pit_gaining_resident+pit_gaining_non_resident
    return (pit_gaining)

'5.4 Prize'   
"Calculation for total tax from prize "
@iterate_jit(nopython=True)
def cal_pit_prize(tti_prize_resident,tti_prize_non_resident,rate1,pit_prize):
    pit_prize_resident = tti_prize_resident*rate1
    pit_prize_non_resident = tti_prize_non_resident*rate1
    pit_prize = pit_prize_resident+pit_prize_non_resident
    return (pit_prize)

'5.5 Donation'   
"Calculation for total tax from donation "
@iterate_jit(nopython=True)
def cal_pit_donation(tti_donation_resident,tti_donation_non_resident,rate1,pit_donation):
    pit_donation_resident = tti_donation_resident*rate1
    pit_donation_non_resident = tti_donation_non_resident*rate1
    pit_donation = pit_donation_resident+pit_donation_non_resident
    return (pit_donation)

''''5.6  Insurance compensation / Income from the alienation of a persons share in the ownership of industrial, other commercial, and public property, including buildings, structures (including unfinished (semi-constructed), industrial, use of subsoil, and other land or property of industrial significance) '   '''
"Calculation for total tax from insurance "

@iterate_jit(nopython=True)
def cal_pit_alienation_property_dev(tti_alienation_property_dev_resident,tti_alienation_property_dev_non_resident,rate_alienation_property_dev_resident,rate_alienation_property_dev_non_resident,pit_alienation_property_dev):
    pit_alienation_property_dev_resident = tti_alienation_property_dev_resident*rate_alienation_property_dev_resident
    pit_alienation_property_dev_non_resident = tti_alienation_property_dev_non_resident*rate_alienation_property_dev_non_resident
    pit_alienation_property_dev = pit_alienation_property_dev_resident+pit_alienation_property_dev_non_resident
    return (pit_alienation_property_dev)


'5.7 Income (107) from alienation of property (except for what is indicated in lines 6 and 8 of this table)'   
"Calculation for total tax from alienation_prop "
@iterate_jit(nopython=True)
def cal_pit_alienation_prop(tti_alienation_prop_resident,tti_alienation_prop_non_resident,rate_alienation_prop_resident,rate_alienation_prop_non_resident,pit_alienation_prop):
    pit_alienation_prop_resident = tti_alienation_prop_resident*rate_alienation_prop_resident
    pit_alienation_prop_non_resident = tti_alienation_prop_non_resident*rate_alienation_prop_non_resident
    pit_alienation_prop = pit_alienation_prop_resident+pit_alienation_prop_non_resident
    return (pit_alienation_prop)

'5. 8. Additional increase in the value of the property / Income received from the alienation of the building, its apartments or other premises by a developer who is not a sole entrepreneur (108)'   
"Calculation for total tax from additional_value_prop "
@iterate_jit(nopython=True)
def cal_pit_additional_value_prop(tti_additional_value_prop_resident,tti_additional_value_prop_non_resident,rate_additional_value_prop_resident,rate_additional_value_prop_non_resident,pit_additional_value_prop):
    pit_additional_value_prop_resident = tti_additional_value_prop_resident*rate_additional_value_prop_resident
    pit_additional_value_prop_non_resident = tti_additional_value_prop_non_resident*rate_additional_value_prop_non_resident
    pit_additional_value_prop = pit_additional_value_prop_resident+pit_additional_value_prop_non_resident
    return (pit_additional_value_prop)
	
'5.9 Rent'   
"Calculation for total tax from rent "
@iterate_jit(nopython=True)
def cal_pit_rent(tti_rent_resident,tti_rent_non_resident,rate_rent_resident,rate_rent_non_resident,pit_rent):
    pit_rent_resident = tti_rent_resident*rate_rent_resident
    pit_rent_non_resident = tti_rent_non_resident*rate_rent_non_resident
    pit_rent = pit_rent_resident+pit_rent_non_resident
    return (pit_rent)

'5.10 Dividends'   
"Calculation for total tax from dividends "
@iterate_jit(nopython=True)
def cal_pit_dividends(tti_dividends_resident,tti_dividends_non_resident,rate_dividends_resident,rate_dividends_non_resident,pit_dividends):
    pit_dividends_resident = tti_dividends_resident*rate_dividends_resident
    pit_dividends_non_resident = tti_dividends_non_resident*rate_dividends_non_resident
    pit_dividends = pit_dividends_resident+pit_dividends_non_resident
    return (pit_dividends)

'5.11 Insurance_premium'   
"Calculation for total tax from insurance_premium "
@iterate_jit(nopython=True)
def cal_pit_insurance_premium(tti_insurance_premium_resident,tti_insurance_premium_non_resident,rate1,pit_insurance_premium):
    pit_insurance_premium_resident = tti_insurance_premium_resident*rate1
    pit_insurance_premium_non_resident = tti_insurance_premium_non_resident*rate1
    pit_insurance_premium = pit_insurance_premium_resident+pit_insurance_premium_non_resident
    return (pit_insurance_premium)

'5.12 Voluntary_pensions'   
"Calculation for total tax from voluntary_pensions "
@iterate_jit(nopython=True)
def cal_pit_voluntary_pensions(tti_voluntary_pensions_resident,tti_voluntary_pensions_non_resident,rate_voluntary_pensions_resident,rate_voluntary_pensions_non_resident,pit_voluntary_pensions):
    pit_voluntary_pensions_resident = tti_voluntary_pensions_resident*rate_voluntary_pensions_resident
    pit_voluntary_pensions_non_resident = tti_voluntary_pensions_non_resident*rate_voluntary_pensions_non_resident
    pit_voluntary_pensions = pit_voluntary_pensions_resident+pit_voluntary_pensions_non_resident
    return (pit_voluntary_pensions)

'5.14 Unpaid_passive_12_month'   
"Calculation for total tax from unpaid_passive_12_month "
@iterate_jit(nopython=True)
def cal_pit_unpaid_passive_12_month(tti_unpaid_passive_12_month_resident,tti_unpaid_passive_12_month_non_resident,rate_unpaid_passive_12_month_resident,rate_unpaid_passive_12_month_non_resident,pit_unpaid_passive_12_month):
    pit_unpaid_passive_12_month_resident = tti_unpaid_passive_12_month_resident*rate_unpaid_passive_12_month_resident
    pit_unpaid_passive_12_month_non_resident = tti_unpaid_passive_12_month_non_resident*rate_unpaid_passive_12_month_non_resident
    pit_unpaid_passive_12_month = pit_unpaid_passive_12_month_resident+pit_unpaid_passive_12_month_non_resident
    return (pit_unpaid_passive_12_month)


'5.15 Foreign_citizen_stateless_person'   
"Calculation for total tax from foreign_citizen_stateless_person "
@iterate_jit(nopython=True)
def cal_pit_foreign_citizen_stateless_person(tti_foreign_citizen_stateless_person_resident,tti_foreign_citizen_stateless_person_non_resident,rate1,pit_foreign_citizen_stateless_person):
    pit_foreign_citizen_stateless_person_resident = tti_foreign_citizen_stateless_person_resident*rate1
    pit_foreign_citizen_stateless_person_non_resident = tti_foreign_citizen_stateless_person_non_resident*rate1
    pit_foreign_citizen_stateless_person = pit_foreign_citizen_stateless_person_resident+pit_foreign_citizen_stateless_person_non_resident
    return (pit_foreign_citizen_stateless_person)

'5.16 Other_income_passive'   
"Calculation for total tax from other_income_passive "
@iterate_jit(nopython=True)
def cal_pit_other_income_passive(tti_other_income_passive_resident,tti_other_income_passive_non_resident,rate1,pit_other_income_passive):
    pit_other_income_passive_resident = tti_other_income_passive_resident*rate1
    pit_other_income_passive_non_resident = tti_other_income_passive_non_resident*rate1
    pit_other_income_passive = pit_other_income_passive_resident+pit_other_income_passive_non_resident
    return (pit_other_income_passive)


'5.17. Other types of passive income '
"Calculation for tax base for income from rent higher than AMD 60 mn"
@iterate_jit(nopython=True)
def cal_pit_rent_high(rent_high,rate_rent_high, pit_rent_high):
    pit_rent_high=rent_high * rate_rent_high
    return (pit_rent_high)

"5.18. Calculation for tax base for income from sale of securities"
@iterate_jit(nopython=True)
def cal_pit_stocks(stocks,rate_stocks, pit_stocks):
    pit_stocks=stocks* rate_stocks
    return (pit_stocks)

	
"5.19 Calculation for total tax from all sources"
@iterate_jit(nopython=True)
def cal_pit_all(pit_wages, cap_allowance, pit_royalty,pit_interest,pit_gaining,pit_prize,pit_donation,pit_alienation_property_dev,pit_alienation_prop,pit_additional_value_prop,pit_rent,pit_dividends,pit_insurance_premium,pit_voluntary_pensions,pit_unpaid_passive_12_month,pit_foreign_citizen_stateless_person,pit_other_income_passive,pit_rent_high,pit_stocks,pitax_all):
    pit_capital = pit_royalty+pit_interest+pit_gaining+pit_prize+pit_donation+pit_alienation_property_dev+pit_alienation_prop+pit_additional_value_prop+pit_rent+pit_dividends+pit_insurance_premium+pit_voluntary_pensions+pit_unpaid_passive_12_month+pit_foreign_citizen_stateless_person+pit_other_income_passive+pit_rent_high+pit_stocks
    if pit_capital < cap_allowance:
        pit_capital = 0
    else:
        pit_capital = pit_capital
    pitax_all =pit_wages+pit_capital
    return (pitax_all)


"Calculation for incorporating behavior - uses tax elasticity of total tax from labour income "
"Elasticity = % Change in income / % Change in tax rate "

@iterate_jit(nopython=True)
def cal_tti_wages_behavior(rate1, rate2, rate3, rate4, tbrk1, tbrk2, tbrk3,
                         rate1_curr_law, rate2_curr_law, rate3_curr_law, 
                         rate4_curr_law, tbrk1_curr_law, tbrk2_curr_law,
                         tbrk3_curr_law,
                         elasticity_pit_taxable_income_threshold,
                         elasticity_pit_taxable_income_value, tti_wages,
                         tti_wages_behavior):
    """
    Compute taxable total income after adjusting for behavior.
    """  
    elasticity_taxable_income_threshold0 = elasticity_pit_taxable_income_threshold[0]
    elasticity_taxable_income_threshold1 = elasticity_pit_taxable_income_threshold[1]
    #elasticity_taxable_income_threshold2 = elasticity_pit_taxable_income_threshold[2]
    elasticity_taxable_income_value0=elasticity_pit_taxable_income_value[0]
    elasticity_taxable_income_value1=elasticity_pit_taxable_income_value[1]
    elasticity_taxable_income_value2=elasticity_pit_taxable_income_value[2]
    if tti_wages<=0:
        elasticity=0
    elif tti_wages<elasticity_taxable_income_threshold0:
        elasticity=elasticity_taxable_income_value0
    elif tti_wages<elasticity_taxable_income_threshold1:
        elasticity=elasticity_taxable_income_value1
    else:
        elasticity=elasticity_taxable_income_value2

    if tti_wages<0:
        marg_rate=0
    elif tti_wages<=tbrk1:
        marg_rate=rate1
    elif tti_wages<=tbrk2:
        marg_rate=rate2
    elif tti_wages<=tbrk3:
        marg_rate=rate3
    else:        
        marg_rate=rate4

    if tti_wages<0:
        marg_rate_curr_law=0
    elif tti_wages<=tbrk1_curr_law:
        marg_rate_curr_law=rate1_curr_law
    elif tti_wages<=tbrk2_curr_law:
        marg_rate_curr_law=rate2_curr_law
    elif tti_wages<=tbrk3_curr_law:
        marg_rate_curr_law=rate3_curr_law
    else:        
        marg_rate_curr_law=rate4_curr_law
    
    frac_change_net_of_pit_rate = ((1-marg_rate)-(1-marg_rate_curr_law))/(1-marg_rate_curr_law)
    frac_change_tti_wages = elasticity*(frac_change_net_of_pit_rate)  
    tti_wages_behavior = tti_wages*(1+frac_change_tti_wages)
    return (tti_wages_behavior)




"Calculation behavior"
@iterate_jit(nopython=True)
def cal_tti_c_behavior(
                        rate1, cap_allowance,
                        rate_royalty_resident,rate_royalty_non_resident,
                        rate_interest_resident,rate_interest_non_resident,
                        rate_alienation_property_dev_resident,rate_alienation_property_dev_non_resident,
                        rate_alienation_prop_resident,rate_alienation_prop_non_resident,
                        rate_additional_value_prop_resident,rate_additional_value_prop_non_resident,
                        rate_rent_resident,rate_rent_non_resident,
                        rate_dividends_resident,rate_dividends_non_resident,
                        rate_voluntary_pensions_resident,rate_voluntary_pensions_non_resident,
                        rate_unpaid_passive_12_month_resident,rate_unpaid_passive_12_month_non_resident,
                        rate_rent_high,rate_stocks,
                        rate_sale_prop,rate_sale_prop_dev,
                        # Ratest current law
                        rate1_curr_law,
                        rate_royalty_curr_law,rate_royalty_non_resident_curr_law,
                        rate_interest_resident_curr_law,rate_interest_non_resident_curr_law,
                        #rate_insurance_resident_curr_law,rate_insurance_non_resident_curr_law,
                        rate_alienation_property_dev_resident_curr_law,rate_alienation_property_dev_non_resident_curr_law,
                        rate_alienation_prop_resident_curr_law,rate_alienation_prop_non_resident_curr_law,
                        rate_additional_value_prop_resident_curr_law,rate_additional_value_prop_non_resident_curr_law,
                        rate_rent_resident_curr_law,rate_rent_non_resident_curr_law,
                        rate_dividends_resident_curr_law,rate_dividends_non_resident_curr_law,
                        rate_voluntary_pensions_resident_curr_law,rate_voluntary_pensions_non_resident_curr_law,
                        rate_unpaid_passive_12_month_resident_curr_law,rate_unpaid_passive_12_month_non_resident_curr_law,
                        rate_rent_high_curr_law,rate_stocks_curr_law,
                        rate_sale_prop_curr_law,rate_sale_prop_dev_curr_law,                      
                        # Elasticities
                        elasticity_pit_capital_income_threshold,
                        elasticity_pit_capital_income_value,
                        # Passive income
                        tti_royalty_resident,tti_royalty_non_resident,
                        tti_interest_resident,tti_interest_non_resident,
                        tti_gaining_resident,tti_gaining_non_resident,
                        tti_prize_resident,tti_prize_non_resident,
                        tti_donation_resident,tti_donation_non_resident,
                        tti_alienation_property_dev_resident,tti_alienation_property_dev_non_resident,
                        tti_alienation_prop_resident,tti_alienation_prop_non_resident,
                        tti_additional_value_prop_resident,tti_additional_value_prop_non_resident,
                        tti_rent_resident,tti_rent_non_resident,
                        tti_dividends_resident,tti_dividends_non_resident,
                        tti_insurance_premium_resident,tti_insurance_premium_non_resident,
                        tti_voluntary_pensions_resident,tti_voluntary_pensions_non_resident,
                        tti_unpaid_passive_12_month_resident,tti_unpaid_passive_12_month_non_resident,
                        tti_foreign_citizen_stateless_person_resident,tti_foreign_citizen_stateless_person_non_resident,
                        tti_other_income_passive_resident,tti_other_income_passive_non_resident,
                        tti_rent_high,tti_stocks,tti_all,
                        # Behaviour                       
                        tti_c_royalty_resident_behavior,tti_c_royalty_non_resident_behavior,tti_c_interest_resident_behavior,tti_c_interest_non_resident_behavior,tti_c_gaining_resident_behavior,tti_c_gaining_non_resident_behavior,tti_c_prize_resident_behavior,tti_c_prize_non_resident_behavior,tti_c_donation_resident_behavior,tti_c_donation_non_resident_behavior,tti_c_insurance_resident_behavior,tti_c_insurance_non_resident_behavior,tti_c_alienation_prop_resident_behavior,tti_c_alienation_prop_non_resident_behavior,tti_c_additional_value_prop_resident_behavior,tti_c_additional_value_prop_non_resident_behavior,tti_c_rent_resident_behavior,tti_c_rent_non_resident_behavior,tti_c_dividends_resident_behavior,tti_c_dividends_non_resident_behavior,tti_c_insurance_premium_resident_behavior,tti_c_insurance_premium_non_resident_behavior,tti_c_voluntary_pensions_resident_behavior,tti_c_voluntary_pensions_non_resident_behavior,tti_c_unpaid_passive_12_month_resident_behavior,tti_c_unpaid_passive_12_month_non_resident_behavior,tti_c_citizen_stateless_resident_behavior,tti_c_citizen_stateless_non_resident_behavior,tti_c_other_income_passive_resident_behavior,tti_c_other_income_passive_non_resident_behavior,tti_c_rate_rent_high_resident_behavior,tti_c_stocks_resident_behavior,tti_c_sale_prop_resident_behavior
                        ):
    """
    Compute capital income under behavioral response
    """
    """
    The deductions (transport and medical) that are being done away with while
    intrducing Standard Deduction is not captured in the schedule also. Thus,
    the two deductions combined (crude estimate gives a figure of 30000) is
    added to "SALARIES" and then "std_deduction" (introduced as a policy
    variable) is deducted to get "Income_Salary". Standard Deduction is being
    intruduced only from AY 2021 onwards, "std_deduction" is set as 30000 for
    AY 2019 and of 2020 thus resulting in no change for those years.
    """

    elasticity_pit_capital_income_threshold0 = elasticity_pit_capital_income_threshold[0]
    elasticity_pit_capital_income_threshold1 = elasticity_pit_capital_income_threshold[1]
    
    elasticity_pit_capital_income_value0=elasticity_pit_capital_income_value[0]
    elasticity_pit_capital_income_value1=elasticity_pit_capital_income_value[1]
    elasticity_pit_capital_income_value2=elasticity_pit_capital_income_value[2]
    
    #tti_c = tti_all + tti_dividends ###<----------- In the old version, salaries are also included here, although this estimatio is only for passive income not income from salaries
    #tti_c = tti_royalty_resident+tti_royalty_non_resident+tti_interest_resident+tti_interest_non_resident+tti_gaining_resident+tti_gaining_non_resident+tti_prize_resident+tti_prize_non_resident+tti_donation_resident+tti_donation_non_resident+tti_insurance_resident+tti_insurance_non_resident+tti_alienation_prop_resident+tti_alienation_prop_non_resident+tti_additional_value_prop_resident+tti_additional_value_prop_non_resident+tti_rent_resident+tti_rent_non_resident+tti_dividends_resident+tti_dividends_non_resident+tti_insurance_premium_resident+tti_insurance_premium_non_resident+tti_voluntary_pensions_resident+tti_voluntary_pensions_non_resident+tti_unpaid_passive_12_month_resident+tti_unpaid_passive_12_month_non_resident+tti_foreign_citizen_stateless_person_resident+tti_foreign_citizen_stateless_person_non_resident+tti_other_income_passive_resident+tti_other_income_passive_non_resident+tti_rent_high+tti_stocks++tti_sale_prop_dev
    tti_c = tti_all
   
    if tti_c<=0:
        elasticity=0
    elif tti_c<=elasticity_pit_capital_income_threshold0:
        elasticity=elasticity_pit_capital_income_value0
    elif tti_c<=elasticity_pit_capital_income_threshold1:
        elasticity=elasticity_pit_capital_income_value1
    else:
        elasticity=elasticity_pit_capital_income_value2    
    # Frac change
    # 1. Royalty-Resident
    frac_change_net_of_pit_royalty_resident_income_rate = ((1-rate_royalty_resident)-(1-rate_royalty_curr_law))/(1-rate_royalty_curr_law)
    frac_change_tti_royalty_resident = elasticity*(frac_change_net_of_pit_royalty_resident_income_rate) 
    # Royalty-Non-Resident
    frac_change_net_of_pit_royalty_non_resident_income_rate = ((1-rate_royalty_non_resident)-(1-rate_royalty_non_resident_curr_law))/(1-rate_royalty_non_resident_curr_law)
    frac_change_tti_royalty_non_resident = elasticity*(frac_change_net_of_pit_royalty_non_resident_income_rate) 
    # 2.Interest-Resident
    frac_change_net_of_pit_interest_resident_income_rate = ((1-rate_interest_resident)-(1-rate_interest_resident_curr_law))/(1-rate_interest_resident_curr_law)
    frac_change_tti_interest_resident = elasticity*(frac_change_net_of_pit_interest_resident_income_rate) 
    # Interest-Non-Resident
    frac_change_net_of_pit_interest_non_resident_income_rate = ((1-rate_interest_non_resident)-(1-rate_interest_non_resident_curr_law))/(1-rate_interest_non_resident_curr_law)
    frac_change_tti_interest_non_resident = elasticity*(frac_change_net_of_pit_interest_non_resident_income_rate) 
    # 3.Gaining-Resident
    frac_change_net_of_pit_gaining_resident_income_rate = ((1-rate1)-(1-rate1_curr_law))/(1-rate1_curr_law)
    frac_change_tti_gaining_resident = elasticity*(frac_change_net_of_pit_gaining_resident_income_rate) 
    # Gaining-Non-Resident
    frac_change_net_of_pit_gaining_non_resident_income_rate = ((1-rate1)-(1-rate1_curr_law))/(1-rate1_curr_law)
    frac_change_tti_gaining_non_resident = elasticity*(frac_change_net_of_pit_gaining_non_resident_income_rate) 
    # 4.Prize-Resident
    frac_change_net_of_pit_prize_resident_income_rate = ((1-rate1)-(1-rate1_curr_law))/(1-rate1_curr_law)
    frac_change_tti_prize_resident = elasticity*(frac_change_net_of_pit_prize_resident_income_rate) 
    # Prize-Non-Resident
    frac_change_net_of_pit_prize_non_resident_income_rate = ((1-rate1)-(1-rate1_curr_law))/(1-rate1_curr_law)
    frac_change_tti_prize_non_resident = elasticity*(frac_change_net_of_pit_prize_non_resident_income_rate) 
    #5. Donation-Resident
    frac_change_net_of_pit_donation_resident_income_rate = ((1-rate1)-(1-rate1_curr_law))/(1-rate1_curr_law)
    frac_change_tti_donation_resident = elasticity*(frac_change_net_of_pit_donation_resident_income_rate) 
    # Donation-Non-Resident
    frac_change_net_of_pit_donation_non_resident_income_rate = ((1-rate1)-(1-rate1_curr_law))/(1-rate1_curr_law)
    frac_change_tti_donation_non_resident = elasticity*(frac_change_net_of_pit_donation_non_resident_income_rate) 
    #6. Insurance-Resident
    frac_change_net_of_pit_alienation_property_dev_resident_income_rate = ((1-rate_alienation_property_dev_resident)-(1-rate_alienation_property_dev_resident_curr_law))/(1-rate_alienation_property_dev_resident_curr_law)
    frac_change_tti_alienation_property_dev_resident = elasticity*(frac_change_net_of_pit_alienation_property_dev_resident_income_rate) 
    # Insurance-Non-Resident
    frac_change_net_of_pit_alienation_property_dev_non_resident_income_rate = ((1-rate_alienation_property_dev_non_resident)-(1-rate_alienation_property_dev_non_resident_curr_law))/(1-rate_alienation_property_dev_non_resident_curr_law)
    frac_change_tti_alienation_property_dev_non_resident = elasticity*(frac_change_net_of_pit_alienation_property_dev_non_resident_income_rate) 
    #7. Alienation_prop-Resident
    frac_change_net_of_pit_alienation_prop_resident_income_rate = ((1-rate_alienation_prop_resident)-(1-rate_alienation_prop_resident_curr_law))/(1-rate_alienation_prop_resident_curr_law)
    frac_change_tti_alienation_prop_resident = elasticity*(frac_change_net_of_pit_alienation_prop_resident_income_rate) 
    # Alienation_prop-Non-Resident
    frac_change_net_of_pit_alienation_prop_non_resident_income_rate = ((1-rate_alienation_prop_non_resident)-(1-rate_alienation_prop_non_resident_curr_law))/(1-rate_alienation_prop_non_resident_curr_law)
    frac_change_tti_alienation_prop_non_resident = elasticity*(frac_change_net_of_pit_alienation_prop_non_resident_income_rate) 
    #8. Additional_value_prop-Resident
    frac_change_net_of_pit_additional_value_prop_resident_income_rate = ((1-rate_additional_value_prop_resident)-(1-rate_additional_value_prop_resident_curr_law))/(1-rate_additional_value_prop_resident_curr_law)
    frac_change_tti_additional_value_prop_resident = elasticity*(frac_change_net_of_pit_additional_value_prop_resident_income_rate) 
    # Additional_value_prop-Non-Resident
    frac_change_net_of_pit_additional_value_prop_non_resident_income_rate = ((1-rate_additional_value_prop_non_resident)-(1-rate_additional_value_prop_non_resident_curr_law))/(1-rate_additional_value_prop_non_resident_curr_law)
    frac_change_tti_additional_value_prop_non_resident = elasticity*(frac_change_net_of_pit_additional_value_prop_non_resident_income_rate) 
    #9. Rent-Resident
    frac_change_net_of_pit_rent_resident_income_rate = ((1-rate_rent_resident)-(1-rate_rent_resident_curr_law))/(1-rate_rent_resident_curr_law)
    frac_change_tti_rent_resident = elasticity*(frac_change_net_of_pit_rent_resident_income_rate) 
    # Rent-Non-Resident
    frac_change_net_of_pit_rent_non_resident_income_rate = ((1-rate_rent_non_resident)-(1-rate_rent_non_resident_curr_law))/(1-rate_rent_non_resident_curr_law)
    frac_change_tti_rent_non_resident = elasticity*(frac_change_net_of_pit_rent_non_resident_income_rate) 
    #10. Dividends-Resident
    frac_change_net_of_pit_dividends_resident_income_rate = ((1-rate_dividends_resident)-(1-rate_dividends_resident_curr_law))/(1-rate_dividends_resident_curr_law)
    frac_change_tti_dividends_resident = elasticity*(frac_change_net_of_pit_dividends_resident_income_rate) 
    # Dividends-Non-Resident
    frac_change_net_of_pit_dividends_non_resident_income_rate = ((1-rate_dividends_non_resident)-(1-rate_dividends_non_resident_curr_law))/(1-rate_dividends_non_resident_curr_law)
    frac_change_tti_dividends_non_resident = elasticity*(frac_change_net_of_pit_dividends_non_resident_income_rate) 
    #11. Insurance_premium-Resident
    frac_change_net_of_pit_insurance_premium_resident_income_rate = ((1-rate1)-(1-rate1_curr_law))/(1-rate1_curr_law)
    frac_change_tti_insurance_premium_resident = elasticity*(frac_change_net_of_pit_insurance_premium_resident_income_rate) 
    # Insurance_premium-Non-Resident
    frac_change_net_of_pit_insurance_premium_non_resident_income_rate = ((1-rate1)-(1-rate1_curr_law))/(1-rate1_curr_law)
    frac_change_tti_insurance_premium_non_resident = elasticity*(frac_change_net_of_pit_insurance_premium_non_resident_income_rate) 
    #12. Voluntary_pensions-Resident
    frac_change_net_of_pit_voluntary_pensions_resident_income_rate = ((1-rate_voluntary_pensions_resident)-(1-rate_voluntary_pensions_resident_curr_law))/(1-rate_voluntary_pensions_resident_curr_law)
    frac_change_tti_voluntary_pensions_resident = elasticity*(frac_change_net_of_pit_voluntary_pensions_resident_income_rate) 
    # Voluntary_pensions-Non-Resident
    frac_change_net_of_pit_voluntary_pensions_non_resident_income_rate = ((1-rate_voluntary_pensions_non_resident)-(1-rate_voluntary_pensions_non_resident_curr_law))/(1-rate_voluntary_pensions_non_resident_curr_law)
    frac_change_tti_voluntary_pensions_non_resident = elasticity*(frac_change_net_of_pit_voluntary_pensions_non_resident_income_rate) 
    #14. Unpaid_passive_12_month-Resident
    frac_change_net_of_pit_unpaid_passive_12_month_resident_income_rate = ((1-rate_unpaid_passive_12_month_resident)-(1-rate_unpaid_passive_12_month_resident_curr_law))/(1-rate_unpaid_passive_12_month_resident_curr_law)
    frac_change_tti_unpaid_passive_12_month_resident = elasticity*(frac_change_net_of_pit_unpaid_passive_12_month_resident_income_rate) 
    # Unpaid_passive_12_month-Non-Resident
    frac_change_net_of_pit_unpaid_passive_12_month_non_resident_income_rate = ((1-rate_unpaid_passive_12_month_non_resident)-(1-rate_unpaid_passive_12_month_non_resident_curr_law))/(1-rate_unpaid_passive_12_month_non_resident_curr_law)
    frac_change_tti_unpaid_passive_12_month_non_resident = elasticity*(frac_change_net_of_pit_unpaid_passive_12_month_non_resident_income_rate) 
    #15. Citizen_stateless-Resident
    frac_change_net_of_pit_citizen_stateless_resident_income_rate = ((1-rate1)-(1-rate1_curr_law))/(1-rate1_curr_law)
    frac_change_tti_citizen_stateless_resident = elasticity*(frac_change_net_of_pit_citizen_stateless_resident_income_rate) 
    # Citizen_stateless-Non-Resident
    frac_change_net_of_pit_citizen_stateless_non_resident_income_rate = ((1-rate1)-(1-rate1_curr_law))/(1-rate1_curr_law)
    frac_change_tti_citizen_stateless_non_resident = elasticity*(frac_change_net_of_pit_citizen_stateless_non_resident_income_rate) 
    #16. Other_income-Resident
    frac_change_net_of_pit_other_income_resident_income_rate = ((1-rate1)-(1-rate1_curr_law))/(1-rate1_curr_law)
    frac_change_tti_other_income_resident = elasticity*(frac_change_net_of_pit_other_income_resident_income_rate) 
    # Other_income-Non-Resident
    frac_change_net_of_pit_other_income_non_resident_income_rate = ((1-rate1)-(1-rate1_curr_law))/(1-rate1_curr_law)
    frac_change_tti_other_income_non_resident = elasticity*(frac_change_net_of_pit_other_income_non_resident_income_rate) 
    #17. Other_income
    frac_change_net_of_pit_rent_high_income_rate = ((1-rate_rent_high)-(1-rate_rent_high_curr_law))/(1-rate_rent_high_curr_law)
    frac_change_tti_rent_high = elasticity*(frac_change_net_of_pit_rent_high_income_rate)
    #18. Stock
    frac_change_net_of_pit_stocks_income_rate = ((1-rate_stocks)-(1-rate_stocks_curr_law))/(1-rate_stocks_curr_law)
    frac_change_tti_stocks = elasticity*(frac_change_net_of_pit_stocks_income_rate)
    # Behavior
	# 1. Royalty-Resident
    tti_c_royalty_resident_behavior = tti_royalty_resident*(1+frac_change_tti_royalty_resident)    
     # Royalty-Non-Resident
    tti_c_royalty_non_resident_behavior = tti_royalty_non_resident*(1+frac_change_tti_royalty_non_resident)    
	 # 2. Interest-Resident
    tti_c_interest_resident_behavior = tti_interest_resident*(1+frac_change_tti_interest_resident)    
      # Interest-Non-Resident
    tti_c_interest_non_resident_behavior = tti_interest_non_resident*(1+frac_change_tti_interest_non_resident) 
	 # 3. Gaining-Resident
    tti_c_gaining_resident_behavior = tti_gaining_resident*(1+frac_change_tti_gaining_resident)    
      # Gaining-Non-Resident
    tti_c_gaining_non_resident_behavior = tti_gaining_non_resident*(1+frac_change_tti_gaining_non_resident) 
 	# 4. Prize-Resident
    tti_c_prize_resident_behavior = tti_prize_resident*(1+frac_change_tti_prize_resident)    
      # Prize-Non-Resident
    tti_c_prize_non_resident_behavior = tti_prize_non_resident*(1+frac_change_tti_prize_non_resident) 
	 #5. Donation-Resident
    tti_c_donation_resident_behavior = tti_donation_resident*(1+frac_change_tti_donation_resident)    
      # Donation-Non-Resident
    tti_c_donation_non_resident_behavior = tti_donation_non_resident*(1+frac_change_tti_donation_non_resident) 
 	# 6. Insurance-Resident
    tti_c_insurance_resident_behavior = tti_alienation_property_dev_resident*(1+frac_change_tti_alienation_property_dev_resident)    
      # Insurance-Non-Resident
    tti_c_insurance_non_resident_behavior = tti_alienation_property_dev_non_resident*(1+frac_change_tti_alienation_property_dev_non_resident) 
	 # 7.Alienation_prop-Resident
    tti_c_alienation_prop_resident_behavior = tti_alienation_prop_resident*(1+frac_change_tti_alienation_prop_resident)    
      # Alienation_prop-Non-Resident
    tti_c_alienation_prop_non_resident_behavior = tti_alienation_prop_non_resident*(1+frac_change_tti_alienation_prop_non_resident) 
 	# 8.Additional_value_prop-Resident
    tti_c_additional_value_prop_resident_behavior = tti_additional_value_prop_resident*(1+frac_change_tti_additional_value_prop_resident)    
      # Additional_value_prop-Non-Resident
    tti_c_additional_value_prop_non_resident_behavior = tti_additional_value_prop_non_resident*(1+frac_change_tti_additional_value_prop_non_resident) 
 	# 9. Rent-Resident
    tti_c_rent_resident_behavior = tti_rent_resident*(1+frac_change_tti_rent_resident)    
    #if tti_c_rent_resident_behavior <= cap_allowance:
        #tti_c_rent_resident_behavior = 0
    tti_c_rent_resident_behavior = max(tti_rent_resident - cap_allowance, 0)
     
      # Rent-Non-Resident
    tti_c_rent_non_resident_behavior = tti_rent_non_resident*(1+frac_change_tti_rent_non_resident) 
    #if tti_c_rent_non_resident_behavior <= cap_allowance:
        #tti_c_rent_non_resident_behavior = 0
    tti_c_rent_non_resident_behavior = max(tti_rent_non_resident - cap_allowance, 0)
 	# 10. Dividends-Resident
    tti_c_dividends_resident_behavior = tti_dividends_resident*(1+frac_change_tti_dividends_resident)    
      # Dividends-Non-Resident
    tti_c_dividends_non_resident_behavior = tti_dividends_non_resident*(1+frac_change_tti_dividends_non_resident) 
 	# 11. Insurance_premium-Resident
    tti_c_insurance_premium_resident_behavior = tti_insurance_premium_resident*(1+frac_change_tti_insurance_premium_resident)    
      # Insurance_premium-Non-Resident
    tti_c_insurance_premium_non_resident_behavior = tti_insurance_premium_non_resident*(1+frac_change_tti_insurance_premium_non_resident) 
	 # 12. Voluntary_pensions-Resident
    tti_c_voluntary_pensions_resident_behavior = tti_voluntary_pensions_resident*(1+frac_change_tti_voluntary_pensions_resident)    
      # Voluntary_pensions-Non-Resident
    tti_c_voluntary_pensions_non_resident_behavior = tti_voluntary_pensions_non_resident*(1+frac_change_tti_voluntary_pensions_non_resident) 
 	# 14. Unpaid_passive_12_month-Resident
    tti_c_unpaid_passive_12_month_resident_behavior = tti_unpaid_passive_12_month_resident*(1+frac_change_tti_unpaid_passive_12_month_resident)    
      # Unpaid_passive_12_month-Non-Resident
    tti_c_unpaid_passive_12_month_non_resident_behavior = tti_unpaid_passive_12_month_non_resident*(1+frac_change_tti_unpaid_passive_12_month_non_resident) 
	 # 15. Citizen_stateless-Resident #
    tti_c_citizen_stateless_resident_behavior = tti_foreign_citizen_stateless_person_resident*(1+frac_change_tti_citizen_stateless_resident)    
      # Citizen_stateless-Non-Resident
    tti_c_citizen_stateless_non_resident_behavior = tti_foreign_citizen_stateless_person_non_resident*(1+frac_change_tti_citizen_stateless_non_resident) 
	 # 16. Other_income_passive-Resident
    tti_c_other_income_passive_resident_behavior = tti_other_income_passive_resident*(1+frac_change_tti_other_income_resident)    
      # Other_income_passive-Non-Resident
    tti_c_other_income_passive_non_resident_behavior = tti_other_income_passive_non_resident*(1+frac_change_tti_other_income_non_resident) 
	 # 17. Rate_rent_high-Resident
    tti_c_rate_rent_high_resident_behavior = tti_rent_high*(1+frac_change_tti_rent_high)    
	 # 18. Stocks-Resident
    tti_c_stocks_resident_behavior = tti_stocks*(1+frac_change_tti_stocks)    
	
    
    return tti_c_royalty_resident_behavior,tti_c_royalty_non_resident_behavior,tti_c_interest_resident_behavior,tti_c_interest_non_resident_behavior,tti_c_gaining_resident_behavior,tti_c_gaining_non_resident_behavior,tti_c_prize_resident_behavior,tti_c_prize_non_resident_behavior,tti_c_donation_resident_behavior,tti_c_donation_non_resident_behavior,tti_c_insurance_resident_behavior,tti_c_insurance_non_resident_behavior,tti_c_alienation_prop_resident_behavior,tti_c_alienation_prop_non_resident_behavior,tti_c_additional_value_prop_resident_behavior,tti_c_additional_value_prop_non_resident_behavior,tti_c_rent_resident_behavior,tti_c_rent_non_resident_behavior,tti_c_dividends_resident_behavior,tti_c_dividends_non_resident_behavior,tti_c_insurance_premium_resident_behavior,tti_c_insurance_premium_non_resident_behavior,tti_c_voluntary_pensions_resident_behavior,tti_c_voluntary_pensions_non_resident_behavior,tti_c_unpaid_passive_12_month_resident_behavior,tti_c_unpaid_passive_12_month_non_resident_behavior,tti_c_citizen_stateless_resident_behavior,tti_c_citizen_stateless_non_resident_behavior,tti_c_other_income_passive_resident_behavior,tti_c_other_income_passive_non_resident_behavior,tti_c_rate_rent_high_resident_behavior,tti_c_stocks_resident_behavior


"Calculation for PIT from capital incorporating behavioural response"
@iterate_jit(nopython=True)
def cal_pit_cap_behavior(rate1,rate_royalty_resident,rate_royalty_non_resident,rate_interest_resident,rate_interest_non_resident,
						rate_alienation_property_dev_resident,rate_alienation_property_dev_non_resident,rate_alienation_prop_resident,rate_alienation_prop_non_resident,
						rate_additional_value_prop_resident,rate_additional_value_prop_non_resident,rate_rent_resident,rate_rent_non_resident,
						rate_dividends_resident,rate_dividends_non_resident,rate_voluntary_pensions_resident,rate_voluntary_pensions_non_resident,
						rate_unpaid_passive_12_month_resident,rate_unpaid_passive_12_month_non_resident,rate_rent_high,rate_stocks,rate_sale_prop,rate_sale_prop_dev,
						tti_c_royalty_resident_behavior,tti_c_royalty_non_resident_behavior,tti_c_interest_resident_behavior,tti_c_interest_non_resident_behavior,
						tti_c_gaining_resident_behavior,tti_c_gaining_non_resident_behavior,tti_c_prize_resident_behavior,tti_c_prize_non_resident_behavior,
						tti_c_donation_resident_behavior,tti_c_donation_non_resident_behavior,tti_c_insurance_resident_behavior,tti_c_insurance_non_resident_behavior,
						tti_c_alienation_prop_resident_behavior,tti_c_alienation_prop_non_resident_behavior,tti_c_additional_value_prop_resident_behavior,tti_c_additional_value_prop_non_resident_behavior,
						tti_c_rent_resident_behavior,tti_c_rent_non_resident_behavior,tti_c_dividends_resident_behavior,tti_c_dividends_non_resident_behavior,
						tti_c_insurance_premium_resident_behavior,tti_c_insurance_premium_non_resident_behavior,tti_c_voluntary_pensions_resident_behavior,tti_c_voluntary_pensions_non_resident_behavior,
						tti_c_unpaid_passive_12_month_resident_behavior,tti_c_unpaid_passive_12_month_non_resident_behavior,tti_c_citizen_stateless_resident_behavior,tti_c_citizen_stateless_non_resident_behavior,tti_c_other_income_passive_resident_behavior,tti_c_other_income_passive_non_resident_behavior,
						tti_c_rate_rent_high_resident_behavior,tti_c_stocks_resident_behavior,pit_c_behavior):
   pit_c_behavior = (
                        (tti_c_royalty_resident_behavior*rate_royalty_resident)+(tti_c_royalty_non_resident_behavior*rate_royalty_non_resident)+
                        (tti_c_interest_resident_behavior*rate_interest_resident)+(tti_c_interest_non_resident_behavior*rate_interest_non_resident)+
                        (tti_c_gaining_resident_behavior*rate1)+(tti_c_gaining_non_resident_behavior*rate1)+
                        (tti_c_prize_resident_behavior*rate1)+(tti_c_prize_non_resident_behavior*rate1)+
                        (tti_c_donation_resident_behavior*rate1)+(tti_c_donation_non_resident_behavior*rate1)+
                        (tti_c_insurance_resident_behavior*rate_alienation_property_dev_resident)+(tti_c_insurance_non_resident_behavior*rate_alienation_property_dev_non_resident)+
                        (tti_c_alienation_prop_resident_behavior*rate_alienation_prop_resident)+(tti_c_alienation_prop_non_resident_behavior*rate_alienation_prop_non_resident)+
                        (tti_c_additional_value_prop_resident_behavior*rate_additional_value_prop_resident)+(tti_c_additional_value_prop_non_resident_behavior*rate_additional_value_prop_non_resident)+
                        (tti_c_rent_resident_behavior*rate_rent_resident)+(tti_c_rent_non_resident_behavior*rate_rent_non_resident)+
                        (tti_c_dividends_resident_behavior*rate_dividends_resident)+(tti_c_dividends_non_resident_behavior*rate_dividends_non_resident)+
                        (tti_c_insurance_premium_resident_behavior*rate1)+(tti_c_insurance_premium_non_resident_behavior*rate1)+
                        (tti_c_voluntary_pensions_resident_behavior*rate_voluntary_pensions_resident)+(tti_c_voluntary_pensions_non_resident_behavior*rate_voluntary_pensions_non_resident)+
                        (tti_c_unpaid_passive_12_month_resident_behavior*rate_unpaid_passive_12_month_resident)+(tti_c_unpaid_passive_12_month_non_resident_behavior*rate_unpaid_passive_12_month_non_resident)+
                        (tti_c_citizen_stateless_resident_behavior*rate1)+(tti_c_citizen_stateless_non_resident_behavior*rate1)+
                        (tti_c_other_income_passive_resident_behavior*rate1)+(tti_c_other_income_passive_non_resident_behavior*rate1)+
                        (tti_c_rate_rent_high_resident_behavior*rate_rent_high)+
                        (tti_c_stocks_resident_behavior*rate_stocks))
                        
   
   return pit_c_behavior
   


"Calculation for PIT from labor income incorporating behavioural response"
@iterate_jit(nopython=True)
def cal_pit_w_behavior(tti_wages_behavior, rate1, rate2, rate3, rate4, tbrk1, tbrk2, tbrk3,rate_IT_sector,IT_sector,pit_w_behavior):
    """
    Compute tax liability given the progressive tax rate schedule specified
    by the (marginal tax) rate* and (upper tax bracket) brk* parameters and
    given taxable income (taxinc)
    """
    # subtract TI_special_rates from TTI to get Aggregate_Income, which is
    # the portion of TTI that is taxed at normal rates
    taxinc = tti_wages_behavior  
    
    if IT_sector==1:
       pit_w_behavior=rate_IT_sector*taxinc
    else:
      pit_w_behavior = (rate1 * min(taxinc, tbrk1) +
                    rate2 * min(tbrk2 - tbrk1, max(0., taxinc - tbrk1)) +
                    rate3 * min(tbrk3 - tbrk2, max(0., taxinc - tbrk2)) +
                    rate4 * max(0., taxinc - tbrk3))
        
    return (pit_w_behavior)



@iterate_jit(nopython=True)
def cal_pit_behavior(pit_c_behavior,pit_w_behavior, pitax_before_credits, sstax):
    """
    Explanation about total PIT calculation
    
    Gross amount of income tax:
    ------------------------------------------------------------------
    Employment contracts, civil contracts, and other incomes = 396.64
    Other sources of income (royalties, interest incomes etc.) = 44.56
    Temporary disability benefits=15.10
    Income declared by individuals (residents and nonresidents)= 2.70
    -----------------------------------------------------------------
    Total gross amount of income tax  = 459 
    
    Cash back from income tax:	
    -----------------------------------------------------------------
    Mortgage 	-22.70
    Dividends	-9.40
    Tuition fee 	-0.20
    -----------------------------------------------------------------
    Total cash back of income tax = 32.3
    
    
    Annual PIT amount, reported on the State Revenue Committee’s official website
    -----------------------------------------------------------------
    Net PIT= 459-32.3= 426.70 (bln. AMD)
    
    """
    
    pitax_before_credits = pit_c_behavior+pit_w_behavior
    

        
    #pitax = pitax-min(sstax*percent_deductible,pitax)
  
    return (pitax_before_credits)

@iterate_jit(nopython=True)
def pit_after_credits(prop_value_ceiling, mortgage_credit_ceiling, pitax_before_credits, prop_value, mortgage_credits, pitax):
    """
    Compute tax liability given the progressive tax rate schedule specified
    by the (marginal tax) rate* and (upper tax bracket) brk* parameters and
    given taxable income (taxinc)
    """
    
    if prop_value > prop_value_ceiling:
        allowable_mortgage_credits = 0
    else:
        allowable_mortgage_credits = min(mortgage_credit_ceiling, mortgage_credits)
        allowable_mortgage_credits = min(allowable_mortgage_credits, pitax_before_credits)
    
    pitax = pitax_before_credits - allowable_mortgage_credits
    
    return (pitax)