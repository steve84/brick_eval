import math
import re
import sqlite3
import pandas as pd

from itertools import combinations
from ddlgenerator.ddlgenerator import Table
from sqlalchemy import create_engine

from extended_models import Score, Property


def findKeyCandidate(df):
    for i in range(len(df.columns)):
        for j in combinations(list(df.columns), i + 1):
            if len(df) == len(df[list(j)].drop_duplicates()):
                return list(j)
    return list()


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

db_file = 'rebrickable.db'
db = sqlite3.connect(db_file)

for csv_file in csv_files:
    # define table name
    file_name = csv_file.split('exports/')[1]
    table_name = file_name.split('.')[0]
    # read csv
    df = pd.read_csv(csv_file)
    df = df.rename(columns={'year': 'year_of_publication'})

    key_candidate = findKeyCandidate(df)

    # fix problem in themes data
    if table_name == 'themes':
        df['parent_id'] = df['parent_id'].where(pd.notnull(df['parent_id']), None)
    
    # create table model
    table = Table(df.to_dict(orient='records'), table_name=table_name, varying_length_text=True)
    # generate sql script
    sql = table.sql('sqlite', inserts=True)
    # define primary key
    pk = 'PRIMARY KEY(%s)' % ','.join(list(map(lambda x: '"%s"' % x, key_candidate)))
    sql = re.sub('\n\);', ',\n%s\n);' % pk, sql)
    # avoid multiple insert statements for sqlite
    sql = re.sub(';\nINSERT INTO %s ((.*)) VALUES ' % table_name, ',', sql)
    # write to db
    cursor = db.cursor()
    cursor.executescript(sql)
    db.commit()


db.close()

conn_string = 'sqlite:///%s' % db_file
engine = create_engine(conn_string)

Score.__table__.create(engine)
Property.__table__.create(engine)

sql = ''
sql += 'CREATE INDEX "inv_index" ON "inventories" ("set_num", "version");\n'
sql += 'CREATE INDEX "inv_parts_index" ON "inventory_parts" ("part_num", "color_id", "is_spare");\n'
sql += 'CREATE INDEX "inv_parts_index_2" ON "inventory_parts" ("inventory_id", "part_num", "color_id");\n'
sql += 'CREATE INDEX "inv_parts_index_3" ON "inventory_parts" ("inventory_id");\n'
sql += 'CREATE INDEX "inv_minifigs_index" ON "inventory_minifigs" ("fig_num");\n'
sql += 'CREATE INDEX "scores_index" ON "scores" ("inventory_number");\n'

db = sqlite3.connect(db_file)
cursor = db.cursor()
cursor.executescript(sql)
db.commit()
db.close()