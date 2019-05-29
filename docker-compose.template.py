import yaml
from xanana.settings.base import DATABASES

image = 'kartoza/postgis:10.0-2.4'
database_settings = DATABASES['default']

compose = '''
version: '3'
services:
  {HOST}:
    environment: 
        POSTGRES_USER: {USER}
        POSTGRES_PASS: {PASSWORD}
        POSTGRES_DBNAME: {NAME}
    image: {image}
    ports:
    - "5432"
    volumes:
      - readingroom-site-db:/source
      - readingroom-db-postgresql:/var/lib/postgresql
    networks:
      - back

  web:
    restart: always
    build: 
      context: .
      dockerfile: Dockerfile
    links:
      - {HOST}
    ports:
      - "8000"
    volumes:
      - ./web/app:/home/django/app
      - /var/www/html/static:/var/www/html/static
      - /var/www/html/media:/var/www/html/media
    networks:
      - front
      - back

volumes:
  readingroom-site-db:
  readingroom-db-postgresql:

networks:
  front:
  back:

'''.format(**database_settings, image=image)

with open('docker-compose.yml', 'w') as composefile:
    composefile.write(compose)

