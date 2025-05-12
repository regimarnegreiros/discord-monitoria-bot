import discord
from discord import app_commands
from discord.ext import commands

from forum_functions.get_forum_posts_id import get_forum_posts
from tools.checks import check_admin_role

class GetPostsId(commands.Cog):
    """Cog que faz um print no terminal o id de todos os posts do fórum."""
    
    def __init__(self, client):
        self.client = client
        super().__init__()
    
    @app_commands.command(name="posts_id", description="Coleta o id de todos os posts do fórum. (Admin)")
    async def getpostsid(self, interaction: discord.Interaction):
        # Verificar se o usuário possui a role de admin
        if not await check_admin_role(interaction):
            return
        
        posts = await get_forum_posts(interaction.guild_id)
        posts_quantity = len(posts)

        message = f"ID das postagens extraídos com sucesso! \n\n{posts}\n\nQuantidade de posts: {posts_quantity}"

        print(message)
        await interaction.response.send_message(message)

async def setup(client):
    await client.add_cog(GetPostsId(client))