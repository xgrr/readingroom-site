RETRIES=10
until psql -h $HOST -U $USER -d $DATABASE -c "select 1" > /dev/null 2>&1 || [ $RETRIES -eq 0 ]; do 
    echo "Waiting for postgres server to start, $((RETRIES)) remaining attempts..." 
    RETRIES=$((RETRIES-=1)) 
    sleep 3 
done
