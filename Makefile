install:
	pip install -r requirements.txt

run-postgres:
	docker run --name edgar-postgres \
		-e POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) \
		-e POSTGRES_USER=moritz \
		-d -p 5432:5432 postgres

stop-postgres:
	docker stop edgar-postgres

start-postgres:
	docker start edgar-postgres

psql:
	docker exec -it edgar-postgres /bin/bash

run-mongo:
	docker run -d --name edgar-mongo --restart always --env-file .env -v `pwd`/db:/data/db -p 27017:27017 mongo
