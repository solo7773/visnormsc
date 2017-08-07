import numpy as np
import math
from scipy.stats import gaussian_kde
#import matplotlib.pyplot as plt

def initialEvalPlot(MedExpr, Slopes, Name, NumExpressionGroups=10, BeforeNorm=True, countDepthFig=None, figPar=None):
    countDepthSubFig = countDepthFig.add_subplot(figPar[0], figPar[1], figPar[2])
    splitby = MedExpr.sort_values()
    grpSize = math.ceil(len(splitby) / NumExpressionGroups)
    grps = np.array([math.floor(x / grpSize) for x in range(len(splitby))])
    sreg = [splitby[grps == i] for i in range(NumExpressionGroups)]
    for ii in range(NumExpressionGroups):
        useg = sreg[ii].index
        rqdens = gaussian_kde(Slopes.loc[useg].values.ravel())
        ax = np.linspace(math.floor(Slopes.loc[useg].min()), math.ceil(Slopes.loc[useg].max()), 512)
        ay = rqdens(ax)
        countDepthSubFig.plot(ax, ay)
    if BeforeNorm == True:
        countDepthSubFig.axvline(x=1, color='k')
    if BeforeNorm == False:
        countDepthSubFig.axvline(x=0, color='k')
    countDepthSubFig.set_title(str(Name))
    countDepthSubFig.set_xlim(-3, 3)
    countDepthSubFig.set_xlabel('Slope')
    countDepthSubFig.set_ylabel('Density')