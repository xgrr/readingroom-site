# readingroom-site
Reading room website

## Preconditions

 - `xgrrlibrary` Ubuntu droplet is running on DigitalOcean and you can ssh into it
 - I log into `https://domains.google.com/m/registrar/lafaek.dev?_ga=2.209548306.1676199185.1567819206-2005771778.1565763758#` and set up a dns record to the IP address of the digitalocean droplet

My IP address was 157.245.140.25
When I `ssh -A root@157.245.140.25` I get a command line prompt

When I ask google for the address of readingroom.lafaek.dev it gives me the right IP address

```bash
josh@josh-ThinkPad-T420:~$ nslookup readingroom.lafaek.dev
Server:		127.0.0.53
Address:	127.0.0.53#53

Non-authoritative answer:
Name:	readingroom.lafaek.dev
Address: 68.183.227.58

josh@josh-ThinkPad-T420:~$ nslookup readingroom.lafaek.dev -n 8.8.8.8
Server:		8.8.8.8
Address:	8.8.8.8#53

Non-authoritative answer:
Name:	readingroom.lafaek.dev
Address: 157.245.140.25
```


## Initial Setup

Based on a fresh install of Ubuntu 18.04

### Install Docker

The easy way:
```
sudo curl -fsSL get.docker.com -o get-docker.sh && \
sudo sh get-docker.sh
```

 - Success: docker -v returns `Docker version...`

### OS Prep

```
apt update
apt install -y nginx gcc python3-venv git libpq-dev python3-dev postgis
apt install gettext 
```

### Pythonic Stuff
```
python3 -m venv env
source env/bin/activate && pip install wheel
# If you are already in the repo dir, skip next 2 lines
git clone https://github.com/xgrr/readingroom-site.git
git checkout redeploy
cd readingroom-site
pip install -r requirements.txt
```
### Database

To run a database you can use the system provided version or Docker.

#### System Version

You need to 'become' the postgres user and create a role with password, and database in the program `psql`.


```
root@ubuntu-s-1vcpu-2gb-nyc1-01:/tmp/readingroom-site# su postgres
postgres@ubuntu-s-1vcpu-2gb-nyc1-01:/tmp/readingroom-site$ psql
postgres=# CREATE ROLE "xgrr";
CREATE ROLE
postgres=# CREATE DATABASE xgrr_site OWNER xgrr;
CREATE DATABASE
postgres=# ALTER ROLE "xgrr" PASSWORD 'xgrr';
postgres=# ALTER ROLE "xgrr" WITH LOGIN;
ALTER ROLE
postgres=# 
``` 

Tell Django what your name, password and database name are. The HOST and PORT bits are important if you change default settings but leave them or ignore them.

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

#### Restoring from a Single File

The original database is backed up to `xanana.psql`. Copy it to the server. One way to do this is to use rsync

```
rsync -avz /home/josh/Downloads/xanana.psql root@157.245.140.25:/tmp/
```

Result:
```
sent 210,751 bytes  received 35 bytes  22,188.00 bytes/sec
total size is 1,420,673  speedup is 6.74
```

As the postgres user restore the xanana.psql file to the database you created earlier
```
psql -d xgrr_site < ./xanana.psql
```


```
docker cp xanana.psql readingroom-site_rrdb_1:/tmp
docker exec --user postgres readingroom-site_rrdb_1 sh -c "psql -d readingroom < /tmp/xanana.psql"
docker exec readingroom-site_rrdb_1 sh -c "rm /tmp/xanana.psql"
```

### Restore database


```
su postgres
# Then as postgres user:
git clone https://github.com/xgrr/readingroom-site-db.git
cd readingroom-site-db
createdb xgrr_site --owner=xgrr
ppg_restore -d xgrr_site .
psql -d xgrr_site -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO xgrr;"

pg_restore --user ${POSTGRES_USER} -W -d ${POSTGRES_DB} /source/
```

Command line should now be available with `psql --user xgrr -d xgrr_site -h localhost -W`

Clean up permissions
```
postgres@ubuntu-s-1vcpu-2gb-nyc1-01:/tmp/readingroom-site$ psql -d xgrr_site
psql (10.10 (Ubuntu 10.10-0ubuntu0.18.04.1))
Type "help" for help.

xgrr_site=# REVOKE ALL
xgrr_site-# ON ALL TABLES IN SCHEMA public 
xgrr_site-# FROM PUBLIC;
REVOKE
xgrr_site=# 
xgrr_site=# GRANT ALL
xgrr_site-# ON ALL TABLES IN SCHEMA public 
xgrr_site-# TO "xgrr";
GRANT
```

SELECT 'ALTER TABLE '|| oid::regclass::text ||' OWNER TO xgrr;'
FROM pg_class WHERE relkind = 'm'
ORDER BY oid;


### Restore Media



### Run the server

Make a file with the database settings you put into psql

nano .env

```
./manage.py makemigrations
./manage.py migrate
./manage.py makemessages -i env -l tet # ignoring the 'env' directory, make tetun translations
./manage.py compilemessages
./manage.py runserver_plus
```


Install nginx and certbot

 - apt install certbot python-certbot-nginx
 - certbot -d readingroom.lafaek.dev -m josh.vdbroek@gmail.com --agree-tos

Select "N" for the email and "2" for redirect

 - certbot renew has to be run within 3 months 

 Success Indicators

  - When a user navigates to "https://readingroom.lafaek.dev/" they see a "Welcome to NGINX" page
  - When a user navigates to "http://readingroom.lafaek.dev/" they get redirected to the "https" secure page

`ssllabs` teslls us how secure our site is, we got an 'A' rating! Nice


## Gunicorn Config
https://docs.gunicorn.org/en/stable/deploy.html#systemd