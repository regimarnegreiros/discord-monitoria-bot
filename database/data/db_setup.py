import os
from os import sep as SEP
from shutil import which
from sys import stderr
from dotenv import load_dotenv

def eprint(*args, **kwargs):
    print(*args, file=stderr, **kwargs)

WD = (os.path.dirname(os.path.abspath(__file__))
            .removesuffix(f"{SEP}database{SEP}data") + SEP)
DBWD = f"{WD}database{SEP}"

if not load_dotenv(dotenv_path=f"{WD}settings{SEP}.env"):
    eprint("error loading environment variables")
    exit(1)

if not which("psql"):
    eprint("PostgreSQL not installed or not in PATH")
    exit(1)

PASSW = os.getenv("PASSW")

CMD = "psql -U monitor_admin -d db_monitoring"

if os.system("createdb -O monitor_admin db_monitoring"):
    eprint("db already exists, regenerating defaults")
    os.system("dropdb db_monitoring")
    os.system("dropuser monitor_admin")
    os.system("createuser -s monitor_admin")
    os.system("createdb -O monitor_admin db_monitoring")

os.system("createuser -s monitor_admin")
if os.name == "nt":
    os.system(f"SET PGPASSWORD=\"{PASSW}\"")
else:
    os.system(f"export PGPASSWORD=\"{PASSW}\"")

os.system(f"{CMD} -c "
          f"\"ALTER USER monitor_admin WITH PASSWORD '{PASSW}';\"")

files = [dir_contents[0] + SEP + file for dir_contents in os.walk(DBWD)
         for file in dir_contents[2] if file.endswith(".sql")]
files.sort(key=lambda file: file[file.rindex(SEP) + 1])

for file in files:
    os.system(f"{CMD} -f {file}")
