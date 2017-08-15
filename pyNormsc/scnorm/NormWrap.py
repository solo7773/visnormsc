
import os
import sys
import copy
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from . import SCnorm_function
from . import GetK

def Normalize(Data, SeqDepth, Slopes, CondNum, PLOT, PropToUse, Tau, NCores, Thresh):
    # change backend
    plt.switch_backend('Agg')
    # set up
    GetMax = 1
    i = 0

    print("Finding K for Condition", CondNum)

    evalFigsOut = None

    if PLOT:
        tmpOutName = 'evaluate_k_for_condition_' + str(CondNum) + '.pdf'
        evalFigsOut = PdfPages(tmpOutName)

    while GetMax > Thresh:
        i += 1
        print('Trying K =', i)
        NormDataList = SCnorm_function.SCnorm_fit(Data=Data, SeqDepth=copy.deepcopy(SeqDepth), Slopes=Slopes, K=i, PropToUse=PropToUse, Tau=Tau, NCores=NCores)

        NAME = 'Condition: ' + str(CondNum) + '\n  K = ' + str(i)

        GetMax = GetK.GetK(NormDataList['NormData'], SeqDepth, Data, Slopes, NAME, PLOT, evalFigsOut, Tau, NCores)

    if PLOT:
        evalFigsOut.close()
        print('Plots of evaluating K have been saved to', os.path.join(os.getcwd(), tmpOutName), file=sys.stderr)

    plt.switch_backend('TkAgg')
    return NormDataList