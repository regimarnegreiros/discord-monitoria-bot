import discord

from bot.client_instance import get_client

async def get_forum_posts(guild_id: int, forum_id: int):
    """Retorna uma lista com o ID de todas as postagens dentro de um canal de fórum, incluindo arquivadas."""

    client = get_client()
    guild = client.get_guild(guild_id)
    if not guild:
        print("O bot não está no servidor especificado!")
        return []

    forum_channel = guild.get_channel(forum_id)
    if not forum_channel or not isinstance(forum_channel, discord.ForumChannel):
        print("Canal inválido ou não é um fórum.")
        return []

    # Obtém as threads ativas
    post_ids = [thread.id for thread in forum_channel.threads]

    # Obtém threads arquivadas
    async for thread in forum_channel.archived_threads(limit=None):
        post_ids.append(thread.id)

    return post_ids
