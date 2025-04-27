import discord
from discord import app_commands
from discord.ext import commands

from tools.checks import check_admin_role, check_monitor
from forum_functions.get_forum_posts_id import get_forum_posts
from forum_functions.get_thread_infos import get_thread_infos
from forum_functions.count_messages import get_users_message_count_in_thread
from tools.json_config import get_semester_and_year, load_json

class InsertHistory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="inserir_histórico", 
        description="Apaga o banco de dados e insere todo o histórico do servidor no banco de dados(comando de administrador).")
    async def insert_history(self, interaction: discord.Interaction):
        """Apaga o banco de dados e insere todo o histórico do servidor no banco de dados."""

        await interaction.response.defer()

        # Verificar se o usuário possui a role de admin
        if not await check_admin_role(interaction):
            return
        
        None # Resetar o Banco de dados

        posts_id = await get_forum_posts(interaction.guild_id)
        print(posts_id)

        try:
            for index, post_id in enumerate(posts_id, start=1):
                thread_info = await get_thread_infos(post_id) # Adicionar informações da thread no banco

                semester, year = get_semester_and_year(
                    interaction.guild_id, thread_info['created_at']) # Colocar a thread no semestre correto
                
                # Colocar os usuários que participaram da thread no banco
                users = await get_users_message_count_in_thread(post_id) 
                for user_id, _ in users.items():
                    try:
                        user = await interaction.guild.fetch_member(user_id)
                    except discord.NotFound:
                        print(f"Membro {user_id} não encontrado no servidor.")
                        continue  # Pular para o próximo usuário
                    
                    data = load_json()
                    server = data[str(interaction.guild_id)]
                    actual_year = server["YEAR"]
                    actual_semester = server["SEMESTER"]
                    if thread_info['owner_id'] == user:
                        continue # Usuário que criou a thread (post)
                    elif await check_monitor(user) and year == actual_year and semester == actual_semester:
                        None # Adicionar como monitor no banco
                    else:
                        None # Adicionar como usuário no banco (Semestres passados)

                print(f"Processando... \033[36mPost {index}\033[0m de {len(posts_id)}")
                print(f"\033[32mPost {post_id} adicionado com sucesso ao banco junto com suas informações.\033[0m")

        except Exception as e:
            print(e)

        await interaction.followup.send(
            "Banco de dados resetado e dados do histórico do servidor adicionados ao banco")

# Função para adicionar a cog ao bot
async def setup(client):
    await client.add_cog(InsertHistory(client))
