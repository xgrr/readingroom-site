## Set up Host

Set up a digitalocean host and SSH into it
ssh -A root@<your-ip-address>

## Add user
adduser <username> (josh)


Install docker - this is for the "easy_install" method, not so secure

```
curl -fsSL get.docker.com -o get-docker.sh
sh get-docker.sh
```

Pull the repo
```
git clone git@github.com:xgrr/readingroom-site.git
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



# Run with uwsgi

Make a directory for the socket
```
sudo mkdir /run/django/ && sudo chown josh:josh /run/django/
```

Run project with that socket file
(env) josh@josh-ThinkPad-T420:~/github/xgrr/readingroom-site$
```
uwsgi --socket /run/django/8001.sock --module xanana.wsgi
```

## Change it to an .ini file

