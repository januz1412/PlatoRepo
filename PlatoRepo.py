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
#     0.0.6 2024-01-09 cam aliases added up to fm18
#     0.0.7 2024-03-04 class IMAGE drafted
#     0.0.8 2024-05-06 draft release for EMC testing

__version__ = "0.0.8_20240506"

import pandas as pd
import os
import numpy as np
import datetime as datetime
from astropy.io import fits


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

def is_odd(num):
    return num & 0x1

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
        CAMID = 'hoegaarden'
    elif camIdAlias.lower() in ['ichtegem', 'anneliesescnell', 'fm8', 'fm08']:
        CAMID = 'ichtegem'
    elif camIdAlias.lower() in ['joup', 'ottostruve', 'fm9', 'fm09']:
        CAMID = 'joup'
    elif camIdAlias.lower() in ['karmeliet', 'yvferrazpereira', 'fm10']:
        CAMID = 'karmeliet'
    elif camIdAlias.lower() in ['leopold7', 'antoniaferrin', 'fm12']:
        CAMID = 'leopold7'
    elif camIdAlias.lower() in ['lupulus', 'chansteen', 'fm13']:
        CAMID = 'lupulus'
    elif camIdAlias.lower() in ['maredsous', 'vanhouten', 'fm14']:
        CAMID = 'maredsous'
    elif camIdAlias.lower() in ['noblesse', 'zdeneksvestka', 'fm15']:
        CAMID = 'noblesse'
    elif camIdAlias.lower() in ['orval', 'cristinaroccati', 'fm16']:
        CAMID = 'orval'
    elif camIdAlias.lower() in ['paixdieu', 'anderscelsius', 'fm17']:
        CAMID = 'paixdieu'
    elif camIdAlias.lower() in ['quintine', 'marcelgolay', 'fm18']:
        CAMID = 'quintine'   
    return CAMID

def de_oddify(array, axis='col'):
    # presently it accept only 2D array
    if axis == 'col':
        # col is the first dimension (or the second in a datacube)
        imgF = array.mean(axis=0)
        oe = 0
        if is_odd(len(imgF)):
            md = -1
        else:
            md = 0
        for col in range(0,len(imgF)+md,2):
            oe = oe + imgF[col] - imgF[col+1]
        print('odd/even (C): ' + str(oe))
        oe = oe / (len(imgF)+md)
        for col in range(len(imgF)):
            if is_odd(col):
                array[:,col] = array[:,col] + oe
            else:
                array[:,col] = array[:,col] - oe
    elif axis == 'row':
        # row is the second dimension (or the third in a datacube)
        imgF = array.mean(axis=1)
        oe = 0
        if is_odd(len(imgF)):
            md = -1
        else:
            md = 0
        for row in range(0,len(imgF)+md,2):
            oe = oe + imgF[row] - imgF[row+1]
        print('odd/even (R): ' + str(oe))
        oe = oe / (len(imgF)+md)
        for row in range(len(imgF)):
            if is_odd(row):
                array[row,:] = array[row,:] + oe
            else:
                array[row,:] = array[row,:] - oe
    else:
        print('ERROR the parameter \'axis\' can assume only the values "col" or "row"')
        exit()
    imgF = 0
    return array

def oee_check(dati, axis='col'):
    oee = 0
    if axis == 'col':
        imgF = dati.mean(axis=0)
        for col in range(0,len(imgF)-1,2):
            oee = oee + imgF[col] - imgF[col+1]
    elif axis == 'row':
        imgF = dati.mean(axis=1)
        for row in range(0,len(imgF)-1,2):
            oee = oee + imgF[row] - imgF[row+1]
    else:
        print('ERROR: \'axis\' input argument can be only either \'col\' or \'row\'')
        exit()
    return oee



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
        
class IMAGES_CAT:
    def __init__(self, rootDir):
        # note: *use wisely*. rootDir can be any directory of the file system
        # the nominal usage is to identify either the facility root or the obsid root
        if rootDir[-1] == os.sep:
            rootDir = rootDir[0:-1]
        self.rootDir = rootDir
        IMAGES_CAT.fileDB = []
        self._obsidTableF = None
        self.toc = None

    def load(self,camId=None):            
        print('Creating the fits file DB for CAM ' + camId + '....')
        for root, dirs_list, files_list in os.walk(self.rootDir):
            for fn in files_list:
                if fn.split('.')[-1].lower() == 'fits':
                    if camId is None:
                        self.cam_id = ''
                        self.fileDB.append(os.path.join(root, fn))
                    elif fn.lower().find(camId2Bier(camId)) != -1:
                        self.fileDB.append(os.path.join(root, fn))
                        self.cam_id = camId
        print(' ..... DONE. ' + str(len(self.fileDB)) + ' files in the DB')
        self.fileDB.sort()
        if os.path.isfile(self.rootDir + '/obs/obsid-table.txt'):
            self._obsidTableFound = True
            self._obsidTableF = self.rootDir + '/obs/obsid-table.txt'
            try:
                self.obsidDB = pd.read_fwf(self._obsidTableF,colspecs=[[0,5],[6,9],[10,15],[16,44],[45,1000]], names=['OBSID', 'FACILITY', 'NUM', 'TIME', 'EXEC'], header=None)
            except FileNotFoundError:
                self.obsidDB = None
    
    def createTOC(self,obsid=None):
        TOC = []
        if obsid is not None:
            obsidT = str(obsid).zfill(5)
        guhLines = ['CAMERA;CAMNUM;FILENAME;OBSID;EXEC;EXECCMMT;DATE-OBS;CCD_READOUT_ORDER;CYCLETIME;READTIME;DIT;OBJ_CNT;EXT_NUM;NUMIMGS;X;Y;EXTNAME;IMGTYPE;CCD_ID;SENSOR_SEL;SOURCE;DITHER\n']
        fcount = 0
        print('\n')
        for f in self.fileDB:
            go = True
            if obsid is not None:
                if f.find('/' + obsidT +'_') == -1:
                    go = False
            if go:
                hdu = fits.open(f, ignore_missing_simple=True, output_verify='exception', checksum=True)
                OBSID = str(hdu[0].header['OBSID'])[-5:] 
                if self.obsidDB is not None:
                    execLine = self.obsidDB[['EXEC']][self.obsidDB['OBSID']==int(OBSID[:-1])].iloc[0,0]
                    EXEC = execLine[:execLine.find(')')+1].replace(';','|') + ';'
                    EXECCMMT = execLine[execLine.find(')')+1:].replace(';','|') + ';'
                else:
                    EXEC = ''
                    EXECCMMT = ''
                CAMNUM = self.cam_id
                CAMID = self.cam_id
                DATEOBS = hdu[0].header['DATE-OBS']
                CCD_READOUT_ORDER = '"' + str(hdu[0].header['CCD_READOUT_ORDER']) + '"'
                CYCLETIME = hdu[0].header['CYCLETIME']
                READTIME = hdu[0].header['READTIME']
                DIT = hdu[0].header['READTIME'] + 0.4
                SYNC_SEL = hdu[0].header['SYNC_SEL']
                objcnt = 0
                for idx in range(1,len(hdu)):
                    if str(hdu[idx].header['XTENSION']) == 'IMAGE':
                        objcnt += 1
                        OBJ_CNT =  objcnt
                        EXT_NUM = idx
                        try:
                            NUMIMGS = hdu[idx].header['NAXIS3']
                        except KeyError:
                            NUMIMGS = ''
                        X =  hdu[idx].header['NAXIS1']
                        Y =  hdu[idx].header['NAXIS2']
                        EXTNAME = str(hdu[idx].header['EXTNAME'])
                        IMGTYPE = EXTNAME[0:EXTNAME.find('_')]

                        CCD_ID = str(hdu[idx].header['CCD_ID'])
                        SENSOR = str(hdu[idx].header['SENSOR_SEL'])

                        TOC.append({
                            'CAMERA': CAMID,
                            'CAMNUM': CAMNUM,
                            'FILENAME': f,
                            'OBSID': OBSID,
                            'EXEC': EXEC,
                            'EXECCMMT': EXECCMMT,
                            'DATE-OBS': DATEOBS,
                            'CCD_READOUT_ORDER': CCD_READOUT_ORDER,
                            'CYCLETIME': CYCLETIME,
                            'READTIME': READTIME,
                            'DIT': DIT,
                            'SYNC_SEL': SYNC_SEL,
                            'OBJ_CNT': OBJ_CNT,
                            'EXT_NUM': EXT_NUM,
                            'NUMIMGS': NUMIMGS,
                            'X': X,
                            'Y': Y,
                            'EXTNAME': EXTNAME,
                            'IMGTYPE': IMGTYPE,
                            'CCD_ID': CCD_ID,
                            'SENSOR': SENSOR,
                            'SEL': "",
                            'SOURCE': '',
                            'DITHER': ''
                        })
                        n = len(TOC)
                hdu.close()
        self.toc = TOC

# for debugging and usage reference:
if False:
    ### proper include and initial configuration:
    # import PlatoRepo as PR
    # rootdir = 'myPath'
    # TH_HK = PR.HK(rootdir)
    # TH_HK.load('my_cam_id')
    ### for the functions:
    # newparam = PR.align2Parameters(RefParam,toBeAlignParam)
    #
    # now the example for debuggin purpose:
    rootdir = '/archive/PLATO/IAS/'
    IAS_HK = HK(rootdir)
    IAS_HK.load('fm4')
    param = 'GTCS_TRP1_POUT'
    TRP1_POUT = IAS_HK.Param(param)
    obsid1234 = TRP1_POUT.getValuesByOBSID(obsid=1234)
    print(obsid1234['Values'])
    print(obsid1234['Time'])
    fromT0toT1 = TRP1_POUT.getValuesByTime(T0='2020-01-01T00:00:00', T1='2025-12-31T00:00:00')
    if min(fromT0toT1['Time']) < '2020-01-01T00:00:00':
        print('condition impossible')
    atTime, Value  = TRP1_POUT.getValueAtTime(T0='2022-10-10T08:00:00')
    refParam = IAS_HK('NFEE_T_CCD1')
    toBeAlignParam = IAS_HK('GTCS_TRP1_1')
    newAlignedParameter = align2Parameters(RefParam,toBeAlignParam)



            

