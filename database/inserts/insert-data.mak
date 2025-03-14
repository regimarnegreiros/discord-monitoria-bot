SCHEMA = ../schema
NULL := /dev/null
SHARED_SUBJECTS = $(shell ls ./subjects/shared_subjects | grep .sql)
OTHER_SUBJECTS = $(shell ls ./subjects | grep .sql)
DB = -d "db_monitoring"

tags_inserts : subjects_inserts
	@ (psql $(DB) -f ./$@.sql >$(NULL) 2>&1) && echo "tags registered" \
		|| echo "tags could not be registered"

subjects_inserts : $(SCHEMA)/make-schema.mak
	@ for subject in $(SHARED_SUBJECTS); do \
		(psql $(DB) -f ./subjects/shared_subjects/$$subject >$(NULL) 2>&1) \
			&& echo "$$subject registered" || "$$subject could not be registered"; \
		done
	@ for subject in $(OTHER_SUBJECTS); do \
		(psql $(DB) -f ./subjects/$$subject >$(NULL) 2>&1) \
			&& echo "$$subject registered" || "$$subject could not be registered"; \
		done

del-all:
	@ (psql $(DB) -c "DELETE FROM tags; DELETE FROM comp_subject;" \
		>$(NULL) 2>&1) && echo "data deleted" || echo "data could not be deleted"
