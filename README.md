# Bot para registros da monitoria

O **Registros de Monitoria** é um bot desenvolvido para auxiliar no gerenciamento e análise de estatísticas de monitoria dentro de um servidor do Discord. Ele coleta e organiza dados sobre a participação dos monitores em canais de fórum e gerando um ranking baseado em diversas métricas.

### Instalação

1. **Instalar Pacotes Python:**

    Você pode instalar os pacotes Python necessários usando pip:

    ```sh
    pip install -r requirements.txt
    ```


### Configuração

1. **Crie uma cópia** do arquivo `config_example.py` e nomeie-a como `config.py`. Em seguida, altere as variáveis no `config.py` com os valores reais do seu servidor e canais.
2. **Crie uma cópia** do arquivo chamado `.env.exemple` e nomeie-a como `.env` na raiz do seu projeto. Substitua as variáveis de ambiente pelos valores reais.


### Executando o Bot

Execute o bot usando o seguinte comando:

```sh
python main.py
```