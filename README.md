# Brick Evaluation Database


## Setup DB

Execute create_tmp_tables.py to create temporary tables:
```
python create_tmp_tables.py
```

Get rebrickable ids of minifigs:

```
python api/scripts/generate_sql_rebrickable_ids.py
```

Copy sql files to docker:
```
sudo docker-compose exec db rm -rf /var/lib/postgresql/data/{db_cleanup,db_migration,db_external_data,rebrickable_minifigs}.sql
sudo docker cp api/db_cleanup.sql brickeval_db_1:/var/lib/postgresql/data && sudo docker cp api/db_migration.sql brickeval_db_1:/var/lib/postgresql/data && sudo docker cp api/db_external_data.sql brickeval_db_1:/var/lib/postgresql/data && sudo docker cp api/rebrickable_ids.sql brickeval_db_1:/var/lib/postgresql/data
```

Remove old tables and store some values (Not neccessary if you started with an empty database) 
```
sudo docker-compose exec db psql -h localhost -p 5432 -U postgres -d brick_eval -f /var/lib/postgresql/data/db_cleanup.sql --set ON_ERROR_STOP=on
```

Start REST-API flask application and make a request to create tables:
```
sudo apt-get install libpq-dev
pip install -r requirements.txt
python api/app.py
curl -H "Accept: application/vnd.api+json" localhost:5000/api/sets
```

Setup database:
```
sudo docker-compose exec db psql -h localhost -p 5432 -U postgres -d brick_eval -f /var/lib/postgresql/data/db_migration.sql --set ON_ERROR_STOP=on
```


### Backup

Create:
```
sudo docker-compose exec db bin/bash -c 'pg_dump -U postgres brick_eval > /var/lib/postgresql/data/db.dump'
```

Restore:
```
sudo docker-compose exec db bin/bash -c 'psql -U postgres brick_eval < /var/lib/postgresql/data/db.dump'
```

