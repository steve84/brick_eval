import re
import sqlite3
import pandas as pd

from ddlgenerator.ddlgenerator import Table


csv_files = [
    'exports/colors.csv',
    'exports/elements.csv',
    'exports/inventories.csv',
    'exports/inventory_minifigs.csv',
    'exports/inventory_parts.csv',
    'exports/inventory_sets.csv',
    'exports/minifigs.csv',
    'exports/part_categories.csv',
    'exports/part_relationships.csv',
    'exports/parts.csv',
    'exports/sets.csv',
    'exports/themes.csv'
]

db_file = 'api/rebrickable_new.db'
db = sqlite3.connect(db_file)

for csv_file in csv_files:
    # define table name
    file_name = csv_file.split('exports/')[1]
    table_name = file_name.split('.')[0]
    # read csv
    df = pd.read_csv(csv_file)
    df = df.rename(columns={'year': 'year_of_publication'})

    # fix problem in themes data
    if table_name == 'themes':
        df['parent_id'] = df['parent_id'].where(pd.notnull(df['parent_id']), None)
   
    table_name += '_tmp'
    # create table model
    table = Table(df.to_dict(orient='records'), table_name=table_name, varying_length_text=True)
    # generate sql script
    sql = table.sql('sqlite', inserts=True)
    # avoid multiple insert statements for sqlite
    sql = re.sub(';\nINSERT INTO %s ((.*)) VALUES ' % table_name, ',', sql)
    # write to db
    cursor = db.cursor()
    cursor.executescript(sql)
    db.commit()


db.close()

