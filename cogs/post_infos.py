import discord
from discord import app_commands
from discord.ext.commands import Cog, Bot

from forum_functions.get_thread_infos import (
    get_thread_infos, TagInfo, AppliedTags)
from tools.checks import check_admin_role

class ThreadInfos(Cog):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot

    @app_commands.command(
                    name="ver_post_infos",
                    description="Mostra as informações de um post.")
    async def thread_infos(self,
                           interaction: discord.Interaction,
                           thread_id: str) -> None:
        """Comando que retorna as informações de uma thread específica."""

        # Verificar se o usuário possui a role de admin
        if not await check_admin_role(interaction):
            return
        
        try:
            # Converte o thread_id para inteiro, caso seja passado como string
            thread_id: int = int(thread_id)
        except ValueError:
            await (interaction
                   .response
                   .send_message("O ID da thread fornecido não é válido."))
            return

        thread_info: (dict | TagInfo) = await get_thread_infos(thread_id)

        # Verifica se as informações da thread foram encontradas
        if not thread_info:
            await (interaction
                   .response
                   .send_message("Não foi possível encontrar a thread"
                                 " ou ela não existe."))
            return

        # Criação da mensagem com as informações da thread
        message: str = f"**Título da Thread:** {thread_info['name']}\n"
        message += f"**ID da Thread**: {thread_info['id']}\n"
        message += f"**Criada em**: {thread_info['created_at']} UTC\n"
        message += (f"**Dono**: {thread_info['owner'].nick}"
                    f" (ID: {thread_info['owner_id']})\n")
        message += f"**Tipo**: {thread_info['type']}\n"

        # Adiciona informações sobre as tags, se houverem
        if thread_info['applied_tags']:
            message += "\n**Tags Aplicadas**:\n"

            tag: AppliedTags
            for tag in thread_info['applied_tags']:
                message += (f"ID da tag: {tag['id']},"
                            f" Nome da tag: {tag['emoji']} {tag['name']}\n")
        else:
            message += "\nNão há tags aplicadas nesta thread."

        await interaction.response.send_message(message)

# Função para adicionar a cog ao bot
async def setup(client: discord.Client) -> None:
    await client.add_cog(ThreadInfos(client))
