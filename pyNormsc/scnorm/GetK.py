
import copy
import numpy as np
import pandas as pd
import math
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt
from . import generalFuncs

def GetK(Data, SeqDepth, OrigData, Slopes, Name, PLOT, evalFigsOut, Tau, NCores):

    Genes = Slopes.index.values # genes for normalizing

    LogData = generalFuncs.redobox(copy.deepcopy(Data), 0)# LOG data

    NormSlopes = generalFuncs.quickreg_p(LogData, SeqDepth, Genes, Tau, NCores)

    MedExp = [(lambda y: np.median(y[y != 0]))(OrigData.iloc[x].values) for x in range(len(OrigData))]
    MedExp = pd.Series(MedExp, index=OrigData.index.values)
    splitby = MedExp.loc[Genes].sort_values()
    grpSize = math.ceil(len(splitby) / 10)
    grps = np.array([math.floor(x / grpSize) for x in range(len(splitby))])
    sreg = [splitby[grps == i] for i in range(10)]

    Mode = []
    DensH = []

    if PLOT:
        tmpFig = plt.figure(100)

    for ii in range(10):
        useg = sreg[ii].index.values
        rqdens = gaussian_kde(NormSlopes.loc[useg].values.ravel())
        ax = np.linspace(math.floor(NormSlopes.loc[useg].min()), math.ceil(NormSlopes.loc[useg].max()), 512)
        ay = rqdens(ax)
        peak = np.argmax(ay)
        Mode.append(ax[peak])
        DensH.append(ay[peak])
        if PLOT:
            plt.plot(ax, ay)
            plt.axvline(x=0, color='k')
            plt.title(str(Name))
            plt.xlim(-3, 3)
            plt.xlabel('Slope')
            plt.ylabel('Density')

    if PLOT:
        tmpFig.savefig(evalFigsOut, format='pdf')
        plt.close(tmpFig)

    MAX = max(map(abs, Mode))
    return MAX