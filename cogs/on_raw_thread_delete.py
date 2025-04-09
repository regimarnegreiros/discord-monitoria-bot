import discord
from discord import app_commands
from discord.ext import commands
from database.data.db_funcs import db_thread_delete

from forum_functions.get_thread_infos import get_thread_infos
from tools.checks import check_thread_object


class OnRawThreadDelete(commands.Cog):
    """Classe que lida com eventos relacionados à exclusão de threads."""

    def __init__(self, client):
        self.client = client
        super().__init__()

    @commands.Cog.listener()
    async def on_raw_thread_delete(self, payload: discord.RawThreadDeleteEvent):
        """Escuta o evento de exclusão de thread e realiza ações associadas."""

        if not await check_thread_object(payload.thread):
            print("Thread não pertence ao servidor e canal de fórum especificados.")
            return

        # Removerá as informações da thread no banco de dados (Necessário implementar ainda)
        thread_infos = await get_thread_infos(payload.thread)
        await db_thread_delete(thread_infos["id"])
        print(f"Informações removidas do banco:\n{thread_infos}")


async def setup(client):
    await client.add_cog(OnRawThreadDelete(client))
