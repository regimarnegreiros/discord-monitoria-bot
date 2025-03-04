import discord

from tools.checks import check_guild_forum_thread

async def get_thread_tag_ids(thread_id: int):
    """Retorna uma lista com os IDs e nomes das tags aplicadas a uma thread específica."""

    # Primeiro, tentamos verificar se a thread existe
    thread, was_archived = await check_guild_forum_thread(thread_id)
    
    # Se não encontramos a thread (arquivada aberta ou não), retornamos um dicionário vazio
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