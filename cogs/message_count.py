import discord
from discord import app_commands
from discord.ext import commands

from forum_functions.count_messages import get_users_message_count_in_thread
from settings.config import FORUM_CHANNEL_ID, GUILD_ID

class MessageCount(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="contar_mensagens", description="Mostra a quantidade de mensagens de um post.")
    async def message_count(self, interaction: discord.Interaction, thread_id: str):
        """Comando que retorna a quantidade de mensagens de cada usuário em uma thread específica."""
        
        try:
            # Converte o thread_id para inteiro, caso seja passado como string
            thread_id = int(thread_id)
        except ValueError:
            await interaction.response.send_message("O ID da thread fornecido não é válido.")
            return

        guild_id = GUILD_ID
        user_message_count = await get_users_message_count_in_thread(guild_id, FORUM_CHANNEL_ID, thread_id)

        if not user_message_count:
            await interaction.response.send_message("Não foi possível encontrar a thread ou não há mensagens de usuários nela.")
            return

        # Cria uma lista de respostas para exibir a contagem de mensagens dos usuários
        message = "Contagem de mensagens por usuário na thread:\n"
        for user_id, count in user_message_count.items():
            user = await interaction.guild.fetch_member(user_id)
            if user:
                message += f"{user.nick} (ID: {user_id}): {count} mensagens\n"

        await interaction.response.send_message(message)

# Função para adicionar a cog ao bot
async def setup(client):
    await client.add_cog(MessageCount(client))
