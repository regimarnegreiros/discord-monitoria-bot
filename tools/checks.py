import discord
from discord import (
    TextChannel, ForumChannel, 
    Interaction, Guild, Thread, Member
)

from bot.client_instance import get_client
from tools.json_config import load_json, get_first_server_id

# Função auxiliar para obter as configurações de um servidor
def get_server_config(guild_id):
    data = load_json()
    return data.get(str(guild_id), None)

# Função para verificar se o bot está no servidor
def check_guild(client, guild_id) -> (Guild | None):
    guild = client.get_guild(guild_id)
    if not guild:
        print("O bot não está no servidor especificado!")
        return None
    return guild

# Função para verificar se o canal é válido e é um canal de texto
def check_channel(guild, channel_id) -> (TextChannel | None):
    channel = guild.get_channel(channel_id)
    if not channel or not isinstance(channel, TextChannel):
        print("Canal inválido ou não é um canal de texto.")
        return None
    return channel

# Função para verificar se o canal é um fórum
def check_forum_channel(guild, forum_id) -> (ForumChannel | None):
    forum_channel = guild.get_channel(forum_id)
    if not forum_channel or not isinstance(forum_channel, ForumChannel):
        print("Canal inválido ou não é um fórum.")
        return None
    return forum_channel

# Função para verificar se a thread existe no canal
async def check_thread(forum_channel, thread_id) -> (tuple[(Thread | None), bool]):
    thread = forum_channel.get_thread(thread_id)
    was_archived = False

    if not thread:
        # print("Thread não encontrada. Buscando threads arquivadas")
        archived_threads = {
            thread.id: thread async for thread in forum_channel.archived_threads(limit=None)
        }
        thread = archived_threads.get(thread_id)

        if not thread:
            # print("Thread não encontrada.")
            return (None, was_archived)

        # print(f"Thread arquivada encontrada: {thread_id}")
        await thread.edit(archived=False)
        # print(f"A thread {thread_id} foi reaberta para acessar o histórico de mensagens.")
        was_archived = True

    return (thread, was_archived)

# Verifica se a thread está num fórum do servidor
async def check_guild_forum_thread(thread_id, guild_id=None) -> tuple[Thread | None, bool]:
    if not guild_id:
        guild_id = get_first_server_id()
        if not guild_id:
            print("Nenhum servidor encontrado no arquivo JSON.")
            return (None, False)

    config = get_server_config(guild_id)
    if not config:
        print(f"Configurações não encontradas para o servidor {guild_id}")
        return (None, False)

    client = get_client()
    guild = check_guild(client, guild_id)
    if not guild:
        return (None, False)

    forum_channel = check_forum_channel(guild, config["FORUM_CHANNEL_ID"])
    if not forum_channel:
        return (None, False)

    return await check_thread(forum_channel, thread_id)

# Função para verificar se o usuário possui a role de admin
async def check_admin_role(interaction: Interaction) -> bool:
    guild_id = interaction.guild.id
    config = get_server_config(guild_id)
    if not config:
        await interaction.response.send_message("Configurações do servidor não encontradas.", ephemeral=True)
        return False

    user = interaction.user
    if config["ADMIN_ROLE_ID"] not in [role.id for role in user.roles]:
        await interaction.response.send_message(
            "Você não tem permissão para usar este comando.",
            ephemeral=True
        )
        return False
    return True

# Verificar se o membro tem cargo de monitor
async def check_monitor(member: Member) -> bool:
    config = get_server_config(member.guild.id)
    if not config:
        return False

    if member.guild.id != int(member.guild.id):
        return False

    role = discord.utils.get(member.guild.roles, id=config["MONITOR_ROLE_ID"])
    return role in member.roles if role else False

# Verifica se a thread pertence ao fórum correto
async def check_thread_object(thread: Thread) -> bool:
    config = get_server_config(thread.guild.id)
    if not config:
        return False

    is_correct_channel = thread.parent_id == config["FORUM_CHANNEL_ID"]
    is_forum_channel = isinstance(thread.parent, ForumChannel)

    return is_correct_channel and is_forum_channel
