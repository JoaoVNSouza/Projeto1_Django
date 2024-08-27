from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from empresarios.models import Empresa, Documento, Metricas
from investidores.models import PropostaInvestimento
from django.contrib import messages
from django.contrib.messages import constants
from datetime import datetime


# Create your views here.
def sugestao(request):
    # Validar se o usuário está logado.
    if not request.user.is_authenticated:
        return HttpResponse('Necessita estar logado para acessar esta página.')

    if request.method == 'GET':
        return render(request, 'sugestao.html', {'areas': Empresa.area_choices})

    elif request.method == 'POST':
        tipo = request.POST.get('tipo')
        area = request.POST.getlist('area')  # Pode selecionar mais de uma.
        valor = request.POST.get('valor')

        # Filtar por tipo.
        if tipo == 'C':  # Conservador.
            empresas = Empresa.objects.filter(
                tempo_existencia='+5').filter(estagio='E')

        elif tipo == 'D':  # Despojado.
            empresas = Empresa.objects.filter(
                tempo_existencia__in=['-6', '+6', '+1']).exclude(estagio='E')

        elif tipo == 'G':  # Genérico.
            empresas = Empresa.objects.all()

        # Filtar por área.
        empresas = empresas.filter(area__in=area)

        # Garantir que sempre tenha pelo menos um porcento do valuation.
        empresas_selecionadas = []

        for empresa in empresas:
            percentual = (float(valor) * 100) / float(empresa.valuation)

            if percentual >= 1:  # Filtar apenas empresas que tenha pelo menos 1%.
                empresas_selecionadas.append(empresa)

        return render(request, 'sugestao.html', {'areas': Empresa.area_choices, 'empresas_selecionadas': empresas_selecionadas})


def ver_empresa(request, id: int):
    empresa = Empresa.objects.get(id=id)
    documentos = Documento.objects.filter(empresa=empresa)
    metricas = Metricas.objects.filter(empresa=empresa)
    propostas = PropostaInvestimento.objects.filter(
        empresa=empresa).filter(status='PA')
    percentual_vendido = 0

    # Prosposta vendidas.
    for proposta in propostas:
        percentual_vendido += proposta.percentual

    # Validar se já vendeu 80%.
    limiar = (80 * empresa.percentual_equity) / 100
    concredizado = False

    if percentual_vendido >= limiar:
        concredizado = True

    # Percentual disponivel.
    percentual_disponivel = empresa.percentual_equity - percentual_vendido

    return render(request, 'ver_empresa.html', {'empresa': empresa, 'documentos': documentos, 'metricas': metricas, 'percentual_vendido': int(percentual_vendido), 'concredizado': concredizado, 'percentual_disponivel': percentual_disponivel})


def realizar_proposta(request, id: int):
    valor = request.POST.get('valor')
    percentual = request.POST.get('percentual')
    empresa = Empresa.objects.get(id=id)
    day = datetime.now().date()

    # Validações.
    # Verificar se a qtde de porcentagem que o investidor quer adiquirir seja menor que a qtde disponível.
    propostas_aceitas = PropostaInvestimento.objects.filter(
        empresa=empresa).filter(status='PA')

    total = 0
    for pa in propostas_aceitas:
        total += pa.percentual

    if total + float(percentual) > empresa.percentual_equity:
        messages.add_message(request, constants.WARNING,
                             'O percentual solicitado ultrapassa o percentual disponível.')
        return redirect(f'/investidores/ver_empresa/{id}')

    valuation = (100 * int(valor)) / int(percentual)
    if valuation < (int(empresa.valuation) / 2):
        messages.add_message(request, constants.WARNING, f'Seu valuation proposto foi R$\
                             {valuation} e deve ser no mínimo {empresa.valuation}')
        return redirect(f'/investidores/ver_empresa/{id}')

    # Salvar proposta.
    proposta = PropostaInvestimento(
        valor=valor,
        percentual=percentual,
        empresa=empresa,
        investidor=request.user,
        status='AS',
        data=day
    )

    proposta.save()

    return redirect(f'/investidores/assinar_contrato/{proposta.id}')


def assinar_contrato(request, id: int):
    proposta = PropostaInvestimento.objects.get(id=id)

    # Validar se proposta já está assinada.
    if proposta.status != 'AS':
        raise Http404()

    if request.method == 'GET':
        return render(request, 'assinar_contrato.html', {'proposta': proposta})

    elif request.method == 'POST':
        selfie = request.FILES.get('selfie')
        rg = request.FILES.get('rg')

        # Validar dados.
        proposta.selfie = selfie
        proposta.rg = rg
        proposta.status = 'PE'
        proposta.save()

        messages.add_message(request, constants.SUCCESS,
                             f'Contrato assinado com sucesso, sua proposta foi enviada a empresa.')
        return redirect(f'/investidores/ver_empresa/{proposta.empresa.id}')
