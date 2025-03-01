import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

from settings.config import PREFIX

# Carregamento do arquivo .env
load_dotenv()
TOKEN = os.getenv('TOKEN')

# Definindo as permissões/intents do bot
client = commands.Bot(command_prefix=PREFIX, intents=discord.Intents.all())

async def load_cogs():
    """Carrega todos os cogs presentes na pasta 'cogs'."""
    for arquivo in os.listdir('cogs'):
        if arquivo.endswith('.py'):
            try:
                await client.load_extension(f"cogs.{arquivo[:-3]}")
            except Exception as e:
                print(f'Erro ao carregar cog {arquivo}: {e}')

@client.hybrid_command(description="Responde o usuário com pong.")
async def ping(ctx: commands.Context):
    """Comando que responde 'Pong' ao usuário."""
    await ctx.send("Pong 🏓")

@client.event
async def on_ready():
    """Evento acionado quando o bot está pronto para usar."""
    await load_cogs()
    await client.tree.sync()
    await client.change_presence(
        status=discord.Status.do_not_disturb, 
        activity=discord.Streaming(
            name=f"{PREFIX}help", 
            url="https://www.youtube.com/watch?v=SECVGN4Bsgg"
        )
    )
    print(f'Conectado como {client.user} (ID: {client.user.id})')

# Rodando o bot
client.run(TOKEN)