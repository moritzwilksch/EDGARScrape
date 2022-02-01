# EDGARScrape 🕷
>A data engineering project to collect fundamental financial data from the SEC EDGAR database and calculate relevant metrics for performing peer group comparisons.

## Architecture
TODO: Folder structure

## Environment Setup
### Set `PYTHONPATH`
```bash
export PYTHONPATH=/path/to/project_root
```
### Pull Postgres Image
```console
docker pull mongo
```

### Set up Mongo User and Password in `.env` File
```bash
# .env
MONGO_INITDB_ROOT_USERNAME=<username>
MONGO_INITDB_ROOT_PASSWORD=<password>
```

### Run Container
```console
docker run -d --name edgar-mongo --env-file .env -p 27017:27017 mongo

# OR:
make run-mongo
```

### To manually connect with `mongosh`
```console
docker exec -it edgar-mongo bash

mongosh
```
