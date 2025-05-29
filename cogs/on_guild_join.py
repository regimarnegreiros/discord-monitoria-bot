import discord
from discord.ext import commands
from tools.json_config import add_server


class OnGuildJoin(commands.Cog):
    """Classe que lida com o evento de entrada do bot em um novo servidor."""

    def __init__(self, client):
        self.client = client
        super().__init__()

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        """Executado quando o bot entra em um novo servidor."""
        add_server(guild.id)


async def setup(client):
    await client.add_cog(OnGuildJoin(client))
