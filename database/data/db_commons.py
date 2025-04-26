import os
from os import sep as SEP
from sys import stderr
from dotenv import load_dotenv
from datetime import date

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

PASSW, DATABASE_URL = os.getenv("DBPASSW"), os.getenv("DB_URL")
