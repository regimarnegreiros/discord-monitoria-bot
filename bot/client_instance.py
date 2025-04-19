import discord
from discord.ext import commands

class ClientBot:
    """Classe que encapsula a instância do bot Discord."""
    
    def __init__(self):
        """Inicializa o cliente do bot e o torna privado."""
        self.__client = commands.Bot(command_prefix=".", intents=discord.Intents.all())

    def get_client(self):
        """Método público para acessar o cliente do bot."""
        return self.__client

# Criando a instância da classe
bot = ClientBot()

def get_client():
    """Função para acessar o client do bot."""
    return bot.get_client()
