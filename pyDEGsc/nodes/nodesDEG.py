
import numpy as np
import pandas as pd


def NODES(data=None, group=None, r=20, smooth_points=1e4, zper=0.5):
    '''
    Nonparametric differential expression analysis for scRNA-seq data.
    :param data: Normalized single cell data.
    :param group: An array of strings containing unique group identifiers for cells. For example c("A","A","B","B").
    :param r: A numeric value indicating number of permutations of outcomes to be done for generating the empirical distribution for D statistic. Default value is 20.
    :param smooth_points: A numeric value indicating number of bins for smoothing, default is 10000.
    :param zper: Indicating quantile of pooled standard errors; default is 0.5.
    :return: A table reporting p-values and q-values with original ordering of genes retained.
    '''
    data = pd.read_csv('C:\\Users\\mq44741340\\OneDrive\\job\\tmp171010\\rResult.csv', header=0, index_col=0)
    group = ['T0'] * 75 + ['T24'] * 71

    # this part is for identifying the groups
    indices = dict()

    U = sorted(list(set(np.array([str(x) for x in group]))))

    for i in U:
        indices[i] = [j for j, v in enumerate(group) if v == i]

    # length of groups
    ns = [len(indices[x]) for x in indices]

    # getting noise distribution from NOISeq and estimate p values
    Zr = None
    for i in range(r):
        print('Randomization run =', i + 1)
        mipermu = np.random.choice(np.arange(len(group)), size=len(group), replace=False) ## randomize labels
        mipermu = data.iloc[:,mipermu] ## randomize matrix columns accordingly
        # get mean and sd by row
        means = []
        sds = []
        jj = 0
        for ii in ns:
            means += [mipermu.iloc[:, range(jj, jj + ii)].mean(axis=1).values.tolist()]
            sds += [mipermu.iloc[:, range(jj, jj + ii)].std(axis=1).values.tolist()]
            jj += ii

        myparam = {'n': ns, 'sd': sds}

        MDperm = MDbio(dat=means, param=myparam, aOper=zper)


def MDbio(dat=None, param=None, aOper=0.5):
    pass