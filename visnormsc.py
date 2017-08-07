from pyNormsc.scnorm import *
import pandas as pd
import numpy as np
from multiprocessing import freeze_support


#egData = pd.read_csv('testData/exampleData.csv', header=0, index_col=0)
#egData = pd.read_csv('testData/bulkH1data.csv', header=0, index_col=0)
egData = pd.read_csv('testData/scH1data.csv', header=0, index_col=0)
#egDataNorm = egData / egData.sum(axis=0) * egData.sum(axis=0).mean()
# print(egData.shape)
#
# ttt = pd.read_table('testData/test.txt', sep='\t', header=0, index_col=0)


#Conditions = np.repeat(np.array(['f', 'c']), 90)
#Conditions = np.array([1] * 48)
Conditions = np.repeat(np.array(['1M', '4M']), 92)
# Conditions = np.repeat(np.array([3, 5]), 90)
# Conditions = np.repeat(np.array([1, 2]), [20, 160])

if __name__ == '__main__':
    freeze_support()
    #checkCountDepth.checkCountDepth(egData, Conditions=Conditions)
    ttt, figInstance = SCnorm.SCnorm(egData, Conditions, True, reportSF=True)
    print('Done')

# import importlib
# importlib.reload(pyNormsc.scnorm.generalFuncs)
# importlib.reload(pyNormsc.scnorm.GetSlopes)
