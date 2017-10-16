
'''
This is for user who are familiar with Python.
It is just an example showing how to run visnormsc
by coding from the scratch.
'''

from pyNormsc.scnorm import *
import pandas as pd
import numpy as np
from multiprocessing import freeze_support
from matplotlib.backends.backend_agg import FigureCanvasAgg

#egData = pd.read_csv('test/testData/exampleData.csv', header=0, index_col=0)
egData = pd.read_csv('test/testData/scH1data.csv', header=0, index_col=0)
egData2 = pd.read_csv('test/testData/trapnellData.csv', header=0, index_col=0)

#Conditions = np.repeat(np.array([1, 2]), 90)
Conditions = np.repeat(np.array(['1M', '4M']), 92)

if __name__ == '__main__':
    freeze_support()
    # check count-depth relationship or do normalization
    #figInstance = checkCountDepth.checkCountDepth(egData, Conditions=Conditions)
    resData, figInstance = SCnorm.SCnorm(egData, Conditions, True, reportSF=True)

    # draw figure
    countDepthCanvas = FigureCanvasAgg(figInstance)
    countDepthCanvas.print_figure('countDepth.png')

print('Done')