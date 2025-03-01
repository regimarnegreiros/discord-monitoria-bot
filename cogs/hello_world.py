import discord
from discord import app_commands
from discord.ext import commands

class HelloWorld(commands.Cog):
    """Cog que envia uma mensagem de 'Hello World' para o usuário."""
    
    def __init__(self, client):
        self.client = client
        super().__init__()
    
    @commands.hybrid_command(description="Envia uma mensagem de Hello world!")
    async def helloworld(self, ctx: commands.Context):
        user = ctx.author.display_name
        await ctx.send(f"Hello World! {user}")

async def setup(client):
    await client.add_cog(HelloWorld(client))