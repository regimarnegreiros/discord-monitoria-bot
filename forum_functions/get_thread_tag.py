import discord

from forum_functions import get_forum_channel
from tools.checks import check_thread, check_archived_thread
from settings.config import GUILD_ID, FORUM_CHANNEL_ID

async def get_thread_tag_ids(thread_id: int):
    """Retorna uma lista com os IDs e nomes das tags aplicadas a uma thread específica."""

    forum_channel = get_forum_channel()

    if not forum_channel:
        return list()

    # Primeiro, tentamos verificar se a thread existe
    thread = check_thread(forum_channel, thread_id)
    
    if not thread:
        # Se não encontramos a thread ativa, verificamos se ela está arquivada
        archived_thread = await check_archived_thread(forum_channel, thread_id)

        if not archived_thread:
            print(f"Thread {thread_id} não encontrada ou arquivada.")
            return []

        # Se a thread está arquivada, tentamos reabri-la
        await archived_thread.edit(archived=False)
        print(f"A thread {thread_id} foi reaberta para acessar as tags.")
        thread = archived_thread  # Atualizando thread para ser a thread reaberta

    # Se não encontramos nem a thread nem a thread arquivada reaberta, retornamos uma lista vazia
    if not thread:
        return []

    # Obtendo as tags aplicadas à thread com 'applied_tags'
    tags = thread.applied_tags

    if not tags:
        return []
    
    # Retornando uma lista com os IDs e nomes das tags
    return [{'id': tag.id, 'name': tag.name, 'emoji': tag.emoji} for tag in tags]
