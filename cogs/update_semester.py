import discord
from discord.ext import commands, tasks
from datetime import datetime, time
from zoneinfo import ZoneInfo

from tools.json_config import load_json, save_json

TZINFO = ZoneInfo("America/Sao_Paulo")

class UpdateSemester(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.verify_semester.start()

    @tasks.loop(time=time(hour=12, minute=00, tzinfo=TZINFO))
    async def verify_semester(self):
        now = datetime.now(TZINFO)
        data = load_json()

        for guild_id, config in data.items():
            if guild_id == "bot_status":
                continue

            sem1 = config.get("SEMESTER_1_START", {"day": 20, "month": 1})
            sem2 = config.get("SEMESTER_2_START", {"day": 15, "month": 7})

            current_year = now.year
            start_1 = datetime(current_year, sem1["month"], sem1["day"],
                               tzinfo=TZINFO)
            start_2 = datetime(current_year, sem2["month"], sem2["day"],
                               tzinfo=TZINFO)

            if now < start_1:
                new_semester = 2
                new_year = current_year - 1
            elif start_1 <= now < start_2:
                new_semester = 1
                new_year = current_year
            else:
                new_semester = 2
                new_year = current_year

            old_semester = config.get("SEMESTER")
            old_year = config.get("YEAR")

            if old_semester != new_semester or old_year != new_year:
                config["SEMESTER"] = new_semester
                config["YEAR"] = new_year
                print(f"Servidor {guild_id}: Semestre atualizado para {new_semester}/{new_year}")

        save_json(data)

    @verify_semester.before_loop
    async def before_verify_semester(self):
        await self.client.wait_until_ready()

async def setup(client):
    await client.add_cog(UpdateSemester(client))
