import discord
from discord import app_commands
from discord.ext import commands

from forum_functions.get_thread_tag import get_thread_tag_ids
from tools.checks import check_admin_role

class ThreadTags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ver_tags", description="Mostra os IDs e os nomes das tags de um post.")
    async def thread_tags(self, interaction: discord.Interaction, thread_id: str):
        """Comando que retorna os IDs e os nomes das tags de uma thread específica."""

        # Verificar se o usuário possui a role de admin
        if not await check_admin_role(interaction):
            return
        
        try:
            # Converte o thread_id para inteiro, caso seja passado como string
            thread_id = int(thread_id)
        except ValueError:
            await interaction.response.send_message("O ID da thread fornecido não é válido.")
            return

        tag_info = await get_thread_tag_ids(thread_id)

        if not tag_info:
            await interaction.response.send_message("Não foi possível encontrar a thread ou não há tags aplicadas nela.")
            return

        # Cria uma lista de respostas para exibir os IDs e nomes das tags
        message = "IDs e Nomes das tags aplicadas à thread:\n"
        for tag in tag_info:
            tag_id = tag['id']
            tag_name = tag['name']
            tag_emoji = tag['emoji']
            message += f"ID da tag: {tag_id}, {tag_emoji} Nome da tag: {tag_name}\n"

        await interaction.response.send_message(message)

# Função para adicionar a cog ao bot
async def setup(client):
    await client.add_cog(ThreadTags(client))
