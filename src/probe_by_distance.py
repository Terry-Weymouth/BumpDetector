import psycopg2
from psycopg2 import sql

connection = None
cursor = None
max_d = 0;

def make_connection():
    global connection, cursor
    connection = psycopg2.connect(user="weymouth",
                                  password="",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="Detroit")
    cursor = connection.cursor()


def probe(id):
    global max_d
    query_str = "select track.id, osm.osm_id, osm.name, osm.highway, "\
            + "ST_Distance(ST_Transform(osm.way,4326),track.long_lat_original) "\
            + "from bicycle_data as track, planet_osm_line as osm "\
            + "where track.id={} and "\
            + "ST_Distance(ST_Transform(osm.way,4326),track.long_lat_original) < 30.0 "\
            + "order by st_distance limit 1;"
    query_str = query_str.format(id)
    query = sql.SQL(query_str)
    cursor.execute(query)
    results = cursor.fetchone()
    if results:
        print(results)
        d = results[4]
        if d > max_d:
            max_d = d
    else:
        print("Missing id =", id)

def main():
    global connection, cursor, max_d
    try:
        make_connection()
        for id in range(1, 2956):
            probe(id)
        print(max_d)
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
        #closing database connection.
        if connection:
            cursor.close()
            connection.close()


if __name__ == "__main__":
    main()
