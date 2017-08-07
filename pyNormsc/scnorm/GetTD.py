
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.tools import tools
from statsmodels.regression.quantile_regression import QuantReg
from multiprocessing import Pool
from functools import partial
import warnings
from . import poly

warnings.filterwarnings('ignore')

def calcuTD(x, O, Y, SeqDepth, Grid, Tau):
    TauGroup, D = Grid[x]
    D = int(D)

    try:
        polyX, centre, scale, alpha, beta = poly.poly(O, D)
    except Exception:
        polyX = None

    if polyX is not None:
        colVars = ['var_' + str(j) for j in range(D)]
        polydata = pd.concat([pd.DataFrame({'Y':Y}), pd.DataFrame(polyX, columns=colVars)], axis=1)
        try:
            rqfit = smf.quantreg('Y~' + '+'.join(colVars), polydata).fit(q=TauGroup)
            revX = poly.predict_poly(polyX, centre, scale, alpha, beta, SeqDepth)
            revX = pd.DataFrame(revX, columns=colVars)
            pdvalsrq = rqfit.predict(revX)

            if min(pdvalsrq) > 0:
                S = QuantReg(pdvalsrq.values, tools.add_constant(SeqDepth)).fit(q=Tau).params[1]
            else:
                S = -50
        except Exception:
            S = -50
    else:
        S = -50
    return S

def GetTD(O, Y, SeqDepth, Grid, Tau, NCores):
    #allS = [calcuTD(x, O, Y, SeqDepth, Grid, Tau) for x in range(len(Grid))]
    #return np.array(allS)
    with Pool(processes=NCores) as p:
        res = p.map_async(partial(calcuTD, O=O, Y=Y, SeqDepth=SeqDepth, Grid=Grid, Tau=Tau), range(len(Grid)))
        res.wait()
    return np.array(res.get())