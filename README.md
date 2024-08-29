# Med Meet API

A Med Meet API é uma solução para o gerenciamento de profissionais de saúde, pacientes e seus respectivos agendamentos, pois através dela, é possível realizar o cadastro, visualização e gerenciamento de médicos, pacientes e seus agendamentos.

## Requisitos

- Python 3.8 ou superior
- SQLite
- Pipenv

## Instalação

### 1. Clonar o Repositório

Clone o repositório para sua máquina:
```git
https://github.com/devjleonardo/mvp-med-meet-backend.git
```

### 2. Criar o Ambiente Virtual

Siga os passos abaixo para criar e ativar o ambiente virtual usando `venv`

  - **1**. Navegue até o diretório do projeto:
```git
cd med-meet-backend
```

  - **2**. Crie o ambiente virtual:
```git
python -m venv venv
```

  - **3**. Ative o ambiente virtual:

    - No Windows:
    ```git
    .\venv\Scripts\activate
    ```
    - No Linux/macOS:
    ```git
    source venv/bin/activate
    ```

### 3. Instalar Dependências

Com o ambiente virtual ativado, instale as dependências do projeto:
```git
pip install -r requirements.txt
```

### 4. Executar a API

Após configurar o ambiente, inicie a aplicação com o seguinte comando
```git
flask run --host 0.0.0.0 --port 5000
```
