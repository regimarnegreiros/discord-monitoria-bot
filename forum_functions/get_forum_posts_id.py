import discord
from tools.json_config import load_json

from bot.client_instance import get_client
from tools.checks import check_guild, check_forum_channel

async def get_forum_posts(guild_id):
    """Retorna uma lista com o ID de todas as postagens
    dentro de um canal de fórum, incluindo arquivadas,
    ordenadas por data de criação."""
    
    # Carregar as configurações do JSON
    data = load_json()

    # Obter o canal de fórum associado ao servidor fornecido
    forum_channel_id = data.get(str(guild_id), {}).get("FORUM_CHANNEL_ID")

    if not forum_channel_id:
        return []

    client = get_client()
    guild = check_guild(client, guild_id)
    if not guild:
        return []

    forum_channel = check_forum_channel(guild, forum_channel_id)
    if not forum_channel:
        return []

    # Obtém as threads ativas
    post_ids = [(thread.id, thread.created_at) for thread in forum_channel.threads]

    # Obtém threads arquivadas
    async for thread in forum_channel.archived_threads(limit=None):
        post_ids.append((thread.id, thread.created_at))
    
    post_ids = [post[0] for post in sorted(post_ids, key=lambda elem: elem[1])]

    return post_ids
