
import numpy as np
from scipy.stats import skew, gaussian_kde, mstats
import pandas as pd
import copy
import math
import statsmodels.formula.api as smf
import warnings
from . import generalFuncs
from . import k_medoids_
from . import GetTD
from . import poly

def SCnorm_fit(Data, SeqDepth, Slopes, K, PropToUse=.25, Tau=.5, NCores=None):
    SeqDepth = pd.DataFrame({'Depth': np.log(SeqDepth)}) # use LOG
    SeqDepth['Sample'] = SeqDepth.index.values

    Genes = Data.index.values
    DataFiltered = Data.loc[Slopes.index.values]
    logData = generalFuncs.redobox(copy.deepcopy(DataFiltered), 0) # use LOG data

    grouping = k_medoids_.KMedoids(n_clusters=K).fit(Slopes.values)
    sreg = [Slopes.loc[grouping.labels_ == x] for x in range(K)]

    # merge small clusters together, defined to be groups with less than 100 genes
    Centers = grouping.cluster_centers_.ravel()
    SIZES = [len(x) for x in sreg]
    while np.any([x < 100 for x in SIZES]):
        i = np.argmin(SIZES)
        tomatch = sorted(abs(Centers - Centers[i]))[1]
        ADDTO = abs(Centers - Centers[i]).tolist().index(tomatch)
        sreg[ADDTO] = sreg[ADDTO].append(sreg[i])
        del sreg[i]
        Centers = np.delete(Centers, i)
        SIZES = [len(x) for x in sreg]

    K = len(sreg) # update K

    NormData = None
    ScaleFactors = None

    ##normalize within each group
    for i in range(K):
        qgenes = sreg[i].index

        dskew = skew(sreg[i].values.ravel())

        ##only want to use modal genes for speed
        rqdens = gaussian_kde(Slopes.loc[qgenes].values.ravel())
        ax = np.linspace(math.floor(Slopes.loc[qgenes].min()), math.ceil(Slopes.loc[qgenes].max()), 512)
        ay = rqdens(ax)
        peak = np.argmax(ay)

        if dskew is not None and abs(dskew) > 0.5:
            PEAK = ax[peak]
        else:
            PEAK = sreg[i].values.ravel().mean()

        NumToSub = int(np.ceil(len(qgenes) * PropToUse))  # use 25% of data near mode, faster
        ModalGenes = abs(PEAK - Slopes.loc[qgenes]).sort_values(by='slope').head(NumToSub).index
        InData = logData.loc[ModalGenes]

        Melted = InData.stack(dropna=False)
        Melted = pd.DataFrame({'Gene': [i for i,j in Melted.index], 'Sample': [j for i, j in Melted.index], 'Counts': Melted.values}, columns=['Gene', 'Sample', 'Counts'])

        LongData = Melted.merge(SeqDepth, how='left', left_on='Sample', right_on='Sample')
        O = LongData.Depth.values
        Y = LongData.Counts.values

        taus = np.arange(.05, .96, .05)
        D = 6
        Grid = np.array(np.meshgrid(taus, np.arange(1, D+1, 1))).reshape(2, -1).T

        AllIter = GetTD.GetTD(O, Y, SeqDepth.Depth.values, Grid, Tau, NCores)

        TauGroup, D = Grid[np.argmin(abs(PEAK - AllIter))]
        D = int(D)

        polyX, centre, scale, alpha, beta = poly.poly(O, D)
        colVars = ['var_' + str(j) for j in range(D)]
        polydata = pd.concat([pd.DataFrame({'Y': Y}), pd.DataFrame(polyX, columns=colVars)], axis=1)

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            rqfit = smf.quantreg('Y~' + '+'.join(colVars), polydata).fit(q=TauGroup)
            revX = poly.predict_poly(polyX, centre, scale, alpha, beta, SeqDepth.Depth.values)
            revX = pd.DataFrame(revX, columns=colVars)
            pdvalsrq = rqfit.predict(revX)

        SF_rq = np.exp(pdvalsrq.values) / np.exp(mstats.mquantiles(Y[np.isfinite(Y)], prob=TauGroup, alphap=1, betap=1))

        normdata_rq = DataFiltered.loc[qgenes,] / SF_rq

        if NormData is None:
            NormData = copy.deepcopy(normdata_rq)
        else:
            NormData = NormData.append(normdata_rq, verify_integrity=True)

        SFmat = np.tile(SF_rq, len(qgenes)).reshape((len(qgenes), -1))
        SFmat = pd.DataFrame(SFmat, index=qgenes, columns=SeqDepth.index)

        if ScaleFactors is None:
            ScaleFactors = copy.deepcopy(SFmat)
        else:
            ScaleFactors = ScaleFactors.append(SFmat, verify_integrity=True)

    toput1 = list(set(Genes) - set(NormData.index.values))
    if len(toput1) > 0:
        NormData = NormData.append(Data.loc[toput1], verify_integrity=True)

        SFones = (np.tile(np.tile(1, Data.shape[1]), len(toput1))).reshape(len(toput1), -1)
        SFones = pd.DataFrame(SFones, index=toput1, columns=ScaleFactors.columns.values)

        ScaleFactors = ScaleFactors.append(SFones, verify_integrity=True)

    NormData = NormData.loc[Genes]
    ScaleFactors = ScaleFactors.loc[Genes]

    NORM = {'NormData': NormData, 'ScaleFactors': ScaleFactors}
    return NORM
