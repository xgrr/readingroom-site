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


### Restore Media



### Run the server

```
./manage.py makemigrations
./manage.py migrate
./manage.py makemessages -i env -l tet # ignoring the 'env' directory, make tetun translations
./manage.py compilemessages
./manage.py runserver_plus
```
