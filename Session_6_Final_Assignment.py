# ----------------------------------------------------------------------------------
# Yining (Johnny) Wang
# Student ID: 1001553311
# Assignment 6 (Final Assignment) Submission
#-----------------------------------------------------------------------------------

'''
The project uses arcGIS API to extract geographic information from China and Canada area.
The number of COVID-19 death, confirmed cases and vaccinated information are extracted and 
loaded on the map indicating using bubble chart. 
'''

# Import libraries
import pandas as pd
from arcgis.gis import GIS
from arcgis.features import FeatureLayer
from arcgis.mapping import WebMap

# Import credential
from credential import Arcgis_id

# Create functions for connection
def arcGIS_connection():
    gis_object = GIS("https://utoronto.maps.arcgis.com", client_id = Arcgis_id)
    return gis_object 

# Set up connection 
gis = arcGIS_connection()

# Search Covid-19 page for the Year 2019
item = gis.content.search("owner:CSSE_covid19", outside_org=True)
src_url = "https://services1.arcgis.com/0MSEUqKaxRlEPj5g/arcgis/rest/services/Coronavirus_2019_nCoV_Cases/FeatureServer/1"
fl = FeatureLayer(url=src_url)

''' For map in China '''
# Get data for China
data_China = fl.query(where="Country_Region='China'")

# For a dataframe and remove NaN row & remove Hong Kong and Maucau which are not provinces
covid_China_df = data_China.sdf
covid_China_df = covid_China_df[["Province_State", "Lat", "Long_", "Confirmed", "Recovered", "Deaths", "Active", "SHAPE"]]
covid_China_df = covid_China_df.sort_values(["Province_State"], ascending = True).dropna(how = 'any', axis = 0)
covid_China_df = covid_China_df.drop(covid_China_df[covid_China_df["Province_State"].isin(["Hong Kong","Macau"])].index, axis = 0).reset_index(drop = True)

# Find the province mapping of China in Year 2020 and locate the web id/find correct contents
china_province = gis.content.search(query="title:China Province Boundaries 2020", outside_org=True)
china_map_id = china_province[4].id
provinces_info = gis.content.get(china_map_id)

# Generate province dataframe
province_flayer = provinces_info.layers[1]
province_df = province_flayer.query(as_df = True)
province_df = province_df.sort_values(["NAME"], ascending = True).reset_index(drop = True)

# Sync the province names for the two dataframes and simplify dataframe
clean_name = []
for name in province_df["NAME"].str.split(" "):
    clean_name.append(name[0])
province_df["NAME"] = clean_name
province_df = province_df[["NAME", "AREA", "Shape__Area", "Shape__Length", "SHAPE"]]

# ***special operation: Change the name of the special province "Inner Mongolia"
province_df.iloc[province_df[province_df["NAME"] == "Inner"].index, 0] = "Inner Mongolia"

# Join two tables 
province_final_df = province_df.merge(covid_China_df, how = "inner", left_on = province_df["NAME"], right_on = covid_China_df["Province_State"])

# Rename one of the Shape name
province_final_df = province_final_df.rename(mapper = {"index" : "Province", "SHAPE_x" : "SHAPE"}, axis = 1)

# Plot confimed cases and death cases in China
map_china = GIS().map("China")
map_china.clear_graphics()
province_final_df.spatial.plot(kind = 'map',
                               map_widget = map_china,
                              renderer_type = 'c',
                              methdo = 'esriClassifyNaturalBreaks',
                              class_count = 5,
                              col = 'Confirmed',
                              cmap = 'inferno',
                              alpha = 0.7)

# Add layer for death cases
map_china.add_layer(fl, {"type" : "FeatureLayer",
                            "renderer" : "ClassedSizeRenderer",
                            "field_name" : "Deaths"})
map_china.legend = True

''' For map in Canada '''
# Plot Canada map
# Search for Covid-19 page
item = gis.content.search("title:Provinces and Territories of Canada", outside_org=True)

# Select the map needed
canada_province_id = item[0].id

# Extract province dataframe and Simplify dataframe for Canada Province
canada_province_info = gis.content.get(canada_province_id)
province_layer_canada = canada_province_info.layers[0]
province_layer_canada_df = province_layer_canada.query(as_df = True)
province_layer_canada_df = province_layer_canada_df[["Name_EN", "Shape_Leng", "Shape_Area", "SHAPE"]]

# Get covid data for Canada
data_Canada = fl.query(where="Country_Region='Canada'")
covid_Canada_df = data_Canada.sdf
covid_Canada_df = covid_Canada_df[["Province_State", "Lat", "Long_", "Confirmed", "Recovered", "Deaths", "Active"]]

# Merge two dataframe together
Canada_final_df = province_layer_canada_df.merge(covid_Canada_df, how = "left", left_on = province_layer_canada_df["Name_EN"], right_on = covid_Canada_df["Province_State"])

# Plot confimed cases and death cases in Canada
map_canada = GIS().map("Canada")
map_canada.clear_graphics()
Canada_final_df.spatial.plot(kind = 'map',
                               map_widget = map_canada,
                              renderer_type = 'c',
                              methdo = 'esriClassifyNaturalBreaks',
                              class_count = 5,
                              col = 'Confirmed',
                              cmap = 'inferno',
                              alpha = 0.7)

# Add layer for death cases
map_canada.add_layer(fl, {"type" : "FeatureLayer",
                            "renderer" : "ClassedSizeRenderer",
                            "field_name" : "Deaths"})
map_canada.legend = True
