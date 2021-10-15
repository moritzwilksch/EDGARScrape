# EDGARScrape
Data Engineering project to use SQLAlchemy for writing scraped data to Postgres in a Docker container.

<img width="569" alt="image" src="https://user-images.githubusercontent.com/58488209/137554713-db375508-3a81-4626-89b0-56d748d6e35d.png">


## Environment Setup
### Pull Postgres Image
```bash
docker pull postgres:latest
```

### Run Container
```bash
docker run --name edgar-postgres -e POSTGRES_PASSWORD=mysecretpassword -d -p 5432:5432 postgres


# OR:
make run
```

### To manually connect with `psql`
```bash
docker exec -it edgar-postgres /bin/bash
psql postgresql://postgres:mysecretpassword@localhost:5432

# OR:
make psql
```
