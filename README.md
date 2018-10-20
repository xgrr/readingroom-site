# readingroom-site
Reading room website

## Initial Setup

Based on a fresh install of Ubuntu 18.04

### OS Prep

```
apt update
apt install -y nginx gcc python3-venv git libpq-dev python3-dev postgis
```

### Pythonic Stuff
```
python3 -m venv env
source env/bin/activate && pip install wheel
git clone https://github.com/xgrr/readingroom-site.git
cd readingroom-site
pip install -r requirements.txt
```
### Database

`./readingroom-site/xanana/settings/local.py` content
```
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "xgrr_site",
        "USER": "xgrr",
        "PASSWORD": "supoer-secret-your-password-is",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

SECRET_KEY = "something-super-secret"

ALLOWED_HOSTS = ['142.93.252.28',] # Put your IP address in here
```
### Postgres Database
```
(env) root@site:~/readingroom-site# su postgres
postgres@site:/root/readingroom-site$ psql
could not change directory to "/root/readingroom-site": Permission denied
psql (10.5 (Ubuntu 10.5-0ubuntu0.18.04))
Type "help" for help.

postgres=# CREATE USER xgrr;
CREATE ROLE
postgres=# ALTER user xgrr PASSWORD 'whatever-your-password-is';
ALTER ROLE
postgres=# CREATE DATABASE xgrr_site USER xgrr;
ERROR:  syntax error at or near "USER"
LINE 1: CREATE DATABASE xgrr_site USER xgrr;
                                  ^
postgres=# CREATE DATABASE xgrr_site OWNER xgrr;
CREATE DATABASE
postgres=# exit;
ERROR:  syntax error at or near "exit"
LINE 1: exit;
```

```
./manage.py migrate
```

Or spool in a copy of the database

### Restore database


```
su postgres
# Then as postgres user:
git clone https://github.com/xgrr/readingroom-site-db.git
cd readingroom-site-db
createdb xgrr_site --owner=xgrr
ppg_restore -d xgrr_site .
psql -d xgrr_site -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO xgrr;"
```

Command line should now be available with `psql --user xgrr -d xgrr_site -h localhost -W`

### Run the server

```
./manage.py makemigrations
./manage.py migrate
./manage.py runserver_plus
```
