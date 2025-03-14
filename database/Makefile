M_ARGS = --no-print-directory

insert-data : make-schema
	@ cd inserts && make -f ./$@.mak $(M_ARGS)

make-schema :
	@ cd schema && make -f ./$@.mak $(M_ARGS)
