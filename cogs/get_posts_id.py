import discord
from discord import app_commands
from discord.ext import commands

from settings.config import GUILD_ID
from settings.config import FORUM_CHANNEL_ID
from settings.config import ADMIN_ROLE_ID
from forum_functions.get_forum_posts_id import get_forum_posts

class GetPostsId(commands.Cog):
    """Cog que faz um print no terminal o id de todos os posts do fórum."""
    
    def __init__(self, client):
        self.client = client
        super().__init__()
    
    @commands.hybrid_command(description="Faz um print no terminal o id de todos os posts do fórum.")
    async def getpostsid(self, ctx: commands.Context):
        # Verificar se o usuário possui a role de admin
        if ADMIN_ROLE_ID not in [role.id for role in ctx.author.roles]:
            await ctx.send("Você não tem permissão para usar este comando.")
            return
        
        posts = await get_forum_posts(GUILD_ID, FORUM_CHANNEL_ID)
        posts_quantity = len(posts)

        message = f"ID das postagens extraídos com sucesso! \n\n{posts}\n\nQuantidade de posts: {posts_quantity}"
        
        print(message)
        await ctx.send(message  )

async def setup(client):
    await client.add_cog(GetPostsId(client))