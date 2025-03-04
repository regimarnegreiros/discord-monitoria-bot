from discord import Client, Guild, ForumChannel, Thread

from bot.client_instance import get_client
from tools.checks import check_guild, check_forum_channel
from settings.config import GUILD_ID, FORUM_CHANNEL_ID

async def get_forum_posts() -> (list[int] | list):
    """Retorna uma lista com o ID de todas as postagens
    dentro de um canal de fórum, incluindo arquivadas."""

    client: Client = get_client()
    guild: (Guild | None) = check_guild(client, GUILD_ID)
    if not guild:
        return []

    forum_channel: (ForumChannel | None) = check_forum_channel(
                                            guild, FORUM_CHANNEL_ID)
    if not forum_channel:
        return []

    # Obtém as threads ativas
    post_ids: list[int] = [thread.id for thread in forum_channel.threads]

    # Obtém threads arquivadas
    thread: Thread
    async for thread in forum_channel.archived_threads(limit=None):
        post_ids.append(thread.id)

    return post_ids