import discord

from bot.client_instance import get_client
from tools.checks import check_guild, check_forum_channel
from settings.config import GUILD_ID, FORUM_CHANNEL_ID

async def get_forum_posts():
    """Retorna uma lista com o ID de todas as postagens dentro de um canal de fórum, incluindo arquivadas."""

    client = get_client()
    guild = check_guild(client, GUILD_ID)
    if not guild:
        return []

    forum_channel = check_forum_channel(guild, FORUM_CHANNEL_ID)
    if not forum_channel:
        return []

    # Obtém as threads ativas
    post_ids = [thread.id for thread in forum_channel.threads]

    # Obtém threads arquivadas
    async for thread in forum_channel.archived_threads(limit=None):
        post_ids.append(thread.id)

    return post_ids
