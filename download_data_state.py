
# coding: utf-8

# In[1]:


import os
import csv
import nhd_to_wqp_process10_v2
import pandas as pd
import shapefile
from shapely.geometry import *
from simpledbf import Dbf5


# In[2]:


# def done_chunks(list_done,state):
#     """
#         Writes into file the chunks that are done processing
#         Args:
#             list_done (list): Input list,
#             state (str): Input String
#     """
#     file = open('done_'+state+'.txt','a+') 
#     file.write('\n--------------------------------\n')
#     file.write('\n'.join(list_done))
#     file.close()


# In[3]:


def download_data(count, endCountExclusive, state_chunks_path, state, wqpsites):
    """
        Forms the NHD-WQP data for the state in the given local folder path
        Args:
            directory (str): Input String,
            state_chunks_path (str): Input String
    """

    from datetime import datetime
    startTime = datetime.now()
    global shapesAll
    shapesAll = getAllShapes("NHD_High_Resolution/NHD_"+ state +"/Shape/")
    print ">>>>>>"
    print len(shapesAll)
    print "<<<<<<"
    # Read the file containing the list of the data paths to the chunks for the state 
    df_Commands = pd.read_csv(state_chunks_path,index_col=False)
    
    # Number of chunks for the state
    len_in_c = endCountExclusive
    # Populate the data-set for each of the chunk 
    while(count < len_in_c):
        curr_df = list(df_Commands.loc[count:count+4, 'File Location'])
        count+=5
      
        final_func(curr_df, wqpsites, shapesAll)
        print "Time taken: "+ str(datetime.now() - startTime)
        print "The number of files done are "+ str(count)

        # Write to done file
        #done_chunks(curr_df, "NE")
    
    


# In[4]:


def final_func(folderpath_list, wqpsites, shapesAll):
    """
        Forms the data set for the nhd to wqp
        Args:
            folderpath_list (list): Input list
    """
    i = 0
    for folderpath in folderpath_list:
#         if i <= 1:
#             i +=1
#             continue
        nhd_to_wqp_process10_v2.create_6_tables_each_folder(folderpath, wqpsites, shapesAll)
        i += 1
        
        
#     from multiprocessing import Pool
#     pool = Pool(processes=20)
#     pool.map(nhd_to_wqp_process10.create_6_tables_each_folder,folderpath_list)
        
        


# In[5]:


def getAllShapes(data_path):
    sf = shapefile.Reader(data_path+"NHDWaterbody.shx")
    shapesAll = sf.shapes()
    return shapesAll




