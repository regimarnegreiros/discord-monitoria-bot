import discord
from discord.ext import commands
from discord import app_commands

from tools.checks import check_thread_object, check_monitor

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
        
        # Verificar se o membro que enviou a mensagem é um monitor
        if await check_monitor(message.author):
            member_id = message.author.id
            print(f"Usuário monitor identificado: {message.author} (ID: {member_id})")
            # Aqui você pode colocar o ID no banco ou realizar outras ações se for monitor
        else:
            print(f"Usuário {message.author} não é monitor.")
            # Aqui você pode colocar o ID no banco ou realizar outras ações não for monitor

async def setup(client):
    await client.add_cog(OnMessage(client))
