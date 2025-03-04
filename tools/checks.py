from discord import TextChannel, ForumChannel, Interaction

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
    if not channel or not isinstance(channel, TextChannel):
        print("Canal inválido ou não é um canal de texto.")
        return None
    return channel

# Função para verificar se o canal é um fórum
def check_forum_channel(guild, forum_id):
    forum_channel = guild.get_channel(forum_id)
    if not forum_channel or not isinstance(forum_channel, ForumChannel):
        print("Canal inválido ou não é um fórum.")
        return None
    return forum_channel

# Função para verificar se a thread existe no canal
async def check_thread(forum_channel, thread_id):
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

# Função para verificar se o usuário possui a role de admin
async def check_admin_role(interaction: Interaction):
    user = interaction.user
    if ADMIN_ROLE_ID not in [role.id for role in user.roles]:
        await interaction.response.send_message(
                "Você não tem permissão para usar este comando.",
                ephemeral=True)
        return False
    return True