# -*- coding: utf-8 -*-
"""
Created on Thu Dec 22 11:49:54 2022

@author: wb305167
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KernelDensity
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from array import array
import random
import time

import statsmodels.api as smf
import sys
sys.path.insert(0, 'C:/Users/wb305167/OneDrive - WBG/python_latest/Tax-Revenue-Analysis')
from stata_python import *

df=pd.read_csv('taxcalc/pit_armenia_oct4.csv')
df.set_index('id_n')
#df1 = df[df['mortgage_credits']<1e7]
df['Mortgage_bool'] = np.where(df['mortgage_credits']>0,1,0)
df['Mortgage'] = np.where(df['mortgage_credits']>10000,"Yes","No")
plot_density_chart(df[['total_income', 'Mortgage']], "Mortgage", 'total_income',
                    category_var="Mortgage", title='Prevalence of Mortgage Uptake', 
                    xlabel='Log of Total Income', logx="Yes", vline=None, 
                    save_figure_name = 'mortgage_uptake.pdf')

# The density chart shows an overlap between those who have mortgages
# and those who don't. We then seperate the total income into equal sized bins 
# and find the probability that any one bin contains those with mortgages

max_x = df['total_income'].max()
min_x = df['total_income'].min()
bins = 100000
bin_width = (max_x-min_x)/bins
df = df.sort_values(by='total_income')
df = df.reset_index()
df= df.drop(['index'], axis=1)
df['bin_mortgage'] = -1
tot_inc = min_x
bin_low = min_x
row=0
i=0
max_row=len(df)
print('Binning row wise Total Income Started')
start = time.time()
while row<max_row:
    if ((df.loc[row,'total_income'] >= bin_low) and
        (df.loc[row,'total_income'] <  bin_low+bin_width)):
        df.loc[row, 'bin_mortgage'] = i
        row = row+1
    else:
        bin_low = bin_low+bin_width
        i=i+1

end = time.time()
print ("Time elapsed binning row wise:", end - start)

# print('Binning of Total Income Started')
# start = time.time()  
# for i in range(bins):        
#     df['bin_mortgage'] = np.where((df['total_income']>=min_x+(i)*bin_width) & (df['total_income']<min_x+(i+1)*bin_width), i,df['bin_mortgage'])
# print('Binning completed')
# end = time.time()
# print ("Time elapsed:", end - start)
#df.loc[df.index[-1], 'bin_mortgage'] =  bins

df_prob = df.groupby(['bin_mortgage'])[["Mortgage_bool"]].mean().reset_index().rename(columns={"Mortgage_bool":"Mortgage_bin_prob"})
df_prob1 = df.groupby(['bin_mortgage'])[["Mortgage_bool"]].count().reset_index().rename(columns={"Mortgage_bool":"Mortgage_bin_count"})

df_prob = pd.merge(df_prob, df_prob1, on='bin_mortgage', how='left')
# We then calculate the number of mortgages per bin
df_prob['Mortgage_num'] = df_prob['Mortgage_bin_prob']*df_prob['Mortgage_bin_count']
# Note that many bins may not have any data points. i.e total income is not
# in the bin
# the chart shows the probability of having mortgages in bins that have 
# total incomes 
ax=df_prob.plot(kind='bar', x='bin_mortgage', y='Mortgage_bin_prob')
ax.xaxis.set_major_locator(ticker.MultipleLocator(100))

# We now adjust the probability of mortgages in the subsequent years
df_prob['Mortgage_bin_prob_2022'] = df_prob['Mortgage_bin_prob']*1.10
df_prob['Mortgage_bin_prob_2023'] = df_prob['Mortgage_bin_prob_2022']*1.10
df_prob['Mortgage_bin_prob_2024'] = df_prob['Mortgage_bin_prob_2023']*1.10
df_prob['Mortgage_bin_prob_2025'] = df_prob['Mortgage_bin_prob_2024']*1.10
df_prob['Mortgage_bin_prob_2026'] = df_prob['Mortgage_bin_prob_2025']*1.0
df_prob['Mortgage_bin_prob_2027'] = df_prob['Mortgage_bin_prob_2026']*1.0

# we merge this back into our main dataframe
df = pd.merge(df, df_prob, on='bin_mortgage', how='left')

# We use the new probabilities to obtain the number of mortgages in 
# subsequent years
df['Mortgage_num_2022'] = df['Mortgage_bin_prob_2022']*df['Mortgage_bin_count']
df['Mortgage_num_2023'] = df['Mortgage_bin_prob_2023']*df['Mortgage_bin_count']
df['Mortgage_num_2024'] = df['Mortgage_bin_prob_2024']*df['Mortgage_bin_count']
df['Mortgage_num_2025'] = df['Mortgage_bin_prob_2025']*df['Mortgage_bin_count']
df['Mortgage_num_2026'] = df['Mortgage_bin_prob_2026']*df['Mortgage_bin_count']
df['Mortgage_num_2027'] = df['Mortgage_bin_prob_2027']*df['Mortgage_bin_count']

# We then calculate the additional new mortgages that we need to incorporate
# during each of the subsequent years
df['Mortgage_num_diff_2022'] = df['Mortgage_num_2022'] - df['Mortgage_num']
df['Mortgage_num_diff_2023'] = df['Mortgage_num_2023'] - df['Mortgage_num_2022']
df['Mortgage_num_diff_2024'] = df['Mortgage_num_2024'] - df['Mortgage_num_2023']
df['Mortgage_num_diff_2025'] = df['Mortgage_num_2025'] - df['Mortgage_num_2024']
df['Mortgage_num_diff_2026'] = df['Mortgage_num_2026'] - df['Mortgage_num_2025']
df['Mortgage_num_diff_2027'] = df['Mortgage_num_2027'] - df['Mortgage_num_2026']

# Next we randomly select the values of new mortgages needed from the 
# existing mortgages
# We the allocate them randomly to those who don't have mortgages
df['mortgage_credits_2021'] = df['mortgage_credits']
df['prop_value_2021'] = df['prop_value']
df['Mortgage_bool_2021'] = np.where(df['mortgage_credits_2021']>0,1,0)
for year in range(2021,2027):
    # create a new column to be filled up. this will be pre-populated
    # by the mortgages during the previous year
    df['mortgage_credits_'+str(year+1)] = df['mortgage_credits_'+str(year)]
    df['prop_value_'+str(year+1)] = df['prop_value_'+str(year)]
    df['Mortgage_bool_'+str(year)] = np.where(df['mortgage_credits_'+str(year)]>0,1,0)
    print('Count of Number of Mortgages in ', year,' : ', len(df[df['Mortgage_bool_'+str(year)]==1]))    
    for i in range(bins):       
        if ((len(df[df['bin_mortgage']==i])) > 0 and
            (len(df[(df['bin_mortgage']==i)&(df['Mortgage_bool_'+str(year)]==1)]) > 0) and
            (len(df[(df['bin_mortgage']==i)&(df['Mortgage_bool_'+str(year)]==0)]) > 0)):

            # find the number of new mortgages to be filled up
            num_choose = round(df[df['bin_mortgage']==i]['Mortgage_num_diff_'+str(year+1)].mean())
            # this is a random selection of mortgage credits from the current 
            # year
            mortgage_rand = df[(df['bin_mortgage']==i)&(df['Mortgage_bool_'+str(year)]==1)][['mortgage_credits_'+str(year), 'prop_value_'+str(year)]].sample(num_choose)
            # this is the random selection of non-mortgages to be replaced 
            # with mortgages
            index_rand = random.choices(df[(df['bin_mortgage']==i)&(df['Mortgage_bool_'+str(year)]==0)].index, k=num_choose)
            # Here the non-mortgages are replaced by new mortgages
            df.loc[index_rand,'mortgage_credits_'+str(year+1)] = mortgage_rand['mortgage_credits_'+str(year)].to_list()
            df.loc[index_rand,'prop_value_'+str(year+1)] = mortgage_rand['prop_value_'+str(year)].to_list()            
    
filtercol = [col for col in df if not col.startswith(('Mortgage_bool', 'Mortgage_num', 'Mortgage_bin', 'bin_mortgage'))]

df = df[filtercol]
df.to_csv('pit_armenia_full_mortgage_updated.csv')


