import discord

from forum_functions import get_forum_channel
from tools.checks import check_thread, check_archived_thread
from settings.config import GUILD_ID, FORUM_CHANNEL_ID

async def get_users_message_count_in_thread(thread_id: int):
    """Retorna um dicionário com os IDs dos usuários e a quantidade de mensagens que cada um enviou em uma thread específica."""

    forum_channel = get_forum_channel()

    if not forum_channel:
        return {}

    # Primeiro, tentamos verificar se a thread existe
    thread, was_archived = await check_thread(forum_channel, thread_id)
    
    # Se não encontramos a thread (arquivada reaberta ou não), retornamos um dicionário vazio
    if not thread:
        return {}

    user_message_count = {}

    # Obtendo todas as mensagens da thread
    async for message in thread.history(limit=None):  # Limite pode ser alterado para evitar sobrecarga
        if message.author.bot:
            continue  # Ignora bots

        user_id = message.author.id
        if user_id not in user_message_count:
            user_message_count[user_id] = 0

        user_message_count[user_id] += 1
    
    if was_archived:
        await thread.edit(archived=True) # Fechando novamente thread arquivada

    return user_message_count

