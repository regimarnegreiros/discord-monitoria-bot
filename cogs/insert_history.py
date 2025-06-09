import discord
from discord import app_commands
from discord.ext import commands

from tools.checks import check_admin_role, check_monitor
from forum_functions.get_forum_posts_id import get_forum_posts
from forum_functions.get_thread_infos import get_thread_infos
from forum_functions.count_messages import get_users_message_count_in_thread
from tools.json_config import get_semester_and_year, load_json
import database.data.db_funcs as db
from database.data.db_commons import MONITORS_OLD # a ser substituido no config.json
from asyncio import sleep
from datetime import datetime
from datetime import timedelta

class InsertHistory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="inserir_histórico", 
        description="Reseta o banco de dados e insere o histórico completo do servidor. (Admin)")
    async def insert_history(self, interaction: discord.Interaction):
        """Apaga o banco de dados e insere todo o histórico do servidor no banco de dados."""

        start: datetime = datetime.now()
        td: timedelta

        # Verificar se o usuário possui a role de admin
        if not await check_admin_role(interaction):
            return
        
        await interaction.response.defer()
        progress_message = await interaction.followup.send("🎲 Resetando banco de dados...")

        data = load_json()
        server = data[str(interaction.guild_id)]
        current_year = server["YEAR"]
        current_semester = server["SEMESTER"]

        await db.db_nuke() # Reseta o Banco de dados

        posts_id = await get_forum_posts(interaction.guild_id)
        semester, year = 0, 0

        try:
            for index, post_id in enumerate(posts_id, start=1):
                td = datetime.now() - start
                curr_fmt: str = f"{f'{td.min} min ' if td.min else ''}{td.seconds:.2f} seg"
                await progress_message.edit(
                    content=f"📄 Processando post {index} de {len(posts_id)} (ID: {post_id})"
                            f"⏱️\n(tempo decorrido: {curr_fmt})..."
                )
                print(f"Processando... \033[36mPost {index}\033[0m de {len(posts_id)}")
                print("Extraindo thread...")

                thread_info = await get_thread_infos(post_id)
                tags: list[int] = [tags["id"] for tags in thread_info["applied_tags"]]
                await sleep(1)

                semester_temp, year_temp = get_semester_and_year(
                    interaction.guild_id, thread_info['created_at']) # Colocar a thread no semestre correto

                if (semester_temp, year_temp) != (semester, year):
                    await db.db_new_semester(semester_temp, year_temp)

                    semester, year = semester_temp, year_temp
                    is_current_semester = (
                        year == current_year
                        and semester == current_semester
                    )
                    monitor_info = MONITORS_OLD.get(year, {}).get(semester, [])

                # Adicionar informações da thread no banco
                await db.db_thread_create(
                    thread_info["id"], thread_info["owner_id"],
                    *tags, timestamp=thread_info["created_at"])

                # Colocar os usuários que participaram da thread no banco
                users = await get_users_message_count_in_thread(post_id)
                not_users: set[int] = set()
                await sleep(1)

                for user_id in users.keys():
                    try:
                        user = await interaction.guild.fetch_member(user_id)
                    except discord.NotFound:
                        print(f"Membro {user_id} não encontrado no servidor.")
                        not_users.add(user_id)
                        continue  # Pular para o próximo usuário

                    if thread_info['owner_id'] == user.id:
                        continue # Usuário que criou a thread (post)
                    elif ((await check_monitor(user)
                          and is_current_semester)
                          or (not is_current_semester
                              and user_id in monitor_info)):
                        # Adicionar como monitor no banco
                        await db.db_new_user(
                            user.id, is_creator=False, is_monitor=True)
                    else:
                        # Adicionar como usuário no banco (Semestres passados)
                        await db.db_new_user(
                            user.id, is_creator=False, is_monitor=False)

                await db.db_thread_answered(
                    post_id, users=(set(users.keys()) - not_users),
                    semester_pair=(semester, year)
                )

                print(f"\033[32mPost {post_id} adicionado com sucesso ao banco.\033[0m")

        except Exception as e:
            await progress_message.edit(
                content="❌ Banco de dados resetado; houve erro na inserção de dados."
            )
        else:
            end: datetime = datetime.now()
            td = end - start
            td_fmt: str = f"{f'{td.min} min ' if td.min else ''}{td.seconds:.2f} seg"
            await progress_message.edit(
                content="✅ Banco de dados resetado e histórico inserido com sucesso!"
                        f" concluido em {td_fmt}"
            )

# Função para adicionar a cog ao bot
async def setup(client):
    await client.add_cog(InsertHistory(client))
