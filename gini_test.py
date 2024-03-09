# -*- coding: utf-8 -*-
"""
Created on Fri Mar  8 23:31:29 2024

@author: wb395723
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def G(v):
    bins = np.linspace(0., 100., 11)
    total = float(np.sum(v))
    yvals = []
    for b in bins:
        bin_vals = v[v <= np.percentile(v, b)]
        bin_fraction = (np.sum(bin_vals) / total) * 100.0
        yvals.append(bin_fraction)
    # perfect equality area
    pe_area = np.trapz(bins, x=bins)
    # lorenz area
    lorenz_area = np.trapz(yvals, x=bins)
    gini_val = (pe_area - lorenz_area) / float(pe_area)
    return bins, yvals, gini_val

#v = np.random.rand(500)
    
df = pd.read_csv('C:/Users/wb395723/OneDrive - WBG/Kosovo-PIT-CIT-Tax-Exp-Model/pit_output2022.csv')
df1 = pd.DataFrame()
df1['pre_tax_inc'] = df['calc_total_inc']
df1[df1['pre_tax_inc']<0]=0
v=df1['pre_tax_inc']
bins, result, gini_val = G(v)
plt.figure()
plt.subplot(2, 1, 1)
plt.plot(bins, result, label="observed")
plt.plot(bins, bins, '--', label="perfect eq.")
plt.xlabel("fraction of population")
plt.ylabel("fraction of wealth")
plt.title("GINI: %.4f" %(gini_val))
plt.legend()
plt.subplot(2, 1, 2)
plt.hist(v, bins=20)


