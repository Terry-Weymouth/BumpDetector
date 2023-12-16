"""
Main function to remove, then rebuild, the track tables using the track data files.
Data files are *_Cleaned.txt in the top level directory ./data
Database table and index SQL statements are in ./src/sql/init_track_tables.sql
    Note: the above will also drop, then create the track-related tables
In addition to loading the data this program also
    sets the nearest road ID and distance in the database
TODO: Processing should start from Raw Data; bypassed for now to concentrate database
"""


def main():
    print("here")


if __name__ == "__main__":
    main()
