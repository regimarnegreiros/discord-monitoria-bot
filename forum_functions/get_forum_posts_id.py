import discord

from bot.client_instance import get_client
from tools.checks import check_guild, check_forum_channel

async def get_forum_posts(guild_id: int, forum_id: int):
    """Retorna uma lista com o ID de todas as postagens dentro de um canal de fórum, incluindo arquivadas."""

    client = get_client()
    guild = check_guild(client, guild_id)
    if not guild:
        return []

    forum_channel = check_forum_channel(guild, forum_id)
    if not forum_channel:
        return []

    # Obtém as threads ativas
    post_ids = [thread.id for thread in forum_channel.threads]

    # Obtém threads arquivadas
    async for thread in forum_channel.archived_threads(limit=None):
        post_ids.append(thread.id)

    return post_ids
