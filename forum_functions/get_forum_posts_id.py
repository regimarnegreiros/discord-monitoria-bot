from forum_functions import get_forum_channel

async def get_forum_posts():
    """Retorna uma lista com o ID de todas as postagens dentro de um canal de fórum, incluindo arquivadas."""

    forum_channel = get_forum_channel()

    if not forum_channel:
        return list()

    # Obtém as threads ativas
    post_ids = [thread.id for thread in forum_channel.threads]

    # Obtém threads arquivadas
    async for thread in forum_channel.archived_threads(limit=None):
        post_ids.append(thread.id)

    return post_ids
