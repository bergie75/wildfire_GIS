from shapely import Point
import geopandas as gpd
from pathlib import Path
import matplotlib.pyplot as plt
import webbrowser as web
from math import pi, sqrt

# hard-coded global address, could improve this?
home_directory = "C:/Users/physi/OneDrive/Desktop/Data Sources/GIS_projects/"


def create_modified_shapefile(sub_folder="Wildfires_1878_2019_Polygon_Data/Shapefile/",
                               filestring="US_Wildfires_1878_2019.shp",
                              outfile="postprocessed_fire_data.shp"):
    # define file path
    path_to_data = home_directory + sub_folder + filestring
    fire_data = gpd.read_file(path_to_data, rows=1000)

    # use isoperimetric inequality to quantify how close fire is to circular
    leng_factor = fire_data["Shape_Leng"] ** 2
    fire_data["Regularity"] = 4 * pi * fire_data["Shape_Area"] / leng_factor

    # create column for buffer radius, to visualize how close to a circle
    fire_data["Buffer_Rad"] = fire_data["Shape_Area"].apply(lambda x: sqrt(x / pi))

    # find centroids and buffer circles around centroids
    fire_data["Centroid"] = fire_data.centroid
    fire_data["Buffer_Circle"] = fire_data.set_geometry("Centroid").buffer(fire_data["Buffer_Rad"])

    # saves results of analysis
    fire_data["Centroid"] = fire_data.apply(lambda x: x["Centroid"].wkt, axis=1)
    fire_data["Buffer_Circle"] = fire_data.apply(lambda x: x["Buffer_Circle"].wkt, axis=1)
    fire_data.to_file(home_directory + outfile, driver='ESRI Shapefile')
    print(fire_data.head(2))

def fire_irregularity_explorer(year=2014, sub_folder="Wildfires_1878_2019_Polygon_Data/Shapefile/",
                               filestring="US_Wildfires_1878_2019.shp"):
    # define file path
    path_to_data = home_directory + sub_folder + filestring

    # geopandas reads in data, data is in a coordinate system with units appropriate for lengths/areas/centroids
    fire_data = gpd.read_file(path_to_data)
    indices = fire_data["FireYear"] == year
    fire_data = fire_data[indices]
    print(f"Fires reported: {len(fire_data)}")

    # use isoperimetric inequality to quantify how close fire is to circular
    leng_factor = fire_data["Shape_Leng"] ** 2
    fire_data["Regularity"] = 4 * pi * fire_data["Shape_Area"] / leng_factor

    # create column for buffer radius, to visualize how close to a circle
    fire_data["Buffer_Rad"] = fire_data["Shape_Area"].apply(lambda x: sqrt(x / pi))

    # find centroids and buffer circles around centroids
    fire_data["Centroid"] = fire_data.centroid
    fire_data["Buffer_Circle"] = fire_data.set_geometry("Centroid").buffer(fire_data["Buffer_Rad"])

    # save map as interactive html
    m = fire_data.explore()
    m = fire_data.set_geometry("Buffer_Circle").explore(m=m, color="red")  # draw buffers on existing map
    outfp = home_directory + f"fire_map_{year}.html"
    m.save(outfp)

    # open file for exploration
    web.open(outfp)

if __name__ == "__main__":
    import argparse as ag

    parser = ag.ArgumentParser()
    # command line program controls
    parser.add_argument("-p", "--program", dest="selected_function",
                        default="create_modified_shapefile", help="select program to run")
    parser.add_argument("-y", "--year", dest="year",
                        default=2014,
                        help="year of fires to examine")
    parser.add_argument("-sf", "--sub_folder_fire", dest="sub_folder_fire", default="Wildfires_1878_2019_Polygon_Data/Shapefile/",
                        help="subdirectory that houses the shapefile with fire data")
    parser.add_argument("-f", "--file", dest="file", default="US_Wildfires_1878_2019.shp",
                        help="final folder and shapefile")

    # read command line and run analysis board
    args = parser.parse_args()
    if args.selected_function == "create_modified_shapefile":
        create_modified_shapefile(sub_folder=args.sub_folder_fire, filestring=args.file)
    else:
        fire_irregularity_explorer(year=int(args.year), sub_folder=args.sub_folder_fire, filestring=args.file)