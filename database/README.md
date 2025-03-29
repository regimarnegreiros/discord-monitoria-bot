# Banco de Dados

## Sobre

O banco de dados utiliza PostgreSQL, integrado ao bot com SQLAlchemy e o driver Psycopg2. Ambos podem ser instalados via Pip.

Embora o SQLAlchemy não dependa diretamente do Psycopg2, este último é necessário para o banco funcionar.

Um ambiente virtual é utilizado para separar as dependências de projeto de dependências do sistema operacional, evitando conflitos de versões de pacotes comuns.

## Instalação

1. Em sistemas Debian/Ubuntu, instale pacotes adicionais:
   - ``libpq-dev`` (pacote para compilação de programas que usam PostgreSQL)
   - ``python3-dev`` (cabeçalhos e bibliotecas para compilar extensões C que usam Python)
   - ``build-essential`` (se necessário: inclui ferramentas essenciais de compilação, como gcc e make)
   - ``postgresql-server-dev-all`` (se necessário: arquivos para compilar extensões e interagir com o servidor PostgreSQL)

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
