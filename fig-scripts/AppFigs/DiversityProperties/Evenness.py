from __future__ import division
import  matplotlib.pyplot as plt

import numpy as np
import random
import scipy as sc
from scipy import stats

import os
import sys
from scipy.stats.distributions import t

import statsmodels.stats.api as sms
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.sandbox.regression.predstd import wls_prediction_std
from statsmodels.stats.outliers_influence import summary_table

import itertools as it

import pandas as pd
from math import log10
import linecache

mydir = os.path.expanduser("~/GitHub/MicrobialScaling/")


def Fig1(ref, Ones):

    datasets = []
    if ref == 'ClosedRef': GoodNames = ['EMPclosed', 'HMP', 'BIGN', 'TARA', 'BOVINE', 'HUMAN', 'LAUB', 'SED', 'CHU', 'CHINA', 'CATLIN', 'FUNGI', 'HYDRO', 'BBS', 'CBC', 'MCDB', 'GENTRY', 'FIA'] # all microbe data is MGRAST

    if ref == 'OpenRef': GoodNames = ['EMPopen', 'HMP', 'BIGN', 'TARA', 'BOVINE', 'HUMAN', 'LAUB', 'SED', 'CHU', 'CHINA', 'CATLIN', 'FUNGI', 'HYDRO', 'BBS', 'CBC', 'MCDB', 'GENTRY', 'FIA'] # all microbe data is MGRAST

    for name in os.listdir(mydir +'data/micro'):
        if name in GoodNames: pass
        else: continue

        if Ones == 'N': path = mydir+'data/micro/'+name+'/'+name+'-SADMetricData_NoMicrobe1s.txt'
        elif Ones == 'Y': path = mydir+'data/micro/'+name+'/'+name+'-SADMetricData.txt'

        num_lines = sum(1 for line in open(path))
        datasets.append([name, 'micro', num_lines])
        print name, num_lines

    for name in os.listdir(mydir +'data/macro'):
        if name in GoodNames: pass
        else: continue

        if Ones == 'N': path = mydir+'data/macro/'+name+'/'+name+'-SADMetricData_NoMicrobe1s.txt'
        elif Ones == 'Y': path = mydir+'data/macro/'+name+'/'+name+'-SADMetricData.txt'

        num_lines = sum(1 for line in open(path))
        datasets.append([name, 'macro', num_lines])
        print name, num_lines


    metrics = ['Evar', 'ESimp', 'Heip\'s', 'O']

    fig = plt.figure()
    for index, i in enumerate(metrics):

        metric = i
        fig.add_subplot(2, 2, index+1)
        fs = 10 # font size used across figures

        MicIntList, MicCoefList, MacIntList, MacCoefList, R2List, metlist = [[], [], [], [], [], []]
        Nlist, Slist, ESimpList, klist, radDATA, BPlist, NmaxList, rareSkews, KindList = [[], [], [], [], [], [], [], [], []]
        EvarList, EQList, EHeipList, OList = [[],[],[],[]]
        SimpDomList, McNList, LogSkewList, POnesList = [[],[],[],[]]

        its = 10000
        for n in range(its):
            print n, metric

            Nlist, Slist, ESimpList, klist, radDATA, BPlist, NmaxList, rareSkews, KindList = [[], [], [], [], [], [], [], [], []]
            EvarList, EQList, EHeipList, OList = [[],[], [],[]]
            SimpDomList, McNList, LogSkewList, POnesList = [[],[],[],[]]

            numMac = 0
            numMic = 0
            radDATA = []

            for dataset in datasets:

                name, kind, numlines = dataset
                lines = []
                small = ['BIGN', 'BOVINE', 'CHU', 'LAUB', 'SED']
                big = ['HUMAN', 'CHINA', 'CATLIN', 'FUNGI', 'HYDRO']

                if kind == 'macro':
                    lines = np.random.choice(range(1, numlines+1), 100, replace=True)

                elif name in small:
                    lines = np.random.choice(range(1, numlines+1), 20, replace=True)

                elif name in big:
                    lines = np.random.choice(range(1, numlines+1), 50, replace=True)

                elif name == 'TARA':
                    lines = np.random.choice(range(1, numlines+1), 50, replace=True)
                else:
                    lines = np.random.choice(range(1, numlines+1), 50, replace=True)

                if Ones == 'N':   path = mydir+'data/'+kind+'/'+name+'/'+name+'-SADMetricData_NoMicrobe1s.txt'
                elif Ones == 'Y': path = mydir+'data/'+kind+'/'+name+'/'+name+'-SADMetricData.txt'

                for line in lines:
                    data = linecache.getline(path, line)
                    radDATA.append(data)

            for data in radDATA:

                data = data.split()
                name, kind, N, S, Var, Evar, ESimp, EQ, O, ENee, EPielou, EHeip, BP, SimpDom, Nmax, McN, skew, logskew, chao1, ace, jknife1, jknife2, margalef, menhinick, preston_a, preston_S = data

                KindList.append(kind)
                N = float(N)
                S = float(S)

                if S < 2 or N < 10: continue # Min species richness

                Nlist.append(float(np.log10(N)))
                Slist.append(float(np.log10(S)))

                # Evenness
                EvarList.append(float(np.log10(float(Evar))))
                EHeipList.append(float(np.log10(float(EHeip))))
                OList.append(float(np.log10(float(O))))
                ESimpList.append(float(np.log10(float(ESimp))))


                if kind == 'micro':
                    numMic += 1
                    klist.append('b')
                if kind == 'macro':
                    klist.append('r')
                    numMac += 1


            if index == 0: metlist = list(EvarList)
            elif index == 1: metlist = list(ESimpList)
            elif index == 2: metlist = list(EHeipList)
            elif index == 3: metlist = list(OList)

            # Multiple regression
            d = pd.DataFrame({'N': list(Nlist)})
            d['y'] = list(metlist)
            d['Kind'] = list(KindList)
            f = smf.ols('y ~ N * Kind', d).fit()

            MacIntList.append(f.params[0])
            MacCoefList.append(f.params[2])

            if f.pvalues[1] < 0.05:
                MicIntList.append(f.params[1] + f.params[0])
            else:
                MicIntList.append(f.params[0])

            if f.pvalues[3] < 0.05:
                MicCoefList.append(f.params[3] + f.params[2])
            else:
                MicCoefList.append(f.params[2])

            R2List.append(f.rsquared)

        MacListX = []
        MacListY = []
        MicListX = []
        MicListY = []

        for j, k in enumerate(KindList):
            if k == 'micro':
                MicListX.append(Nlist[j])
                MicListY.append(metlist[j])

            elif k == 'macro':
                MacListX.append(Nlist[j])
                MacListY.append(metlist[j])


        MacPIx, MacFitted, MicPIx, MicFitted = [[],[],[],[]]
        macCiH, macCiL, micCiH, micCiL = [[],[],[],[]]

        lm = smf.ols('y ~ N * Kind', d).fit()
        print metric, '\n', lm.summary()
        f1 = smf.ols('y ~ N', d).fit()
        print metric, '\n', f1.summary()

        st, data, ss2 = summary_table(lm, alpha=0.05)
        # ss2: Obs, Dep Var Population, Predicted Value, Std Error Mean Predict,
        # Mean ci 95% low, Mean ci 95% upp, Predict ci 95% low, Predict ci 95% upp,
        # Residual, Std Error Residual, Student Residual, Cook's D

        fittedvalues = data[:,2]
        predict_mean_se = data[:,3]
        predict_mean_ci_low, predict_mean_ci_upp = data[:,4:6].T
        predict_ci_low, predict_ci_upp = data[:,6:8].T


        for j, kval in enumerate(KindList):
            if kval == 'macro':

                macCiH.append(predict_mean_ci_upp[j])
                macCiL.append(predict_mean_ci_low[j])
                MacPIx.append(Nlist[j])
                MacFitted.append(f.fittedvalues[j])

            elif kval == 'micro':

                micCiH.append(predict_mean_ci_upp[j])
                micCiL.append(predict_mean_ci_low[j])
                MicPIx.append(Nlist[j])
                MicFitted.append(f.fittedvalues[j])

        MicPIx, MicFitted, micCiH, micCiL = zip(*sorted(zip(MicPIx, MicFitted, micCiH, micCiL)))
        MacPIx, MacFitted, macCiH, macCiL = zip(*sorted(zip(MacPIx, MacFitted, macCiH, macCiL)))

        for i in range(len(MicListX)):
            plt.scatter(MacListX[i], MacListY[i], color = 'LightCoral', alpha= 1 , s = 4, linewidths=0.5, edgecolor='Crimson')
            plt.scatter(MicListX[i], MicListY[i], color = 'SkyBlue', alpha= 1 , s = 4, linewidths=0.5, edgecolor='Steelblue')

        plt.fill_between(MacPIx, macCiL, macCiH, color='r', lw=0.0, alpha=0.3)
        plt.fill_between(MicPIx, micCiL, micCiH, color='b', lw=0.0, alpha=0.3)

        MicInt = round(np.mean(MicIntList), 2)
        MicCoef = round(np.mean(MicCoefList), 2)
        MacInt = round(np.mean(MacIntList), 2)
        MacCoef = round(np.mean(MacCoefList), 2)
        r2 = round(np.mean(R2List), 2)

        if index == 0:

            plt.ylim(-1.7, 0.2)
            plt.xlim(0, 7)
            plt.text(.3, -1.35, r'$micro$'+ ' = '+str(round(MicInt,2))+'*'+r'$N$'+'$^{'+str(round(MicCoef,2))+'}$', fontsize=fs-1, color='Steelblue')
            plt.text(.3, -1.5, r'$macro$'+ ' = '+str(round(MacInt,2))+'*'+r'$N$'+'$^{'+str(round(MacCoef,2))+'}$', fontsize=fs-1, color='Crimson')
            plt.text(.3, -1.65,  r'$R^2$' + '=' +str(round(r2,3)), fontsize=fs-1, color='k')


        if index == 1:

            plt.ylim(-3.5, 0.2)
            plt.xlim(0, 7)
            plt.text(.3, -2.5, r'$micro$'+ ' = '+str(round(MicInt,2))+'*'+r'$N$'+'$^{'+str(round(MicCoef,2))+'}$', fontsize=fs-1, color='Steelblue')
            plt.text(.3, -2.9, r'$macro$'+ ' = '+str(round(MacInt,2))+'*'+r'$N$'+'$^{'+str(round(MacCoef,2))+'}$', fontsize=fs-1, color='Crimson')
            plt.text(.3, -3.3,  r'$R^2$' + '=' +str(round(r2,3)), fontsize=fs-1, color='k')

        if index == 2:

            plt.ylim(-3.0, 0.2)
            plt.xlim(0, 7)
            plt.text(.2, -2.2, r'$micro$'+ ' = '+str(round(MicInt,2))+'*'+r'$N$'+'$^{'+str(round(MicCoef,2))+'}$', fontsize=fs-1, color='Steelblue')
            plt.text(.2, -2.5, r'$macro$'+ ' = '+str(round(MacInt,2))+'*'+r'$N$'+'$^{'+str(round(MacCoef,2))+'}$', fontsize=fs-1, color='Crimson')
            plt.text(.2, -2.8,  r'$R^2$' + '=' +str(round(r2,3)), fontsize=fs-1, color='k')

        if index == 3:
            plt.ylim(-1.5, 0.2)
            plt.xlim(0, 7)
            plt.text(.2, -1.1, r'$micro$'+ ' = '+str(round(MicInt,2))+'*'+r'$N$'+'$^{'+str(round(MicCoef,2))+'}$', fontsize=fs-1, color='Steelblue')
            plt.text(.2, -1.25, r'$macro$'+ ' = '+str(round(MacInt,2))+'*'+r'$N$'+'$^{'+str(round(MacCoef,2))+'}$', fontsize=fs-1, color='Crimson')
            plt.text(.2, -1.4,  r'$R^2$' + '=' +str(round(r2,3)), fontsize=fs-1, color='k')

        plt.xlabel('Number of reads or individuals, '+ '$log$'+r'$_{10}$', fontsize=fs)
        plt.ylabel(metric, fontsize=fs)
        plt.tick_params(axis='both', which='major', labelsize=fs-1)

    plt.subplots_adjust(wspace=0.4, hspace=0.4)
    if ref == 'OpenRef'and Ones =='N': plt.savefig(mydir+'/figs/appendix/Evenness/SupplementaryEvennessFig-OpenRef_NoMicrobe1s.png', dpi=600, bbox_inches = "tight")
    elif ref == 'OpenRef'and Ones =='Y': plt.savefig(mydir+'/figs/appendix/Evenness/SupplementaryEvennessFig-OpenRef.png', dpi=600, bbox_inches = "tight")
    elif ref == 'ClosedRef'and Ones =='Y': plt.savefig(mydir+'/figs/appendix/Evenness/SupplementaryEvennessFig-ClosedRef.png', dpi=600, bbox_inches = "tight")
    elif ref == 'ClosedRef'and Ones =='N': plt.savefig(mydir+'/figs/appendix/Evenness/SupplementaryEvennessFig-ClosedRef_NoMicrobe1s.png', dpi=600, bbox_inches = "tight")

    #plt.close()

    return



Fig1(ref='ClosedRef', Ones='Y')
#Fig1(ref='ClosedRef', Ones='N')
#Fig1(ref='OpenRef', Ones='Y')
#Fig1(ref='OpenRef', Ones='N')
