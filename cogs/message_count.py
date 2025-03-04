import discord
from discord import app_commands
from discord.ext.commands import Cog, Bot

from forum_functions.count_messages import get_users_message_count_in_thread
from tools.checks import check_admin_role

class MessageCount(Cog):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot

    @app_commands.command(
                    name="contar_mensagens",
                    description="Mostra a quantidade de mensagens de um post.")
    async def message_count(self,
                            interaction: discord.Interaction,
                            thread_id: str) -> None:
        """Comando que retorna a quantidade de mensagens
        de cada usuário em uma thread específica."""

        # Verificar se o usuário possui a role de admin
        if not await check_admin_role(interaction):
            return
        
        try:
            # Converte o thread_id para inteiro, caso seja passado como string
            thread_id: int = int(thread_id)
        except ValueError:
            await (interaction
                   .response
                   .send_message("O ID da thread fornecido não é válido."))
            return

        user_message_count: (dict[int, int] | dict)
        user_message_count = await get_users_message_count_in_thread(thread_id)

        if not user_message_count:
            await (interaction
                   .response
                   .send_message("Não foi possível encontrar a thread"
                                 " ou não há mensagens de usuários nela."))
            return

        # Cria uma lista de respostas
        # para exibir a contagem de mensagens dos usuários
        message: str = "Contagem de mensagens por usuário na thread:\n"
        user_id: int
        count: int
        for user_id, count in user_message_count.items():
            user: discord.Member = await (interaction
                                          .guild
                                          .fetch_member(user_id))
            if user:
                message += f"{user.nick} (ID: {user_id}): {count} mensagens\n"

        await interaction.response.send_message(message)

# Função para adicionar a cog ao bot
async def setup(client: discord.Client) -> None:
    await client.add_cog(MessageCount(client))
