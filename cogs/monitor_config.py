import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timezone
import re

from database.data.db_funcs import db_available_semesters, db_modify_monitor_semester
from tools.json_config import load_json, get_semester_and_year


class MonitorConfig(commands.Cog):
    """Cog que permite adicionar ou remover o status de monitor de usuários."""

    def __init__(self, client):
        self.client = client
        super().__init__()

    async def autocomplete_semestres(
        self,
        interaction: discord.Interaction,
        current: str
    ) -> list[app_commands.Choice[str]]:
        count, semesters = await db_available_semesters()
        semesters = list(semesters)

        # Descobrir semestre atual
        try:
            current_semester, current_year = get_semester_and_year(
                guild_id=interaction.guild_id,
                raw_date=datetime.now(timezone.utc)
            )
        except Exception as e:
            print(f"[autocomplete_semestres] Erro ao determinar semestre atual: {e}")
            current_semester, current_year = None, None

        # Adicionar semestre atual se não estiver
        if (current_year, current_semester) not in semesters:
            semesters.append((current_year, current_semester))

        choices = []
        for ano, semestre in semesters:
            label = f"{semestre}º semestre de {ano}"
            if ano == current_year and semestre == current_semester:
                label += " (Semestre Atual)"

            if current.lower() in label.lower():
                choices.append(
                    app_commands.Choice(
                        name=label,
                        value=f"{ano}/{semestre}"
                    )
                )

        return choices[:25]

    @app_commands.command(
        name="configurar_monitor",
        description="Adiciona ou remove o cargo de monitor de um ou mais usuários em um semestre."
    )
    @app_commands.describe(
        usuarios="Mencione os usuários ou cole os IDs separados por espaço",
        semestre="Semestre no formato Ano/Semestre",
        monitor="Defina se os usuários serão monitores (Sim ou Não)"
    )
    @app_commands.autocomplete(semestre=autocomplete_semestres)
    async def configurar_monitor(
        self,
        interaction: discord.Interaction,
        usuarios: str,
        semestre: str,
        monitor: bool
    ):
        await interaction.response.defer(ephemeral=True)

        # Extrair IDs de mentions ou IDs puros
        user_ids = re.findall(r"\d+", usuarios)
        membros: list[discord.Member] = [
            interaction.guild.get_member(int(uid)) for uid in user_ids
        ]
        membros = [m for m in membros if m]

        if not membros:
            await interaction.followup.send("Nenhum usuário válido foi encontrado.", ephemeral=True)
            return

        # Validação do semestre
        try:
            year, semester = map(int, semestre.split("/"))
        except ValueError:
            await interaction.followup.send("Formato de semestre inválido. Use `Ano/Semestre`.", ephemeral=True)
            return

        # Carrega configs do servidor
        config = load_json()
        guild_config = config.get(str(interaction.guild_id), {})

        current_year = guild_config.get("YEAR")
        current_semester = guild_config.get("SEMESTER")

        monitor_role_id = guild_config.get("MONITOR_ROLE_ID")
        monitor_role = interaction.guild.get_role(monitor_role_id) if monitor_role_id else None

        # Caso seja semestre atual → só mexer no cargo
        if year == current_year and semester == current_semester:
            if monitor_role:
                for membro in membros:
                    try:
                        if monitor:
                            await membro.add_roles(monitor_role, reason="Promovido a monitor")
                        else:
                            await membro.remove_roles(monitor_role, reason="Removido de monitoria")
                    except discord.Forbidden:
                        await interaction.followup.send(f"Não consegui gerenciar o cargo de {membro.mention} (permissões insuficientes).", ephemeral=True)
                        continue

            status_msg = "adicionados como monitores ✅" if monitor else "removidos da monitoria ❌"
            await interaction.followup.send(
                f"{', '.join(m.mention for m in membros)} foram **{status_msg}** no semestre atual `{semestre}`.",
                ephemeral=True
            )
            return

        # Se não for semestre atual → só mexer no banco
        _, available = await db_available_semesters()
        valid_semestres = [f"{ano}/{sem}" for ano, sem in available]

        if semestre not in valid_semestres:
            await interaction.followup.send("Esse semestre não está disponível no sistema.", ephemeral=True)
            return

        for membro in membros:
            await db_modify_monitor_semester(
                userID=membro.id,
                is_monitor=monitor,
                semester=semester,
                year=year
            )

        status_msg = "adicionados como monitores ✅" if monitor else "removidos da monitoria ❌"
        await interaction.followup.send(
            f"{', '.join(m.mention for m in membros)} foram **{status_msg}** no semestre `{semestre}` (apenas banco de dados).",
            ephemeral=True
        )


async def setup(client):
    await client.add_cog(MonitorConfig(client))
