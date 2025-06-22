import sqlalchemy as sql
from sqlalchemy import text
from sqlalchemy.ext import asyncio as aio
from sqlalchemy.exc import IntegrityError
from database.data import db_commons as com
import discord as disc
from bot.client_instance import get_client
from forum_functions.count_messages import get_users_message_count_in_thread
from forum_functions.get_thread_infos import get_thread_infos
from tools.json_config import get_first_server_id, load_json, get_semester_and_year
from tools.checks import check_monitor
from datetime import datetime
from collections.abc import Callable, Awaitable
from typing import Any
from asyncpg import Record
from asyncpg.exceptions import ForeignKeyViolationError as FKVE
from asyncio import sleep

ENGINE: aio.AsyncEngine = aio.create_async_engine(com.DATABASE_URL)

type db_funcs_t = Callable[
    [aio.AsyncConnection, Any],
    Awaitable[bool] | Awaitable[list]]

async def db_nuke() -> bool:
    """
    Recria o banco de dados. Todos os dados são perdidos.

    **TOME CUIDADO EXTREMO AO UTILIZAR ESSA FUNÇÃO**
    """

    global ENGINE

    from os import name, system
    from asyncio import sleep

    if name == "posix":
        CMD = "sudo -u postgres psql -U postgres -c"
    else:
        CMD = f"psql postgres://postgres:{com.PASSW}@localhost:5432/postgres -c"

    if ENGINE is not None:
        await ENGINE.dispose()
        ENGINE.sync_engine.dispose()
        ENGINE = None

    ret: int = system(f"{CMD} \"REVOKE ALL PRIVILEGES "
                      "ON DATABASE db_monitoring FROM monitor_admin;\"")
    ret = system(f"{CMD} \"DROP DATABASE db_monitoring WITH (FORCE);\"")
    ret = system(f"{CMD} \"DROP OWNED BY monitor_admin CASCADE;\"")

    from database.data.db_setup import eng_setup
    eng_setup()
    ret = system(f"{CMD} \"ALTER USER monitor_admin WITH LOGIN PASSWORD '{com.PASSW}'\"")

    await sleep(1)
    ENGINE = aio.create_async_engine(com.DATABASE_URL, pool_pre_ping=True)

    return ret

def connection_execute(
    db_func: db_funcs_t
):
    """
    Realiza operações no banco com as funções pelo gerenciador de contexto
    """

    _CONN: aio.AsyncConnection

    async def execute(*args: Any, **kwargs: Any) -> bool:
        res: bool

        async with ENGINE.connect() as _CONN:
            res = await db_func(_CONN, *args, **kwargs)
            await _CONN.commit()

        return res

    return execute

# Funcoes de Escuta

@connection_execute
async def db_new_user(
    _CONN: aio.AsyncConnection, userID: int,
    is_creator: bool = True,
    is_monitor: bool | None = None
) -> bool:
    """
    Insere um novo usuário no banco de dados ou incrementa total de dúvidas.  
    Chamado a cada criação de thread
    """

    user: disc.Member = com.user_id_to_member(userID)
    res: sql.CursorResult | None = None

    if is_monitor == None:
        is_monitor = await check_monitor(user) # checa para semestre atual

    try:
        creator_val: int = int(is_creator)
        new_data: str = (f"{userID}, {is_monitor}, "
                         f"({creator_val}, 0, 0)")
        if is_monitor: new_data += f", ({1- creator_val}, 0)"

        res = await _CONN.execute(text(
            f"INSERT INTO users VALUES ({new_data})"
        ))

    except IntegrityError:
        await _CONN.rollback()

        if not is_monitor:
            if is_creator:
                res = await _CONN.execute(text(
                    "UPDATE users SET questions_data.total = "
                    "(questions_data).total + 1 "
                    f"WHERE discID = {userID}"
                ))
        else:
            data: tuple[str]
            if is_creator:
                data = ("questions_data.total", "(questions_data).total")
            else:
                data = ("monitor_data.answered", "(monitor_data).answered")

            # se nao estiver como monitor no banco, atualize
            if not (await _CONN.execute(text(
                "SELECT is_monitor FROM users "
                f"WHERE discID = {userID}"
            ))).fetchall()[0][0]:
                await _CONN.execute(text(
                    "UPDATE users SET is_monitor = TRUE "
                    f"WHERE discID = {userID}"
                ))

            res = await _CONN.execute(text(
                f"UPDATE users SET {data[0]} = "
                f"{data[1]} + 1 "
                f"WHERE discID = {userID}"
            ))

    return True if res is None else res.rowcount > 0

@connection_execute
async def db_thread_answered(
    _CONN: aio.AsyncConnection, threadID: int,
    users: set[int] | None = None,
    semester_pair: tuple[int, int] = None,
    from_on_message: bool = False
) -> bool:
    """
    Checa se uma thread foi respondida.

    Se sim, incrementa answered no monitor_data de monitores participantes,
    questions_data das materias da thread e do criador da thread, e sincroniza
    os participantes em user_thread com os da thread.

    Returns:

        Retorna ``True`` se monitor respondeu, ``False`` caso contrário
            - (obs.: sempre retornará ``False`` para semestres passados)
    """

    userID: int
    user: disc.Member | None
    old_users: set[int] | list[tuple[int]]
    semester: int
    year: int
    semester_pair: tuple[int, int]
    monitor_answered: bool = False

    server_info: dict = load_json()[str(get_first_server_id())]
    current_pair: tuple[int, int] = (
        server_info["SEMESTER"], server_info["YEAR"]
    )

    if not semester_pair:
        semester_pair = current_pair
    else:
        semester_pair = tuple(sorted(semester_pair))

    is_old_semester: bool = current_pair != semester_pair

    old_users = (await _CONN.execute(text(
                    "SELECT discID FROM user_thread "
                    f"WHERE threadID = {threadID}"
                ))).fetchall()
    old_users = {rec[0] for rec in old_users}

    if not users:
        users = set((await get_users_message_count_in_thread(threadID)).keys())
    
    if len(users) >= 2:
        await _CONN.execute(text(
            f"UPDATE thread SET is_answered = TRUE WHERE threadID = {threadID}"
        ))

    semester, year = semester_pair
    semester_info: list[int] | list = (
        com.MONITORS_OLD.get(year, {}).get(semester, [])
    )

    for userID in users - old_users: # usuarios fora do banco
        user = com.user_id_to_member(userID)
        is_monitor: bool = await check_monitor(user)

        # semestre atual e monitor ou monitor em 2o sem. 2024
        if ((not is_old_semester and is_monitor)
            or (is_old_semester and userID in semester_info)):
            monitor_answered = True

        await _CONN.execute(text(
            "INSERT INTO user_thread (discID, threadID) VALUES "
            f"({userID}, {threadID})"
        ))

    return monitor_answered

@connection_execute
async def db_new_semester(
    _CONN: aio.AsyncConnection,
    semester: int | None = None,
    year: int | None = None
) -> bool:
    """
    Registra novo semestre. Se ``semester`` e ``year`` forem -1,
    registra semestre atual.
    """

    if (semester, year) == (None, None):
        current: dict[str, int] = com.get_semester()
        (semester, year) = (current["semester"], current["year"])

    elif semester not in range(1, 3) or year < 2023:
        raise ValueError("invalid semester or year")

    await _CONN.execute(text(
        "INSERT INTO semester (semester_year, semester) VALUES"
        f"({year}, {semester})"
    ))

@connection_execute
async def db_thread_delete(_CONN: aio.AsyncConnection, threadID: int) -> bool:
    """
    Remove do banco as threads deletadas.

    Pareado com on_raw_thread_delete
    """

    res: sql.CursorResult = await _CONN.execute(text(
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

    Pareado com on_guild_role_update
    """

    res1: sql.CursorResult
    res2: sql.CursorResult

    res1 = await _CONN.execute(text(
        f"UPDATE users SET is_monitor = {after_is_monitor} "
        f"WHERE discID = {after_id}"
    ))
    res2 = await _CONN.execute(text(
        f"UPDATE users SET monitor_data = (0, 0) "
        f"WHERE discID = {after_id} AND monitor_data IS NULL"
    ))

    return res1.rowcount > 0 and res2.rowcount > 0

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
    _, tagIDs = com.tag_reorder(*tagIDs)

    db_tags: list[int] = [row[0] for row in select.fetchall()]

    if set(tagIDs) != set(db_tags):
        # tags fora do banco
        for tag in set(tagIDs) - set(db_tags):
            try:
                res: sql.CursorResult = await _CONN.execute(text(
                    "INSERT INTO tag_thread (threadID, tagID) VALUES"
                    f"({threadID}, {tag})"
                ))
                if res.rowcount != len(set(tagIDs) - set(db_tags)):
                    ret_val = False
            except FKVE as e:
                continue

        # tags no banco a serem deletadas
        for tag in set(db_tags) - set(tagIDs):
            try:
                res: sql.CursorResult = await _CONN.execute(text(
                    f"DELETE FROM tag_thread WHERE tagID = {tag} "
                    f"AND threadID = {threadID}"
                ))
                if res.rowcount != len(set(db_tags) - set(tagIDs)):
                    ret_val = False
            except FKVE as e:
                continue

    return ret_val

@connection_execute
async def db_thread_create(
    _CONN: aio.AsyncConnection,
    threadID: int,
    creatorID: int,
    *tagIDs: int,
    timestamp: datetime|str = "CURRENT_TIMESTAMP"
) -> bool:
    """
    Salva informações de criação da thread no banco

    Pareado com on_thread_create
    """

    ts_fmt: str
    new_user: disc.Member | None = com.user_id_to_member(creatorID)
    is_monitor: bool = await check_monitor(new_user)

    if not (isinstance(timestamp, datetime)
            and timestamp == "CURRENT_TIMESTAMP"):
        timestamp = ts_fmt = "CURRENT_TIMESTAMP"
    elif isinstance(timestamp, datetime):
        server_id: int = get_first_server_id()
        server_info: dict = load_json()[str(server_id)]
        ts_semester: tuple[int, int] = get_semester_and_year(server_id, timestamp)

        current_semester: tuple[int, int] = (
            server_info["SEMESTER"], server_info["YEAR"]
        )
        monitors_info: list[int] | list = (
            com.MONITORS_OLD.get(ts_semester[1], {}).get(ts_semester[0], [])
        )

        ts_fmt = "'" + f"{timestamp:%Y-%m-%d %H:%M:%S.%f}"[:-1] + "'"

        # monitor no semestre atual ou se na lista de monitores
        is_monitor = is_monitor and (
            ts_semester == current_semester
            or creatorID in monitors_info
        )

    res: bool = True
    _, tagIDs = com.tag_reorder(*tagIDs)

    if not await db_new_user(creatorID, is_monitor=is_monitor):
        com.eprint("User could not be registered")
        return False

    thread_insert: sql.CursorResult = await _CONN.execute(text(
        "INSERT INTO thread"
        f" VALUES ({threadID}, {creatorID}, {ts_fmt}, "
        "FALSE, FALSE, (SELECT MAX(semesterID) FROM semester))"
    ))

    await _CONN.commit()

    if thread_insert.rowcount == 0:
        res = False

    for tag in tagIDs:
        if (await _CONN.execute(text(
            "INSERT INTO tag_thread (tagID, threadID)"
            f" VALUES ({tag}, {threadID})"
        ))).rowcount == 0:
            res = False

    return res

# Funcoes de consulta

@connection_execute
async def db_ranking(
    _CONN: aio.AsyncConnection,
    semester: int | None = None,
    year: int | None = None,
    option: str = "monitors"
) -> list[dict[int, dict[str, int]]] | list:
    """
    Retorna os monitores do semestre atual e seus dados de suporte,
    ordenados por quantidade de dúvidas resolvidas, ou uma lista vazia
    caso haja erro ou não haja monitores.

    Parameters:
        semester :`int`: Semestre, 1 ou 2
        year :`int`: Ano
        option :`str`:
            Valores:
                "monitors" (Padrão): Retorna dados de monitores
                "users": Retorna dados de não monitores
                "both": Retorna dados de monitores e não monitores
    """

    res: (list[tuple[int, str|Record]]
        | list[tuple[list[dict[str, Any]]]])
    data: tuple[int] | dict[str, int]
    ret: list[dict[int, dict[str, int]]] | list = []
    guild_data: dict = load_json()[str(get_first_server_id())]
    current_semester: int = guild_data["SEMESTER"]
    current_year: int = guild_data["YEAR"]

    option_map: dict[str, str] = {
        "monitors": "SELECT discID, monitor_data FROM monitors mon "
                    "ORDER BY (mon.monitor_data).answered DESC, "
                    "(mon.monitor_data).solved DESC",
        # somente quem nao so criou thread
        "users": "SELECT discID, questions_data FROM helpers h "
                 "ORDER BY (h.questions_data).answered DESC, "
                 "(h.questions_data).solved DESC",
        "both": ""
    }

    if option not in option_map:
        raise ValueError(f"Invalid option {option}")

    if (semester, year) in ((None, None), (current_semester, current_year)):
        if option != "both":
            res = (await _CONN.execute(text(
                option_map[option]
            ))).fetchall()
        else:
            res = (await _CONN.execute(text(
                option_map["monitors"]
            ))).fetchall()
            res += (await _CONN.execute(text(
                option_map["users"]
            ))).fetchall()

        if not res: return list()

        for entry in res:
            if type(entry[1]) == Record:
                data = {
                    "answered": entry[1]["answered"],
                    "solved": entry[1]["solved"],
                }
            else:
                data = eval(entry[1])
                data = {
                    "answered": data[-2],
                    "solved": data[-1]
                }

            ret.append({int(entry[0]): data})
    elif type(semester) == type(year) == int:
        res = (await _CONN.execute(text(
            "SELECT user_data FROM semester WHERE "
            f"semester_year = {year} AND semester = {semester}"
        ))).fetchall()

        if not res[0][0]: return list()

        for entry in res[0][0]:
            if option == "monitors":
                if entry["is_monitor"]:
                    ret.append({entry["discID"]: entry["monitor_data"]})
            elif option == "users":
                if not entry["is_monitor"]:
                    data = ({k: entry["questions_data"][k]
                             for k in ("answered", "solved")})
                    ret.append({entry["discID"]: data})
            else:
                if entry["is_monitor"]:
                    ret.append({entry["discID"]: entry["monitor_data"]})
                else:
                    data = ({k: entry["questions_data"][k]
                             for k in ("answered", "solved")})
                    ret.append({entry["discID"]: data})
    else:
        raise ValueError(
            "Semester must be 1 or 2, year must be valid, "
            "or both must be None"
        )

    ret = list(filter(lambda x: tuple(
                            (list(x.values())[0]).values()
                      ) != (None, None), ret))

    if ret:
        ret = sorted(
            ret,
            key=lambda x: list(x.values())[0]["solved"], reverse=True
        )
        ret = sorted(
            ret,
            key=lambda x: list(x.values())[0]["answered"], reverse=True
        )

    return ret

@connection_execute
async def db_subject_ranking(
    _CONN: aio.AsyncConnection,
    semester: int | None = None,
    year: int | None = None
) -> list[dict[int, dict[str, int]]] | list:
    """
    Retorna dados da matéria para um dado semestre e ano.
    """

    data: tuple[int] | dict[str, int]
    entry: dict
    subject: tuple[int, str, dict]
    guild_data: dict = load_json()[str(get_first_server_id())]
    current_semester: int = guild_data["SEMESTER"]
    current_year: int = guild_data["YEAR"]
    ret: list[dict[int, dict[str, int]]] = []

    if (semester, year) in ((None, None), (current_semester, current_year)):
        subject_info: list[tuple[int, str, str|Record]] = (
            await _CONN.execute(text(
            "SELECT tags.tagID, tags.subjectID, sub.questions_data "
            "FROM tags INNER JOIN subjects sub "
            "ON sub.subjectID = tags.subjectID "
            "WHERE sub.questions_data <> (0,0,0) "
            "ORDER BY (sub.questions_data).total DESC, "
            "(sub.questions_data).answered DESC, "
            "(sub.questions_data).solved DESC"))
        ).fetchall()

        if not subject_info: return list()

        for entry in subject_info:
            if type(entry[-1]) == "str":
                data = eval(entry[-1])
                data = {
                    "total": data[0],
                    "answered": data[1],
                    "solved": data[2]
                }
            else:
                data = {
                    "total": entry[-1]["total"],
                    "answered": entry[-1]["answered"],
                    "solved": entry[-1]["solved"]
                }
            ret.append({"tagID": entry[0], "questions_data": data})

    elif type(semester) == type(year) == int:
        subject_tag: list[tuple[int, str]] = (await _CONN.execute(text(
            "SELECT tags.tagID, tags.subjectID "
            "FROM tags INNER JOIN subjects sub "
            "ON sub.subjectID = tags.subjectID "
        ))).fetchall()

        res: list[tuple[list[dict]]] = (await _CONN.execute(text(
            "SELECT subject_data FROM semester "
            f"WHERE semester_year = {year} AND semester = {semester}"
        ))).fetchall()

        if not res[0][0]: return list() # [([{...}],)]

        for entry in res[0][0]:
            for subject in subject_tag:
                if entry["subject_id"] in subject:
                    ret.append(
                        {"tagID": subject[0],
                        "questions_data": entry["questions_data"]}
                    )
                    break

    else:
        raise ValueError(
            "Semester must be 1 or 2, year must be valid, "
            "or both must be None"
        )

    ret = list(
        filter(
            (lambda x: tuple(x["questions_data"].values())
             not in ((None, None, None), (0,0,0))),
            ret
        )
    )

    if ret:
        ret = sorted(
            ret,
            key=lambda x: x["questions_data"]["total"],
            reverse=True
        )
        ret = sorted(
            ret,
            key=lambda x: x["questions_data"]["answered"],
            reverse=True
        )
        ret = sorted(
            ret,
            key=lambda x: x["questions_data"]["solved"],
            reverse=True
        )

    return ret

@connection_execute
async def db_available_semesters(
    _CONN: aio.AsyncConnection
) -> tuple[int, list[tuple[int]] | list]:
    """
    Retorna uma tupla com a quantidade de semestres disponíveis
    e quais são.
    """

    res: sql.CursorResult = await _CONN.execute(text(
        "SELECT semester_year, semester FROM semester "
        "ORDER BY semester_year, semester"
    ))

    rowcount: int = res.rowcount
    rows: list[tuple[str | int]] = res.fetchall()
    rows = [tuple(map(int, i)) for i in rows]

    return (rowcount, rows)

@connection_execute
async def db_semester_info(
    _CONN: aio.AsyncConnection,
    semester: int,
    year: int
) -> dict:
    ...

@connection_execute
async def db_user_info(_CONN, userID):
    return (await _CONN.execute(text(
        f"SELECT * from users where discID = {userID}"
    ))).fetchall()
