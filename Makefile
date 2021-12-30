run:
	docker run --name edgar-postgres \
		-e POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) \
		-e POSTGRES_USER=moritz \
		-d -p 5432:5432 postgres

stop:
	docker stop edgar-postgres

start:
	docker start edgar-postgres

psql:
	docker exec -it edgar-postgres /bin/bash

# psql -d edgar -U moritz