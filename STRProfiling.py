#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 20:10:38 2020

@author: luc

# build a class for STR profiling data storage, management and similarity search

"""

# change markerInfor as private
import pandas as pd
from collections import OrderedDict

# contains str class definition and percentage match calculation by given a str class
class STRProfile:
    
    species = "human"
    marker_list = ['AMEL', 'CSF1PO', 'D2S1338', 'D3S1358', 'D5S818', 'D7S820', 'D8S1179', 
                   'D13S317', 'D16S539', 'D18S51', 'D19S433', 'D21S11', 'FGA', 'TH01', 'TPOX', 'vWA']
    
    # set default of all marker infor as empty
    def __init__(self,name):
        self.name = name
        self.markerInfor =  {key: '' for key in self.marker_list}
        '''
        self.markerInfor = {'AMEL':'', 'CSF1PO':'', 'D2S1338':'', 'D3S1358':'', 'D5S818':'', 'D7S820':'',
                            'D8S1179':'', 'D13S317':'', 'D16S539':'', 'D18S51':'', 'D19S433':'',
                            'D21S11':'', 'FGA':'', 'TH01':'', 'TPOX':'', 'vWA':''}
        '''
    #funtion to update marker infor for STRProfile by given list of markers and values
    def addMarkerInfor(self, markers, values):
        for item in zip(markers, values):
            if item[0] in self.marker_list:
                self.markerInfor[item[0]] = item[1]
        
    def PctMatchCalc(self, ReferSTR):
        '''
        input = STRProfile
        output = percentage match between two STRProfile
        calculation alogrithm = 2 * No. shared alleles/(No. query alleles + No. reference alleles)
        (Tanabe) 
        Not consider about handling cases in which allele data is missing for the query or the reference: 
        Article: DOI=10.11418/jtca1981.18.4_329
        Review: PubMed=23136038
        '''
        SharedAllelCount = 0
        QueryAllelCount = 0
        ReferAllelCOunt = 0
        
        for key, value in self.markerInfor.items():
            queryAllel = str(value).split(",")
            referAllel = str(ReferSTR.markerInfor[key]).split(",")
            QueryAllelCount = QueryAllelCount + len(queryAllel)
            ReferAllelCOunt = ReferAllelCOunt + len(referAllel)
            SharedAllelCount = SharedAllelCount + len(list(set(queryAllel) & set(referAllel)))
            PctMatch = SharedAllelCount * 2 / (QueryAllelCount + ReferAllelCOunt)

        return PctMatch


# a list of STR objects, contains function of grouppairs
class STRProfileList(STRProfile):
    
    def __init__(self, STRProfile_list):
        self.obj = STRProfile_list
       

    def GroupPairs(self):
        '''
            input = STRProfileList
            output = List of STRProfileList contains paired objects
        '''
        group_list = []
        for idx, obj in enumerate(self.obj):
            ListSTR = []
            ListSTR.append(self.obj[idx])
            i = idx + 1
            while i < len(self.obj):
                if self.obj[idx].PctMatchCalc(self.obj[i])> 0.9:
                    ListSTR.append(self.obj[i])
                    self.obj.pop(i)          
                else:
                    i = i + 1
            group_list.append(STRProfileList(ListSTR))
        
        return group_list
    
# generate class STRProfileList object by given excel file, first column has to be sample name        
def ImportFromExcel(file_address):
    '''
        input = file address contains STR profile information
        output = List of STRProfile objects for all samples in the file
    '''

    sample_list = pd.read_excel(file_address, index_col = 0)
    sample_name = sample_list.index
    values = sample_list.values.tolist()
    marker = list(sample_list.columns.values)
    STRProfile_list = []

    for idx, val in enumerate(sample_name):
        val = STRProfile(val)
        val.addMarkerInfor(marker, values[idx])
        STRProfile_list.append(val)
        
        
    return STRProfileList(STRProfile_list)

# write list of STRProfileList into excel

def WriteToExcel(list_of_STRProfileList):
    '''
        input = a list of STRProfileList
        output = excel file generation
    '''
    header = ['name', 'PctMatch', 'AMEL', 'CSF1PO', 'D2S1338', 'D3S1358', 'D5S818', 'D7S820', 'D8S1179', 
              'D13S317', 'D16S539', 'D18S51', 'D19S433', 'D21S11', 'FGA', 'TH01', 'TPOX', 
              'vWA']
    
    all_group = OrderedDict()
    for idx, val in enumerate(list_of_STRProfileList):    
        STRList = val.obj
        df = OrderedDict()
        for item in STRList:
            name = item.name
            value = item.markerInfor
            df[name] = value.copy()
            df[name]["name"] = name
            if item != STRList[0]:
                pct = item.PctMatchCalc(STRList[0])
                df[name]["PctMatch"] = '{:.2%}'.format(pct)
    
                    
        all_group[idx] = pd.DataFrame((df[key] for key in df), columns = header)
    
    
    total_df = pd.concat(all_group, ignore_index = False, sort = False)
    total_df.to_excel("group_infor.xlsx")








