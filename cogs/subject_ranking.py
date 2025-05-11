import discord
from discord import app_commands
from discord.ext import commands

from database.data.db_funcs import db_available_semesters, db_subject_ranking

class SubjectRanking(commands.Cog):
    """Cog que exibe o ranking de matérias baseado em dados de questões."""

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

    @app_commands.command(name="ranking_materias", description="Exibe o ranking de matérias por semestre.")
    @app_commands.describe(semestre="Escolha o semestre")
    @app_commands.autocomplete(semestre=autocomplete_semestres)
    async def ranking_materias(self, interaction: discord.Interaction, semestre: str):
        await interaction.response.defer()

        try:
            year, semester = map(int, semestre.split("/"))
        except ValueError:
            await interaction.followup.send("Formato de semestre inválido.", ephemeral=True)
            return

        _, available = await db_available_semesters()
        valid_semestres = [f"{ano}/{sem}" for ano, sem in available]

        if semestre not in valid_semestres:
            await interaction.followup.send("Esse semestre não está disponível no sistema.", ephemeral=True)
            return

        ranking = await db_subject_ranking(semester=semester, year=year)

        if not ranking:
            await interaction.followup.send("Nenhuma matéria encontrada para esse semestre.", ephemeral=True)
            return

        msg_lines: list[str] = [f"📚 **Ranking de Matérias - {semester}º Semestre de {year}**\n"]
        for idx, subject_data in enumerate(ranking, 1):
            tag_id = subject_data["tagID"]
            data = subject_data["questions_data"]

            msg_lines.append(
                f"{idx}. {tag_id} - "
                f"Total: {data['total']} | "
                f"Respondidas: {data['answered']} | "
                f"Resolvidas: {data['solved']}"
            )

        await interaction.followup.send("\n".join(msg_lines), allowed_mentions=discord.AllowedMentions(users=False))

async def setup(client):
    await client.add_cog(SubjectRanking(client))
