# Banco de Dados

## Sobre

O banco de dados utiliza PostgreSQL, integrado ao bot com SQLAlchemy e o driver Psycopg2. Ambos podem ser instalados via Pip.

Embora o SQLAlchemy não dependa diretamente do Psycopg2, este último é necessário para o banco funcionar.

Um ambiente virtual é utilizado para separar as dependências de projeto de dependências do sistema operacional, evitando conflitos de versões de pacotes comuns.

## Instalação

### Windows

1. Baixe e instale o [PostgreSQL](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads).

   Não precisa instalar o Stack Builder, então desmarque a opção.

2. Entre em um perfil de administrador, digite ``path`` na barra de pesquisa, e clique na 1ª opção.

3. Clique em "Variáveis de Ambiente", e, em "Variáveis do Sistema", clique 2 vezes em "Path".

4. Clique em "Novo", depois "Procurar", e busque pela pasta "PostgreSQL/_versão instalada_/bin".

5. Clique nos "OK"s disponíveis.

### Linux

1. Instale o pacote ``postgresql`` com seu gerenciador de pacotes. Recomenda-se seguir os passos [aqui](https://www.postgresql.org/download/) ou no site de sua distribuição para garantir o bom funcionamento do PostgreSQL.

2. Em sistemas Debian/Ubuntu, instale pacotes adicionais:
   - ``libpq-dev`` (pacote para compilação de programas que usam PostgreSQL)
   - ``python3-dev`` (cabeçalhos e bibliotecas para compilar extensões C que usam Python)
   - ``build-essential`` (se necessário: inclui ferramentas essenciais de compilação, como gcc e make)
   - ``postgresql-server-dev-all`` (se necessário: arquivos para compilar extensões e interagir com o servidor PostgreSQL)

3. Crie e ative um ambiente virtual:
   
   ```sh
   python -m venv <caminho_do_ambiente>
   source <caminho_do_ambiente>/bin/activate
   ```

4. Instale as dependências com o comando:
   
   ```sh
   pip install -r requirements.txt
   ```

   Alternativamente, você pode usar o pacote psycopg2-binary via Pip.

## Setup

Com as dependências instaladas, execute:

```sh
python database/data/db_setup.py
```

Ou, no Debian/Ubuntu:

```sh
python3 database/data/db_setup.py
```
