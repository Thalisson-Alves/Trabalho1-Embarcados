# Trabalho 1 - Fundamentos de Sistemas Embarcados

## Especificação

Automação predial ...

## Instalação

### Servidor Distribuído

Esse passo é opcional, mas recomendado. Primeiro vamos criar um ambiente virtual para instalar as dependências do projeto.

```bash
# Criando um ambiente virtual com nome `venv`
python3 -m venv venv
# Ativando o ambiente virtual
source venv/bin/activate
```

Agora vamos instalar as bibliotecas necessárias para rodar o projeto.

```bash
# Atualizando o pip
pip3 install -U pip

# Instalando bibliotecas
pip3 install -r requirements.txt
```

Por fim precisamos configurar o arquivo `src/distribuido/config.json`.

Nesse arquivo precisamos alterar os seguintes campos:

- ip_servidor_central: Com o IP 
