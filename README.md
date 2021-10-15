# EDGARScrape
Data Engineering project to use SQLAlchemy for writing scraped data to Postgres in a Docker container.

# Environment Setup
## Postgres in Docker
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