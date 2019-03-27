
# coding: utf-8

# In[1]:


import shapefile
import pandas as pd
from shapely.geometry import *
from simpledbf import Dbf5
import csv
import os,glob
import shutil


# In[6]:


def partition_df_i(i,state, directory_wb, df_wb, data_path):
    """
        Partitions the water bodies dataframe into ith chunk for the given state
        and stores the dbf path, shape path, start and end indices in file info.csv
        Args:
            i (str): Input String ,state (str): Input String 
    """
    
    # Size of the chunk
    n=200
    
    # Path to store the chunk i
    directory_batch = directory_wb+'/'+state+'_Lakes_'+str(i/n)
    print(directory_batch)
    # Form the ith chunk and store it in folder path locally
    if os.path.exists(directory_batch): 
        shutil.rmtree(directory_batch)
    os.makedirs(directory_batch)
    df_wb[i:i + n].to_csv(directory_batch+'/lakes.csv', encoding = 'utf-8')
    
    # Store the path of the dbf file, path of shape file, start and end indices
    # of the partitioned chunk in file info.csv
    cols = ['dbf_path','shape_path','start_index','end_index']
    df=pd.DataFrame(columns=cols)
    if i+n > len(df_wb):
        end_index = len(df_wb)-1
    else:
        end_index = i+n-1
    df.loc[len(df)] = [data_path+'NHDWaterbody.dbf',data_path+'NHDWaterbody.shx',i,end_index]
    df.to_csv(directory_batch+'/info.csv')
    


# In[7]:


def partition_df(directory_wb,state):
    """
        Partitions the water bodies dataframe into chunks of specified size
        Args:
            directory_wb (str): Input String ,state (str): Input String 
    """
    global df_wb, data_path;
    # Local data path to the shape files 
    data_path = "NHD_High_Resolution/NHD_"+state+"/Shape/"
    # Reading in the .dbf file and converting to pandas dataframe
    dbf = Dbf5(data_path+"NHDWaterbody.dbf")
    
    df_wb = dbf.to_dataframe()
    
    # Creating directory to store partitioned data
    if os.path.exists(directory_wb): 
        shutil.rmtree(directory_wb)
    os.makedirs(directory_wb)
    
    [partition_df_i(i, state, directory_wb, df_wb, data_path) for i in range(0,len(df_wb),200)]


# In[8]:


def write_chunks_path(partitionname, csvfile, state, no_of_chunks):
    with open(csvfile, mode='wb') as csv_file:
        fieldnames = ['File Location']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        count = 0
        base = partitionname +'/' + state + "_Lakes_"

        for i in range(0, no_of_chunks):
            print base+str(count)
            writer.writerow({'File Location': base+str(count)})
            count +=1




# partition_df("partitions", "Missouri")


# # In[11]:


# write_chunks_path('MO_chunks_paths.csv', 'Missouri', 1000)

