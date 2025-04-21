import os
import json
from datetime import date

# Define o caminho do arquivo JSON como constante
JSON_FILE_PATH = "settings/config.json"

# Conteúdo padrão
DEFAULT_CONFIG = {
    "bot_status": {
        "activity_name": "/ajuda",
        "streaming_url": "https://www.youtube.com/watch?v=SECVGN4Bsgg"
    },
    "id_servidor_exemplo_1234567890": {
        "FORUM_CHANNEL_ID": None,
        "MONITOR_ROLE_ID": None,
        "ADMIN_ROLE_ID": None,
        "SOLVED_TAG_ID": None,
        "SEMESTER": date.today().month // 7 + 1,
        "YEAR": date.today().year
    }
}

# Carregar o JSON
def load_json():
    try:
        with open(JSON_FILE_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Salvar o JSON
def save_json(data):
    with open(JSON_FILE_PATH, 'w') as f:
        json.dump(data, f, indent=4)

# Adicionar um novo servidor com valores vazios
def add_server(guild_id):
    data = load_json()

    # Verificar se o servidor já existe
    if str(guild_id) in data:
        print(f"O servidor com ID {guild_id} já existe.")
        return

    # Adicionar o servidor com valores vazios
    data[str(guild_id)] = {
        "FORUM_CHANNEL_ID": None,
        "MONITOR_ROLE_ID": None,
        "ADMIN_ROLE_ID": None,
        "SOLVED_TAG_ID": None
    }

    save_json(data)
    print(f"Servidor com ID {guild_id} adicionado com valores vazios!")

# Remover um servidor
def remove_server(guild_id):
    data = load_json()

    # Verificar se o servidor existe
    if str(guild_id) not in data:
        print(f"O servidor com ID {guild_id} não foi encontrado.")
        return

    del data[str(guild_id)]
    save_json(data)
    print(f"Servidor com ID {guild_id} removido com sucesso!")

# Atualizar as configurações de um servidor
def update_server(guild_id, forum_channel_id=None, monitor_role_id=None, admin_role_id=None, solved_tag_id=None):
    data = load_json()

    # Verificar se o servidor existe
    if str(guild_id) not in data:
        print(f"O servidor com ID {guild_id} não foi encontrado.")
        return

    server = data[str(guild_id)]

    # Atualizar os valores apenas se forem fornecidos
    if forum_channel_id is not None:
        server["FORUM_CHANNEL_ID"] = forum_channel_id
    if monitor_role_id is not None:
        server["MONITOR_ROLE_ID"] = monitor_role_id
    if admin_role_id is not None:
        server["ADMIN_ROLE_ID"] = admin_role_id
    if solved_tag_id is not None:
        server["SOLVED_TAG_ID"] = solved_tag_id

    save_json(data)
    print(f"As configurações do servidor com ID {guild_id} foram atualizadas.")

# Atualizar o status do bot
def update_bot_status(activity_name=None, streaming_url=None):
    data = load_json()

    if "bot_status" not in data:
        data["bot_status"] = {}

    if activity_name is not None:
        data["bot_status"]["activity_name"] = activity_name
    if streaming_url is not None:
        data["bot_status"]["streaming_url"] = streaming_url

    save_json(data)
    print(f"Status do bot atualizado com sucesso!")

# Garante que o arquivo de configuração exista
def ensure_config_exists():
    if not os.path.exists(JSON_FILE_PATH):
        os.makedirs(os.path.dirname(JSON_FILE_PATH), exist_ok=True)
        with open(JSON_FILE_PATH, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        print("Arquivo de configuração criado com bot_status padrão.")

# Retorna o primeiro ID de servidor encontrado no JSON (ignorando bot_status)
def get_first_server_id() -> int | None:
    data = load_json()
    guild_keys = [key for key in data if key != "bot_status"]
    
    if not guild_keys:
        return None
    
    return int(guild_keys[0])