
import sys
import multiprocessing
import numpy as np
import pandas as pd
import math
from matplotlib.figure import Figure
import warnings
from . import GetSlopes
from . import initialEvalPlot

def checkCountDepth(Data = None, NormalizedData= None, Conditions = None, Tau = .5, FilterCellProportion = .10,
                    FilterExpression = 0, NumExpressionGroups = 10, NCores=None):
    """ Check count depth
    Data: un-normalized data, G-by-S matrix, G is the number of genes, S is the number of cells/samples
    NormalizedData: None or equal to Data
    Conditions: numpy array
    Tau: 0 < float < 1
    FilterCellProportion: 0 <= float <= 1
    FilterExpression: any float
    NumExpressionGroups: integer > 0
    NCores: cpu cores, None or integer > 0
    """
    ## checks
    if Data is None:
        print('Data must be given')
        sys.exit()
    elif Data.index.dtype_str != 'object':
        Data.index = ['X_' + str(x) for x in Data.index]
        print('Row names are renamed and now start with X_')
    elif sum(Data.index.duplicated()):
        print('Duplicate indexes/row names found in the input data.')
        sys.exit()
    elif Data.columns.dtype_str != 'object':
        print('Must supply sample/cell names!')
        sys.exit()
    if Conditions is None:
        Conditions = [1] * Data.shape[1]
    if Data.shape[1] != len(Conditions):
        print("Number of columns in expression matrix must match length of conditions vector!")
        sys.exit()
    if NCores is None:
        NCores = multiprocessing.cpu_count()
        NCores = NCores - 1 if NCores > 1 else NCores
        print(NCores, 'CPU cores will be used.')
    Conditions = np.array([str(x) for x in Conditions])
    Levels = sorted(list(set(Conditions)))
    print('Conditions: ', Levels)
    if not hasattr(FilterCellProportion, '__iter__'):
        FilterCellProportion = [FilterCellProportion] * len(Levels)
    elif 1 < len(FilterCellProportion) != len(Levels):
        print('If length of FilterCellProportion > 1, it should equal the number of condition types.')
        sys.exit()

    DataList = [Data.iloc[:, Conditions == x] for x in Levels]

    FilterCellProportion = [max([FilterCellProportion[x], 10 / DataList[x].shape[1]]) for x in range(len(Levels))]

    SeqDepthList = [DataList[x].sum(axis=0) for x in range(len(Levels))]

    PropZerosList = [(x != 0).sum(axis=1) / x.shape[1] for x in DataList]

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        MedExprAll = pd.Series([np.median(x[x != 0]) for x in Data.values], index=Data.index)
        MedExprList = [pd.Series([np.median(y[y != 0]) for y in x.values], index=x.index) for x in DataList]

    BeforeNorm = True
    # switch to normalized data
    if NormalizedData is not None:
        DataList = [NormalizedData.iloc[:, Conditions == x] for x in Levels]
        BeforeNorm = False

    GeneFilterList = [PropZerosList[x][(PropZerosList[x] >= FilterCellProportion[x]) & (MedExprAll >= FilterExpression)].index for x in range(len(Levels))]

    # Get median quantile regr. slopes.
    SlopesList = []
    for x in range(len(Levels)):
        print('Parsing condition', Levels[x])
        SlopesList.append(GetSlopes.GetSlopes(DataList[x].loc[GeneFilterList[x]], SeqDepthList[x], Tau, 10, NCores))

    # Data, SeqDepth, Slopes, CondNum, PLOT = TRUE, PropToUse, outlierCheck, Tau
    ROWS = math.ceil(len(Levels) / 2)
    countDepthFig = Figure(figsize=(5, 4), dpi=100, tight_layout=True)
    for x in range(len(Levels)):
        initialEvalPlot.initialEvalPlot(MedExpr=MedExprList[x][GeneFilterList[x]], Slopes=SlopesList[x], Name=Levels[x], NumExpressionGroups=NumExpressionGroups, BeforeNorm=BeforeNorm, countDepthFig=countDepthFig, figPar=[ROWS, 2, x+1])
    return countDepthFig