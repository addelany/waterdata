## Part 1- Retrieve lake to site mappings ##
Lake to sites mapping is captured in 6 csv files. These 6 tables hold the WB and their metadata, the bounding boxes and their metadata, the sites and their metadata, and the relationships among the WB, the bounding boxes, and the sites. It also captures things like the distance from a site to the edge of a WB, whether the site is inside or outside the WB etc.

The 6 csv files generated in the dataset are: 

1.*Waterbody* - Table that stores details of water body
  This table stores details of the water body from NHD. Attributes of this table are :
  NHD_LAKE_ID - The ID given for the water body in NHD web-site
  AREA(sqkm) - Area of the water body in sq kms
  ELEVATION(feet) - Elevation of the water body in feet
  SHAPE_LENG(decimaldegrees) - Length of the water body shape in decimal degrees
  SHAPE_AREA(sqdecimaldegrees) - Area of the water body shape in square decimal degrees
    
2.*Bounding Box* - Table that stores details about the bounding box - coordinates of each WB read from Shapefiles in NHD. Attributes of   this table are:
  BB_ID - ID for the water body bounding box
  North - Minimum Latitude
  South - Maximum Latitude
  West - Minimum Longitude
  East - Maximum Longitude
  
3.*Sites* - Table that stores details of the sites (obtained from WQP)

4.*W2B* - Relation Table from Water Body to Bounding-Box. This table stores the relation between water body and bounding box.              Attributes of this table are:

  NHD_LAKE_ID - The ID given for the water body in NHD web-site
  GNIS_NAME - Name of the water body as per the Geographic Name Information System
  BB_ID - ID for the water body bounding box

5.*B2S* - Relation Table from Bounding-Box to Sites. This table stores the relation between water body and bounding box. Attributes of   this table are:
  BB_ID - ID for the water body bounding box
  SITE_ID - ID for the site as per the WQP
  
6.*W2S* - Relation Table from Water Body to Sites. This table stores the relation between water body and sites (obtained from WQP).       Attributes of this table are:
  NHD_LAKE_ID - The ID given for the water body in NHD web-site
  GNIS_NAME - Name of the water body as per the Geographic Name Information System
  SITE_ID - ID for the site as per the WQP
  MonitoringLocationName - Name of the site as per WQP
  IsInsideLake - True/False depending on whether the site is inside the water body or not
  DistToShore(m) - Distance of the site to the shore of the water body in meters

### Usage Guide ###

To retrieve site information for water bodies in a state, following steps are to be done.

**1. Obtain the water bodies (WB) data from NHD**
The NHD High Resolution is available on the NHD web-site as a shapefile or file geodatabase. These can be downloaded by state. Here the scripts use them in shapefile format. Download shapefiles for water bodies of the state of interest from here and store locally in the path NHD_High_Resolution/NHD_state. 

**2. Obtain the site csv files from WQP**
The site data can be downloaded from WQP by mentioning the country and state, choosing site type as Lake, Reservoir, Impoundment and data as Site data only. The csv file containing the site data for each state is stored locally in the path WQP_Sites/sites_statecode.csv

**3. Retrieve the dataset (6 tables) for WBs in the state**
In this step run the notebook Lake2Site.ipynb. 


## Part 2- Retrieve raw site data ##
The raw site data is obtained for each state from WQP using a web service call. The raw data is then filtered based on the Lake to site mappings obtained in Part 1.

### Usage guide ###
In this part, run the notebook GETSITEDATA.ipynb.


