import numpy as np
import math
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt

def initialEvalPlot(MedExpr, Slopes, Name, NumExpressionGroups=10, BeforeNorm=True, figPar=None):
    plt.subplot(figPar[0], figPar[1], figPar[2])
    splitby = MedExpr.sort_values()
    grpSize = math.ceil(len(splitby) / NumExpressionGroups)
    grps = np.array([math.floor(x / grpSize) for x in range(len(splitby))])
    sreg = [splitby[grps == i] for i in range(NumExpressionGroups)]
    for ii in range(NumExpressionGroups):
        useg = sreg[ii].index
        rqdens = gaussian_kde(Slopes.loc[useg].values.ravel())
        ax = np.linspace(math.floor(Slopes.loc[useg].min()), math.ceil(Slopes.loc[useg].max()), 512)
        ay = rqdens(ax)
        plt.plot(ax, ay)
    if BeforeNorm == True:
        plt.axvline(x=1, color='k')
    if BeforeNorm == False:
        plt.axvline(x=0, color='k')
    plt.title(str(Name))
    plt.xlim(-3, 3)
    plt.xlabel('Slope')
    plt.ylabel('Density')