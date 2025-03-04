from forum_functions import get_forum_channel
from tools.checks import check_thread

async def get_users_message_count_in_thread(thread_id: int):
    """Retorna um dicionário com os IDs dos usuários e 
    a quantidade de mensagens que cada um enviou em uma thread específica."""

    # Primeiro, tentamos verificar se a thread existe
    try:
        forum_channel = get_forum_channel()
        thread, was_archived = await check_thread(forum_channel, thread_id)

        assert (forum_channel and thread)
    # Se não encontramos a thread (arquivada reaberta ou não),
    # retornamos um dicionário vazio
    except (AttributeError, AssertionError):
        return dict()

    user_message_count = {}

    # Obtendo todas as mensagens da thread
    # Limite pode ser alterado para evitar sobrecarga
    async for message in thread.history(limit=None):
        if message.author.bot:
            continue  # Ignora bots

        user_id = message.author.id
        if user_id not in user_message_count:
            user_message_count[user_id] = 0

        user_message_count[user_id] += 1
    
    if was_archived:
        await thread.edit(archived=True) # Fechando novamente thread arquivada

    return user_message_count

