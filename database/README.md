# Banco de Dados

## Sobre

O banco de dados utiliza PostgreSQL, integrado ao bot com SQLAlchemy e o driver Psycopg2. Ambos podem ser instalados via Pip.

Embora o SQLAlchemy não dependa diretamente do Psycopg2, este último é necessário para o banco funcionar.

## Instalação

1. Em sistemas Debian/Ubuntu, instale pacotes adicionais:
   - ``libpq-dev``
   - ``python3-dev``
   - ``build-essential`` (se necessário)
   - ``postgresql-server-dev-all`` (se necessário)

2. Instale as dependências com o comando:
   
   ```sh
   pip install -r requirements.txt
   ```


Alternativamente, você pode usar o pacote psycopg2-binary via Pip.

3. Crie e ative um ambiente virtual:
   
   ```sh
   python -m venv <caminho_do_ambiente>
   source <caminho_do_ambiente>/bin/activate
   ```
   

## Setup

Com as dependências instaladas, execute:

```sh
python database/data/db_setup.py
```

Ou, no Debian/Ubuntu:

```sh
python3 database/data/db_setup.py
```
