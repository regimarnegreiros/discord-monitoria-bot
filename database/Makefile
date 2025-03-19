M_ARGS = --no-print-directory
SHUTUP = >/dev/null 2>&1

make-triggers : insert-data
	@ cd triggers && make -f ./$@.mak $(M_ARGS)

insert-data : make-schema
	@ cd inserts && make -f ./$@.mak $(M_ARGS)

make-schema :
	@ cd schema && make -f ./$@.mak $(M_ARGS)

schema-regen :
	@ cd schema && (make -f ./make-schema.mak schema_del $(M_ARGS) $(SHUTUP))
	@ cd schema && (make -f ./make-schema.mak $(M_ARGS) $(SHUTUP) \
					&& echo "schema regenerated")

data-regen : schema-regen
	@ cd inserts && (make -f ./insert-data.mak $(M_ARGS) $(SHUTUP) \
					 && echo "data regenerated")
	@ cd triggers && (make -f ./make-triggers.mak $(M_ARGS) $(SHUTUP) \
					  && echo "triggers regenerated")
