import discord
from discord import app_commands
from discord.ext import commands

from database.data.db_funcs import db_available_semesters, db_ranking

class MonitorRanking(commands.Cog):
    """Cog que envia um ranking de monitores com base no semestre escolhido."""

    def __init__(self, client):
        self.client = client
        super().__init__()

    @app_commands.command(name="ranking_monitores", description="Exibe o ranking de monitores por semestre.")
    async def ranking_monitores(self, interaction: discord.Interaction):
        count, semesters = await db_available_semesters()

        if count == 0:
            await interaction.response.send_message("Nenhum semestre disponível foi encontrado no banco de dados.")
            return

        options = [
            discord.SelectOption(
                label=f"{sem[1]}º semestre de {sem[0]}",
                value=f"{sem[0]}-{sem[1]}"
            ) for sem in semesters
        ]

        select = discord.ui.Select(
            placeholder="Escolha o semestre",
            options=options,
            custom_id="select_semester"
        )

        async def select_callback(interaction_select: discord.Interaction):
            ranking: list[dict[int, dict[str, int]]] | list

            selected_value = interaction_select.data["values"][0]
            year, semester = map(int, selected_value.split("-"))
            ranking = await db_ranking(semester=semester, year=year)

            if not ranking:
                await interaction_select.response.send_message(
                    "Nenhum monitor encontrado para esse semestre.")
                return

            msg_lines: list[str] = ["📊 **Ranking de Monitores - "
                         f"{semester}º Semestre de {year}**\n"]
            for idx, monitor in enumerate(ranking, 1):
                monitorID: int = list(monitor.keys())[0]
                member_name = f"<@{monitorID}>"

                try:
                    member = await interaction_select.guild.fetch_member(monitorID)
                    member_name = f"**{member.display_name}**"
                except discord.NotFound:
                    member_name = "**Membro desconhecido**"  # Membro saiu do servidor
                except discord.HTTPException:
                    member_name = "**Erro de conexão com API**"  # Algum erro de conexão com a API

                msg_lines.append(
                    f"{idx}. {member_name} - "
                    f"Respondidas: {monitor[monitorID]['answered']} | "
                    f"Resolvidas: {monitor[monitorID]['solved']}"
                )

            await interaction_select.response.send_message(
                "\n".join(msg_lines),
                allowed_mentions=discord.AllowedMentions(users=False))

        select.callback = select_callback

        view = discord.ui.View()
        view.add_item(select)

        await interaction.response.send_message("Selecione o semestre para visualizar o ranking:", view=view, ephemeral=True)

async def setup(client):
    await client.add_cog(MonitorRanking(client))
