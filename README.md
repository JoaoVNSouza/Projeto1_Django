Este projeto é uma aplicação web desenvolvida com Django e Python para gerenciar o cadastro de pessoas e investidores. O código está estruturado no GitHub e segue uma organização baseada em boas práticas do Django.

Tecnologias Utilizadas
* Linguagem: Python
* Framework: Django
* Banco de Dados: SQLite3

Instalação e Configuração

1. Clonar o repositório
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio

2. Criar e ativar um ambiente virtual (opcional, mas recomendado)
python -m venv venv
source venv/bin/activate  # Para Linux/Mac
venv\Scripts\activate     # Para Windows

3. Instalar dependências
pip install -r requirements.txt

4. Executar migrações do banco de dados
python manage.py migrate

5. Criar um superusuário (opcional, para acesso ao painel admin)
python manage.py createsuperuser

6. Executar o servidor de desenvolvimento
python manage.py runserver

A aplicação estará disponível em: http://127.0.0.1:8000/

Funcionalidades
Cadastro de usuários (pessoas e investidores)
Sistema de autenticação e login
Interface para gerenciamento de cadastros
Painel administrativo do Django


Licença
Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.
