import discord

from bot.client_instance import get_client
from tools.checks import check_guild, check_forum_channel, check_thread
from settings.config import GUILD_ID, FORUM_CHANNEL_ID

async def get_thread_tag_ids(thread_id: int):
    """Retorna uma lista com os IDs e nomes das tags aplicadas a uma thread específica."""

    client = get_client()
    guild = check_guild(client, GUILD_ID)
    if not guild:
        return []

    forum_channel = check_forum_channel(guild, FORUM_CHANNEL_ID)
    if not forum_channel:
        return []

    # Primeiro, tentamos verificar se a thread existe
    thread, was_archived = await check_thread(forum_channel, thread_id)

    # Se não encontramos a thread (arquivada reaberta ou não),
    # retornamos uma lista vazia
    if not thread:
        return []

    # Obtendo as tags aplicadas à thread com 'applied_tags'
    tags = thread.applied_tags

    if not tags:
        return []
    
    if was_archived:
        await thread.edit(archived=True) # Fechando novamente thread arquivada
    
    # Retornando uma lista com os IDs e nomes das tags
    return [{'id': tag.id, 'name': tag.name, 'emoji': tag.emoji} for tag in tags]
