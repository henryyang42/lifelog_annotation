pip3 install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python scripts/init_db.py
python scripts/insert_diaries.py
python scripts/insert_tweets.py
python scripts/create_accounts.py
