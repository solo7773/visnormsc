
import numpy as np
import pandas as pd
import copy

def pQ(data=None, frac=0.5, throw_sd=1, hard_outlier=500):
    '''
    :param data: rows, genes; columns, cells; Expression data frame with genes in rows. pQ can be applied to raw-count, FPKM or other expression quantification formats. Gene names should be supplied as rownames whereas sample names as column names.
    :param frac: determines a threshold thr = Q1-frac*IQR; cells with detected genes less than thr+1 would be  thrown away.
    :param throw_sd: A non zero value will throw away genes that have no non-pseudo count entry after normalization, default is 1.
    :param hard_outlier: A hard lower bound for minimum number of detected genes, default 500.
    :return: normalized data as a  data frame retaining orginal row and column names.
    '''
    # get threshold
    thr = np.floor(th(data, frac, hard_outlier))

    FPKMbackup = copy.deepcopy(data)

    # finding cells which have thr+1 genes
    if (thr != 0):
        bu = FPKMbackup.apply(lambda x: (x > 0).sum(), axis=0) > thr
        FPKMreduced = FPKMbackup.loc[:, bu]

        # cells thrown away
        print("No. of discarded cells:", len(bu) - sum(bu))
    else:
        FPKMreduced = FPKMbackup

    # minimum number expressed genes in remaining cells
    det_no = min(FPKMreduced.apply(lambda x: (x > 0).sum(), axis=0))

    # Q normalization
    X = quantileNormalize(FPKMreduced)

    # Find value for det_no + 1 ranked genes
    key = X.iloc[:,0].sort_values(ascending=False).values[int(thr+1)]

    # level tails
    X[X<=key] = key

    # throw zero deviation genes
    if throw_sd != 0:
        B = X.std(axis=1, skipna=True) > 1e-6
        X = X.loc[B,:]

    print('Dimensions of supplied expression matrix:\n', 'Genes =', data.shape[0], '; Cells =', data.shape[1])
    print('Dimensions of supplied processed matrix:\n', 'Genes =', X.shape[0], '; Cells =', X.shape[1])

    return X


def quantileNormalize(df_input):
    # rows genes, columns cells
    df = df_input.copy()
    rankMedian = df.stack().groupby(df.rank(method='first').stack().astype(int)).median()
    df2 = df.rank(method='min').stack().astype(int).map(rankMedian).unstack()
    return df2


def th(d=None, frac=0.5, hard_out=None):
    # get number of detected genes
    expr = d.apply(lambda x: (x > 0).sum(), axis=0)
    th = np.floor(expr.quantile([0, 0.25, 0.5, 0.75, 1]).iloc[1] - abs(expr.quantile([0, 0.25, 0.5, 0.75, 1]).iloc[3] - expr.quantile([0, 0.25, 0.5, 0.75, 1]).iloc[1]) * frac)

    if (th < hard_out):
        th = hard_out

    return th

