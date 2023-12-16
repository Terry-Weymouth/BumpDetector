from six import moves
import geopandas as gpd
from shapely import from_wkt
from shapely.geometry import LineString, mapping
import psycopg2
from psycopg2 import sql
from src.config.get_config import get_database_access
import matplotlib.pyplot as plt


def make_connection():
    try:
        config = get_database_access()
        connection = psycopg2.connect(**config)
        cursor = connection.cursor()
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    return cursor


def line_to_coords(geom):
    m = mapping(geom)
    list_of_tuples = m['coordinates'] # alternative -> geom.coords[:]
    list_of_lists = list(map(list, list_of_tuples))
    return list_of_lists


def main():
    query_str = "select osm_id, ST_AsEWKT(ST_Transform(way,4326)) from planet_osm_line where name='Forestdale Road'"
    query = sql.SQL(query_str)
    cursor = make_connection()
    cursor.execute(query)
    query_results = cursor.fetchall()
    id = []
    geom = []
    for record in query_results:
        id.append(record[0])
        geom.append(from_wkt(record[1].split(';')[1]))
    frame_data = {
        'id': id,
        'geometry': geom
    }
    gdf = gpd.GeoDataFrame(frame_data, crs="EPSG:4326")
    gdf['coords'] = gdf.apply(lambda row: line_to_coords(row.geometry), axis=1)
    gdf.plot()


if __name__ == "__main__":
    main()
