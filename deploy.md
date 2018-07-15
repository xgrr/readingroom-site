Pull the repo

Install some apty things like psycopg2 requirements

apt-get install -y python3-venv
python3 -m venv env
source env/bin/activate
pip install --upgrade pip
pip install wheel
pip install -r requirements.txt
pip install flake8

Run the postgresql database
docker run --name readingroom_db -p 32769:5432 -v `pwd`/xanana.psql:/source.psql kartoza/postgis:10.0-2.4

Restore the postgresql database
docker exec -u postgres readingroom_db bash -c "psql < /source.psql"