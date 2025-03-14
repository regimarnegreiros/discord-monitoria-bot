/* sync op qtd_duvidas on_thread_* (ex.: on_thread_create: +1 qtd_duvidas_total em materia, semestre) */

/*
    let tagID 1 = resolvida, subjectID 2 = POO;
    insert tag_thread.index 1 = (NULL, 2);
    if update tag_thread.tagID = (1), update subject.stats.solved += 1;
    if delete tag_thread.tagID, update subject.stats.solved -= 1; (?)
*/
/*
CREATE OR REPLACE FUNCTION solved_tag_increment() RETURNS TRIGGER AS $$
DECLARE
    is_solved       BOOLEAN;
    solved_count    INT;
BEGIN
    IF (TG_OP = 'UPDATE') THEN
        
    ELSIF (TG_OP = 'DELETE') THEN

    ENDIF
        

CREATE TRIGGER solved_tag_incrementer
AFTER UPDATE OR DELETE ON tag_thread
FOR EACH ROW EXECUTE FUNCTION solved_tag_increment();
*/
-- if (lower(nome) like '%resolvid%' from tags) incr (dados).resolvidas from materia, incr (dados).resolvidas from aluno
