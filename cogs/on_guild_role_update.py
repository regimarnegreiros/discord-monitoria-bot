import discord
from discord import app_commands
from discord.ext import commands

from tools.checks import check_monitor


class OnGuildRoleUpdate(commands.Cog):
    """Classe que lida com eventos relacionados à atualização de cargos na guilda."""

    def __init__(self, client):
        self.client = client
        super().__init__()

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """Escuta o evento de atualização de cargo e realiza ações associadas.

        Args:
            before: O membro antes da atualização.
            after: O membro após a atualização.
        """
        
        # Verifica se o membro ganhou ou perdeu o cargo de monitor utilizando a função check_monitor
        before_monitor = await check_monitor(before)
        after_monitor = await check_monitor(after)

        # Se houve uma mudança no status de "monitor"
        if before_monitor != after_monitor:
            if after_monitor:
                print(f"{after.nick} ganhou o cargo de monitor.")  # O membro ganhou o cargo
                # Implementar função que adiciona o cargo de monitor do banco de dados no semestre atual 
            else:
                print(f"{after.nick} perdeu o cargo de monitor.")  # O membro perdeu o cargo
                # Implementar função que remove o cargo de monitor do banco de dados no semestre atual


async def setup(client):
    await client.add_cog(OnGuildRoleUpdate(client))
