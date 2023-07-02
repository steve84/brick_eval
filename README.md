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
sudo docker-compose exec db bin/bash -c 'pg_dump -Fc -U postgres brick_eval > /var/lib/postgresql/data/db.dump'
```

Restore:
```
sudo docker-compose exec db bin/bash -c 'pg_restore -h localhost -p 5432 -U postgres -d brick_eval < /var/lib/postgresql/data/db.dump'
```


### Import new data
Precondition: DB dump of the existing data is available (for rollback scenarios)

Execute update_db.sh to import the newest data sets:
```
update_db.sh
```

When the python server is up then execute the following statement in another terminal window:
```
curl -H "Accept: application/vnd.api+json" localhost:5000/api/sets
```

Then switch back to the iniital terminal and kill the server by pressing CTRL+c (then the script continues). After successful execution do the following checks:
```
# has_unique_part = true, unique_parts not empty, unique_character = true, is_minidoll = false and rebrickable_id not null
select has_unique_part, unique_parts, unique_character, is_minidoll, rebrickable_id from minifigs where lower(name) like 'blade';

# has_stickers = true, rebrickable_id is not null, lego_slug is not null and calc and check date = today
select s.has_stickers, s.rebrickable_id, s.lego_slug, sc.calc_date, sp.check_date from sets s
join scores sc on sc.id = s.score_id
join set_prices sp on sp.set_id = s.id
where set_num = '10316-1'
order by sp.check_date desc;
```

Set eol states back to 1 (only if eol states changed):
```
update sets set eol = '1' where eol in ('2', '3');
```

If everthing looks good, update the eol states based on stonewars and lego websites (in this order).
