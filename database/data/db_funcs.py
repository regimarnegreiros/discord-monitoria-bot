import sqlalchemy as sql
from sqlalchemy.dialects.postgresql import ARRAY as psql_arr, DATE as psql_DATE
from sqlalchemy import text
from sqlalchemy.ext import asyncio as aio
from sqlalchemy.exc import IntegrityError
from database.data import db_commons as com
import discord as disc
from bot.client_instance import get_client
from tools.json_config import get_first_server_id
from tools.checks import check_monitor

ENGINE: sql.Engine = aio.create_async_engine(com.DATABASE_URL)

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
    Insere um novo usuário no banco de dados ou incrementa total de dúvidas.  
    Chamado a cada criação de thread
    """
    user: disc.Member = (get_client().get_guild(get_first_server_id())
                                     .get_member(userID))

    try:
        res: sql.CursorResult
        if not (await check_monitor(user)):
            res  = await _CONN.execute(text(
                "INSERT INTO users "
                "(dicsID, is_monitor, questions_data) VALUES "
                f"({userID}, FALSE, (1, 0, 0));"
            ))
        else:
            res  = await _CONN.execute(text(
                "INSERT INTO users VALUES "
                f"({userID}, FALSE, (1, 0, 0), (0, 0));"
            ))
    except IntegrityError:
        await _CONN.rollback()
        res = await _CONN.execute(text(
            "UPDATE users SET questions_data.total = "
            "(questions_data).total + 1 "
            f"WHERE discID = {userID}"
        ))

    return res.rowcount > 0

@connection_execute
async def db_new_semester(_CONN: aio.AsyncConnection) -> None:
    """
    Registra novo semestre
    """

    current: dict[str, int] = com.get_semester()

    await _CONN.execute(text(
        "INSERT INTO semester (semester_year, semester) VALUES"
        f"({current['year']}, {current['semester']})"
    ))

@connection_execute
async def db_semester_info(
    _CONN: aio.AsyncConnection,
    semester: int,
    year: int
) -> dict:
    ...

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

    res: sql.CursorResult

    if after_is_monitor:
        res = await _CONN.execute(text(
            "INSERT INTO monitors (discID, monitor_data) VALUES "
            f"({after_id}, (0, 0))"
        ))
    else:
        res = await _CONN.execute(text(
            f"DELETE FROM monitors WHERE discID = {after_id}"
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


@connection_execute
async def db_monitors(
    _CONN: aio.AsyncConnection
) -> list[dict[int, dict[str, int]]]:
    """
    Retorna os monitores do semestre atual e seus dados de suporte,
    ordenados por quantidade de dúvidas resolvidas
    """

    res: list[tuple[str]] = (await _CONN.execute(text(
        "SELECT discID, monitor_data FROM monitors "
        "ORDER BY monitor_data.solved DESC"
    ))).fetchall()

    ret: list[dict[int, dict[str, int]]] = []

    for entry in res:
        monitor_data: tuple[int] | dict[str, int] = eval(entry[1])
        monitor_data = {"answered": monitor_data[0], "solved": monitor_data[1]}

        ret.append({"monitorID": int(entry[0]), "monitor_data": monitor_data})
    
    return ret
