import sqlalchemy as sql
from sqlalchemy import text
import db_commons as com
import discord as disc

ENGINE: sql.Engine = sql.create_engine(com.DATABASE_URL)
METADATA:sql.MetaData = sql.MetaData()

def connection_execute(db_func: function) -> function:
    """
    Realiza operações no banco com as funções pelo gerenciador de contexto
    """
    def execute(*args, **kwargs):
        with ENGINE.connect() as CONN:
            res = db_func(CONN, *args, **kwargs)
            CONN.commit()
        return res
    return execute

@connection_execute
def db_thread_delete(CONN: sql.Connection, threadID: int) -> bool:
    """
    Remove do banco as threads deletadas.

    Pareado com on_raw_thread_delete
    """
    threads: sql.Table = sql.Table("threads", METADATA, extend_existing=True)
    res = CONN.execute(threads.delete().where(threads.c.threadID == threadID))
    return res.rowcount > 0

@connection_execute
def db_monitor_update(CONN: sql.Connection) -> bool:
    """
    update users set is_monitor = true where discID = after.id  
    update semester set monitors = (monitors).append(after.id)  
    **to be implemented**

    Pareado com on_guild_role_update
    """
    raise NotImplementedError("funcao ainda sera implementada")

@connection_execute
def db_thread_update(CONN: sql.Connection, threadID: int, *tagIDs) -> bool:
    """
    Atualiza a tabela tag_thread com as tags atuais de uma thread

    Se a thread conter tags fora do banco, insere-as nele.

    Caso o banco contenha tags diferentes da thread, exclui-as.

    Pareado com on_raw_thread_update
    """
    select: sql.CursorResult

    ret_val: bool = True
    tag_thread: sql.Table = sql.Table("tag_thread", METADATA,
                                      extend_existing=True)
    select = CONN.execute(
        tag_thread.select()
                  .where(tag_thread.c.threadID == threadID)
    )
    db_tags = [row["tagID"] for row in select.fetchall()]

    if set(tagIDs) != set(db_tags):
        # tags fora do banco
        for tag in set(tagIDs) - set(db_tags):
            res: sql.CursorResult = CONN.execute(tag_thread.insert()
                        .values(threadID = threadID, tagID = tag))
            if res.rowcount != len(set(tagIDs) - set(db_tags)):
                ret_val = False

        # tags no banco a serem deletadas
        for tag in set(db_tags) - set(tagIDs):
            res: sql.CursorResult = CONN.execute(tag_thread.delete()
                        .where(tag_thread.c.tagID == tag))
            if res.rowcount != len(set(db_tags) - set(tagIDs)):
                ret_val = False
    
    return ret_val

@connection_execute
def db_thread_create(
    CONN: sql.Connection,
    threadID: int,
    creatorID: int,
    date: sql.Date, *tagIDs: int
) -> bool:
    """
    Salva informações de criação da thread no banco

    Pareado com on_thread_create
    """
    res: bool = True
    thread: sql.Table = sql.Table("thread", METADATA, extend_existing=True)
    tag_thread: sql.Table = sql.Table("tag_thread", METADATA,
                                      extend_existing=True)
    thread_insert = CONN.execute(
        thread.insert().values(threadID = threadID,
                               threadCreatorID = creatorID,
                               creationDate = date)
    )

    if thread_insert.rowcount == 0:
        res = False

    for tag in tagIDs:
        if CONN.execute(
            tag_thread.insert().values(tagID = tag, threadID = threadID)
        ).rowcount == 0:
            res = False
    
    return res
