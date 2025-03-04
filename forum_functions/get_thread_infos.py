from discord import Thread, PartialEmoji, Member, ChannelType, ForumTag
from datetime import datetime
from tools.checks import check_guild_forum_thread

type AppliedTags = dict[str, int | str | (PartialEmoji | None) | bool]
type TagInfo = dict[
    str, ((list[AppliedTags] | list) | (datetime | None)
          | int | str | (Member | None) | ChannelType)
]

async def get_thread_infos(
        thread_id: int) -> (dict | TagInfo):
    """Retorna um dicionário com informações da thread específica."""

    # Primeiro, tentamos verificar se a thread existe
    thread: (Thread | None)
    was_archived: bool 
    thread, was_archived = await check_guild_forum_thread(thread_id)
    
    # Se não encontramos a thread (arquivada aberta ou não),
    # retornamos um dicionário vazio
    if not thread:
        return {}

    # Obtendo as tags aplicadas à thread
    tags: list[ForumTag] = thread.applied_tags

    if was_archived:
        await thread.edit(archived=True) # Fechando novamente thread arquivada
    
    return {
        'applied_tags': [{
            'id': tag.id,
            'name': tag.name,
            'emoji': tag.emoji,
            'moderatade': tag.moderated
        } for tag in tags] if tags else [],
        'created_at': thread.created_at,
        'id': thread.id,
        'name': thread.name,
        'owner': thread.owner,
        'owner_id': thread.owner_id,
        'type': thread.type
    }
