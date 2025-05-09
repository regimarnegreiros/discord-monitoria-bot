import discord
from discord import app_commands
from discord.ext import commands

from database.data.db_funcs import db_available_semesters, db_ranking

class MonitorRanking(commands.Cog):
    """Cog que envia um ranking de monitores com base no semestre escolhido."""

    def __init__(self, client):
        self.client = client
        super().__init__()

    async def autocomplete_semestres(
        self,
        interaction: discord.Interaction,
        current: str
    ) -> list[app_commands.Choice[str]]:
        count, semesters = await db_available_semesters()

        if count == 0:
            return []

        choices = [
            app_commands.Choice(
                name=f"{sem[1]}º semestre de {sem[0]}",
                value=f"{sem[0]}/{sem[1]}"
            ) for sem in semesters
            if current.lower() in f"{sem[1]}º semestre de {sem[0]}".lower()
        ]

        return choices[:25]  # Limite do Discord

    @app_commands.command(name="ranking_monitores", description="Exibe o ranking de monitores por semestre.")
    @app_commands.describe(semestre="Escolha o semestre")
    @app_commands.autocomplete(semestre=autocomplete_semestres)
    async def ranking_monitores(self, interaction: discord.Interaction, semestre: str):
        await interaction.response.defer()

        try:
            year, semester = map(int, semestre.split("/"))
        except ValueError:
            await interaction.followup.send("Formato de semestre inválido.", ephemeral=True)
            return

        # Verificação extra para garantir que o semestre existe
        _, available = await db_available_semesters()
        valid_semestres = [f"{ano}/{sem}" for ano, sem in available]

        if semestre not in valid_semestres:
            await interaction.followup.send("Esse semestre não está disponível no sistema.", ephemeral=True)
            return

        ranking = await db_ranking(semester=semester, year=year)

        if not ranking:
            await interaction.followup.send("Nenhum monitor encontrado para esse semestre.", ephemeral=True)
            return

        msg_lines: list[str] = ["📊 **Ranking de Monitores - "
                                f"{semester}º Semestre de {year}**\n"]
        for idx, monitor in enumerate(ranking, 1):
            monitorID: int = list(monitor.keys())[0]
            member_name = f"<@{monitorID}>"

            try:
                member = await interaction.guild.fetch_member(monitorID)
                member_name = f"**{member.display_name}**"
            except discord.NotFound:
                member_name = "**Membro desconhecido**"
            except discord.HTTPException:
                member_name = "**Erro de conexão com API**"

            msg_lines.append(
                f"{idx}. {member_name} - "
                f"Respondidas: {monitor[monitorID]['answered']} | "
                f"Resolvidas: {monitor[monitorID]['solved']}"
            )

        await interaction.followup.send("\n".join(msg_lines), allowed_mentions=discord.AllowedMentions(users=False))

async def setup(client):
    await client.add_cog(MonitorRanking(client))
