import numpy as np
import pandas as pd
from statsmodels.tools import tools
from statsmodels.regression.quantile_regression import QuantReg
#import statsmodels.formula.api as smf
from multiprocessing import Pool
from functools import partial
import warnings

def calcuSlope(i, LogData, SeqDepth, Genes, Tau):
    if i % round(len(Genes) / 10) == 0:
        print(i / round(len(Genes) / 10) * 10, '%')
    X = Genes[i]
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        validIdx = np.logical_not(np.isnan(LogData.loc[X].values)) & (SeqDepth.values > 0)
        mod = QuantReg(LogData.loc[X].values[validIdx], tools.add_constant(np.log(SeqDepth.values[validIdx])))
        # mod = smf.quantreg('response ~ variable',
        #                   pd.DataFrame({'response': LogData.loc[X], 'variable': np.log(SeqDepth)}))
        slope = mod.fit(q=Tau).params[1]
    return slope

def quickreg_p(LogData, SeqDepth, Genes, Tau, NCores):
    with Pool(processes=NCores) as p:
        res = p.map_async(partial(calcuSlope, LogData=LogData, SeqDepth=SeqDepth, Genes=Genes, Tau=Tau), range(len(Genes)))
        res.wait()
    return pd.DataFrame(res.get(), index=Genes, columns=['slope'])

def quickreg(LogData, SeqDepth, Genes, Tau, NCores):
    def calcuSlope(i):
        if i % round(len(Genes) / 10) == 0:
            print(i / round(len(Genes) / 10) * 10, '%')
        X = Genes[i]
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            validIdx = np.logical_not(np.isnan(LogData.loc[X].values)) & (SeqDepth.values > 0)
            mod = QuantReg(LogData.loc[X].values[validIdx], tools.add_constant(np.log(SeqDepth.values[validIdx])))
            #mod = smf.quantreg('response ~ variable',
            #                   pd.DataFrame({'response': LogData.loc[X], 'variable': np.log(SeqDepth)}))
            slope = mod.fit(q=Tau).params[1]
        return slope
    res = [calcuSlope(x) for x in range(len(Genes))]
    return pd.DataFrame(res, index=Genes, columns=['slope'])

def redobox(DATA, smallc):
    DATA[DATA <= smallc] = np.nan
    y = np.log(DATA)
    return y
