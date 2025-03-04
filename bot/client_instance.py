from discord import Intents
from discord.ext.commands import Bot
from settings.config import PREFIX

class ClientBot:
    """Classe que encapsula a instância do bot Discord."""
    
    def __init__(self) -> None:
        """Inicializa o cliente do bot e o torna privado."""
        self.__client: Bot = Bot(command_prefix=PREFIX,
                                intents=Intents.all())

    def get_client(self) -> Bot:
        """Método público para acessar o cliente do bot."""
        return self.__client

# Criando a instância da classe
bot = ClientBot()

def get_client() -> Bot:
    """Função para acessar o client do bot."""
    return bot.get_client()
