
# coding: utf-8

# In[1]:


import csv
import pandas as pd


# In[4]:
def concatenate(folderpath, state):


    folders = pd.read_csv(folderpath)
# state = "LakeToSiteMappings/MISSOURI"
    folders = folders['File Location']
    count = 0
    b2s_dfs = []
    waterbody_dfs = []
    bbs_dfs = []
    w2b_dfs = []
    sites_dfs =[]
    w2s_dfs = []



    for folder in folders:
        b2s = pd.read_csv(folder + "/tables/b2s.csv")
        if not b2s.empty:
            #count += len(b2s)
            b2s_dfs.append(b2s)

    b2s_final = pd.concat(b2s_dfs)
    b2s_final.to_csv(state + "/B2S.csv", index=False)

    for folder in folders:
        waterbody = pd.read_csv(folder + "/tables/waterbody.csv")
        if not waterbody.empty:
            #count += len(b2s)
            waterbody_dfs.append(waterbody)

    waterbody_final = pd.concat(waterbody_dfs)
    waterbody_final.to_csv(state + "/WATERBODIES.csv", index=False)


    for folder in folders:
        bb = pd.read_csv(folder + "/tables/boundingbox.csv")
        if not bb.empty:
            #count += len(b2s)
            bbs_dfs.append(bb)

    bb_final = pd.concat(bbs_dfs)
    bb_final.to_csv(state + "/BOUNDINGBOX.csv", index=False)


    for folder in folders:
        w2b = pd.read_csv(folder + "/tables/w2b.csv")
        if not w2b.empty:
            #count += len(b2s)
            w2b_dfs.append(w2b)

    w2b_final = pd.concat(w2b_dfs)
    w2b_final.to_csv(state + "/W2B.csv", index=False)


    for folder in folders:
        sites = pd.read_csv(folder + "/tables/sites.csv")
        if not sites.empty:
            #count += len(b2s)
            sites_dfs.append(sites)

    sites_final = pd.concat(sites_dfs)
    sites_final.to_csv(state +  "/SITES.csv", index=False)

    for folder in folders:
        w2s = pd.read_csv(folder + "/tables/w2s.csv")
        if not w2s.empty:
            #count += len(b2s)
            w2s_dfs.append(w2s)

    w2s_final = pd.concat(w2s_dfs)
    w2s_final.to_csv(state + "/W2S.csv", index=False)
