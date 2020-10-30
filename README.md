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
