# <img src="https://cdn-icons-png.flaticon.com/512/330/330430.png" alt="Brasil" width="50" height="50" class="text-align: botton;"> Português
# Projeto Django

Este é um projeto Django que pode ser facilmente configurado e executado no seu ambiente local. Siga as instruções abaixo para configurar e iniciar o projeto.

## Requisitos

Antes de começar, certifique-se de ter o seguinte instalado:

- **Python 3.x** - Você pode baixar o Python [aqui](https://www.python.org/downloads/).
- **pip** - O gerenciador de pacotes do Python. Para verificar se o pip está instalado, execute `pip --version` no terminal.

## Passo 1: Clonar o repositório

Primeiro, clone este repositório para o seu ambiente local:

```bash
git clone git@github.com:fergamorim/TestMagalu.git
cd AiqFome
```

## Passo 2: Crie um ambiente virtual do Python
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Passo 3: Instale as bibliotecas python em seu ambiente virtual
```bash
pip install -r requirements.txt
```

## Passo 4: Compile e gere as tables do projeto
```bash
python3 manage.py makemigrations
python3 manage.py makemigrations Customer_api
python3 manage.py migrate
```

## Passo 4: Inicie o projeto
```bash
python3 manage.py runserver
```

### Explicação:
1. **Passo 1**: Clone o repositório para o diretório local.
2. **Passo 2**: Criação de um ambiente virtual, que ajuda a isolar dependências.
3. **Passo 3**: Instalar as dependências do projeto a partir do arquivo `requirements.txt`.
4. **Passo 4**: Criar as tabelas do banco de dados.

# Documentação e Colletion postman

## Swagger

Para acessar a documentação Swagger da API, basta abrir em seu navegador a seguinte URL apartir do projeto iniciado.
http://localhost:8000/docs/swagger/

## Collection Postman

Para poder testar as APIs foi criado neste diretorio: /AiqFome/Postman_collection/ um arquivo .json que pode ser importado na ferramenta Postman. Você pode baixar o Python [aqui](https://www.postman.com/downloads/).
Nesta Colletion é possivel encontrar todos os Endpoints criados neste projeto e testa-los.


# <img src="https://cdn-icons-png.flaticon.com/512/206/206626.png" alt="US" width="50" height="50" class="text-align: botton;"> English 
# Django Project

This is a Django project that can be easily set up and run in your local environment. Follow the instructions below to configure and start the project.

## Requirements

Before you begin, make sure you have the following installed:

- **Python 3.x** - You can download Python [here](https://www.python.org/downloads/).
- **pip** - The Python package manager. To check if pip is installed, run `pip --version` in the terminal.

## Step 1: Clone the repository

First, clone this repository to your local environment:

```bash
git clone git@github.com:fergamorim/TestMagalu.git
cd AiqFome
```

## Step 2: Create a Python virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Step 3: Install the Python libraries in your virtual environment
```bash
pip install -r requirements.txt
```

## Step 4: Compile and generate the project tables
```bash
python3 manage.py makemigrations
python3 manage.py makemigrations Customer_api
python3 manage.py migrate
```

## Step 4: Start the project
```bash
python3 manage.py runserver
```

### Explanation:
1. **Step 1**: Clone the repository to your local directory.
2. **Step 2**: Create a virtual environment, which helps isolate dependencies.
3. **Step 3**: Install the project's dependencies from the `requirements.txt` file.
4. **Step 4**: Create the database tables.

# Documentation and Postman Collection

## Swagger
To access the Swagger API documentation, simply open the following URL in your browser after starting the project:
http://localhost:8000/docs/swagger/

## Postman Collection
To test the APIs, a `.json` file has been created in the directory: `/AiqFome/Postman_collection/`, which can be imported into the Postman tool. You can download Postman [here](https://www.postman.com/downloads/).
In this Collection, you will find all the endpoints created in this project, and you can test them.
