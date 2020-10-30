import importlib
import inspect
import math
import pandas as pd
import sqlite3
from operator import itemgetter
from sqlalchemy import create_engine
from sqlalchemy.inspection import inspect as sqla_inspect


def getSqlValue(colDef, value):
    if colDef.type.python_type == str:
        return '"%s"' % value
    elif colDef.type.python_type == bool:
        return '1' if value else '0'
    else:
        return str('NULL' if str(value) == 'nan' else str(value))


def adjustListToSqlTypes(valueList, cols):
    res_list = list()
    for i, row in enumerate(valueList):
        row_list = list()
        for j, col in enumerate(row):
            row_list.append(getSqlValue(cols[j], col))

        res_list.append(row_list)
    return res_list

db_file = 'rebrickable.db'
conn_string = 'sqlite:///%s' % db_file

module = importlib.import_module('models')
modules = list(filter(lambda x: hasattr(x, '__tablename__'), map(lambda x: x[1], inspect.getmembers(module, inspect.isclass))))

engine = create_engine(conn_string)

for m in modules:
    tablename = m.__tablename__

    df_new = pd.read_csv('exports/%s.csv' % tablename)
    df_new = df_new.rename(columns={'year': 'year_of_publication'})
    
    df_old = pd.read_sql_table(tablename, conn_string)

    col_defs = [col for col in sqla_inspect(m).columns]
    pk_defs = [key for key in sqla_inspect(m).primary_key]
    cols = [col.name for col in col_defs]
    pk = [key.name for key in pk_defs]
    indices_of_pk = [cols.index(p) for p in pk if cols.index(p) > -1]
    bool_cols = map(lambda x: x.name, filter(lambda x: x.type.python_type == bool, col_defs))

    for bool_col in bool_cols:
        df_new[bool_col] = df_new[bool_col].map(lambda x: True if x == 't' else False)

    dfm = df_new.merge(df_old, on=pk, how='left', indicator=True, suffixes=('', '_y'))
    df_inserts = dfm[dfm['_merge'] == 'left_only']
    df_inserts_indices = df_inserts.index

    df_inserts[cols].to_sql(tablename, con=engine, index=False, if_exists='append', method='multi')

    dfm = df_old.merge(df_new, on=pk, how='left', indicator=True, suffixes=('', '_y'))
    df_deletions = dfm[dfm['_merge'] == 'left_only']

    sql_stmts = ''
    for row in adjustListToSqlTypes(df_deletions[cols].values.tolist(), col_defs):
        if len(pk) == 1:
            pk_values =  [itemgetter(*indices_of_pk)(row)]
        else:
            pk_values = itemgetter(*indices_of_pk)(row)
        sql_stmts += 'DELETE FROM %s WHERE (%s) IN ((%s));\n' % (tablename, ','.join(pk), ','.join(pk_values))


    dfm = df_new.merge(df_old, on=cols, how='left', indicator=True, suffixes=('', '_y'))
    df_updates = dfm[dfm['_merge'] == 'left_only']
    df_updates = df_updates.drop(index=df_inserts_indices)

    for row in adjustListToSqlTypes(df_updates[cols].values.tolist(), col_defs):
        import pdb;pdb.set_trace()
        if len(pk) == 1:
            pk_values =  [itemgetter(*indices_of_pk)(row)]
        else:
            pk_values = itemgetter(*indices_of_pk)(row)
        sql_stmts += 'UPDATE %s SET (%s) = (%s) WHERE (%s) IN ((%s));\n' % (tablename, ','.join(cols), ','.join(row), ','.join(pk), ','.join(pk_values))
    
    if sql_stmts != '':
        import pdb;pdb.set_trace()
        # write to db
        db = sqlite3.connect(db_file)
        cursor = db.cursor()
        cursor.executescript(sql_stmts)
        db.commit()
        db.close()
    
    df_actual = pd.read_sql_table(tablename, conn_string)
    df_actual = df_actual.sort_values(by=cols).reset_index(drop=True)
    df_new = df_new.sort_values(by=cols).reset_index(drop=True)
    if not df_actual.eq(df_new).any(axis=1).any():
        print('Table %s was not correctly updated!')

