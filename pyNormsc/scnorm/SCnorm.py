
import multiprocessing
import logging
import pandas as pd
import numpy as np
import sys
import copy
from . import GetSlopes
from . import NormWrap
from . import SCnorm_function
from . import checkCountDepth
from . import scaleNorm

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=0)
#logging.disable(100)

def SCnorm(Data=None, Conditions=None, PLOT=False, PropToUse = .25, Tau = .5, reportSF = False, FilterCellNum = 10, K = None, NCores = None, FilterExpression = 0, Thresh = 0.1):
    '''
    :param Data:
    :param Conditions:
    :param PLOT: save plots of evaluating K of each condition
    :param PropToUse: 0 < float < 1
    :param Tau: 0 < float < 1
    :param reportSF:
    :param FilterCellNum: integer > 0
    :param K: {'condition name': integer > 0}
    :param NCores: integer > 0
    :param FilterExpression: any float
    :param Thresh: any float
    :return normalized data and matplotlib figure instance
    '''

    ## checks
    if Data.isnull().values.any():
        print("Data contains at least one value of NA. Unsure how to proceed.")
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
        print('Must supply conditions.')
        sys.exit()
    if Data.shape[1] != len(Conditions):
        print("Number of columns in expression matrix must match length of conditions vector!")
        sys.exit()
    if K is not None:
        print("SCnorm will normalize assuming", K, "is the optimal number of groups. It is not advised to set this.")
    if NCores is None:
        NCores = multiprocessing.cpu_count()
        NCores = NCores - 1 if NCores > 1 else NCores
        logging.info('%s CPU cores will be used.', str(NCores))

    Conditions = np.array([str(x) for x in Conditions])
    Levels = sorted(list(set(Conditions)))
    logging.info('Conditions: ' + str(Levels))
    # make sure K's order matches Levels' order
    if K is not None:
        K = [K[x] for x in Levels]
        logging.info('K: %s', str(K))

    DataList = [Data.iloc[:, Conditions == x] for x in Levels] # split condition

    Genes = Data.index.values

    SeqDepthList = [DataList[x].sum(axis=0) for x in range(len(Levels))]

    # Get median quantile regr. slopes.
    SlopesList = []
    for x in range(len(Levels)):
        print('Parsing condition', Levels[x])
        SlopesList.append(GetSlopes.GetSlopes(copy.deepcopy(DataList[x]), SeqDepthList[x], Tau, FilterCellNum, NCores))

    NumZerosList = [(DataList[x] != 0).sum(axis=1) for x in range(len(Levels))]

    GeneFilterList = [NumZerosList[x][NumZerosList[x] >= FilterCellNum].index for x in range(len(Levels))]

    GeneFilterOUT = {'GenesFilteredOutCondition_' + str(Levels[x]): NumZerosList[x][NumZerosList[x] < FilterCellNum].index.values if (NumZerosList[x] < FilterCellNum).any() else ['No'] for x in range(len(Levels))}
    #GeneFilterOUT = pd.DataFrame.from_dict(GeneFilterOUT)

    print('Gene filter is applied within each condition.')

    for x in GeneFilterOUT:
        if len(GeneFilterOUT[x]) == 1:
            print(x, ': ', GeneFilterOUT[x][0], 'gene(s) were not included in the normalization due to having less than', FilterCellNum, 'non-zero values.')
        else:
            print(x, ': ', len(GeneFilterOUT[x]), 'gene(s) were not included in the normalization due to having less than', FilterCellNum, 'non-zero values.')

    print("A list of these genes can be accessed in output, see GUI.")

    # Data, SeqDepth, Slopes, CondNum, PLOT = TRUE, PropToUse, outlierCheck, Tau

    # if K is not provided
    if K is None:
        NormList = [NormWrap.Normalize(Data=copy.deepcopy(DataList[x]), SeqDepth=copy.deepcopy(SeqDepthList[x]), Slopes=copy.deepcopy(SlopesList[x]), CondNum=Levels[x], PLOT=PLOT, PropToUse=PropToUse, Tau=Tau, NCores=NCores, Thresh=Thresh) for x in range(len(Levels))]

    # if specific k then do:
    # if length of k is less than number of conditions.
    if K is not None:
        if hasattr(K, '__iter__') and len(K) == len(Levels):
            pass
        elif not hasattr(K, '__iter__'):
            K = [K] * len(Levels)
        else:
            print('Check that if the specification of K is correct!')
            sys.exit()
        NormList = [SCnorm_function.SCnorm_fit(Data=copy.deepcopy(DataList[x]), SeqDepth=copy.deepcopy(SeqDepthList[x]), Slopes=copy.deepcopy(SlopesList[x]), K=K[x], PropToUse=PropToUse, NCores=NCores) for x in range(len(Levels))]

    FilterCellProportion = [FilterCellNum / DataList[x].shape[1] for x in range(len(Levels))]

    NORMDATA = pd.concat([NormList[x]['NormData'] for x in range(len(Levels))], axis=1)

    print("Plotting count-depth relationship for normalized data...")

    figInstance = checkCountDepth.checkCountDepth(Data=copy.deepcopy(Data), NormalizedData=NORMDATA, Conditions=Conditions, Tau=Tau, FilterCellProportion=FilterCellProportion, FilterExpression=FilterExpression, NCores=NCores)

    if len(Levels) > 1:
        # Scaling
        # Genes = Reduce(intersect, GeneFilterList)
        print("Scaling data between conditions...")
        ScaledNormData = scaleNorm.scaleNormMultCont(NormList, Data, Genes)
        ScaledNormData = [ScaledNormData, GeneFilterOUT]
        if reportSF == True:
            return ScaledNormData, figInstance
        else:
            nouse = ScaledNormData[0].pop('ScaleFactors')
            return ScaledNormData, figInstance
    else:
        NormDataFull = NormList[0]['NormData']
        ScaleFactorsFull = NormList[0]['ScaleFactors']
        if reportSF == True:
            FinalNorm = [{'NormalizedData': NormDataFull, 'ScaleFactors': ScaleFactorsFull}, GeneFilterOUT]
            return FinalNorm, figInstance
        else:
            FinalNorm = [{'NormalizedData': NormDataFull}, GeneFilterOUT]
            return FinalNorm, figInstance