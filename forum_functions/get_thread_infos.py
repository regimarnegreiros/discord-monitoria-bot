import discord

from tools.checks import check_guild_forum_thread


async def get_thread_infos(thread_or_id):
    """Retorna um dicionário com informações sobre a thread especificada.

    Esta função funciona tanto com um ID de thread (int ou str) quanto com um 
    objeto `discord.Thread`. Se um ID for fornecido, a função buscará o 
    objeto da thread. Se um objeto `discord.Thread` for passado, a função 
    o utilizará diretamente.

    Args:
        thread_or_id (Union[int, str, discord.Thread]): O ID da thread ou 
                                                      um objeto `discord.Thread`.

    Returns:
        dict: Um dicionário contendo informações sobre a thread, como 
              tags aplicadas, data de criação, dono e tipo.
    
    Raises:
        ValueError: Se a entrada não for nem um ID de thread válido nem um 
                    objeto `discord.Thread`.
    """
    # Se a entrada for um objeto discord.Thread, usamos ele diretamente
    if isinstance(thread_or_id, discord.Thread):
        thread = thread_or_id
        was_archived = False  # Definimos como False caso seja um objeto de thread diretamente
    # Se a entrada for um ID de thread (int ou str), buscamos o objeto da thread
    elif isinstance(thread_or_id, (int, str)):
        thread, was_archived = await check_guild_forum_thread(thread_or_id)
    else:
        raise ValueError("O parâmetro deve ser um objeto discord.Thread ou um ID de thread.")

    # Se a thread não for encontrada, retornamos um dicionário vazio
    if not thread:
        return {}

    # Obtendo as tags aplicadas à thread
    tags = thread.applied_tags

    # Se a thread estava arquivada, reabrimos ela
    if was_archived:
        await thread.edit(archived=True)  # Reabre a thread arquivada
    
    # Retorna um dicionário com as informações da thread
    return {
        'applied_tags': [{
            'id': tag.id,
            'name': tag.name,
            'emoji': tag.emoji,
            'moderated': tag.moderated
        } for tag in tags] if tags else [],
        'created_at': thread.created_at,
        'id': thread.id,
        'name': thread.name,
        'owner': thread.owner,
        'owner_id': thread.owner_id,
        'type': thread.type
    }
