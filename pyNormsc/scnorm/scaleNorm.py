
import numpy as np
import pandas as pd
import math

def scaleNormMultCont(NormData, OrigData, Genes):
    NumCond = len(NormData)
    AllGenes = Genes
    K = 4
    avgexp = np.log(OrigData.loc[Genes].apply(lambda x: np.median(x[x != 0]), axis=1, raw=True))  # conditional median
    groups = K
    splitby = avgexp.sort_values()
    splitS = math.ceil(len(splitby) / groups)
    grps = np.array([math.floor(x / splitS) for x in range(len(splitby))])
    sreg = [splitby[grps == i] for i in range(groups)]

    # Need to put a check here later on to make sure the rownames are in the same order
    OC = pd.concat([NormData[x]['NormData'] for x in range(NumCond)], axis=1)

    ScaleMat = []
    ScaleFacs = []
    for i in range(NumCond):

        C1 = NormData[i]['NormData']
        SF = NormData[i]['ScaleFactors']

        for r in range(groups):
            qgenes = sreg[r].index.values

            ss1 = np.array([np.mean(x[x != 0]) for x in C1.loc[qgenes].values])
            os = np.array([np.mean(x[x != 0]) for x in OC.loc[qgenes].values])

            rr = np.median([x for x in (ss1 / os) if not np.isnan(x)])  # print(rr)
            C1.loc[qgenes] = np.round((C1.loc[qgenes] / rr), 2)
            SF.loc[qgenes] = SF.loc[qgenes] * rr

        ScaleMat.append(C1.loc[AllGenes])  # ensures order remains the same here

        ScaleFacs.append(SF.loc[AllGenes])  # ensures order remains the same here

    ScaleMatAll = pd.concat([x for x in ScaleMat], axis=1)
    ScaleFacsAll = pd.concat([x for x in ScaleFacs], axis=1)

    ScaledData = {'NormalizedData': ScaleMatAll, 'ScaleFactors': ScaleFacsAll}
    return ScaledData