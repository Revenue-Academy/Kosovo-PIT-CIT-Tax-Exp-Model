# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 02:55:33 2022

@author: wb395723
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.integrate import simps
from numpy import trapz


# # Compute the area using the composite trapezoidal rule.
# area = trapz(y, dx=5)
# print("area =", area)


data=pd.read_excel('MKD_Gini.xlsx', usecols=['Income', 'Equality', 'GTI_2018', 'Net_Income_2018'])

x=data.Income
y1=data.Equality
y2=data.GTI_2018
y3=data.Net_Income_2018

area1 = trapz(y2, dx=10)
gini1 = (5000 - area1)/5000
print("gini is =", gini1)

area2 = trapz(y3, dx=10)
gini2 = (5000 - area2)/5000
print("gini is =", gini2)

plt.plot(x, y1)
plt.plot(x, y2, color='green')
plt.plot(x, y3, color='red', linestyle='--')




plt.show()