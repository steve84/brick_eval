import gzip
import os
import re
import sqlite3
import shutil
import subprocess
import pandas as pd

from datetime import datetime

from ddlgenerator.ddlgenerator import Table


export_dir = 'test_exports/'
old_export_dir = 'test_exports_old/'

if not os.path.exists(export_dir) or not os.path.isdir(export_dir):
    os.mkdir(export_dir)

if not os.path.exists(old_export_dir) or not os.path.isdir(old_export_dir):
    os.mkdir(old_export_dir)


for f in os.listdir(export_dir):
    src_full_path = '%s%s' % (export_dir, f)
    trgt_full_path = '%s%s' % (old_export_dir, f)
    src_creation_date = datetime.utcfromtimestamp(
        os.path.getctime(src_full_path)
    )
    src_creation_date_str = str(src_creation_date.date())
    src_creation_date_str = src_creation_date_str.replace('-', '_')
    trgt_name = '%s.%s' % (trgt_full_path, src_creation_date_str)
    shutil.copy2(src_full_path, trgt_name)
    os.remove(src_full_path)

subprocess.run([
    'curl',
    'https://rebrickable.com/media/downloads/{colors,elements,inventories,inventory_minifigs,inventory_parts,inventory_sets,minifigs,part_categories,part_relationships,parts,sets,themes}.csv.gz',
    '-o',
    '%s#1.csv.gz' % export_dir])


gz_files = [
    '%s%s' % (export_dir, gz_file) for gz_file in os.listdir(export_dir)
]

db_file = 'api/rebrickable_new.db'
db = sqlite3.connect(db_file)

for gz_file in gz_files:
    # define table name
    file_name = gz_file.split('exports/')[1]
    table_name = file_name.split('.')[0]
    # read csv
    df = pd.read_csv(gzip.open(gz_file))
    df = df.rename(columns={'year': 'year_of_publication'})

    # fix problem in themes data
    if table_name == 'themes':
        df['parent_id'] = df['parent_id'].where(
            pd.notnull(df['parent_id']),
            None)

    table_name += '_tmp'
    print("Create table '{}'".format(table_name))
    # create table model
    table = Table(
        df.to_dict(orient='records'),
        table_name=table_name,
        varying_length_text=True)
    # generate sql script
    sql = table.sql('sqlite', inserts=True)
    # avoid multiple insert statements for sqlite
    sql = re.sub(';\nINSERT INTO %s ((.*)) VALUES ' % table_name, ',', sql)
    # write to db
    cursor = db.cursor()
    cursor.executescript(sql)
    db.commit()


db.close()
