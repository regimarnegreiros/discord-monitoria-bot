import db_commons as com
import os
from shutil import which
import sqlalchemy as sql
from sqlalchemy import text

if os.name == "posix":
    CMD = "sudo -u postgres psql -U postgres -c "
else:
    CMD = f"psql postgres://postgres:{com.PASSW}@localhost:5432/postgres -c "

if not which("psql"):
    com.eprint("PostgreSQL not installed or not in PATH")
    exit(1)

if os.name == "posix":
    SHUTUP: str = ">/dev/null 2>&1"
    hba_line_old: str = ("local   all             all"
                         "                                     peer")
    hba_line_new: str = ("local   all             all"
                         "                                     scram-sha-256")
    hba_file: str = os.popen("sudo -u postgres psql -t -P format=unaligned"
                             " -c \"SHOW hba_file;\"").read()

    os.system(f"sudo sed -i '/{hba_line_old}/c\\{hba_line_new}' {hba_file}")
    os.system(f"systemctl --version {SHUTUP}"
              " && sudo systemctl restart postgresql"
              "|| /etc/init.d/postgresql restart")
    
    del SHUTUP, hba_line_new, hba_line_old, hba_file

os.system(CMD + "\"CREATE USER monitor_admin"
          f" WITH ENCRYPTED PASSWORD '{com.PASSW}';\"")
os.system(CMD + "\"CREATE DATABASE db_monitoring;\"")

# GRANTS
os.system(CMD + "\"ALTER DATABASE db_monitoring OWNER TO monitor_admin;\"")
os.system(CMD + "\"GRANT ALL PRIVILEGES ON DATABASE db_monitoring"
                " TO monitor_admin WITH GRANT OPTION;\"")
os.system(CMD + "\"GRANT ALL PRIVILEGES ON SCHEMA public"
                " TO monitor_admin;\"")
os.system(CMD + "\"GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public"
                " TO monitor_admin;\"")
os.system(CMD + "\"GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public"
                " TO monitor_admin;\"")

DATABASE_URL = com.DATABASE_URL.replace("asyncpg", "psycopg2")
engine: sql.Engine = sql.create_engine(DATABASE_URL)
with engine.connect() as con:
    for file in com.files:
        with open(file, encoding="utf-8") as query:
            con.execute(text(query.read()))
            con.commit()
engine.dispose()
