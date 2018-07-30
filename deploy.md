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

Install some apty things like psycopg2 requirements
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

Run the postgresql database
From the dir above the database git pull (which is likely `cd..`)

# From the docker-compose dir
docker-compose up
# From the readingroom-site-db repo
docker cp . readingroom-site_db_1:/source
docker-compose exec -u postgres db sh -c "pg_restore -d mohinga_db /source"

