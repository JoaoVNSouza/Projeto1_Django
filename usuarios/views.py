from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.messages import constants
from django.contrib import auth


# Create your views here.
def cadastro(request):
    if request.method == 'GET':
        return render(request, 'cadastro.html')

    elif request.method == 'POST':
        # Pegar os dados do formulário.
        username = request.POST.get('username')
        password = request.POST.get('senha')
        confirm_senha = request.POST.get('confirmar_senha')

        # Validar os dados
        if not password == confirm_senha:
            messages.add_message(request, constants.ERROR,
                                 'As senhas não conferem')
            return redirect('/usuarios/cadastro')

        if len(password) < 6:
            messages.add_message(request, constants.ERROR,
                                 'A senha deve conter pelo menos 6 caracteres')
            return redirect('/usuarios/cadastro')

        # Verificar se já existe.
        user_exists = User.objects.filter(username=username).exists()

        if user_exists:
            messages.add_message(request, constants.ERROR,
                                 'O usuário já existe.')
            return redirect('/usuarios/cadastro')
        else:
            user = User.objects.create_user(
                username=username, password=password)
            user.save()

        messages.add_message(request, constants.SUCCESS,
                             'Usuário cadastrado com sucesso.')
        return redirect('/usuarios/logar')


def logar(request):
    if request.method == 'GET':
        return render(request, 'logar.html')

    elif request.method == 'POST':
        # Pegar os dados.
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        # Validações se usuário existe e se as senhas conferem.
        user = auth.authenticate(username=username, password=senha)

        if user:
            auth.login(request, user)
            return redirect('/empresarios/cadastrar_empresa')

        else:
            messages.add_message(request, constants.ERROR,
                                 'Usuário ou senhas inválidas.')

            return redirect('/empresarios/cadastrar_empresa')
