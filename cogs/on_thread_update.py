import discord
from discord.ext import commands

from forum_functions.get_thread_infos import get_thread_infos
from tools.checks import check_thread_object
from database.data.db_funcs import db_thread_update

class OnThreadUpdate(commands.Cog):
    """Classe que lida com eventos relacionados à atualização de threads."""

    def __init__(self, client):
        self.client = client
        super().__init__()

    @commands.Cog.listener()
    async def on_thread_update(self, before: discord.Thread, after: discord.Thread):
        """Escuta o evento de atualização de thread e realiza ações associadas."""

        # Verificando se a thread foi arquivada ou desarquivada
        if before.archived != after.archived:
            # A mudança não foi relacionada a arquivar ou desarquivar, portanto, ignorar.
            return
        if not await check_thread_object(after):
            # Thread não pertence ao servidor e canal de fórum especificados.
            return

        # Obter informações atuais da thread no Discord
        thread_infos = await get_thread_infos(after)
        print(f"Novas informações da thread:\n{thread_infos}")

        # Buscar as tags e resolução da thread no banco de dados
        await db_thread_update(after.id,
                         *[tag["id"] for tag in thread_infos["applied_tags"]])

        # Comparar as tags (matérias) atuais da thread com as tags do banco
            # Se as tags (matérias) mudaram, atualizar as informações no banco para refletir a alteração

        # Comparar o status de resolução da thread com o banco
            # Se a thread (dúvida) foi resolvida (tag resolvida adicionada), atualizar as informações no banco para refletir a alteração
            # Se a tag resolvida for removida, atualizar as informações da thread (dúvida) no banco para refletir a alteração


async def setup(client):
    await client.add_cog(OnThreadUpdate(client))
