from django.shortcuts import render, redirect, HttpResponse
from .models import Empresa, Documento
from django.contrib import messages
from django.contrib.messages import constants


# Create your views here.
def cadastrar_empresa(request):
    if request.method == 'GET':
        return render(request, 'cadastrar_empresa.html', {
            'tempo_existencia_choices': Empresa.tempo_existencia_choices,
            'area_choices': Empresa.area_choices
        })

    elif request.method == "POST":
        nome = request.POST.get('nome')
        cnpj = request.POST.get('cnpj')
        site = request.POST.get('site')
        tempo_existencia = request.POST.get('tempo_existencia')
        descricao = request.POST.get('descricao')
        data_final = request.POST.get('data_final')
        percentual_equity = request.POST.get('percentual_equity')
        estagio = request.POST.get('estagio')
        area = request.POST.get('area')
        publico_alvo = request.POST.get('publico_alvo')
        valor = request.POST.get('valor')
        pitch = request.FILES.get('pitch')
        logo = request.FILES.get('logo')

        try:
            empresa = Empresa(
                user=request.user,
                nome=nome,
                cnpj=cnpj,
                site=site,
                tempo_existencia=tempo_existencia,
                descricao=descricao,
                data_final_captacao=data_final,
                percentual_equity=percentual_equity,
                estagio=estagio,
                area=area,
                publico_alvo=publico_alvo,
                valor=valor,
                pitch=pitch,
                logo=logo
            )
            empresa.save()

        except:
            messages.add_message(request, constants.ERROR,
                                 'Erro interno do sistema')
            return redirect('/empresarios/cadastrar_empresa')

        messages.add_message(request, constants.SUCCESS,
                             'Empresa criada com sucesso')
        return redirect('/empresarios/cadastrar_empresa')


def listar_empresas(request):

    # Validar para que somente usuários logados acessam a página.
    if not request.user.is_authenticated:
        return redirect('/usuarios/logar')

    if request.method == 'GET':
        empresas = Empresa.objects.filter(user=request.user)
        return render(request, 'listar_empresas.html', {'empresas': empresas})

    elif request.method == 'POST':
        pass


def empresa(request, id: int):
    empresa = Empresa.objects.get(id=id)

    if request.method == 'GET':
        return render(request, 'empresa.html', {'empresa': empresa})

    elif request.method == 'POST':
        pass


def add_doc(request, id: int):

    if request.method == 'POST':
        empresa = Empresa.objects.get(id=id)
        titulo = request.POST.get('titulo')
        arquivo = request.FILES.get('arquivo')

        # Validações se o arquivo está OK.
        if not arquivo:
            messages.add_message(request, constants.ERROR,
                                 'Envie um arquivo.')
            return redirect(f'/empresarios/empresas/{id}')
        # Validar formato de arquivo da imagem.

        formato = arquivo.name.split('.')[-1].lower()
        print(formato, '\n')
        if not formato in ['jpg', 'jpeg', 'png', 'pdf']:
            messages.add_message(request, constants.ERROR,
                                 'Formato de arquivo incorreto. Envie um arquivo em formato JPG, JPEG, PNG ou PDF.')
            return redirect(f'/empresarios/empresas/{id}')

        documento = Documento.objects.create(
            empresa=empresa,
            titulo=titulo,
            arquivo=arquivo
        )
        documento.save()

        messages.add_message(request, constants.SUCCESS,
                             'Arquivo cadastrado com sucesso.')

        return redirect(f'/empresarios/empresas/{id}')
