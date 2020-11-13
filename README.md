# NAME
prod description

## Documentation

### Installation
* [Slack configuration](docs/slack.md)
* [Zoom configuration](docs/zoom.md)
* [Google auth configuration](docs/google.md)
* [GitHub auth configuration](docs/github.md)


## Local development

### Configure the env file

```
$ cp env.example .env
```
Replace the default values by the ones in Slack.

```
$ cd docker/
$ docker-compose build
$ docker-compose up
``` 

This will mount the code inside the container.
It starts a postgres DB, and a separate container for the migrations.

### Create a superuser
In order to use the Django admin locally, you will need a super user.
After having the application up and running:
```
$ docker-compose exec response python manage.py createsuperuser
```
And follow the prompts.

### Run migrations
```
docker-compose exec response python manage.py
```

### Clean up database
If you want to start fresh, run:
```
$ docker-compose down
$ docker volume rm response_postgres_data
```

