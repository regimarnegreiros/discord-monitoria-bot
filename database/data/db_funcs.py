import sqlalchemy as sql
from sqlalchemy.dialects.postgresql import ARRAY as psql_arr, DATE as psql_DATE
from sqlalchemy import text
from sqlalchemy.ext import asyncio as aio
from sqlalchemy.exc import IntegrityError
from database.data import db_commons as com
import discord as disc
from bot.client_instance import get_client
from settings.config import GUILD_ID
from tools.checks import check_monitor
from datetime import date

ENGINE: sql.Engine = aio.create_async_engine(com.DATABASE_URL)
METADATA:sql.MetaData = sql.MetaData()

def connection_execute(db_func):
    """
    Realiza operações no banco com as funções pelo gerenciador de contexto
    """
    async def execute(*args, **kwargs):
        async with ENGINE.connect() as _CONN:
            res = await db_func(_CONN, *args, **kwargs)
            await _CONN.commit()
        return res
    return execute

@connection_execute
async def db_new_user(_CONN: aio.AsyncConnection, userID: int) -> bool:
    """
    Insere um novo usuário no banco de dados
    """
    user: disc.Member = get_client().get_guild(GUILD_ID).get_member(userID)

    try:
        res: sql.CursorResult = await _CONN.execute(text(
            "INSERT INTO users VALUES "
            f"({userID}, {await check_monitor(user)}, (1, 0, 0));"
        ))
    except IntegrityError:
        await _CONN.rollback()
        res = await _CONN.execute(text(
            "UPDATE users SET questions_data.total ="
                        " (questions_data).total + 1 "
            f"WHERE discID = {userID}"
        ))

    return res.rowcount > 0

@connection_execute
async def db_new_semester(
    _CONN: aio.AsyncConnection
) -> None:
    """
    Registra novo semestre

    Na mudança de semestre, copia lista de monitores do semestre anterior.
    """

    curr_date: date = date.today()
    year: int = curr_date.year
    semester: int = round(curr_date.month / 12) + 1

    await _CONN.execute(text(
        "INSERT INTO semester (semester_year, semester) VALUES"
        f"({year}, {semester})"
    ))

    await _CONN.execute(text(
        "UPDATE semester"
        "SET monitors ="
            "(SELECT monitors FROM semester "
            f"WHERE semester_year = {year if semester == 2 else year - 1}"
            f"AND semester = {1 if semester == 2 else semester})"
        f"WHERE semester_year = {year if semester == 2 else year - 1} "
        f"AND semester = {1 if semester == 2 else semester}"
    ))

        

@connection_execute
async def db_thread_delete(_CONN: aio.AsyncConnection, threadID: int) -> bool:
    """
    Remove do banco as threads deletadas.

    Pareado com on_raw_thread_delete
    """

    res = await _CONN.execute(text(
        f"DELETE FROM thread WHERE threadID = {threadID}"
    ))
    return res.rowcount > 0

@connection_execute
async def db_monitor_update(
    _CONN: aio.AsyncConnection, after_id: int,
    after_is_monitor: bool
) -> bool:
    """
    Atualiza o status de monitor do usuário no banco de dados.

    Lista de monitores é atualizada automaticamente.

    Pareado com on_guild_role_update
    """

    res = await _CONN.execute(text(
        f"UPDATE users SET is_monitor = {after_is_monitor}"
        f"WHERE discID = {after_id}"
    ))

    return res.rowcount > 0
    

@connection_execute
async def db_thread_update(
    _CONN: aio.AsyncConnection,
    threadID: int, *tagIDs: int
) -> bool:
    """
    Atualiza a tabela tag_thread com as tags atuais de uma thread

    Se a thread conter tags fora do banco, insere-as nele.

    Caso o banco contenha tags diferentes da thread, exclui-as.

    Pareado com on_raw_thread_update
    """

    ret_val: bool = True
    select: sql.CursorResult = await _CONN.execute(text(
        "SELECT tagID, threadID FROM tag_thread "
        f"WHERE threadID = {threadID}"
    ))

    db_tags: list[sql.Row] = [row[0] for row in select.fetchall()]

    if set(tagIDs) != set(db_tags):
        # tags fora do banco
        for tag in set(tagIDs) - set(db_tags):
            res: sql.CursorResult = await _CONN.execute(text(
                "INSERT INTO tag_thread (threadID, tagID) VALUES"
                f"({threadID}, {tag})"
            ))
            if res.rowcount != len(set(tagIDs) - set(db_tags)):
                ret_val = False

        # tags no banco a serem deletadas
        for tag in set(db_tags) - set(tagIDs):
            res: sql.CursorResult = await _CONN.execute(text(
                f"DELETE FROM tag_thread WHERE tagID = {tag}"
            ))
            if res.rowcount != len(set(db_tags) - set(tagIDs)):
                ret_val = False
    
    return ret_val

@connection_execute
async def db_thread_create(
    _CONN: aio.AsyncConnection,
    threadID: int,
    creatorID: int,
    *tagIDs: int
) -> bool:
    """
    Salva informações de criação da thread no banco

    Pareado com on_thread_create
    """
    res: bool = True
    
    if not await db_new_user(creatorID):
        com.eprint("User could not be registered")
        return False
    
    thread_insert: sql.CursorResult = await _CONN.execute(text(
        "INSERT INTO thread (threadID, threadCreatorID, creationDate)"
        f" VALUES ({threadID}, {creatorID}, CURRENT_TIMESTAMP)"
    ))

    if thread_insert.rowcount == 0:
        res = False

    for tag in tagIDs:
        if (await _CONN.execute(text(
            "INSERT INTO tag_thread (tagID, threadID)"
            f" VALUES ({tag}, {threadID})"
        ))).rowcount == 0:
            res = False
    
    return res
