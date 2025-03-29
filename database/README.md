# Banco de Dados

## Sobre

O banco de dados foi projetado com PostgreSQL, e integrado ao bot por meio do SQLAlchemy, com Psycopg2 como driver. Ambos são instalados por meio do gerenciador de pacotes para Python Pip (ou outro de sua preferência).

A instalação do SQLAlchemy não tem como dependência obrigatória o Psycopg, mas é necessário que este seja instalado para o banco funcionar.

## Instalação

Rode o comando ``pip install -r requirements.txt`` no diretório principal (discord-monitoria-bot) para instalar os pacotes necessários.

Em máquinas baseadas em Debian (incluindo Ubuntu), o Psycopg2 não pode ser instalado sem antes instalar outros pacotes pelo APT.

Eles são:

- libpq-dev
- python3-dev
- build-essential (se necessário)
- postgresql-server-dev-all (se necessário)

Outra opção, pelo Pip, é o pacote psycopg2-binary. Para todos os casos, será necessário criar um ambiente virtual para instalar os requisitos: execute ``python -m venv``, seguido do caminho para onde o ambiente virtual ficará. Após isso, execute ``source /caminho/para/ambiente/bin/activate`` para ativar o ambiente e instalar os pacotes Pip.

## Setup

Após concluir os passos anteriores, caso esteja no diretório principal, execute ``python database/data/db_setup.py`` (ou ``python3`` ao invés de ``python``, no Debian/Ubuntu).

