from django.shortcuts import render, redirect, HttpResponse
from .models import Empresa, Documento, Metricas
from investidores.models import PropostaInvestimento
from django.contrib import messages
from django.contrib.messages import constants
from datetime import datetime, timedelta


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
        nome_empresa = request.GET.get('empresa')
        empresas = Empresa.objects.filter(user=request.user)

        # Filtrar empresas por nome buscado.
        if nome_empresa:
            empresas = empresas.filter(nome__icontains=nome_empresa)

        return render(request, 'listar_empresas.html', {'empresas': empresas, 'nome_empresa': nome_empresa})


def dashboard(request, id: int):
    # Pegar dados da empresa e dia.
    empresa = Empresa.objects.get(id=id)
    today = datetime.now().date()

    seven_days_ago = today - timedelta(days=6)
    proposta_por_dia = {}  # {dia: quantia}

    for i in range(7):
        day = seven_days_ago + timedelta(days=i)

        propostas = PropostaInvestimento.objects.filter(
            empresa=empresa, status='PA', data=day)
        total_dia = 0
        for proposta in propostas:
            total_dia += proposta.valor

        proposta_por_dia[day.strftime('%d/%m/%Y')] = int(total_dia)

    for dia, total in proposta_por_dia.items():
        print(f'Data: {dia}, Total de Propostas: {total}')

    # Gerar gráfico.
    return render(request, 'dashboard.html', {'labels': list(proposta_por_dia.keys()), 'values': list(proposta_por_dia.values())})


def empresa(request, id: int):
    empresa = Empresa.objects.get(id=id)

    # Validar se não está tentando entrar na empresa de outro usuário.
    if not empresa.user == request.user:
        messages.add_message(request, constants.ERROR,
                             'Essa empresa não é sua.')
        return redirect(f'/empresarios/listar_empresas')

    if request.method == 'GET':
        documentos = Documento.objects.filter(empresa=empresa)

        # Método 1.
        # Percentual de propostas vendidas.

        percentual_vendido = 0
        for pi in PropostaInvestimento.objects.filter(status='PA'):
            percentual_vendido += pi.percentual

        # Método 2.
        total_captado = sum(PropostaInvestimento.objects.filter(
            status='PA').values_list('valor', flat=True))

        valuation_atual = (100 * float(total_captado) /
                           float(percentual_vendido)) if percentual_vendido != 0 else 0

        propostas_investimentos_enviadas = PropostaInvestimento.objects.filter(
            empresa=empresa).filter(status='PE')

        # print(propostas_investimentos_enviadas)
        return render(request, 'empresa.html', {'empresa': empresa, 'documentos': documentos, 'propostas': propostas_investimentos_enviadas, 'total_captado': total_captado, 'valuation_atual': valuation_atual})

    elif request.method == 'POST':
        pass


def add_doc(request, id: int):

    if request.method == 'POST':
        empresa = Empresa.objects.get(id=id)
        titulo = request.POST.get('titulo')
        arquivo = request.FILES.get('arquivo')

        # Validar se o usuário é o dono da empresa.
        if not empresa.user == request.user:
            messages.add_message(request, constants.ERROR,
                                 'Essa empresa não é sua.')
            return redirect(f'/empresarios/listar_empresas')

        # Validações se o arquivo está OK.
        if not arquivo:
            messages.add_message(request, constants.ERROR,
                                 'Envie um arquivo.')
            return redirect(f'/empresarios/empresas/{id}')

        # Validar formato de arquivo da imagem.
        formato = arquivo.name.split('.')[-1].lower()

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


def excluir_doc(request, id: int):

    # Pegar o documento.
    documento = Documento.objects.get(id=id)

    # Validar se o usuário é o dono da empresa.
    if documento.empresa.user != request.user:
        messages.add_message(request, constants.ERROR,
                             "Esse documento não é seu")
        return redirect(f'/empresarios/empresas/{documento.empresa.id}')

    # Deletar o documento.
    documento.delete()

    messages.add_message(request, constants.SUCCESS,
                         'Documento deletado com sucesso')

    return redirect(f'/empresarios/empresas/{documento.empresa.id}')


def add_metrica(request, id: int):

    if request.method == 'POST':
        empresa = Empresa.objects.get(id=id)
        titulo = request.POST.get('titulo')
        valor = request.POST.get('valor')

        # Validar se o usuário é o dono da empresa.
        pass

        metrica = Metricas(
            empresa=empresa,
            titulo=titulo,
            valor=valor
        )
        metrica.save()

        messages.add_message(request, constants.SUCCESS,
                             'Métrica cadastrada com sucesso')

        return redirect(f'/empresarios/empresas/{id}')


def gerenciar_proposta(request, id: int):
    acao = request.GET.get('acao')
    proposta_investimento = PropostaInvestimento.objects.get(id=id)

    if acao == 'aceitar':
        messages.add_message(request, constants.SUCCESS, 'Proposta aceita')
        proposta_investimento.status = 'PA'
    elif acao == 'rejeitar':
        messages.add_message(request, constants.SUCCESS, 'Proposta rejeitada')
        proposta_investimento.status = 'PR'

    proposta_investimento.save()

    return redirect(f'/empresarios/empresas/{proposta_investimento.empresa.id}')
