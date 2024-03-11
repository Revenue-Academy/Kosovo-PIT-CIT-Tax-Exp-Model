# -*- coding: utf-8 -*-
"""
Created on Thu Nov 11 18:28:24 2021

@author: wb305167
"""
import copy
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from tkinter import *
import tkinter.font as tkfont
from datetime import datetime

#from taxcalc import *
from taxcalc.utils import *
from taxcalc.display_funcs import *
from PIL import Image,ImageTk


def make_float(item):
    if isinstance(item, list):
        return [float(x) for x in item]
    else:
        return float(item)
    
def read_reform_dict(block_selected_dict):
    #print('block_selected_dict in read_reform_dict: ',block_selected_dict)
    years=[]
    for k in block_selected_dict.keys():
        if (block_selected_dict[k]['selected_year'] not in years):
            years = years + [block_selected_dict[k]['selected_year'][0]]
    ref = {}
    ref['policy']={}
    for year in years:
        policy_dict = {}
        for k in block_selected_dict.keys():
            #print('block_selected_dict.keys() ', k)
            if block_selected_dict[k]['selected_year'][0]==year:
                policy_dict['_'+block_selected_dict[k]['selected_item']]=[make_float(block_selected_dict[k]['selected_value'][0])]
        ref['policy'][int(year)] = policy_dict
    years = [int(x) for x in years]
    years.sort()
    return years, ref

def concat_dicts(block_selected_dict, elasticity_dict):
    years=[]
    max = 0
    for k in block_selected_dict.keys():
        if int(k) > max:
            max = int(k)
    for i in range(1,len(elasticity_dict)+1):
        block_selected_dict[str(max+i)] = elasticity_dict[str(i)]
    #ref = {}
    return block_selected_dict

def write_file(df, text_data, filename, window=None, footer_row_num=None):
    df.to_csv(filename+'.csv', mode='w')
    with open(filename+'.txt','w') as f:
        f.write(text_data)
    f.close
    if (window is not None) and (footer_row_num is not None):
        footer = ["footer", "*Data saved in file "+ filename]
        display_table(window, data=footer, footer=footer_row_num+2)
    
def weighted_total_tax(calc, tax_list, category, year, tax_dict, gdp=None, attribute_var = None):
    for tax_type in tax_list:
        tax_dict[tax_type][year][category] = {}
        tax_dict[tax_type][year][category]['value'] = calc.weighted_total_tax_dict(tax_type, tax_type+'ax')       #Function in calculator class
        #print(tax_dict[tax_type][year][category]['value'])
        tax_dict[tax_type][year][category]['value_bill'] = {}
        tax_dict[tax_type][year][category]['value_bill_str'] = {}
        if gdp is not None:
            tax_dict[tax_type][year][category]['value_gdp'] = {}
            tax_dict[tax_type][year][category]['value_gdp_str'] = {}        
        for k in tax_dict[tax_type][year][category]['value'].keys():
            tax_dict[tax_type][year][category]['value_bill'][k] = tax_dict[tax_type][year][category]['value'][k]/1e+6
            tax_dict[tax_type][year][category]['value_bill_str'][k] = '{0:.2f}'.format(tax_dict[tax_type][year][category]['value_bill'][k])        
            if gdp is not None:
                tax_dict[tax_type][year][category]['value_gdp'][k] = ((tax_dict[tax_type][year][category]['value'][k]/1e+6)/gdp[str(year)])*100
                tax_dict[tax_type][year][category]['value_gdp_str'][k] = '{0:.2f}'.format(tax_dict[tax_type][year][category]['value_gdp'][k])  
    #print('tax_dict ', tax_dict)
    return tax_dict
       
def weighted_total_tax_diff(tax_list, category1, category2, year, tax_dict, gdp=None, attribute_var = None):
    for tax_type in tax_list:
        tax_dict[tax_type][year][category2]['value_bill_diff'] = {}
        tax_dict[tax_type][year][category2]['value_bill_diff_str'] = {}
        if gdp is not None:
            tax_dict[tax_type][year][category2]['value_diff_gdp'] = {}
            tax_dict[tax_type][year][category2]['value_diff_gdp_str'] = {}
        for k in tax_dict[tax_type][year][category1]['value_bill'].keys():
            tax_dict[tax_type][year][category2]['value_bill_diff'][k] = (tax_dict[tax_type][year][category2]['value_bill'][k] -
                                                                  tax_dict[tax_type][year][category1]['value_bill'][k])
            tax_dict[tax_type][year][category2]['value_bill_diff_str'][k] = '{0:.2f}'.format(tax_dict[tax_type][year][category2]['value_bill_diff'][k])
            if gdp is not None:
                tax_dict[tax_type][year][category2]['value_diff_gdp'][k] = ((tax_dict[tax_type][year][category2]['value_bill'][k] -
                                                                  tax_dict[tax_type][year][category1]['value_bill'][k])/gdp[str(year)])*100
                tax_dict[tax_type][year][category2]['value_diff_gdp_str'][k] = '{0:.2f}'.format(tax_dict[tax_type][year][category2]['value_diff_gdp'][k])                
    return tax_dict

def screen_print(tax_list, category, year, tax_dict, item, item_desc):
    for tax_type in tax_list:
        print("The "+tax_type.upper()+" "+item_desc+" in billions is: ", tax_dict[tax_type][year][category][item]['All'])

    
def generate_policy_revenues():
    from taxcalc.growfactors import GrowFactors
    from taxcalc.policy import Policy
    from taxcalc.records import Records
    from taxcalc.gstrecords import GSTRecords
    from taxcalc.corprecords import CorpRecords
    from taxcalc.parameters import ParametersBase
    from taxcalc.calculator import Calculator
    from taxcalc.utils import dist_variables

    f = open('global_vars.json')
    global_variables = json.load(f)
    verbose = global_variables['verbose']
    start_year = int(global_variables['start_year'])
    end_year = int(global_variables['end_year'])
    data_start_year = int(global_variables['data_start_year'])
    attribute_varlist = global_variables['attribute_vars']
    percent_gdp=global_variables['percent_gdp']
    if percent_gdp==0:
        GDP_Nominal = None
    else:
        GDP_Nominal = global_variables['GDP_Nominal']       
    #print('display_revenue_table in generate policy revenues ',global_variables['cit'+'_display_revenue_table'])
    if len(attribute_varlist)==0: 
        attribute_var = None
    else:
        attribute_var = attribute_varlist[0]

    '''Create empty lists to store variable names i.e. pit, cit, vat in tax_list; citax, totax in tax_collection_var_list'''
    tax_list=[]
    tax_collection_var_list = []
    id_varlist = []
    # start the simulation for pit/cit/vat    
    if global_variables['pit']:
        #tax_list = tax_list + ['pit', 'sst']
        tax_list = tax_list + ['pit']
        tax_collection_var_list = tax_collection_var_list + ['pitax']
        id_varlist = id_varlist + [global_variables['pit_id_var']]        
        recs = Records(data=global_variables['pit_data_filename'], weights=global_variables['pit_weights_filename'], gfactors=GrowFactors(growfactors_filename=global_variables['GROWFACTORS_FILENAME']))
        #tax_collection_var = 'pitax'
        tax_collection_var = {}
        for tax_type in tax_list:
            tax_collection_var[tax_type] = tax_type+'ax'
    else:
        recs = None
    if global_variables['cit']:
        tax_list = tax_list + ['cit', 'tot']
        tax_collection_var_list = tax_collection_var_list + ['citax'] 
        id_varlist = id_varlist + [global_variables['cit_id_var']]        
        crecs = CorpRecords(data=global_variables['cit_data_filename'], weights=global_variables['cit_weights_filename'], gfactors=GrowFactors(growfactors_filename=global_variables['GROWFACTORS_FILENAME']))
        #tax_collection_var = 'citax'
        tax_collection_var = {}
        for tax_type in tax_list:
            tax_collection_var[tax_type] = tax_type+'ax'
        
    else:
        crecs = None
    if global_variables['vat']:
        tax_list = tax_list + ['vat']
        tax_collection_var_list = tax_collection_var_list + ['vatax']
        id_varlist = id_varlist + [global_variables['vat_id_var']]         
        grecs = GSTRecords(data=global_variables['vat_data_filename'], weights=global_variables['vat_weights_filename'], gfactors=GrowFactors(growfactors_filename=global_variables['GROWFACTORS_FILENAME']))
        tax_collection_var = 'vatax'
    else:
        grecs = None  
    
    adjust_behavior = 0
    for tax_type in tax_list:
        adjust_behavior = adjust_behavior or global_variables[tax_type+'_adjust_behavior']
        #adjust_behavior = global_variables[tax_type+'_adjust_behavior']
    
    '''For distribution tables create dictionaries to store names of distribution_json_filename (e.g. cit_distribution_armenia.json), and 
    distribution_vardict_dict to store the distribution variables (e.g. 'DIST VARIABLES' i.e. weight, calc_gti, citax; DIST TABLE COLUMNS;
    DECILE ROW NAMES, STD ROW NAMES etc.)'''
    chart_list = []
    distribution_json_filename = {}
    distribution_vardict_dict = {}
    income_measure = {}
    for tax_type in tax_list:
        #print(tax_type)
        if global_variables[tax_type+'_distribution_table']:
            distribution_json_filename[tax_type] = 'taxcalc/'+global_variables[tax_type+'_distribution_json_filename']
            f = open(distribution_json_filename[tax_type])
            distribution_vardict_dict[tax_type] = json.load(f)
            #print('distribution_vardict_dict[tax_type] ', distribution_vardict_dict[tax_type])
            income_measure[tax_type] = distribution_vardict_dict[tax_type]['income_measure']
            print('income measure', income_measure[tax_type])

    '''  Open refom json file containing reforms added in the model and assign them to block_selected_dict for running reform policy in calculator'''

    f = open('reform.json')
    block_selected_dict = json.load(f)
    if verbose:
        print("block_selected_dict from json",block_selected_dict)
    
    # create Policy object containing current-law policy
    pol = Policy(DEFAULTS_FILENAME=global_variables['DEFAULTS_FILENAME'])
    
    # specify Calculator objects for current-law policy
    calc1 = Calculator(policy=pol, records=recs, corprecords=crecs, gstrecords=grecs, verbose=verbose)    
    assert isinstance(calc1, Calculator)
    assert calc1.current_year == data_start_year
    np.seterr(divide='ignore', invalid='ignore')

    '''Run reform policy using block_selected_dict '''

    pol2 = Policy(DEFAULTS_FILENAME=global_variables['DEFAULTS_FILENAME'])      
    years, reform=read_reform_dict(block_selected_dict)
    pol2.implement_reform(reform['policy'])
    calc2 = Calculator(policy=pol2, records=recs, corprecords=crecs, gstrecords=grecs, verbose=verbose)

    #tax_collection_var = tax_collection_var_list[0]
    id_var = id_varlist[0]

    '''Run reform policy using behavioral elasticities '''

    if adjust_behavior:
        elasticity_dict = {}
        for tax_type in tax_list:
            f = open('taxcalc/'+tax_type+'_elasticity_selection.json')
            elasticity_dict[tax_type] = json.load(f)
            if len(elasticity_dict[tax_type])>0:
                print(elasticity_dict)
                block_selected_dict = concat_dicts(block_selected_dict, elasticity_dict[tax_type])
        #print('block_selected_dict in adjust behavior',block_selected_dict)
        pol3 = Policy(DEFAULTS_FILENAME=global_variables['DEFAULTS_FILENAME'])   
        years, reform=read_reform_dict(block_selected_dict)
        #print('reform dict in adjust behavior', reform)
        pol3.implement_reform(reform['policy'])
        calc3 = Calculator(policy=pol3, records=recs, corprecords=crecs, gstrecords=grecs, verbose=verbose)
      
    #print("block_selected_dict after merging: ", block_selected_dict)     

    '''  Store the tax collection under current law, reform, difference, behavior in "revenue_dict" 
      Tax collection will be retreived from the dataframe or dataframe_cit in calc and stored in "revenue_dict"  '''  
        
    #total_revenue_text={}
    #reform_revenue_text={}
    #revenue_amount_dict = {}
    #num = 1
    #first_time = True
    #rows = []

    revenue_dict={}
    i=1
    #j=0

    ''' window_dict is a tkinter window '''

    window_dict={}
    row_num = {}
    data_row = {}
    l_TAB3 = {}

    '''dt1 and dt2 are used to store distribution table values - tax collection by weighted deciles '''
    dt1 = {}
    dt2 = {}

    ''' dt3 and dt4 are used to store distribution table values - tax collection by income level '''
    dt3 = {}
    dt4 = {}

    ''' dt1_percentile and dt2_percentile are used to store distribution table values - tax collection by percentiles '''
    dt1_percentile = {}
    dt2_percentile = {}


    dt = {}
    dt_percentile = {}

    ''' df_tax1 and df_tax2 stores values from calc.dataframe '''
    df_tax1 = {}
    df_tax2 = {}

    ''' title header store name of title in tables'''
    title_header = {}

    ''' positional variables for table '''
    shift_x = 600
    shift_y = 140    
    shift = 500

    '''Create empty dictionaries to store values for each tax type i.e. pit, cit, vat'''
    for tax_type in tax_list:
        revenue_dict[tax_type]={}
        dt1[tax_type] = {}
        dt2[tax_type] = {}
        dt3[tax_type] = {}
        dt4[tax_type] = {}
        dt1_percentile[tax_type] = {}
        dt2_percentile[tax_type] = {}
        dt[tax_type] = {}
        dt_percentile[tax_type] = {}
        df_tax1[tax_type] = {}
        df_tax2[tax_type] = {}
        for year in range(data_start_year, end_year+1):
            revenue_dict[tax_type][year]={}
        print(tax_type)
        #print(tax_type+'_display_revenue_table')
        #print(global_variables[tax_type+'_display_revenue_table'])
    
        #If the display revenue table is 1 (for e.g. cit_display_revenue_table = 1) in globalvars.json then create a window to show revenue table
        
        if global_variables[tax_type+'_display_revenue_table']:
            window_dict[tax_type] = tk.Toplevel()
            window_dict[tax_type].geometry("600x600+"+str(shift_x)+"+"+str(shift_y)) 
            window_dict[tax_type].font = ("Courier New", 12)
            shift_x = shift_x + shift
            shift_y = shift_y            
        
        #display_table(window, header=True) - display the headers i.e. Year, Current Law, Reform, Difference
            header = ["header","Year", "Current Law", "Reform", "Diff"]
            
            if global_variables[tax_type+'_adjust_behavior']:
                header = header + ['Reform (Behavior)', "Diff"]
            title_header[tax_type] = [["title", tax_type.upper()+" Projections (millions)"], header]
            if percent_gdp:
                title_header[tax_type] = [["title", tax_type.upper()+" Projections (% of GDP)"], header]
            row_num[tax_type] = display_table(window_dict[tax_type], data=title_header[tax_type], header=True) #since row_index = 'title', row_num will stop at 1 in display_table func


    #tax_type = tax_list[0]
    data = {}
    for year in range(data_start_year, end_year+1):       
        calc1.advance_to_year(year)
        calc2.advance_to_year(year)
        calc1.calc_all()
        #data[year] = calc1.dataframe_cit(['id_n','calc_gti', 'calc_turnover_small', 'citax', 'totax'])
        data[year] = calc1.dataframe(['id_n', 'calc_total_inc', 'pitax'])
        calc2.calc_all()
       
        #print("Gini Coefficient", calc1.gini(gross_i_w))
        
        '''
        Revenue dict is a dictionary containing for each category of policy i.e. current law, reform and difference, 
        the value of weighted total tax collection for each tax in the format dict[tax_type][year][category][value]
        for e.g {"cit": {"2022": {"current_law": {"value": {"All": 279643855688.247}, "value_bill": {"All": 279.643855688247}, "value_bill_str": {"All": "279.64"}}
        
        '''
        '''First category is current Law'''
        revenue_dict = weighted_total_tax(calc1, tax_list, 'current_law', year, revenue_dict, GDP_Nominal, attribute_var)              
        if verbose:
            print(f'TAX COLLECTION FOR THE YEAR - {year} \n')        
            screen_print(tax_list, 'current_law', year, revenue_dict, 'value_bill', 'Collection')
        
        '''Second category is reform'''
        revenue_dict = weighted_total_tax(calc2, tax_list, 'reform', year, revenue_dict, GDP_Nominal, attribute_var)
        if verbose:        
            print(f'\nTAX COLLECTION FOR THE YEAR UNDER REFORM - {year} \n')       
            screen_print(tax_list, 'reform', year, revenue_dict, 'value_bill', 'Collection')
        
        '''Third category is difference between current policy and reform'''
        revenue_dict = weighted_total_tax_diff(tax_list, 'current_law', 'reform', year, revenue_dict, GDP_Nominal, attribute_var)
        if verbose:        
            screen_print(tax_list, 'reform', year, revenue_dict, 'value_bill_diff', 'Collection difference under Reform')

        
        if global_variables[tax_type+'_display_revenue_table']:
            for tax_type in tax_list:
                if percent_gdp:
                    data_row[tax_type] = [str(year), revenue_dict[tax_type][year]['current_law']['value_gdp_str']['All'], 
                                      revenue_dict[tax_type][year]['reform']['value_gdp_str']['All'], 
                                      revenue_dict[tax_type][year]['reform']['value_diff_gdp_str']['All']]                     
                else:
                    data_row[tax_type] = [str(year), revenue_dict[tax_type][year]['current_law']['value_bill_str']['All'], 
                                      revenue_dict[tax_type][year]['reform']['value_bill_str']['All'], 
                                      revenue_dict[tax_type][year]['reform']['value_bill_diff_str']['All']]       

        if adjust_behavior:
        #redo the calculations by including behavioral adjustment
            calc3.advance_to_year(year)
            calc3.calc_all()

            '''Fourth category added to revenue_dict is 'behavior' if behavior is selected in tab3'''
            revenue_dict = weighted_total_tax(calc3, tax_list, 'reform_behavior', year, revenue_dict, GDP_Nominal, attribute_var)
            if verbose:            
                print(f'\nTAX COLLECTION FOR THE YEAR UNDER REFORM WITH BEHAVIOR ADJUSTMENT - {year} \n')
                screen_print(tax_list, 'reform_behavior', year, revenue_dict, 
                             'value_bill', 'Collection with Behavioral Adjustment')
            
            '''Fifth category added to revenue_dict is difference between current policy or reform and behavior'''

            revenue_dict = weighted_total_tax_diff(tax_list, 'current_law', 'reform_behavior', year, revenue_dict, GDP_Nominal, attribute_var)
            if verbose:
                screen_print(tax_list, 'reform_behavior', year, revenue_dict, 
                             'value_bill_diff',
                             'Collection difference with Behavioral Adjustment')
            if global_variables[tax_type+'_display_revenue_table']:
                for tax_type in tax_list:
                    if percent_gdp:
                        data_row[tax_type] = data_row[tax_type] + [revenue_dict[tax_type][year]['reform_behavior']['value_gdp_str']['All'], 
                                                           revenue_dict[tax_type][year]['reform_behavior']['value_diff_gdp_str']['All']]
                    else:
                        data_row[tax_type] = data_row[tax_type] + [revenue_dict[tax_type][year]['reform_behavior']['value_bill_str']['All'], 
                                                           revenue_dict[tax_type][year]['reform_behavior']['value_bill_diff_str']['All']]
        
        print('data_row', data_row)                        
        
        
        '''
        Display table is a function in display_func.py with following arguments
        display_table(window, data=None, header=None, year=None, row=None, footer=None, all=None, dataframe=None)
        Here window is the tkinter window, data is the row to be added to the table i.e. for each year - weighted tax collection under
        current law, reform and difference; row is the row number where data is to be added - the display function gives the last row + 1 as output 
        to be used as input in the next iteration so that a new row can be added with that row position
        e.g.
        data_row['cit'] = ['2022', 279.64, 279.64, 0]   
        '''
        #Note that from previous step the row_num has been increased by 1 - 
        #Thus after first row containing headers, output of display_table was 2 - thus row_num for first loop with year 2022 is 2.
        #After the first loop with year=2022, output of display_table is 3 and so on
        #If arguments in display_table func do not have header and row is specified then row is not none 
        
        for tax_type in tax_list:
            print('tax_type is', tax_type)
            if global_variables[tax_type+'_display_revenue_table']:
                if year>=start_year:
                    row_num[tax_type] = display_table(window_dict[tax_type], 
                                                    data = data_row[tax_type], 
                                                    row = row_num[tax_type])
            #display_table(window, revenue_dict_pit=revenue_dict_pit, year=year, row=i)
        
            i=i+1
            dt1[tax_type][year]={}
            dt2[tax_type][year]={}
            dt3[tax_type][year]={}
            dt4[tax_type][year]={}
            dt1_percentile[tax_type][year]={}
            dt2_percentile[tax_type][year]={}      
            df_tax1[tax_type][year] = {}
            df_tax2[tax_type][year] = {}
            #print(tax_type+'_distribution_table')
            income_measure = {}
            distribution_json_filename[tax_type] = 'taxcalc/'+global_variables[tax_type+'_distribution_json_filename']
            f = open(distribution_json_filename[tax_type])
            distribution_vardict_dict[tax_type] = json.load(f)
            income_measure[tax_type] = distribution_vardict_dict[tax_type]['income_measure']

            if global_variables[tax_type+'_distribution_table']:
                #print(tax_type+'_distribution_table')
                if not global_variables[tax_type+'_display_distribution_table_by_attribute']:
                    dist_table_attribute_var=None
                else:
                    dist_table_attribute_var = attribute_var
                '''
                Generate distribution tables by output categories (weighted deciles, income or percentiles) by using the calc1.distribution_tables_dict function in
                Calculator class which creates two tables for each output category - dt1 using calc1 (baseline or current law) and dt2 using calc2 (reform)
                Calc.distribution_tables_dict function uses a function self.distribution_table_dataframe to generate self or baseline dist table and 
                calc2.distribution_table_dataframe to generate reform dist table
                                
                '''
                output_in_averages = True
                output_categories = 'weighted_deciles' 
                dt1[tax_type][year], dt2[tax_type][year] = calc1.distribution_tables_dict(tax_type, calc2, output_categories, 
                                                    distribution_vardict_dict[tax_type], income_measure=income_measure[tax_type],
                                                    averages=output_in_averages,
                                                    scaling=True, attribute_var=dist_table_attribute_var)
                
                output_categories = 'standard_income_bins'
                output_in_averages = False
                dt3[tax_type][year], dt4[tax_type][year] = calc1.distribution_tables_dict(tax_type, calc2, output_categories, 
                                                    distribution_vardict_dict[tax_type], income_measure=income_measure[tax_type],
                                                    averages=output_in_averages,
                                                    scaling=True, attribute_var=dist_table_attribute_var)
                
            
                output_categories = 'weighted_percentiles'
                dt1_percentile[tax_type][year], dt2_percentile[tax_type][year] = calc1.distribution_tables_dict(tax_type, calc2, output_categories, 
                                                    distribution_vardict_dict[tax_type], income_measure=income_measure[tax_type],
                                                    averages=output_in_averages,
                                                    scaling=True, attribute_var=dist_table_attribute_var)

            if tax_type=='pit':
                df_tax1[tax_type][year]['All'] = calc1.dataframe([id_var, 'weight', income_measure[tax_type], tax_collection_var[tax_type]])
                df_tax1[tax_type][year]['All'].set_index(id_var)
                df_tax2[tax_type][year]['All'] = calc2.dataframe([id_var, 'weight', income_measure[tax_type], tax_collection_var[tax_type]])
                df_tax2[tax_type][year]['All'].set_index(id_var)
            elif tax_type=='cit':
                df_tax1[tax_type][year]['All'] = calc1.dataframe_cit([id_var, 'weight', income_measure[tax_type], tax_collection_var[tax_type]])
                df_tax1[tax_type][year]['All'].set_index(id_var)
                df_tax2[tax_type][year]['All'] = calc2.dataframe_cit([id_var, 'weight', income_measure[tax_type], tax_collection_var[tax_type]])
                df_tax2[tax_type][year]['All'].set_index(id_var)
            elif tax_type=='tot':
                df_tax1[tax_type][year]['All'] = calc1.dataframe_cit([id_var, 'weight', income_measure[tax_type], tax_collection_var[tax_type]])
                df_tax1[tax_type][year]['All'].set_index(id_var)
                df_tax2[tax_type][year]['All'] = calc2.dataframe_cit([id_var, 'weight', income_measure[tax_type], tax_collection_var[tax_type]])
                df_tax2[tax_type][year]['All'].set_index(id_var)
            elif tax_type=='vat':
                df_tax1[tax_type][year]['All'] = calc1.dataframe_vat([id_var, 'weight', income_measure[tax_type], tax_collection_var])
                df_tax1[tax_type][year]['All'].set_index(id_var)
                df_tax2[tax_type][year]['All'] = calc2.dataframe_vat([id_var, 'weight', income_measure[tax_type], tax_collection_var])
                df_tax2[tax_type][year]['All'].set_index(id_var)
                #print('dt1_percentile[tax_type][year] ', dt1_percentile[tax_type][year])
        #print('df_tax1', df_tax1)
    for year in range(data_start_year, end_year+1):
        dfcalc = data.get(year)     
        dfcalc.to_csv('{}'.format(tax_type) + '_output'+ '{}'.format(year) + '.csv')

    def calc_gini(df_tax12, tax_type):
        """
        Return gini.
        """
        gini = pd.DataFrame()
        gini['weight'] = df_tax12['All']['weight'+'_'+str(start_year)]
        gini['pre_tax_income'] =abs(df_tax12['All'][income_measure[tax_type]+'_'+str(start_year)])
        gini['pitax_current_law'] = df_tax12['All'][tax_collection_var[tax_type]+'_'+str(start_year)]
        gini['pitax_reform'] = df_tax12['All'][tax_collection_var[tax_type]+'_ref_'+str(start_year)]  

        #gini.to_csv('df_for_gini.csv', index=False)
        #print('gini ', gini)
        varlist = ['pre_tax_income', 'pitax_current_law', 'pitax_reform']
        kakwani_list = []
        gini= gini.sort_values(by='pre_tax_income')
        #gini['weight'] = 100
        gini['cumulative_weight']=np.cumsum(gini['weight'])
        sum_weight = (gini['weight']).sum()
        # This is the cumulative population plotted on the X Axis
        gini['percentage_cumul_pop'] = gini['cumulative_weight']/sum_weight
        gini['total_income'] = gini['weight']*gini['pre_tax_income']
        # This is the cumulative income plotted on the Y Axis
        gini['cumulative_total_income']= np.cumsum(gini['total_income'])
        sum_total_income = sum(gini['total_income'])
        gini['percentage_cumul_income'] = gini['cumulative_total_income']/sum_total_income
        # This is the gap between the 45 degree line and the Lorenz curve
        # We are trying to calculate "A"
        # 45 degree line means that the "Y Value" is the same as the
        # the "X Value" i.e. gini['percentage_cumul_pop']
        gini['height'] = gini['percentage_cumul_pop']-gini['percentage_cumul_income']
        print('gini ', gini)
        # We insert a zero row in the beginning inorder to have a reading 
        # for the origin (0,0) of the Lorenz curve 
        gini1 = pd.DataFrame([[np.nan]*len(gini.columns)], columns=gini.columns)
        #gini = gini1.append(gini, ignore_index=True)
        gini = pd.concat([gini1, gini], axis=0)      
        # taking care of the NANs including filling 0 in the first row
        gini['percentage_cumul_pop']= gini['percentage_cumul_pop'].fillna(0)
        gini['percentage_cumul_income']= gini['percentage_cumul_income'].fillna(0)
        gini['height']= gini['height'].fillna(0)
        gini['base'] = gini.percentage_cumul_pop.diff()
        gini['base']= gini['base'].fillna(0)
        # Calculate the area of the trapezoid
        gini['integrate_area']= 0.5*gini['base']*(gini['height']+gini['height'].shift())
        sum_integrate_area = gini['integrate_area'].sum()
        # The Gini is 2xA where A is the area between the 45 degree
        # line and the Lorenz Curve
        gini_index0 = 2*(sum_integrate_area)
        kakwani_list = kakwani_list + [gini_index0]
        
        # Repeat the process to calculate the Concentration Coefficient
        # for the remaining variables. We retain the same order
        # as that when we calculated the Gini for Income
        # so we do not sort the values
        
        for var in varlist[1:]:
            # We drop the zero row we created earlier
            gini = gini[1:]
            # We use the same columns "total_income"
            # This could be renamed as "Y var" to be more general
            gini['total_income'] = gini['weight']*gini[var]
            gini['cumulative_total_income']= np.cumsum(gini['total_income'])
            sum_total_income = sum(gini['total_income'])
            gini['percentage_cumul_income'] = gini['cumulative_total_income']/sum_total_income
            gini['height'] = gini['percentage_cumul_pop']-gini['percentage_cumul_income']            
            gini1 = pd.DataFrame([[np.nan]*len(gini.columns)], columns=gini.columns)
            gini = pd.concat([gini1, gini], axis=0)
            gini['percentage_cumul_pop']= gini['percentage_cumul_pop'].fillna(0)
            gini['percentage_cumul_income']= gini['percentage_cumul_income'].fillna(0)
            gini['height']= gini['height'].fillna(0)
            gini['base'] = gini.percentage_cumul_pop.diff()
            gini['base']= gini['base'].fillna(0)
            gini['integrate_area']= 0.5*gini['base']*(gini['height']+gini['height'].shift())
            sum_integrate_area = gini['integrate_area'].sum()
            gini_index = 2*(sum_integrate_area)
            kakwani_list = kakwani_list + [gini_index-gini_index0]
        return kakwani_list
     
    def merge_distribution_table_dicts(dt1, dt2, tax_type, data_start_year, end_year):
        #print('dt1 ',dt1)
        #print('dt1[tax_type][start_year] ', dt1[tax_type][start_year])
        #print(dt1[tax_type][data_start_year].keys())
        #print(tax_type)
        attribute_types = dt1[tax_type][data_start_year].keys()
        print('attribute types in merge dist table func', attribute_types)
        dt = {}
        distribution_json_filename[tax_type] = 'taxcalc/'+global_variables[tax_type+'_distribution_json_filename']
        f = open(distribution_json_filename[tax_type])
        distribution_vardict_dict[tax_type] = json.load(f)
        income_measure[tax_type] = distribution_vardict_dict[tax_type]['income_measure']
        print('imeasure', income_measure[tax_type])
        for year in range(data_start_year, end_year+1):
            for attribute_value in attribute_types:
                dt1[tax_type][year][attribute_value] = dt1[tax_type][year][attribute_value].rename(columns={'weight': 'weight_'+str(year), tax_collection_var[tax_type]:tax_collection_var[tax_type]+'_'+str(year), income_measure[tax_type]:income_measure[tax_type] +'_'+str(year)})
                dt2[tax_type][year][attribute_value] = dt2[tax_type][year][attribute_value].rename(columns={'weight': 'weight_ref_'+str(year), tax_collection_var[tax_type]:tax_collection_var[tax_type]+'_ref_'+str(year), income_measure[tax_type]:income_measure[tax_type]+'_ref_'+str(year)})               
        #print('dt1 ',dt1)
        #print('dt2 ',dt2)
        for attribute_value in attribute_types:            
            dt[attribute_value] = dt1[tax_type][data_start_year][attribute_value][['weight_'+str(data_start_year), tax_collection_var[tax_type]+'_'+str(data_start_year), income_measure[tax_type]+'_'+str(data_start_year)]]
            #to cover years, if any, in the data before the start year e.g. data start year is 2018 but start year is 2022 - then years from 2018-2021 will be covered
            for year in range(data_start_year+1, start_year+1):
                dt[attribute_value]=dt[attribute_value].join(dt1[tax_type][year][attribute_value][['weight_'+str(year), tax_collection_var[tax_type]+'_'+str(year), income_measure[tax_type]+'_'+str(year)]])
            #to cover year from start to end year
            for year in range(start_year, end_year+1):
                dt[attribute_value]=dt[attribute_value].join(dt2[tax_type][year][attribute_value][['weight_ref_'+str(year), tax_collection_var[tax_type]+'_ref_'+str(year), income_measure[tax_type]+'_ref_'+str(year)]])     
        #print('dt', dt)
        return dt 
        
    
    with open('revenue_dict.json', 'w') as f:
        json.dump(revenue_dict, f)
    #save the results of each tax type in separate files
    df = {}
    # save the results into a csv file
    #for tax_type in [tax_list[0]]:
    for tax_type in tax_list:
        filename_chart_rev_projection = tax_type+'_revenue_projection'
        revenue_dict_df = {}
        for k, v in revenue_dict[tax_type].items():
            revenue_dict_df[k] = {}
            for k1 in revenue_dict[tax_type][year]['current_law']['value'].keys():
                revenue_dict_df[k]['current_law_'+k1] = revenue_dict[tax_type][k]['current_law']['value_bill_str'][k1]
                revenue_dict_df[k]['reform_'+k1] = revenue_dict[tax_type][k]['reform']['value_bill_str'][k1]
                if adjust_behavior:
                    revenue_dict_df[k]['reform_behavior_'+k1] = revenue_dict[tax_type][k]['reform_behavior']['value_bill_str'][k1]
                    
        df[tax_type] = pd.DataFrame.from_dict(revenue_dict_df)
        print(df[tax_type], 'df tax_type')
        df_str = df[tax_type].to_string()
        df_reform = pd.DataFrame.from_dict(reform)
        df_reform_str = df_reform.to_string()
        text_output1 = df_str + '\n\n' + df_reform_str + '\n\n'
        write_file(df[tax_type], text_output1, filename_chart_rev_projection)
        chart_list = chart_list + [tax_type+'_revenue_projection']  

        if global_variables[tax_type+'_display_revenue_table']:
            last_row = row_num[tax_type]
            l_TAB3[tax_type] = tk.Button(window_dict[tax_type],
                                     text="Save Results",
                                     command=lambda: write_file(df[tax_type], 
                                                                text_output1, 
                                                                filename_chart_rev_projection, 
                                                                window_dict[tax_type], 
                                                                last_row
                                                                ))
            l_TAB3[tax_type].grid(row=row_num[tax_type]+2, column=2, pady = 10, sticky=tk.W)
    #footer = ["footer", "*Data saved in file "+ filename1]
    #row_num = display_table(window, data=footer, footer=row_num+2)
    
    '''
   ---------------------------------------------------------------------------------------
    ###### DISTRIBUTION TABLES ##############
    --------------------------------------------------------------------------------------    
    '''   
    def display_distribution_table_window(tax_type):
        window_dist = {}
        row_num = {}
        df_tax12={}
        dt12={}
        dt34={}
        #dt_tax_all12 = {}
        #dt_tax_all34 = {}
        #print(tax_list)
        #tax_type = tax_list[0]
        #tax_type = tax_list
        
        #for tax_type in [tax_list[0]]:
        #for tax_coll_var in tax_collection_var:
        # for tax_type in tax_list:
        df_tax12 = merge_distribution_table_dicts(df_tax1, df_tax2, tax_type, data_start_year, end_year)  
        print('df_tax12 in gini function is', df_tax12)
        dt12 = merge_distribution_table_dicts(dt1, dt2, tax_type, data_start_year, end_year)
        dt34 = merge_distribution_table_dicts(dt3, dt4, tax_type, data_start_year, end_year)
        dt_percentile = merge_distribution_table_dicts(dt1_percentile, dt2_percentile, tax_type, data_start_year, end_year)
        if tax_type == 'pit':
            kakwani_list = calc_gini(df_tax12, tax_type)
        else:
            kakwani_list = [np.NaN]
        print('kakwani', kakwani_list)
        #print('gini ', gini_list)
        #print('dt12[tax_type][All]', dt12[tax_type]['All'])
        #print('dt34[tax_type][All]', dt34[tax_type]['All'])
        
        # dt12[tax_type]['All'].update(dt12[tax_type]['All'].select_dtypes(include=np.number).applymap('{:,.0f}'.format))
        # dt12[tax_type]['All'].to_pickle('file1.pkl')
        # dt12[tax_type]['All'] = pd.read_pickle('file1.pkl')
    
        # dt34[tax_type]['All'].update(dt34[tax_type]['All'].select_dtypes(include=np.number).applymap('{:,.0f}'.format))
        # dt34[tax_type]['All'].to_pickle('file2.pkl')
        # dt34[tax_type]['All'] = pd.read_pickle('file2.pkl')

        dt12['All'].update(dt12['All'].select_dtypes(include=np.number).applymap('{:,.0f}'.format))
        dt12['All'].to_pickle('file1.pkl')
        dt12['All'] = pd.read_pickle('file1.pkl')
    
        dt34['All'].update(dt34['All'].select_dtypes(include=np.number).applymap('{:,.0f}'.format))
        dt34['All'].to_pickle('file2.pkl')
        dt34['All'] = pd.read_pickle('file2.pkl')
    
        dt_tax_all12 = dt12['All'][dt12['All'].columns[dt12['All'].columns.str.contains(tax_collection_var[tax_type])]]
        dt_tax_all34 = dt34['All'][dt34['All'].columns[dt34['All'].columns.str.contains(tax_collection_var[tax_type])]]
    
        dt_tax_all12 = dt_tax_all12.reset_index()
        dt_tax_all34 = dt_tax_all34.reset_index()
        
        #print('dt_tax_all34', dt_tax_all34)
    
        # dt_tax_all12 = pd.DataFrame.from_dict(dt_tax_all12[tax_type])
        # dt_tax_all12.insert(0, 'Dist_var', dt_tax_all12.index)
        # dt_tax_all34 = pd.DataFrame.from_dict(dt_tax_all34[tax_type])
        # dt_tax_all12.insert(0, 'Dist_var', dt_tax_all12.index)
        # distribution_json_filename[tax_type] = 'taxcalc/'+global_variables[tax_type+'_distribution_json_filename']
        # f = open(distribution_json_filename[tax_type])
        # distribution_vardict_dict[tax_type] = json.load(f)
        # income_measure = distribution_vardict_dict[tax_type]['income_measure']

        #print('dt_tax_all34 columns', dt_tax_all34.columns)
    # ETR is calculated for the Start Year
        dt_percentile['All']['ETR'] = dt_percentile['All'][tax_collection_var[tax_type]+'_'+str(start_year)]/dt_percentile['All'][income_measure[tax_type]+'_'+str(start_year)]           
        dt_percentile['All']['ETR_ref'] = dt_percentile['All'][tax_collection_var[tax_type]+'_ref_'+str(start_year)]/dt_percentile['All'][income_measure[tax_type]+'_ref_'+str(start_year)]    
        dt_percentile['All'].update(dt_percentile['All'].select_dtypes(include=np.number).applymap('{:,.4f}'.format))            
        dt_percentile['All']['ETR'] = dt_percentile['All']['ETR'].fillna(0)
        dt_percentile['All']['ETR_ref'] = dt_percentile['All']['ETR_ref'].fillna(0)
    # Adjust this for number of years selected
        filename2 = tax_type+'_distribution_table'
        text_output2 = dt12['All'].to_string() + '\n\n'
        filename3 = tax_type+'_distribution_table_top1'
        text_output3 = dt12['All'].to_string() + '\n\n'
        filename4 = tax_type+'_distribution_table_income_bins'
        text_output4 = dt34['All'].to_string() + '\n\n'
    
        write_file(dt_tax_all12, text_output2, filename2)
        write_file(dt_tax_all12, text_output3, filename3)
        write_file(dt_tax_all34, text_output4, filename4)
        filename_etr = tax_type+'_etr'
        text_output_etr = dt_percentile['All'].to_string() + '\n\n'
        #print('dt_percentile[tax_type][All]', dt_percentile[tax_type]['All'])
        write_file(dt_percentile['All'], text_output_etr, filename_etr)            
    
        if global_variables[tax_type+'_display_distribution_table_byincome']:
            window_dist[tax_type] = tk.Toplevel()
            window_dist[tax_type].geometry("1000x700+600+140")
            header1 = ["header","", tax_type.upper()]
            header2 = ["header",'Gross Taxable Income']
            for year in range(data_start_year, start_year+1):
                header1 = header1+[tax_type.upper()]
                header2 = header2+['Current Law '+str(year)]                    
            for year in range(start_year, end_year+1):
                header1 = header1+[tax_type.upper()]                    
                header2 = header2+['Reform '+str(year)]          
            title_header = [["title", tax_type.upper()+" Contribution by Income Groups (fig in Euros)"],
                            header1, header2]
            row_num[tax_type] = display_table(window_dist[tax_type], data=title_header, header=True)
            row_num[tax_type] = display_table(window_dist[tax_type], row = row_num[tax_type], dataframe=dt_tax_all34)
            l = tk.Button(window_dist[tax_type],text="Save Results",command=lambda: write_file(dt_tax_all34, text_output4, filename4, window_dist[tax_type], row_num[tax_type]))
            l.grid(row=row_num[tax_type]+2, column=2, pady = 10, sticky=tk.W)
    
        elif global_variables[tax_type+'_display_distribution_table_bydecile']:
            window_dist[tax_type] = tk.Toplevel()
            window_dist[tax_type].geometry("1000x700+600+140")
            header1 = ["header","", tax_type.upper()+' (Euros)']
            header2 = ["header",'Decile']
            for year in range(data_start_year, start_year+1):
                header1 = header1+[tax_type.upper()+' (Euros)']
                header2 = header2+['Current Law '+str(year)]                    
            for year in range(start_year, end_year+1):
                header1 = header1+[tax_type.upper()+' (Euros)']                    
                header2 = header2+['Reform '+str(year)]          
            title_header = [["title", tax_type.upper()+" Tax Liability - Distribution by Deciles"],
                            header1, header2]     
            row_num[tax_type] = display_table(window_dist[tax_type], data=title_header, header=True)
            row_num[tax_type] = display_table(window_dist[tax_type], row = row_num[tax_type], dataframe=dt_tax_all12)
            l = tk.Button(window_dist[tax_type],text="Save Results",command=lambda: write_file(dt_tax_all12, text_output2, filename2, window_dist[tax_type], row_num[tax_type]))
            l.grid(row=row_num[tax_type]+2, column=2, pady = 10, sticky=tk.W)
        return kakwani_list
        
    for tax_type in tax_list:
        if global_variables[tax_type+'_distribution_table']:
            kakwani_list = display_distribution_table_window(tax_type)
            global_variables[tax_type +'_display_revenue_table'] = 1
            chart_list = chart_list + [tax_type+'_distribution_table']
            chart_list = chart_list + [tax_type+'_distribution_table_top1']
            chart_list = chart_list + [tax_type+'_distribution_table_income_bins']
            chart_list = chart_list + [tax_type+'_etr']
            global_variables['kakwani_list'] = kakwani_list
                 
    global_variables['charts_ready'] = 1
    print('chart_list ', chart_list)
    global_variables['chart_list'] = chart_list

    with open('global_vars.json', 'w') as f:        
        f.write(json.dumps(global_variables, indent=2))
    

        

       
    
