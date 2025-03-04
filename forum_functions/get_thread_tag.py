import discord

from forum_functions import get_forum_channel
from tools.checks import check_thread, check_archived_thread
from settings.config import GUILD_ID, FORUM_CHANNEL_ID

async def get_thread_tag_ids(thread_id: int):
    """Retorna uma lista com os IDs e nomes das tags aplicadas a uma thread específica."""

    forum_channel = get_forum_channel()

    if not forum_channel:
        return list()

    thread, was_archived = await check_thread(forum_channel, thread_id)
    
    # Se não encontramos a thread (arquivada reaberta ou não), retornamos uma lista vazia
    if not thread:
        return []

    # Obtendo as tags aplicadas à thread com 'applied_tags'
    tags = thread.applied_tags

    if was_archived:
        await thread.edit(archived=True) # Fechando novamente thread arquivada

    if not tags:
        return []
    
    # Retornando uma lista com os IDs e nomes das tags
    return [{'id': tag.id, 'name': tag.name, 'emoji': tag.emoji} for tag in tags]
