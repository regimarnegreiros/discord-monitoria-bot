import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

from settings.config import PREFIX
from bot.client_instance import get_client

# Carregamento do arquivo .env
load_dotenv(dotenv_path='settings/.env')
TOKEN = os.getenv('TOKEN')

# Obtendo a instancia global de client
client: discord.Client = get_client()

async def load_cogs() -> None:
    """Carrega todos os cogs presentes na pasta 'cogs'."""
    arquivo: str
    for arquivo in os.listdir('cogs'):
        if arquivo.endswith('.py'):
            try:
                await client.load_extension(f"cogs.{arquivo[:-3]}")
            except Exception as e:
                print(f'Erro ao carregar cog {arquivo}: {e}')

@client.tree.command(name="ping", description="Responde o usuário com pong.")
async def ping(interaction: discord.Interaction) -> None:
    """Comando que responde 'Pong 🏓' ao usuário."""
    await interaction.response.send_message("Pong 🏓")

@client.event
async def on_ready() -> None:
    """Evento acionado quando o bot está pronto para usar."""
    await load_cogs()
    await client.tree.sync()
    await client.change_presence(
        status=discord.Status.do_not_disturb, 
        activity=discord.Streaming(
            name=f"/ajuda", 
            url="https://www.youtube.com/watch?v=SECVGN4Bsgg"
        )
    )
    print(f'Conectado como {client.user} (ID: {client.user.id})')

# Rodando o bot
client.run(TOKEN)
