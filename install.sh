pip3 install -r requirements.txt
python3 manage.py makemigrations
python3 manage.py migrate
python3 scripts/init_db.py
python3 scripts/insert_diaries.py
python3 scripts/create_accounts.py
