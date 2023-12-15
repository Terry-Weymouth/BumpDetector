import geopandas as gpd
import psycopg2
from src.config.get_config import get_database_access
from examples.sqlalchemy_config import get_sqlalchemy_engine
import matplotlib.pyplot as plt


def make_connection():
    engine = None
    try:
        engine = get_sqlalchemy_engine()
    except (Exception) as error:
        print("Error while connecting to PostgreSQL", error)
    return engine


def main():
    engine = make_connection()
    if engine is None:
        return
    # Query OSM highway data from PostgreSQL database
    query = """
        SELECT osm_id, name, highway, way
        FROM planet_osm_roads
        WHERE highway IS NOT NULL;
    """
    gdf = gpd.read_postgis(query, engine, geom_col='way')

    # Plot the map
    fig, ax = plt.subplots(figsize=(10, 10))
    gdf.plot(ax=ax, column='highway', legend=True, legend_kwds={'loc': 'upper left'}, markersize=1)
    plt.title("OSM Highway Data")

    # Save the plot as an image (e.g., PNG format)
    # output_image = "output_map.png"
    # plt.savefig(output_image)

    # Close the database connection
    engine.dispose(True)

    # Show the plot (optional)
    plt.show()


if __name__ == "__main__":
    main()
