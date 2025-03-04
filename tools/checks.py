from discord import (
    TextChannel, ForumChannel, Interaction, Client,
    Guild, Thread, User, Member
)

from settings.config import ADMIN_ROLE_ID, GUILD_ID, FORUM_CHANNEL_ID
from bot.client_instance import get_client

def check_guild(client: Client, guild_id: int) -> (Guild | None):
    """Checa se o Bot está no servidor"""

    guild: (Guild | None) = client.get_guild(guild_id)

    if not guild:
        print("O bot não está no servidor especificado!")
        return None

    return guild

def check_channel(guild: Guild, channel_id: int) -> (TextChannel | None):
    """Checa se o Canal é válido e é um Canal de Texto"""

    channel: (TextChannel | None) = guild.get_channel(channel_id)

    if not isinstance(channel, TextChannel):
        print("Canal inválido ou não é um canal de texto.")
        return None

    return channel

def check_forum_channel(guild: Guild, forum_id: int) -> (ForumChannel | None):
    """Checa se o Canal é um Fórum"""

    forum_channel: (ForumChannel | None) = guild.get_channel(forum_id)

    if not isinstance(forum_channel, ForumChannel):
        print("Canal inválido ou não é um fórum.")
        return None
    return forum_channel

async def check_thread(forum_channel: ForumChannel,
                       thread_id: int) -> (tuple[(Thread | None), bool]):
    """Checa se a Thread existe no Canal"""

    # Primeiro, tentamos verificar se a thread existe
    thread: (Thread | None) = forum_channel.get_thread(thread_id)
    was_archived: bool = False

    if not thread:
        # Se não encontramos a thread ativa, verificamos se ela está arquivada
        print("Thread não encontrada. Buscando threads arquivadas")

        # Obtendo todas as threads arquivadas do canal de fórum
        archived_threads: dict[int, Thread] = {
            thread.id: thread async for thread in
                              forum_channel.archived_threads(limit=None)
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

async def check_guild_forum_thread(
            thread_id: int) -> (tuple[(Thread | None), bool]):
    thread: (Thread | None) = None
    was_archived: bool = False

    # Verifica se o bot está no servidor
    client: Client = get_client()
    guild: (Guild | None) = check_guild(client, GUILD_ID)
    if not guild:
        return (thread, was_archived)

    # Verifica se o fórum exite
    forum_channel: (ForumChannel | None) = check_forum_channel(
                                            guild,FORUM_CHANNEL_ID)
    if not forum_channel:
        return (thread, was_archived)

    # Verifica se a thread existe
    thread, was_archived = await check_thread(forum_channel, thread_id)
    return (thread, was_archived)

async def check_admin_role(interaction: Interaction) -> bool:
    """Checa se o Usuário possui a Role de admin"""

    user: (User | Member) = interaction.user

    if ADMIN_ROLE_ID not in [role.id for role in user.roles]:
        await interaction.response.send_message(
                "Você não tem permissão para usar este comando.",
                ephemeral=True)
        return False
    return True