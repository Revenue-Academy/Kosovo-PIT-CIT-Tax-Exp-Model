"""
This is a file that allows sampling of a large dataset.
"""
import sys
sys.path.insert(0, 'C:/Users/wb305167/OneDrive - WBG/python_latest/Tax-Revenue-Analysis')
#from stata_python import *
import pandas as pd
import numpy as np

pit_df_2021=pd.read_csv('taxcalc/pit_armenia_full_mortgage_updated1.csv')

pit_df_2021['total_income']=pit_df_2021['salary']+pit_df_2021['other_income']+pit_df_2021['civil_contract']

pit_df_2021=pit_df_2021.sort_values(by=['total_income'])
pit_df_2021=pit_df_2021.reset_index()
# allocate the data into bins
pit_df_2021['bin'] = pd.qcut(pit_df_2021['total_income'], 10, labels=False)
pit_df_2021['weight']=1
# bin_ratio is the fraction of the number of records selected in each bin
# 1/10,...1/5, 1/1
bin_ratio=[10,10,10,10,10,10,10,5,2,1]
frames=[]
df={}
for i in range(len(bin_ratio)):
    # find out the size of each bin
    bin_size=len(pit_df_2021[pit_df_2021['bin']==i])//bin_ratio[i]
    # draw a random sample from each bin
    df[i]=pit_df_2021[pit_df_2021['bin']==i].sample(n=bin_size)
    df[i]['weight'] = bin_ratio[i]
    frames=frames+[df[i]]

pit_sample_2021= pd.concat(frames)
pit_sample_2021.to_csv('taxcalc/pit_armenia_full_mortgage_updated1_sample.csv')

varlist = ['total_income', 'salary','other_income','deduction',
           'Total_tax','social_fee', 'civil_contract','mortgage_credits_2021','mortgage_credits_2022','mortgage_credits_2023']
total_weight_population = pit_df_2021['weight'].sum()

total_weight_sample = pit_sample_2021['weight'].sum()
#comparing the statistic of the population and sample
for var in varlist:
    pit_sample_2021['weighted_'+var] = pit_sample_2021[var]*pit_sample_2021['weight']
    sample_sum = pit_sample_2021['weighted_'+var].sum()
    population_sum = pit_df_2021[var].sum()
    print("            Sample Sum for ", var, " = ", sample_sum)
    print("        Population Sum for ", var, " = ", population_sum)
    print(" Sampling Error for Sum(%) ", var, " = ", "{:.2%}".format((population_sum-sample_sum)/population_sum))
    sample_mean = sample_sum/total_weight_sample
    population_mean = population_sum/total_weight_population
    print("           Sample Mean for ", var, " = ", sample_mean)
    print("       Population Mean for ", var, " = ", population_mean)
    print("Sampling Error for Mean(%) ", var, " = ", "{:.2%}".format((population_mean-sample_mean)/population_mean))    
    
    
growthrate=1.225

nrows = len(pit_sample_2021)
weights_df = pd.DataFrame(index = range(nrows))


for i in range(2021, 2031):
    weights_df["WT" + str(i)] = pit_sample_2021["weight"].values

weights=weights_df["WT2021"].values
    
#weights_df["WT2021"] = weights * growthrate   
    
for i in range(2021, 2031):
    weights_df["WT" + str(i)] = weights * growthrate       
   

weights_df.to_csv("taxcalc/pit_weights_armenia_mortgage_updated_sample.csv", index = False)    
    
    
