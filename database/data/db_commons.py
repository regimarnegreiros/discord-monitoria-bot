import os
from os import sep as SEP
from sys import stderr
from dotenv import load_dotenv
from datetime import date
from bot.client_instance import get_client
from tools.json_config import get_first_server_id, load_json
from discord import Member

WD: str
DBWD: str
files: list[str]
PASSW: str | None
DATABASE_URL: str | None

def eprint(*args, **kwargs) -> None:
    print(*args, file=stderr, **kwargs)

def get_semester(
    option: str = "current"
) -> dict[str, int] | dict[str, dict[str, int]]:
    """
    Retorna semestre atual, anterior, ou ambos  

    ### Opções:
    - ``"current"``: padrão, retorna semestre atual  
    - ``"previous"``: retorna semestre anterior  
    - ``"both"``: retorna semestre atual e anterior
    """

    curr_date: date = date.today()
    current: dict[str, int] = {
        "year": curr_date.year,
        "semester": curr_date.month // 7 + 1 # month < 7: 1; else 2
    }
    previous: dict[str, int] = {
        "year": current["year"] - (current["semester"] % 2),
        "semester": 3 - current["semester"]
        # year: year - 1 if semester = 1; semester: 2 if 1, 1 if 2
    }
    both: dict[str, dict[str, int]] = {
        "current": current,
        "previous": previous
    }

    return both.get(option, current)

def tag_reorder(*tagIDs: int) -> tuple[bool, tuple[int]]:
    """
    Reordena tags: tag resolvida na ultima posição.

    Parameters:

        tagIDs: as tags a serem reorganizadas
    
    Returns:

        Tupla contendo booleano de se há tag resolvida nas tags e
        as tags reorganizadas 
    """

    data: dict = load_json()
    solved_tag: int = data[str(get_first_server_id())]["SOLVED_TAG_ID"]

    # ultima tag a ser inserida
    if solved_tag in tagIDs:
        aux: list = list(tagIDs)
        index: int = aux.index(solved_tag)
        aux[index], aux[-1] = aux[-1], aux[index]
        tagIDs = tuple(aux)

    return (solved_tag in tagIDs, tagIDs)

def user_id_to_member(
    userID: int,
    guildID: int | None = None
) -> Member | None:
    """Converte id de usuário (`int`) para `Member`.

    Retorna `None` se o usuário não existir na `Guild`
    """

    if not guildID:
        guildID = get_first_server_id()

    return get_client().get_guild(guildID).get_member(userID)

WD = (os.path.dirname(os.path.abspath(__file__))
            .removesuffix(f"{SEP}database{SEP}data") + SEP)
DBWD = f"{WD}database{SEP}"

files = [dir_contents[0] + SEP + file
                    for dir_contents in os.walk(DBWD)
                    for file in dir_contents[2] if file.endswith(".sql")]
files.sort(key=lambda file: file[file.rindex(SEP) + 1])

if not load_dotenv(dotenv_path=f"{WD}settings{SEP}.env"):
    eprint("error loading environment variables")
    exit(1)

del WD, DBWD, files

PASSW, DATABASE_URL = os.getenv("DBPASSW"), os.getenv("DB_URL")
