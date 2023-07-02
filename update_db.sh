#!/bin/bash

echo "Get rebrickable ids"
python api/scripts/generate_sql_rebrickable_ids.py

echo "Load temp tables"
python create_tmp_tables.py

echo "Copy sql scripts to docker container"
docker-compose exec db rm -rf /var/lib/postgresql/data/{db_cleanup,db_migration,db_external_data,rebrickable_ids}.sql
docker cp api/db_cleanup.sql brickeval_db_1:/var/lib/postgresql/data && docker cp api/db_migration.sql brickeval_db_1:/var/lib/postgresql/data && docker cp api/db_external_data.sql brickeval_db_1:/var/lib/postgresql/data && docker cp rebrickable_ids.sql brickeval_db_1:/var/lib/postgresql/data

echo "Clean up old db"
docker-compose exec db psql -h localhost -p 5432 -U postgres -d brick_eval -f /var/lib/postgresql/data/db_cleanup.sql --set ON_ERROR_STOP=on

echo "Start api"
python api/app.py

echo "Setup database"
docker-compose exec db psql -h localhost -p 5432 -U postgres -d brick_eval -f /var/lib/postgresql/data/db_migration.sql --set ON_ERROR_STOP=on


cd api/scripts
echo "Check new sets"
python get_prices.py --years $(date +%Y) --max_items 100000
echo "Recheck the available sets (eol = 1, 2 or 3)"
python get_prices.py --eol 1,2,3 --max_days_since 1 --max_items 100000
