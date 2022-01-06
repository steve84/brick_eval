# Brick Evaluation Database


## Setup DB

Execute create_tmp_tables.py to create temporary tables:
```
python create_tmp_tables.py
```

Copy sql files to docker:
```
sudo docker-compose exec db rm -rf /var/lib/postgresql/data/db_cleanup.sql
sudo docker-compose exec db rm -rf /var/lib/postgresql/data/db_migration.sql
sudo docker cp api/db_cleanup.sql brickeval_db_1:/var/lib/postgresql/data
sudo docker cp api/db_migration.sql brickeval_db_1:/var/lib/postgresql/data
```

Remove old tables and store some values:
```
sudo docker-compose exec db psql -h localhost -p 5432 -U postgres -d brick_eval -f /var/lib/postgresql/data/db_cleanup.sql --set ON_ERROR_STOP=on
```

Start REST-API flask application and make a request to create tables:
```
sudo apt-get install libpq-dev
pip install -r requirements.txt
python api/app.py
curl localhost:5000/api/sets
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



## Monkey Patch
flask_restless/search.py

```
if '__' in field_name:
    field_name, field_name_in_relation = \
        field_name.split('__')
    relation = getattr(model, field_name)
    relation_model = relation.mapper.class_
    field = getattr(relation_model, field_name_in_relation)
    direction = getattr(field, val.direction)
    -------------------
    query = query.join(relation)
    -------------------
    query = query.order_by(direction())
```