import discord
from discord import app_commands
from discord.ext import commands
from tools.json_config import load_json  # Certifique-se que o caminho está correto

class SolvedThread(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="resolvido", description="Marca esta thread como resolvida.")
    async def resolvido(self, interaction: discord.Interaction):
        thread = interaction.channel

        # Verificar se é uma thread de fórum
        if not isinstance(thread, discord.Thread) or not isinstance(thread.parent, discord.ForumChannel):
            await interaction.response.send_message(
                "❌ Este comando só pode ser usado dentro de uma **thread de fórum**.",
                ephemeral=True
            )
            return

        # Carregar configurações do servidor
        guild_id = str(interaction.guild.id)
        config = load_json().get(guild_id)

        if config is None:
            await interaction.response.send_message(
                "⚠️ Este servidor não está configurado corretamente. Contate um administrador.",
                ephemeral=True
            )
            return

        # Obter valores do JSON
        forum_channel_id = config.get("FORUM_CHANNEL_ID")
        monitor_role_id = config.get("MONITOR_ROLE_ID")
        solved_tag_id = config.get("SOLVED_TAG_ID")

        # Verificar se está no canal de fórum correto
        if thread.parent.id != forum_channel_id:
            await interaction.response.send_message(
                "❌ Este comando só pode ser usado em threads do canal de fórum configurado.",
                ephemeral=True
            )
            return

        # Verificar permissões
        author = interaction.user
        thread_creator = thread.owner
        has_monitor_role = any(role.id == monitor_role_id for role in author.roles)

        if author != thread_creator and not has_monitor_role:
            await interaction.response.send_message(
                "🚫 Você não tem permissão para marcar esta thread como resolvida.",
                ephemeral=True
            )
            return

        # Aplicar a tag "Resolvido"
        # Aplicar a tag "Resolvido"
        try:
            solved_tag = discord.utils.get(thread.parent.available_tags, id=solved_tag_id)

            if not solved_tag:
                await interaction.response.send_message(
                    "❌ A tag 'Resolvido' não foi encontrada no canal de fórum.",
                    ephemeral=True
                )
                return

            # Pega as tags já aplicadas na thread
            current_tags = thread.applied_tags if thread.applied_tags else []

            # Se a tag "Resolvido" não estiver na lista, adiciona
            if solved_tag not in current_tags:
                current_tags.append(solved_tag)

            await thread.edit(applied_tags=current_tags)
            await interaction.response.send_message("✅ Esta thread foi marcada como **resolvida**!")
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Ocorreu um erro ao aplicar a tag: `{e}`",
                ephemeral=True
            )

    @commands.Cog.listener()
    async def on_ready(self):
        try:
            self.client.tree.add_command(self.resolvido)
            print("[/resolvido] registrado com sucesso.")
        except Exception as e:
            print(f"Erro ao registrar o comando /resolvido: {e}")

async def setup(client):
    await client.add_cog(SolvedThread(client))
