# Trabalho 1 - Fundamentos de Sistemas Embarcados

## Especificação

Automação predial ...

## Instalação

### Servidor Central

São utilizadas apenas módulos _builtin_ de python, logo não é necessário instalar dependências via `pip`.

A única configuração necessária a ser feita no Servidor Central é no arquivo `src/central/config.json`. Onde é necessário alterar os seguintes campos:

- ip: IP pelo qual esse **Servidor Central** ficará disponível para receber requisições. (Pode ser deixado como 0.0.0.0)
- port: Porta pelo qual esse **Servidor Central** ficará disponível para receber requisições.
- log_file: Caminho do arquivo que será utilizado para para escrever os _logs_ dos comandos solicitados pelo usuário. (Opcional)
- rooms: Lista das salas que o **Servidor Central** se comunicará para enviar os comados.
    - name: Nome da sala que será apresentado no **Servidor Central**. É recomendado colocar um nome único para melhor identificação da sala.
    - ip: IP que será usado para se comunicar com o **Servidor Distribuído** que está instalado nesta sala.
    - port: Porta que será usada para se comunicar com o **Servidor Distribuído** que está instalado nesta sala.

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

Por fim precisamos configurar o arquivo `src/distribuido/config.json`. Nesse arquivo precisamos alterar os seguintes campos:

- ip_servidor_central: IP que será usado para se comunicar com o **Servidor Central** via socket
- porta_servidor_central: Porta que será usada para se comunicar com o **Servidor Central** via socket
- ip_servidor_distribuido: IP pelo qual esse **Servidor Distribuído** ficará disponível para receber requisições. (Pode ser deixado como 0.0.0.0)
- porta_servidor_distribuido: Porta pelo qual esse **Servidor Distribuído** ficará disponível para receber requisições
- inputs: Os campos `gpio` devem ser configurados de acordo com os pinos da *GPIO*
- ouputs: Os campos `gpio` devem ser configurados de acordo com os pinos da *GPIO*
- sensor_temperatura: Os campos `gpio` devem ser configurados de acordo com os pinos da *GPIO*

_**IMPORTANTE**_: O campo `tag` dos dispositivos _inputs_ e _outputs_ **não** deve ser alterado!!
