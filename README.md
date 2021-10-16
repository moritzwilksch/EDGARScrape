# EDGARScrape
Data Engineering project to use SQLAlchemy for writing scraped data to Postgres in a Docker container.

<img width="569" alt="image" src="https://user-images.githubusercontent.com/58488209/137554713-db375508-3a81-4626-89b0-56d748d6e35d.png">

## Architecture
Documentation for EDGAR API can be found [here](https://www.sec.gov/edgar/sec-api-documentation).
<img width="1378" alt="image" src="https://user-images.githubusercontent.com/58488209/137567439-bcb0f527-0086-4ed2-9e18-90f004932ff9.png">


## Environment Setup
### Pull Postgres Image
```console
docker pull postgres:latest
```

### Run Container
```console
docker run --name edgar-postgres -e POSTGRES_PASSWORD=mysecretpassword -d -p 5432:5432 postgres


# OR:
make run
```

### To manually connect with `psql`
```console
docker exec -it edgar-postgres /bin/bash
psql postgresql://postgres:mysecretpassword@localhost:5432

# OR:
make psql
```
