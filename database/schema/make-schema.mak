prog = psql
user = $(shell whoami)
NULL := /dev/null
DB = -d "db_monitoring"

schema_many_to_many : schema_creation
	@ psql $(DB) -f ./many_to_many.sql >$(NULL) 2>&1 && echo "2nd part of schema done" \
		|| echo "2nd part of schema creation failed"

schema_creation : schema_setup
	@ psql $(DB) -f ./schema.sql >$(NULL) 2>&1 && echo "1st part of schema done" \
		|| echo "1st part of schema creation failed"

schema_setup : pre-setup
	@ psql $(DB) -f ./setup.sql >$(NULL) 2>&1 && echo "setup done" \
		|| echo "setup failed"

pre-setup: psql
	@ # tests CRUD permissions
	@ (psql -c "CREATE TABLE test(a int); INSERT INTO test VALUES(1);" >$(NULL) 2>&1 \
	  && psql -c "SELECT * FROM test; DROP TABLE test;" >$(NULL) 2>&1) || { \
		sudo -u postgres createuser $(user); \
		sudo -u postgres createdb $(user); \
		sudo -u postgres psql -c "ALTER USER $(user) WITH SUPERUSER;"; \
	}

	@ (psql -l | grep "db_monitoring" >$(NULL)) 2>&1 || createdb db_monitoring

$(prog):
	@ which $@ >$(NULL)

schema_del:
	@ psql -c "DROP DATABASE db_monitoring;" >$(NULL) 2>&1 && echo "schema deleted" \
		|| echo "failed to delete schema"
