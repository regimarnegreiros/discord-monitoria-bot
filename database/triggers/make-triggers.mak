SHUTUP = >/dev/null 2>&1
DB = -d "db_monitoring"

triggers:
	@ psql $(DB) -f ./$@.sql $(SHUTUP) && echo "triggers created" \
		|| echo "triggers could not be created"
