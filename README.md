## Local development


```
$ docker-compose build
$ docker-compose up
``` 

This will mount the code inside the container.
It starts a postgres DB, and a separate container for the migrations.

### Clean up database
If you want to start fresh, run:
```
$ docker-compose down
$ docker volume rm response_postgres_data
```

