prog = psql
user = $(shell whoami)

$(prog):
	@ which $@ >/dev/null

pre-setup: psql
	@ sudo -u postgres createuser $(user)
	@ sudo -u postgres createdb $(user)
	@ sudo -u postgres psql -c "ALTER USER $(user) WITH SUPERUSER;"

schema_setup : pre-setup
	@ psql -f ./schema/setup.sql
	@ psql -f ./schema/schema.sql
	@ psql -f ./schema/many-to-many.sql
