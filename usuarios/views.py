from django.shortcuts import render, HttpResponse
from django.contrib.auth.models import User


# Create your views here.
def cadastro(request):
    if request.method == 'GET':
        return render(request, 'cadastro.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('senha')
        confirm_senha = request.POST.get('confirmar_senha')

        # Validar os dados
        if not password == confirm_senha:
            return HttpResponse('As senhas não conferem')

        if len(password) < 6:
            return HttpResponse('Senha muito curta')

        # Verificar se já existe.
        user_exists = User.objects.filter(username=username).exists()

        user = User.objects.create_user(username=username, password=password)
        user.save()

        return HttpResponse('Usuário cadastrado com sucesso!, bem vindo {}'.format(username))
