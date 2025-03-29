import discord
from discord.ext import commands
from discord import app_commands

from forum_functions.get_thread_infos import get_thread_infos
from tools.checks import check_thread_object


class OnThreadCreate(commands.Cog):
    """Classe que lida com eventos relacionados à criação de threads."""

    def __init__(self, client):
        self.client = client
        super().__init__()

    @commands.Cog.listener()
    async def on_thread_create(self, thread: discord.Thread):
        """Escuta o evento de criação de thread e realiza ações associadas."""

        if not await check_thread_object(thread):
            print("Thread não pertence ao servidor e canal de fórum especificados.")
            return

        # Adicionará as informações da thread no banco de dados (Necessário implementar ainda)
        thread_infos = await get_thread_infos(thread.id)
        print(f"Informações adicionadas ao banco:\n{thread_infos}")


async def setup(client):
    await client.add_cog(OnThreadCreate(client))
