# Bot para registros da monitoria

O **Registros de Monitoria** é um bot desenvolvido para auxiliar no gerenciamento e análise de estatísticas de monitoria dentro de um servidor do Discord. Ele coleta e organiza dados sobre a participação dos monitores em canais de fórum e gerando um ranking baseado em diversas métricas.

### Instalação

1. **Instalar Pacotes Python:**

    Você pode instalar os pacotes Python necessários usando pip:

    ```sh
    pip install -r requirements.txt
    ```

2. **Setup do Banco de Dados:**

    Cheque [este README](./database/README.md).

### Configuração

1. Ao iniciar o bot pela primeira vez, ele criará automaticamente um arquivo chamado `config.json`. Edite as variáveis dentro desse arquivo, substituindo pelos valores reais do seu servidor e canais.
2. **Crie uma cópia** do arquivo chamado `.env.exemple` e nomeie-a como `.env` na raiz do seu projeto. Substitua as variáveis de ambiente pelos valores reais.


### Executando o Bot

Execute o bot usando o seguinte comando:

```sh
python main.py
```
