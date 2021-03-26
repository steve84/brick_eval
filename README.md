# Brick Evaluation Database


Setup DB

python3 create_db.py
sqlacodegen sqlite:///rebrickable.db > models.py
Create views v_inventory_minifig_parts and v_inventory_parts from queries.txt
Cleanup statements from queries.txt

Python dependencies
ddlgenerator
python3
pandas
sqlacodegen
sqlite3
sqlalchemy

sudo docker-compose exec db pg_dump -U postgres brick_eval > db.dump
sudo docker-compose exec db bin/bash -c 'pg_dump -U postgres brick_eval > /var/lib/postgresql/data/db.dump'
sudo docker-compose exec db bin/bash -c 'psql -U postgres brick_eval_2 < /var/lib/postgresql/data/db.dump'


sudo docker cp api/db_migration.sql brickeval_db_1:/var/lib/postgresql/data
sudo docker-compose exec db psql -h localhost -p 5432 -U postgres -d brick_eval_2 -f /var/lib/postgresql/data/db_migration.sql --set ON_ERROR_STOP=on
