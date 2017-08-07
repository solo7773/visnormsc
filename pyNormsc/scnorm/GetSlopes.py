import sys
import multiprocessing
from . import generalFuncs

def GetSlopes(Data=None, SeqDepth=None, Tau = .5, FilterCellNum = 10, NCores=None):
    """ do something
     Data: x-by-y, x are genes, y are cells/samples
     SeqDepth: if not given, set to colsum of Data
     """
    if Data is None:
        print('Input data is required.')
        sys.exit()
    if NCores is None:
        NCores = multiprocessing.cpu_count()
        NCores = NCores - 1 if NCores > 1 else NCores
    if SeqDepth is None:
        SeqDepth = Data.sum(axis=0)

    NumNonZeros = (Data != 0).sum(axis=1)

    Genes = NumNonZeros[NumNonZeros >= FilterCellNum].index

    LogData = generalFuncs.redobox(Data, 0)  # log data

    if sys.platform == 'win32':
        #NCores = 1
        pass

    AllReg = generalFuncs.quickreg_p(LogData, SeqDepth, Genes, Tau, NCores)

    return AllReg