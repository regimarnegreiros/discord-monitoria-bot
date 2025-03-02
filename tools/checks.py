import discord
from discord import app_commands
from discord.ext import commands

from settings.config import ADMIN_ROLE_ID

# Função para verificar se o bot está no servidor
def check_guild(client, guild_id):
    guild = client.get_guild(guild_id)
    if not guild:
        print("O bot não está no servidor especificado!")
        return None
    return guild

# Função para verificar se o canal é válido e é um canal de texto
def check_channel(guild, channel_id):
    channel = guild.get_channel(channel_id)
    if not channel or not isinstance(channel, discord.TextChannel):
        print("Canal inválido ou não é um canal de texto.")
        return None
    return channel

# Função para verificar se o canal é um fórum
def check_forum_channel(guild, forum_id):
    forum_channel = guild.get_channel(forum_id)
    if not forum_channel or not isinstance(forum_channel, discord.ForumChannel):
        print("Canal inválido ou não é um fórum.")
        return None
    return forum_channel

# Função para verificar se a thread existe no canal
def check_thread(forum_channel, thread_id):
    thread = forum_channel.get_thread(thread_id)
    if not thread:
        print("Thread não encontrada.")
        return None
    return thread

# Função para verificar se uma thread está arquivada
async def check_archived_thread(forum_channel, thread_id):
    # Obtendo todas as threads arquivadas do canal de fórum
    archived_threads = [thread async for thread in forum_channel.archived_threads(limit=None)]
    
    # Procurando pela thread arquivada
    for archived_thread in archived_threads:
        if archived_thread.id == thread_id:
            print(f"Thread arquivada encontrada: {thread_id}")
            return archived_thread

    print("Thread arquivada não encontrada.")
    return None

# Função para verificar se o usuário possui a role de admin
async def check_admin_role(interaction: discord.Interaction):
    user = interaction.user
    if ADMIN_ROLE_ID not in [role.id for role in user.roles]:
        await interaction.response.send_message("Você não tem permissão para usar este comando.", ephemeral=True)
        return False
    return True