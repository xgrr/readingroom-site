## Set up Host

Set up a digitalocean host and SSH into it
ssh -A root@<your-ip-address>


Install docker - this is for the "easy_install" method, not so secure

```
curl -fsSL get.docker.com -o get-docker.sh
sh get-docker.sh
```

Pull the repo and the database dump
```
git clone git@github.com:xgrr/readingroom-site.git
git clone git@github.com:xgrr/readingroom-site-db.git
```

Install some apty things like psycopg2 requirements|
```
apt install -y \
  python-pip \
  python3-venv \
  libmysqlclient-dev \  
  postgresql-client-common
```

```
apt install -y python-pip python3-venv
python3 -m venv env
source env/bin/activate
pip install --upgrade pip
pip install wheel
pip install -r requirements.txt
pip install flake8
```
Copy over the database dump - it's currently called "xanana.psql"


Run the postgresql database
From the dir above the database git pull (which is likely `cd..`)
```
docker run --name readingroom_db -p 32769:5432 -v`pwd`/readingroom-site-db:/source kartoza/postgis:10.0-2.4
```
Restore the postgresql database
```
docker exec -u postgres readingroom_db bash -c "pg_restore /source"
```
