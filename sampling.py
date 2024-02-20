
import pandas as pd
import numpy as np


pit_df_2021=pd.read_csv('taxcalc/pit_macedonia.csv')

# allocate the data into bins
pit_df_2021['bin'] = pd.qcut(pit_df_2021['total_gross_i'], 10, labels=False)
pit_df_2021['weight']=1
# bin_ratio is the fraction of the number of records selected in each bin
# 1/10,...1/5, 1/1
bin_ratio=[20,20,20,20,20,20,20,20,10,1]
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
pit_sample_2021['id_n'] = pit_sample_2021.index
pit_sample_2021.to_csv('pit_data_training.csv')

