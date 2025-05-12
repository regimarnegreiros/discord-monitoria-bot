import discord
from discord import app_commands
from discord.ext import commands

from forum_functions.get_thread_infos import get_thread_infos
from tools.checks import check_admin_role

class ThreadInfos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ver_post_infos", description="Mostra as informações de um post. (Admin)")
    async def thread_infos(self, interaction: discord.Interaction, thread_id: str):
        """Comando que retorna as informações de uma thread específica."""

        # Verificar se o usuário possui a role de admin
        if not await check_admin_role(interaction):
            return
        
        try:
            # Converte o thread_id para inteiro, caso seja passado como string
            thread_id = int(thread_id)
        except ValueError:
            await interaction.response.send_message("O ID da thread fornecido não é válido.")
            return

        thread_info = await get_thread_infos(thread_id)

        # Verifica se as informações da thread foram encontradas
        if not thread_info:
            await interaction.response.send_message("Não foi possível encontrar a thread ou ela não existe.")
            return

        # Criação da mensagem com as informações da thread
        message = f"**Título da Thread:** {thread_info['name']}\n"
        message += f"**ID da Thread**: {thread_info['id']}\n"
        message += f"**Criada em**: {thread_info['created_at']} UTC\n"
        message += f"**Dono**: {thread_info['owner'].nick} (ID: {thread_info['owner_id']})\n"
        message += f"**Tipo**: {thread_info['type']}\n"

        # Adiciona informações sobre as tags, se houverem
        if thread_info['applied_tags']:
            message += "\n**Tags Aplicadas**:\n"
            for tag in thread_info['applied_tags']:
                message += f"ID da tag: {tag['id']}, Nome da tag: {tag['emoji']} {tag['name']}\n"
        else:
            message += "\nNão há tags aplicadas nesta thread."

        await interaction.response.send_message(message)

# Função para adicionar a cog ao bot
async def setup(client):
    await client.add_cog(ThreadInfos(client))
