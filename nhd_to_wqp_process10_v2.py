
import shapefile
import pandas as pd
from shapely.geometry import *
from simpledbf import Dbf5
from geopandas import *
import os,glob
import shutil
import pandas as pd
import csv

# To avoid throwing of warnings
pd.options.mode.chained_assignment = None 


def create_6_tables_each_folder(folderpath, wqpsitesfile, shapesAll):
    """
        Forms the data set for the nhd to wqp
        Args:
            folderpath (string): Input String
    """

  

    # Getting all the polygon shape files 
    
    global shapes, all_sites_df, df_sites, df_master_sites_table

    all_sites_df = pd.read_csv(wqpsitesfile)
    df_sites = pd.DataFrame()
    df_master_sites_table = pd.DataFrame()

    print df_sites
    df = pd.read_csv(folderpath+'/lakes.csv')
   
    # Read the info file to get the start and end index for shapes
    df_info = pd.read_csv(folderpath+'/info.csv')
    start = df_info.loc[0]['start_index']
    end =  df_info.loc[0]['end_index'] + 1
    print "start:", start, " end:", end 
    shapes = shapesAll[start:end]
    print len(shapes)
    
    # Create tables data path within the folder
    table_data_path = folderpath+'/tables'
    if os.path.exists(table_data_path): 
        shutil.rmtree(table_data_path)
    os.makedirs(table_data_path)
    print "Start"
    # Create 1. water body dataset
    wb_table = create_wb_table(df)
    wb_table.to_csv(table_data_path+'/waterbody.csv',index=None)
    print "part1"
    # Create 2. bounding-box dataset
    bbox_table = create_bbox_table(df,shapes,start)
    bbox_table.to_csv(table_data_path+'/boundingbox.csv', index=None)
    print "part2" 
    # Create 3. water body to bounding-box (w2b) dataset
    w2b_master_table,w2b_table = create_w2b_table(df,shapes,bbox_table)
    w2b_table.to_csv(table_data_path+'/w2b.csv',index=None)
    print "part3"
    # Create 4. bounding-box to site (b2s) & 5. water body to site (w2s) dataset
    b2s_table,w2s_table = create_b2s_table(shapes,w2b_master_table,start)
    b2s_table.to_csv(table_data_path+'/b2s.csv',index=None)
    print "part4"
    #  5. water body to site dataset(w2s)
    w2s_table.to_csv(table_data_path+'/w2s.csv',index=None)
    print "part5"
    # Create 6. sites dataset
    create_sites_table(b2s_table)
    df_sites.to_csv(table_data_path+'/sites.csv',index=None)
    print "part6"

    


# In[49]:


def create_wb_table(df):
    """
        Creates the dataframe of details of water bodies
        Args:
            df (pandas dataframe): Input dataframe
        Returns:
            df_wb (pandas dataframe)
    """
    df_wb = df[['Permanent_','GNIS_Name','GNIS_ID', 'AreaSqKm', 'Elevation', 'FType', 'FCode', 'FDate',
                           'Shape_Leng', 'Shape_Area']]
    df_wb = df_wb.rename(index=str, columns={"Permanent_":"NHD_LAKE_ID",'AreaSqKm':'AREA(sqkm)',
                                                     'Elevation':'ELEVATION(feet)','Shape_Leng':'SHAPE_LENG(decimaldegrees)',
                                                     'Shape_Area': 'SHAPE_AREA(sqdecimaldegrees)'})
    return df_wb


# In[50]:


def create_bbox_table(df,shapes,start):
    """
        Creates the dataframe of details of bounding box of water body
        Args:
            df (pandas dataframe): Input dataframe, shapes (list): Input list,
            start (str): Input string
        Returns:
            df_bbox (pandas dataframe)
    """
    bbox_columns = ['BB_ID', 'North', 'South', 'West', 'East']
    df_bbox = pd.DataFrame(columns=bbox_columns)
    bbox_data = map(lambda (index,y): ('bb_'+str(index+start),y.bbox[3],y.bbox[1],y.bbox[0],y.bbox[2]), enumerate(shapes))
    df_bbox = pd.DataFrame(bbox_data,columns=bbox_columns,index=None)
    return df_bbox


# In[51]:


def create_w2b_table(df,shapes,df_bbox):
    """
        Creates the dataframe of relation of bounding box to water body
        Args:
            df (pandas dataframe): Input dataframe, 
            shapes (list): Input list,
            df_bbox (pandas dataframe): Input dataframe
        Returns:
            (df_w2b,w2b_table) (pandas dataframe, pandas dataframe)
    """
    # Columns for W2B table
    w2b_columns = ['NHD_LAKE_ID','BB_ID']
    df_w2b = pd.DataFrame(columns=w2b_columns)
    
    # Processes the NHD water body dataframe, picking required columns, indexing the dataframe
    df_v1 = pd.DataFrame(df[['Permanent_','GNIS_Name']])
    df_v1['Index'] = range(len(df_v1))
    df_v1.set_index('Index')
    
    # Processes Bounding Box dataframe, indexing the dataframe
    df_bbox['Index'] = range(len(df_bbox))
    df_bbox.set_index('Index')
    
    # Joins the NHD water body dataframe and Bounding Box dataframe
    df_w2b = df_v1.merge(df_bbox,left_on = 'Index',right_on='Index')
    
    # Projects only required columns and renames the joined dataframe 
    df_w2b = df_w2b[['Permanent_','GNIS_Name','BB_ID']]
    df_w2b = df_w2b.rename(index=str, columns={"Permanent_":"NHD_LAKE_ID"})
    
    # Reorders the columns in the joined dataframe
    w2b_table = df_w2b[w2b_columns]
    
    return (df_w2b,w2b_table)


# In[52]:


def create_b2s_table(shapes,w2b_master_table,start):
    """
        Produce relation between sites, water body and bounding-box in dataframe
        Args:
            shapes (list): Input list,
            w2b_master_table (pandas dataframe): Input dataframe,
            start (int): Input int
        Returns:
            b2s_table,w2s_table (pandas dataframe, pandas dataframe)
    """
    df_master_table = pd.DataFrame()
    
    # Columns for B2S table
    b2s_cols = ['BB_ID', 'SITE_ID']
    
    # Columns for W2S table
    w2s_cols = ['NHD_LAKE_ID', 'GNIS_Name', 'SITE_ID', 'MonitoringLocationName', 'IsInsideLake', 'DistToShore(m)']
    
    # Produce relation between sites, water body and bounding-box
    map(lambda (index,y) : func_2(index,y,start), enumerate(shapes))
    
    # Form details about sites table
    df_master_table = df_master_sites_table.rename(index=str, columns={"MonitoringLocationIdentifier":"SITE_ID",'point_in_polygon':'IsInsideLake',
                                                     'distance':'DistToShore(m)'})
    # Join the W2B and df_master_table to produce relation between sites, water body, bounding box
    
    if df_master_table.empty:
        import numpy as np
        df_master_table[b2s_cols[0]] = np.nan
        df_master_table[b2s_cols[1]] = np.nan
    joined_master_table = df_master_table.merge(w2b_master_table,left_on = 'BB_ID',right_on='BB_ID')
   
    # Form the B2S table and W2S table with columns
    b2s_table = joined_master_table.loc[:,b2s_cols]
    w2s_table = joined_master_table.loc[:,w2s_cols]
    
    # Rename few column names in W2S table
    w2s_table = w2s_table.rename(index=str, columns={"GNIS_Name":"GNIS_LAKE_NAME"})
    
    return b2s_table,w2s_table


# In[75]:


def func_2(index,shape,start):
    """
       Helper function to produce relation between sites, water body and 
       bounding-box in dataframe
        Args:
            index (int): Input int,
            shape (shapely.geometry.polygon.ShapeFile): Input ShapeFile,
            start (int): Input int
    """
    # Get bounding box of the water body
    bbox = shape.bbox
    sites_b=[]
    
    # Global variables
    global df_sites,df_master_sites_table
    global df_sites
    
    # Construct polygon
    polygon = construct_polygon(shape)
    #bbox_list = [str(x) for x in bbox]
    bbox_id = 'bb_'+str(index+start)
    print bbox_id
   
    # Query WQP on boundary box coordinates (WSEN):
    df_sites_bbox = web_service_call(bbox, bbox_id)

    try:

        if not df_sites_bbox.empty:
            print "#sites:", len(df_sites_bbox)
            #print df_sites_bbox

    except Exception,e:
        print e

    # Obtain the data of valid site IDs that lie within the lake polygon
    df_master_sites = validate_site_ids(df_sites_bbox,polygon,bbox_id)
   
    df_master_sites_table = df_master_sites_table.append(df_master_sites,ignore_index=True)

    # Obtain details of site IDs
    df_sites = df_sites.append(df_sites_bbox,ignore_index=True)
   


# In[54]:


# Construct polygon of the water body
def construct_polygon(points):
    """ 
        Constructs polygon of the water body
        Args:
            points (list): Input String
        Returns:
            polygon (shapely.geometry.polygon.Polygon)
    """
    polygon = shape(points)
    return polygon


# In[73]:


# Query WQP with the bounding box co-ordinates
def web_service_call(bbox, bbox_id):
    """
        Retrieves data from water quality portal using web service client
        Args:
            bbox (list): Input list
        Returns:
            result_df (pandas DataFrame)
    """
    
    result_df = all_sites_df[(all_sites_df['LatitudeMeasure'] >= bbox[1]) & (all_sites_df['LatitudeMeasure'] <= bbox[3]) & (all_sites_df['LongitudeMeasure'] >= bbox[0]) & (all_sites_df['LongitudeMeasure'] <= bbox[2])]
    
    return result_df


# In[56]:


def validate_site_ids(df,polygon,bbox_id):
    """
        Checks if the site ids lies at a distance of less than 100 m 
        from the water body polygon and returns dataframe with site and whether it 
        lies inside/outside the polygon, its distance from it
        Args:
            df (pandas dataframe): Input dataframe,
            polygon (shapely.geometry.polygon.Polygon): Input Polygon,
            bbox_id (str): Input String
        Returns:
            df_sites_master_inner (pandas dataframe)
    """
    
    if (df is None) or df.empty:
        return
    
    # Initialize values
    site_ids_list = []
    extra_site_ids_list = []
    
    df['lat_long'] = tuple(zip( df['LongitudeMeasure'], df['LatitudeMeasure']))
    df['lat_long'] = df['lat_long'].apply(lambda lat_long_tuple: Point(lat_long_tuple[0], lat_long_tuple[1]))
    
    
    df['point_in_polygon'] = df['lat_long'].apply(lambda point: is_point_in_polygon(point, polygon))
    df['distance'] = df.apply(lambda row:dist_poly(row['lat_long'],row['point_in_polygon'],polygon),axis=1)
    
    df = df.dropna(subset=['distance'])
   
    df_sites_master_inner = df[['MonitoringLocationIdentifier','MonitoringLocationName','point_in_polygon','distance']]

    df_sites_master_inner['BB_ID'] = bbox_id
    return df_sites_master_inner


# In[57]:


# Checks presence of point inside the polygon
def is_point_in_polygon(point,polygon):
    """
        Checks presence of point inside the polygon
        Args:
            point (list): Input list, polygon (shapely.geometry.polygon.Polygon): Input polygon 
        Returns:
            bool
    """
    if polygon.contains(point):
        return True
    else:
        return False


# In[58]:


def dist_poly(lat_long,is_inside,polygon):
    """
        Returns distance of the point depending on whether it is inside or outside
        the water body polygon
        Args:
            lat_long (tuple): Input tuple
            is_inside (bool): Input bool, 
            polygon (shapely.geometry.polygon.Polygon): Input Polygon
        Returns:
            (float)
    """
    if is_inside:
        return dist_in_poly(lat_long,polygon)
    else:
        return dist_out_poly(polygon,lat_long)
        


# In[59]:


def dist_in_poly(point,polygon):
    """
        Calculates distance of point from the boundary of the polygon
        Args:
            point (shapely.geometry.point.Point): Input Point, 
            polygon (shapely.geometry.polygon.Polygon): Input Polygon
        Returns:
            dist (float)
    """
    new_point = polygon.boundary.interpolate(polygon.boundary.project(point))
   # print new_point
   # print point
    dist = geopy.distance.vincenty((new_point.y,new_point.x),(point.y,point.x)).m
    dist = float("{0:.3f}".format(dist))
    return dist


# In[60]:


# Function to check if all of the points lie at a distance of around 100 m from the boundary
# and calculate the distance

import geopy
from shapely.geometry import Polygon, Point, LinearRing
from geopy.distance import vincenty
def dist_out_poly(poly,point):
    """
        Check if the point lies at a distance of less than 100 m from the boundary
        of the polygon and calculate the distance
        Args:
            poly (shapely.geometry.polygon.Polygon): Input Polygon
            point (shapely.geometry.point.Point): Input Point, 
        Returns:
            distance_points (float)
    """
    pol_ext = poly.boundary
    d = pol_ext.project(point)
    p = pol_ext.interpolate(d)
    #print "point", point
   # print "interpol", p
    distance_points = geopy.distance.vincenty((point.y,point.x),(p.y,p.x)).m
    if distance_points<=100:
        return float("{0:.3f}".format(distance_points))
    else:
        return None
    


# In[61]:


def create_sites_table(b2s_table):
    """
        Form sites table
        Args:
            b2s_table (pandas dataframe): Input pandas dataframe
    """
    global df_sites
    # Getting the unique site values for the dataframe
    site_vals = set(b2s_table['SITE_ID'].values.tolist())
    print site_vals
    # list of column names needed in sites dataframe
    list_cols = ['OrganizationIdentifier','OrganizationFormalName','SITE_ID','MonitoringLocationName','MonitoringLocationTypeName',
     'MonitoringLocationDescriptionText','HUCEightDigitCode','DrainageAreaMeasure/MeasureValue','DrainageAreaMeasure/MeasureUnitCode',
     'ContributingDrainageAreaMeasure/MeasureValue','ContributingDrainageAreaMeasure/MeasureUnitCode',
     'LatitudeMeasure','LongitudeMeasure','SourceMapScaleNumeric','HorizontalAccuracyMeasure/MeasureValue',
     'HorizontalAccuracyMeasure/MeasureUnitCode','HorizontalCollectionMethodName',
     'HorizontalCoordinateReferenceSystemDatumName','VerticalMeasure/MeasureValue','VerticalMeasure/MeasureUnitCode',
     'VerticalAccuracyMeasure/MeasureValue','VerticalAccuracyMeasure/MeasureUnitCode',
     'VerticalCollectionMethodName','VerticalCoordinateReferenceSystemDatumName',
     'CountryCode','StateCode','CountyCode','AquiferName','FormationTypeText','AquiferTypeName','ConstructionDateText',
     'WellDepthMeasure/MeasureValue','WellDepthMeasure/MeasureUnitCode','WellHoleDepthMeasure/MeasureValue',
     'WellHoleDepthMeasure/MeasureUnitCode','ProviderName']
    
    # Renaming and reordering the column names
    if 'SITE_ID' in df_sites:
        print df_sites['SITE_ID']
    df_sites = df_sites.rename(index=str, columns={"MonitoringLocationIdentifier":"SITE_ID"})
    print len(df_sites)
    print df_sites['SITE_ID']
    df_sites = df_sites[df_sites['SITE_ID'].isin(site_vals)]
    
    # Putting SITE_ID in the beginning of the dataframe
    a, b = list_cols.index('SITE_ID'), list_cols.index('OrganizationIdentifier')
    list_cols[b], list_cols[a] = list_cols[a], list_cols[b]
    
    df_sites = df_sites.loc[:,list_cols]
    df_sites.drop(df_sites.columns[[34,35]], axis=1, inplace=True)


