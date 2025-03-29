import os
from os import sep as SEP
from sys import stderr
from dotenv import load_dotenv

WD: str
DBWD: str
files: list[str]
PASSW: str | None
DATABASE_URL: str | None

def eprint(*args, **kwargs) -> None:
    print(*args, file=stderr, **kwargs)

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
