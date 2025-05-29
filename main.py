import os
import discord
from dotenv import load_dotenv

from bot.client_instance import get_client
from tools.json_config import load_json, ensure_config_exists, add_server

# Carregamento do arquivo .env
load_dotenv(dotenv_path='settings/.env')
TOKEN = os.getenv('TOKEN')

# Obtendo a instância global de client
client = get_client()

# Função para carregar os cogs
async def load_cogs():
    """Carrega todos os cogs presentes na pasta 'cogs'."""
    for arquivo in os.listdir('cogs'):
        if arquivo.endswith('.py'):
            try:
                await client.load_extension(f"cogs.{arquivo[:-3]}")
            except Exception as e:
                print(f'Erro ao carregar cog {arquivo}: {e}')

# Comando de ping
@client.tree.command(name="ping", description="Responde o usuário com pong.")
async def ping(interaction: discord.Interaction):
    """Comando que responde 'Pong 🏓' ao usuário."""
    await interaction.response.send_message("Pong 🏓")

@client.event
async def on_ready():
    """Evento acionado quando o bot está pronto para usar."""

    # Presença inicial de "ligando"
    await client.change_presence(
        status=discord.Status.idle,
        activity=discord.Game(name="Ligando...")
    )

    # Garante que o arquivo de configuração existe
    ensure_config_exists()
    for guild in client.guilds:
        add_server(guild.id)
    
    # Carrega os cogs
    await load_cogs()
    await client.tree.sync()

    # Executa a verificação de semestre após carregar os cogs
    cog = client.get_cog("UpdateSemester")
    if cog:
        await cog.verify_semester()

    # Carrega o status do bot
    status = load_json().get("bot_status", {})
    await client.change_presence(
        status=discord.Status.do_not_disturb,
        activity=discord.Streaming(
            name=status.get("activity_name"),
            url=status.get("streaming_url")
        )
    )

    print(f'Conectado como {client.user} (ID: {client.user.id})')

# Rodando o bot
client.run(TOKEN)
