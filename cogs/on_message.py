import discord
from discord.ext import commands
from discord import app_commands

from tools.checks import check_thread_object, check_monitor
from database.data.db_funcs import db_new_user, db_thread_answered

class OnMessage(commands.Cog):
    """Classe que lida com eventos relacionados ao envio de mensagens."""

    def __init__(self, client):
        self.client = client
        super().__init__()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Escuta o evento de criação de mensagem e realiza ações associadas."""

        if not message.thread:
            return

        thread = message.thread
        if not await check_thread_object(thread):
            return

        if message.author == thread.owner:
            print(f"Usuário {message.author} é o criador da thread.")
            # Colocar aqui a lógica específica para quando o usuário for o criador da thread.
            return

        is_monitor = await check_monitor(message.author)

        # Verificar se o membro que enviou a mensagem é um monitor
        if is_monitor:
            member_id = message.author.id
            print(f"Usuário monitor identificado: {message.author} (ID: {member_id})")
        else:
            print(f"Usuário {message.author} não é monitor.")
            # Aqui você pode colocar o ID no banco ou realizar outras ações não for monitor

        await db_new_user(member_id, is_creator=False, is_monitor=is_monitor)
        await db_thread_answered(thread.id)

async def setup(client):
    await client.add_cog(OnMessage(client))
