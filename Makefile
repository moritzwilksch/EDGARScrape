run:
	docker run --name edgar-postgres -e POSTGRES_PASSWORD=ThisIsSecretAF -d -p 5432:5432 postgres

stop:
	docker stop edgar-postgres

start:
	docker start edgar-postgres

psql:
	docker exec -it edgar-postgres /bin/bash
	psql postgresql://postgres:ThisIsSecretAF@localhost:5432