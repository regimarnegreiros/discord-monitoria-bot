import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime

from tools.json_config import update_server, update_semester_dates, load_json
from tools.checks import check_admin_role

class ServerConfig(commands.GroupCog, name="configurar"):
    def __init__(self, bot):
        self.bot = bot

    # Subcomando: Cargo de Monitor
    @app_commands.command(name="cargo_de_monitor", description="Define o cargo de monitor. (Admin)")
    @app_commands.describe(monitor_role="Cargo de monitor")
    async def monitor_role(
        self,
        interaction: discord.Interaction,
        monitor_role: discord.Role
    ):
        if not await check_admin_role(interaction):
            return

        update_server(interaction.guild.id, monitor_role_id=monitor_role.id)
        await interaction.response.send_message(f"✅ Cargo de monitor definido para {monitor_role.mention}.", ephemeral=True)

    # Subcomando: Cargo de Administrador
    @app_commands.command(name="cargo_de_administrador", description="Define o cargo de administrador. (Admin)")
    @app_commands.describe(admin_role="Cargo de administrador")
    async def admin_role(
        self,
        interaction: discord.Interaction,
        admin_role: discord.Role
    ):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Você não tem permissão para usar este comando.", ephemeral=True)
            return

        update_server(interaction.guild.id, admin_role_id=admin_role.id)
        await interaction.response.send_message(f"✅ Cargo de administrador definido para {admin_role.mention}.", ephemeral=True)

    # Subcomando: Canal de Fórum
    @app_commands.command(name="canal_do_forum", description="Define o canal de fórum. (Admin)")
    @app_commands.describe(forum_channel="Canal do fórum")
    async def forum_channel(
        self,
        interaction: discord.Interaction,
        forum_channel: discord.ForumChannel
    ):
        if not await check_admin_role(interaction):
            return

        update_server(interaction.guild.id, forum_channel_id=forum_channel.id)
        await interaction.response.send_message(f"✅ Canal de fórum definido para {forum_channel.mention}.", ephemeral=True)

    # Subcomando: Tag de Resolvido
    @app_commands.command(name="tag_de_resolvido", description="Define a tag de resolvido. (Admin)")
    @app_commands.describe(solved_tag="Tag de resolvido")
    async def solved_tag(
        self,
        interaction: discord.Interaction,
        solved_tag: str
    ):
        if not await check_admin_role(interaction):
            return

        update_server(interaction.guild.id, solved_tag_id=int(solved_tag))
        await interaction.response.send_message("✅ Tag de resolvido atualizada com sucesso.", ephemeral=True)

    @solved_tag.autocomplete("solved_tag")
    async def solved_tag_autocomplete(self, interaction: discord.Interaction, current: str):
        config_data = load_json()
        server_config = config_data.get(str(interaction.guild.id), {})
        forum_id = server_config.get("FORUM_CHANNEL_ID")

        if not forum_id:
            return []

        forum_channel = interaction.guild.get_channel(int(forum_id))
        if not isinstance(forum_channel, discord.ForumChannel):
            return []

        return [
            app_commands.Choice(name=f"{tag.emoji or ''} {tag.name}", value=str(tag.id))
            for tag in forum_channel.available_tags
            if current.lower() in tag.name.lower()
        ][:25]

    # Subcomando: Data de Início do Semestre
    @app_commands.command(name="inicio_de_semestre", description="Define a data de início do semestre. (Admin)")
    @app_commands.describe(
        semestre="Número do semestre (1 ou 2)",
        dia="Dia de início",
        mes="Mês de início"
    )
    async def semester_start(
        self,
        interaction: discord.Interaction,
        semestre: int,
        dia: int,
        mes: int
    ):
        if not await check_admin_role(interaction):
            return

        try:
            datetime(year=2024, month=mes, day=dia)
            update_semester_dates(interaction.guild.id, semestre, dia, mes)
            await interaction.response.send_message(
                f"✅ Data do semestre {semestre} atualizada para {dia:02d}/{mes:02d}.", ephemeral=True
            )
        except ValueError:
            await interaction.response.send_message("❌ Data inválida.", ephemeral=True)

    # Subcomando: Ver configuraçÕes
    @app_commands.command(name="ver_configuracoes", description="Mostra as configurações atuais do servidor. (Admin)")
    async def view_config(
        self,
        interaction: discord.Interaction
    ):
        if not await check_admin_role(interaction):
            return

        config_data = load_json()
        server_id = str(interaction.guild.id)
        config = config_data.get(server_id)

        if not config:
            await interaction.response.send_message("⚠️ Nenhuma configuração encontrada para este servidor.", ephemeral=True)
            return

        forum_channel = interaction.guild.get_channel(config.get("FORUM_CHANNEL_ID"))
        monitor_role = interaction.guild.get_role(config.get("MONITOR_ROLE_ID"))
        admin_role = interaction.guild.get_role(config.get("ADMIN_ROLE_ID"))
        solved_tag_id = config.get("SOLVED_TAG_ID")

        # Tenta encontrar a tag pelo ID no canal de fórum
        solved_tag_name = "❌ Não definido"
        if forum_channel and isinstance(forum_channel, discord.ForumChannel) and solved_tag_id:
            for tag in forum_channel.available_tags:
                if tag.id == solved_tag_id:
                    solved_tag_name = f"{tag.emoji or ''} {tag.name}"
                    break

        semestre = config.get("SEMESTER", "Não definido")
        ano = config.get("YEAR", "Não definido")

        sem1 = config.get("SEMESTER_1_START", {})
        sem2 = config.get("SEMESTER_2_START", {})

        msg = (
            f"📋 **Configurações do Servidor:**\n"
            f"**Canal do Fórum:** {forum_channel.mention if forum_channel else '❌ Não definido'}\n"
            f"**Cargo de Monitor:** {monitor_role.mention if monitor_role else '❌ Não definido'}\n"
            f"**Cargo de Administrador:** {admin_role.mention if admin_role else '❌ Não definido'}\n"
            f"**Tag de Resolvido:** {solved_tag_name}\n"
            f"\n📅 **Semestre Atual:** {semestre} ({ano})\n"
            f"🗓️ Início do 1º Semestre: {sem1.get('day', '--'):02d}/{sem1.get('month', '--'):02d}\n"
            f"🗓️ Início do 2º Semestre: {sem2.get('day', '--'):02d}/{sem2.get('month', '--'):02d}"
        )

        await interaction.response.send_message(msg, ephemeral=True)

# Registrar a cog
async def setup(bot):
    await bot.add_cog(ServerConfig(bot))
