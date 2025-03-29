import db_commons as com
import os
from shutil import which
import sqlalchemy as sql
from sqlalchemy import text

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

os.system(f"{"sudo -u postgres " if os.name == "posix" else ""}psql -c "
          "\"CREATE USER monitor_admin"
          f" WITH ENCRYPTED PASSWORD '{com.PASSW}';\"")
os.system(f"{"sudo -u postgres " if os.name == "posix" else ""}psql -c "
          "\"CREATE DATABASE db_monitoring;\"")

# GRANTS
os.system(f"{"sudo -u postgres " if os.name == "posix" else ""}psql -c "
          "\"ALTER DATABASE db_monitoring OWNER TO monitor_admin;\"")
os.system(f"{"sudo -u postgres " if os.name == "posix" else ""}psql -c "
          "\"GRANT ALL PRIVILEGES ON DATABASE db_monitoring"
          " TO monitor_admin WITH GRANT OPTION;\"")
os.system(f"{"sudo -u postgres " if os.name == "posix" else ""}psql -c "
          "\"GRANT ALL PRIVILEGES ON SCHEMA public"
          " TO monitor_admin;\"")
os.system(f"{"sudo -u postgres " if os.name == "posix" else ""}psql -c "
          "\"GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public"
          " TO monitor_admin;\"")
os.system(f"{"sudo -u postgres " if os.name == "posix" else ""}psql -c "
          "\"GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public"
          " TO monitor_admin;\"")

engine: sql.Engine = sql.create_engine(com.DATABASE_URL)
with engine.connect() as con:
    for file in com.files:
        with open(file) as query:
            con.execute(text(query.read()))
engine.dispose()
