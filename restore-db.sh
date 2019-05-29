
SERVICE=rrdb
. env/bin/activate
echo "Set permissions on /source"
docker-compose exec ${SERVICE} bash -c 'chmod a+x /source && chmod -R a+r /source'
echo "Disconnect all current connections"
docker-compose exec -u postgres ${SERVICE} bash -c "psql << EOF
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'readingroom'
AND pid <> pg_backend_pid();
EOF"
echo "Drop database (if exists)"
docker-compose exec -u postgres ${SERVICE} bash -c 'dropdb --if-exists $POSTGRES_DBNAME'
echo "Createdb"
docker-compose exec -u postgres ${SERVICE} bash -c 'createdb -T template_postgis -E UTF-8 $POSTGRES_DBNAME'
echo "Restore database from /source"

# WARNING: There are some hardcoded values here

docker cp ../readingroom-site-db/. readingroom-site_rrdb_1:/source/
docker-compose exec -u postgres ${SERVICE} bash -c 'pg_restore -d "$POSTGRES_DBNAME" -Fd /source'
docker exec readingroom-site_rrdb_1 rm -rf /source/*

# Then we want to migrate, restart our Django app
docker-compose exec -u django web bash -c ". env/bin/activate && cd app && ./manage.py migrate"
docker-compose restart web