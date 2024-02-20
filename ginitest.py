# -*- coding: utf-8 -*-
"""
Created on Wed Jul 13 15:53:57 2022

@author: wb395723
"""

import pandas as pd
import numpy as np

data=pd.read_csv('df_for_gini.csv')

data['bin'] = pd.qcut(data, 11, labels=None)

data1 = data.grouby(data.bin).sum()

