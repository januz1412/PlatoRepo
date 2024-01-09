#!/usr/bin/env python3

# Owned
__author__ = "Giana Nicolini (INAF - OATo)"
__copyright__ = "TBD"
__credits__ = [""]
__license__ = "GPL"
__maintainer__ = "Giana Nicolini"
__email__ = "gianalfredo.nicolini@inaf.it"
__status__ = "beta"

# Change Log
# Ver       Date       Description
# --------- ---------- -----------------------------------------------
#     0.0.1 2023-12-20 Beta
#     0.0.2 2023-12-21 "timestamp" column used in case no param dedicated timestamp "_ts" exists 
#     0.0.3 2024-01-03 function "align2Parameters" added
#     0.0.4 2024-01-05 function "getValueAtTime" added
#     0.0.5 2024-01-09 few cam aliases added
__version__ = "0.0.5_20240109"

import pandas as pd
import os
import numpy as np
import datetime as datetime


# how to share variables among classes:
#
# class Child():
#   def __init__(self):
#     self.var_2 = "World"
#
# class Main():
#   def __init__(self):
#     self.var_1 = "Hello"
#     self.child = Child()
#     print("Inside class:", self.var_1, self.child.var_2)
#
# main = Main()
# print("Outside class:", main.var_1, main.child.var_2)

# How to share variables among methods:
#
# class TestClass(object):
#
#     def __init__(self):
#         self.test = None
#
#     def current(self, test):
#         """Just a method to get a value"""
#         self.test = test
#         print(test)
#
#     def next_one(self):
#         """Trying to get a value from the 'current' method"""
#         new_val = self.test
#         print(new_val)

def camId2Bier(camIdAlias):
    CAMID = None
    if camIdAlias.lower() in ['achel', 'hypatia', 'pfm']:
        CAMID = 'achel'
    elif camIdAlias.lower() in ['brigand', 'arthureddington', 'fm1', 'fm01']:
        CAMID = 'brigand'
    elif camIdAlias.lower() in ['chimay', 'carolineherschel', 'fm2', 'fm02']:
        CAMID = 'chimay'
    elif camIdAlias.lower() in ['duvel', 'bengtstromgren', 'fm3', 'fm03']:
        CAMID = 'duvel'
    elif camIdAlias.lower() in ['elfique', 'acoradini', 'fm4', 'fm04']:
        CAMID = 'elfique'
    elif camIdAlias.lower() in ['floreffe', 'paulledoux', 'fm5', 'fm05']:
        CAMID = 'floreffe'
    elif camIdAlias.lower() in ['gueuze', 'francoisepraderie', 'fm6', 'fm06']:
        CAMID = 'gueuze'
    elif camIdAlias.lower() in ['hoegaarden', 'robertemdem', 'fm7', 'fm07']:
        CAMID = 'h'
    elif camIdAlias.lower() in ['ichtegem', 'anneliesescnell', 'fm8', 'fm08']:
        CAMID = 'i'
    elif camIdAlias.lower() in ['joup', 'ottostruve', 'fm9', 'fm09']:
        CAMID = 'j'
    elif camIdAlias.lower() in ['karmeliet', 'yvferrazpereira', 'fm10']:
        CAMID = 'k'
    elif camIdAlias.lower() in ['l', 'fmdacostalobo', 'fm11']:
        CAMID = 'l'
        
        
    return CAMID

def align2Parameters(RefParam,toBeAlignParam):
    # this routine aligns the values of two parameters in order to have identical size and time base
    # The update interval of the first parameter is taken as reference in order to compute the new vector
    # Values of the second parameeter outside the domain of the firstone are ignored.
    # For both parameters, the expected format is the HK class
    refT = RefParam['Time']
    newT = []
    newV = []

    p2T = toBeAlignParam['Time']
    p2OV = toBeAlignParam['Values']
    dT = datetime.datetime.fromisoformat(refT[1]) - datetime.datetime.fromisoformat(refT[0])

    lastidx2 = 0
    for idx in range(len(refT)-1):
        Tinf = datetime.datetime.fromisoformat(refT[idx]) - dT/2
        Tsup = datetime.datetime.fromisoformat(refT[idx]) + dT/2
        np = 0
        VV = 0
        for idx2 in range(lastidx2,len(p2T)):
            # print(str(idx) + ' - ' + str(idx2))
            t2 = datetime.datetime.fromisoformat(p2T[idx2])
            if t2 >= Tinf and t2 <= Tsup:
                lastidx2 = idx2
                VV = VV + p2OV[idx2]
                np += 1
            if t2 > Tsup:
                break
        if np != 0:
            newT.append(refT[idx])
            newV.append(VV/np)
        else:
            newT.append(refT[idx])
            newV.append(0.0)
    Tinf = datetime.datetime.fromisoformat(refT[idx+1]) - dT/2
    Tsup = datetime.datetime.fromisoformat(refT[idx+1]) + dT/2
    np = 0
    VV = 0
    for idx2 in range(lastidx2,len(p2T)):
        # print(str(idx) + ' - ' + str(idx2))
        t2 = datetime.datetime.fromisoformat(p2T[idx2])
        if t2 >= Tinf and t2 <= Tsup:
            VV = VV + p2OV[idx2]
            np += 1
        if t2 > Tsup:
            break
    if np != 0:
        newT.append(refT[idx])
        newV.append(VV/np)
    else:
        newT.append(refT[idx])
        newV.append(0.0)
    tab = {"Time": newT, "Values":newV}
    newP = pd.DataFrame(tab)

    return newP


class HK:
    def __init__(self, rootDir):
        # note: *use wisely*. rootDir can be any directory of the file system
        # the nominal usage is to identify either the facility root or the obsid root
        if rootDir[-1] == os.sep:
            rootDir = rootDir[0:-1]
        self.rootDir = rootDir
        HK.fileDB = []

    def load(self,camId=None):            
        print('Creating the HK file DB for CAM ' + camId + '....')
        for root, dirs_list, files_list in os.walk(self.rootDir):
            for fn in files_list:
                if fn.split('.')[-1].lower() == 'csv':
                    if camId is None:
                        HK.fileDB.append(os.path.join(root, fn))
                    elif fn.lower().find(camId2Bier(camId)) != -1:
                        HK.fileDB.append(os.path.join(root, fn))
        print(' ..... DONE. ' + str(len(self.fileDB)) + ' files in the DB')
        self.fileDB.sort()

    class Param:
        def __init__(self,pName):
            # pName can be any HK parameter included in the csv headers not ending with "_ts":
            # Examples
            # For TCS-HK  -> GTCS_TRP1_1_T
            # For N-FEE-HK -> NFEE_MODE
            print('Creating the HK file DB for the parameter ' + pName + '....')
            self.fileDB = []
            self.pName = pName
            for f in HK.fileDB:
                ### TO IMPLEMENT: NA, None, Null, empty
                try:
                    pDB = pd.read_csv(f,header=0,low_memory=False)
                    test = pDB[pName]
                except (KeyError, pd.errors.EmptyDataError):
                    pass
                else:
                    # print(f)
                    self.fileDB.append(f)
            print(' ..... DONE. ' + str(len(self.fileDB)) + ' files in the DB')


        def getValuesByOBSID(self,obsid,OOLL=None,OOLH=None):
            obsidT = str(obsid).zfill(5)
            # define the time values
            try:
                pTime = self.pName+'_ts'
                tab = pd.read_csv(self.fileDB[0],header=0, usecols=[pTime])
            except ValueError:
                # in this case the column with the deidcated timestamps "_ts" does not exists
                pTime = 'timestamp'
                
            self.values = pd.DataFrame(columns=[pTime,self.pName])
            fc = 0
            OOL = False
            for f in self.fileDB:
                if f.find('/obs/' + obsidT) != -1:
                    print(f)
                    tab = pd.read_csv(f,header=0, usecols=[pTime, self.pName]).drop_duplicates(subset=pTime, keep='first')
                    if OOLL is not None:
                        self.values = pd.concat([self.values, tab[tab[self.pName] < OOLL]], axis=0 , ignore_index=True)
                        OOL = True
                    if OOLH is not None:
                        self.values = pd.concat([self.values, tab[tab[self.pName] > OOLH]], axis=0 , ignore_index=True)
                        OOL = True
                    if not OOL:
                        self.values = pd.concat([self.values, tab], axis=0 , ignore_index=True)
                    fc += 1
            self.values.rename(columns={pTime: "Time", self.pName: "Values"}, inplace=True)
            self.values.drop_duplicates(subset='Time', keep='first', inplace=True)
            self.values.sort_values(by=['Time'], inplace=True, ignore_index=True)
            # self.values.reset_index(drop=True)
            return self.values
            

        def getValuesByTime(self,T0,T1,OOLL=None,OOLH=None):
            try:
                pTime = self.pName+'_ts'
                tab = pd.read_csv(self.fileDB[0],header=0, usecols=[pTime])
            except ValueError:
                # in this case the column with the deidcated timestamps "_ts" does not exists
                pTime = 'timestamp'
                
            self.values = pd.DataFrame(columns=[pTime,self.pName])
            fc = 0
            OOL = False
            for f in self.fileDB:
                tab = pd.read_csv(f,header=0, usecols=[pTime, self.pName]).drop_duplicates(subset=pTime, keep='first')
                try:
                    minT = min(tab[pTime])
                    maxT = max(tab[pTime])
                except (ValueError, TypeError):
                    pass
                else:
                    if pd.isna(minT) or pd.isna(maxT):
                        pass
                    else:
                        if min(tab[pTime]) < T1 and max(tab[pTime]) > T0:
                            print(f)
                            if OOLL is not None:
                                self.values = pd.concat([
                                    self.values,
                                    tab[(tab[self.pName] < OOLL) & (tab[pTime] >= T0) & (tab[pTime] <= T1)]
                                    ], axis=0 , ignore_index=True)
                                OOL = True
                            if OOLH is not None:
                                self.values = pd.concat([
                                    self.values,
                                    tab[(tab[self.pName] > OOLH) & (tab[pTime] >= T0) & (tab[pTime] <= T1)]
                                    ], axis=0 , ignore_index=True)
                                OOL = True
                            if not OOL:
                                self.values = pd.concat([
                                    self.values,
                                    tab[(tab[pTime] >= T0) & (tab[pTime] <= T1)]
                                    ], axis=0 , ignore_index=True)
                            fc += 1
            self.values.rename(columns={pTime: "Time", self.pName: "Values"}, inplace=True)
            self.values.drop_duplicates(subset='Time', keep='first', inplace=True)
            self.values.sort_values(by=['Time'], inplace=True, ignore_index=True)
            return self.values

        def getValueAtTime(self,T0):
            # print(T0)
            deltaT = 1 # minute
            while True:
                Tmindt = datetime.datetime.fromisoformat(T0) - datetime.timedelta(minutes=deltaT)
                Tmaxdt = datetime.datetime.fromisoformat(T0) + datetime.timedelta(minutes=deltaT)
                dTi = Tmaxdt - Tmindt
                Tmin = Tmindt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
                Tmax = Tmaxdt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
                print(Tmin)
                list = self.getValuesByTime(Tmin,Tmax)
                if len(list) > 0:
                    break
                else:
                    deltaT += 1
            lastT = '2000-01-01T00:00:00.000'
            lastV = 0
            Time = None
            Value = None

            for idx in range(len(list)):
                theT = list['Time'][idx]
                # print(theT)
                # print(dTi)
                if theT >= T0:
                    dTs = datetime.datetime.fromisoformat(theT) - datetime.datetime.fromisoformat(T0)
                    if dTs < dTi:
                        Value = list['Values'][idx]
                        Time = theT
                    else:
                        Value = lastV
                        Time = lastT
                    break
                lastT = theT
                lastV = list['Values'][idx]
                dTi = datetime.datetime.fromisoformat(T0) - datetime.datetime.fromisoformat(theT) 
            print('The value of ' + self.pName + ' at time ' + Time + ' is ' + str(Value))
            return [Time, Value]
        

# for debugging purpose:
# rootdir = '/archive/PLATO/IAS/'
# IAS_HK = HK(rootdir)
# IAS_HK.load('fm4')
# param = 'GTCS_TRP1_POUT'
# TRP1 = IAS_HK.Param(param)
#         

