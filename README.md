# readingroom-site
Reading room website

## Initial Setup

Based on a fresh install of Ubuntu 18.04

### Install Docker

The easy way:
```
sudo curl -fsSL get.docker.com -o get-docker.sh && \
sudo sh get-docker.sh
```

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

