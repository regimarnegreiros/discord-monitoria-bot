from forum_functions import get_forum_channel
from tools.checks import check_thread

async def get_thread_tag_ids(thread_id: int):
    """Retorna uma lista com os IDs e nomes 
    das tags aplicadas a uma thread específica."""

    try:
        forum_channel = get_forum_channel()
        thread, was_archived = await check_thread(forum_channel, thread_id)
        
        # Obtendo as tags aplicadas à thread com 'applied_tags'
        tags = thread.applied_tags

        assert (forum_channel and thread and tags)
    # Se não encontramos a thread (arquivada reaberta ou não),
    # retornamos uma lista vazia
    except (AttributeError, AssertionError):
        return list()

    if was_archived:
        await thread.edit(archived=True) # Fechando novamente thread arquivada
    
    # Retornando uma lista com os IDs e nomes das tags
    return [{
                'id': tag.id,
                'name': tag.name,
                'emoji': tag.emoji
            } for tag in tags]
