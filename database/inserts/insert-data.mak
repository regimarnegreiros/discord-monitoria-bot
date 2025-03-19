SCHEMA = ../schema
SHUTUP = >/dev/null 2>&1
SHARED_SUBJECTS = $(shell ls ./subjects/shared_subjects | grep .sql)
OTHER_SUBJECTS = $(shell ls ./subjects | grep .sql)
DB = -d "db_monitoring"

tags_inserts : subjects_inserts
	@ (psql $(DB) -f ./$@.sql $(SHUTUP)) && echo "tags registered" \
		|| echo "tags could not be registered"

subjects_inserts : $(SCHEMA)/make-schema.mak
	@ for subject in $(SHARED_SUBJECTS); do \
		(psql $(DB) -f ./subjects/shared_subjects/$$subject $(SHUTUP)) \
	  done && echo "shared subjects registered" \
	  	|| "shared subjects could not be registered";
	@ for subject in $(OTHER_SUBJECTS); do \
		(psql $(DB) -f ./subjects/$$subject $(SHUTUP)) \
			&& echo "$${subject%.sql} registered" || "$${subject%.sql} could not be registered"; \
		done

del-all:
	@ (psql $(DB) -c "DELETE FROM tags; DELETE FROM comp_subject;" $(SHUTUP)) \
		&& echo "data deleted" || echo "data could not be deleted"
