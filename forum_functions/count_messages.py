import discord

from bot.client_instance import get_client
from tools.checks import check_guild, check_forum_channel, check_thread, check_archived_thread
from settings.config import GUILD_ID, FORUM_CHANNEL_ID

async def get_users_message_count_in_thread(thread_id: int):
    """Retorna um dicionário com os IDs dos usuários e a quantidade de mensagens que cada um enviou em uma thread específica."""

    client = get_client()
    guild = check_guild(client, GUILD_ID)
    if not guild:
        return {}

    forum_channel = check_forum_channel(guild, FORUM_CHANNEL_ID)
    if not forum_channel:
        return {}

    # Primeiro, tentamos verificar se a thread existe
    thread = check_thread(forum_channel, thread_id)
    
    if not thread:
        # Se não encontramos a thread ativa, verificamos se ela está arquivada
        archived_thread = await check_archived_thread(forum_channel, thread_id)

        if not archived_thread:
            print(f"Thread {thread_id} não encontrada ou arquivada.")
            return {}

        # Se a thread está arquivada, tentamos reabri-la
        await archived_thread.edit(archived=False)
        print(f"A thread {thread_id} foi reaberta para acessar o histórico de mensagens.")
        thread = archived_thread  # Atualizando thread para ser a thread reaberta

    # Se não encontramos nem a thread nem a thread arquivada reaberta, retornamos um dicionário vazio
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

    return user_message_count

