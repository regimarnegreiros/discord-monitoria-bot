from discord import (
    TextChannel, ForumChannel, 
    Interaction, Guild, Thread
)

from settings.config import ADMIN_ROLE_ID, GUILD_ID, FORUM_CHANNEL_ID, MONITOR_ROLE_ID
from bot.client_instance import get_client

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
    # Primeiro, tentamos verificar se a thread existe
    thread = forum_channel.get_thread(thread_id)
    was_archived = False

    if not thread:
        # Se não encontramos a thread ativa, verificamos se ela está arquivada
        print("Thread não encontrada. Buscando threads arquivadas")

        # Obtendo todas as threads arquivadas do canal de fórum
        archived_threads = {
            thread.id: thread async for thread in forum_channel
                                                  .archived_threads(limit=None)
        }
        
        # Procurando pela thread arquivada
        try:
            archived_thread = archived_threads[thread_id]
        except KeyError:
            print("Thread não encontrada.")
            return (thread, was_archived) # None, False

        print(f"Thread arquivada encontrada: {thread_id}")

        # Se a thread está arquivada, tentamos reabri-la
        await archived_thread.edit(archived=False)
            
        print(
            f"A thread {thread_id} foi reaberta"
            " para acessar o histórico de mensagens."
        )

        thread = archived_thread # Atualizando thread para ser a reaberta
        was_archived = True
        
    return (thread, was_archived)

async def check_guild_forum_thread(thread_id) -> (tuple[(Thread | None), bool]):
    was_archived = False
    thread = None

    # Verifica se o bot está no servidor
    client = get_client()
    guild = check_guild(client, GUILD_ID)
    if not guild:
        return (thread, was_archived)

    # Verifica se o fórum exite
    forum_channel = check_forum_channel(guild, FORUM_CHANNEL_ID)
    if not forum_channel:
        return (thread, was_archived)

    # Verifica se a thread existe
    thread, was_archived = await check_thread(forum_channel, thread_id)
    return (thread, was_archived)

# Função para verificar se o usuário possui a role de admin
async def check_admin_role(interaction: Interaction) -> bool:
    user = interaction.user
    if ADMIN_ROLE_ID not in [role.id for role in user.roles]:
        await interaction.response.send_message(
                "Você não tem permissão para usar este comando.",
                ephemeral=True)
        return False
    return True

async def check_thread_object(thread: Thread) -> bool:
    """
    Verifica se a thread foi criada no servidor e canal de fórum específicos.

    Args:
        thread (Thread): O objeto Thread a ser verificado.

    Returns:
        bool: Retorna True se a thread for do servidor e canal de fórum especificados, 
              caso contrário, retorna False.
    """
    is_correct_guild = thread.guild.id == GUILD_ID
    is_correct_channel = thread.parent_id == FORUM_CHANNEL_ID
    is_forum_channel = isinstance(thread.parent, ForumChannel)

    return is_correct_guild and is_correct_channel and is_forum_channel