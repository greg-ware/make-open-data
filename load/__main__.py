"""
This module runs extraction of data from the sources defined in the sources.yml file.
"""
import yaml
import os
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory


from load.loaders import load_file_from_storage, load_file_to_pg,\
      load_shapefile_from_storage, load_shapefile_to_pg,\
      list_tables_in_pg

STORAGE_TO_PG = "storage_to_pg.yml"

if __name__ == "__main__":
    production = '--production' in sys.argv

    with open(Path(os.path.dirname(__file__)) / STORAGE_TO_PG, "r") as ymlfile:
        storage_to_pg = yaml.safe_load(ymlfile)

    tables_in_pg_list = list_tables_in_pg(storage_to_pg)

    for pg_table, data_infos in storage_to_pg.items():
        
        if pg_table in tables_in_pg_list:
            print(f"Table already exist: {pg_table}")

        elif not production and data_infos.get('production', False):
            print(f"Skipping {pg_table} in non-production mode")

        else:
            print(f"Processing {pg_table}")
            if data_infos['file_format'] in ['csv', 'json']:
                with NamedTemporaryFile(suffix='.csv', delete=True) as tmpfile:
                    tmpfile_csv_path = tmpfile.name
                    
                    print(f"Loading from storage: {pg_table}")
                    load_file_from_storage(tmpfile_csv_path, data_infos)
                    
                    print(f"Loading to PG: {pg_table}")
                    load_file_to_pg(tmpfile_csv_path, pg_table, data_infos)
                    
                    print("***")
            elif  data_infos['file_format'] == 'shape':
                with TemporaryDirectory() as tmpfolder, NamedTemporaryFile(suffix='.zip', delete=True) as tmpzipfile:
                    tmpfolder_name = tmpfolder
                    tmpzip_name = tmpzipfile.name

                    print(f"Loading from storage: {pg_table}")
                    load_shapefile_from_storage(tmpfolder_name, tmpzip_name, data_infos)

                    print(f"Loading to PG: {pg_table}")
                    load_shapefile_to_pg(tmpfolder_name, pg_table, data_infos)