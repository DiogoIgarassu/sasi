from django.shortcuts import render
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from django.contrib.auth.decorators import login_required
import datetime
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
import csv


scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('secret_client.json', scope)
client = gspread.authorize(creds)


@login_required
def busca_auxlio(request):

    tipo_busca = request.GET.get('tipo_busca', None)
    busca = request.GET.get('busca', None)
    beneficiarios = []
    mensagem = None

    try:
        if tipo_busca:
            sheet = client.open('Aux_emergencial').sheet1
            dados = sheet.get_all_records()
            if tipo_busca == 'CPF':
                busca = int(busca)
                for dic in dados:
                    if busca == dic['CPF']:
                        beneficiarios.append(dic)
            elif tipo_busca == 'Nome':
                busca = busca.upper()
                for dic in dados:
                    if busca in dic['NOME']:
                        beneficiarios.append(dic)
            else:
                mensagem = "Nenhum beneficiário encontrato."
    except:
        mensagem = "Dados inválidos."


    #pp.pprint(beneficiarios)
    return render(request, 'beneficiarios/busca_auxilio.html', {'beneficiarios': beneficiarios, 'mensagem': mensagem})


@login_required
def busca_cestas(request, cpf=None):

    if cpf:
        tipo_busca = "CPF"
        busca = cpf
        unique = True
    else:
        tipo_busca = request.GET.get('tipo_busca', None)
        busca = request.GET.get('busca', None)
        unique = False
    beneficiarios = []
    mensagem = None

    try:
        if tipo_busca:
            sheet = client.open('cesta_basica_emergencial').sheet1
            dados = sheet.get_all_records()
            if tipo_busca == 'CPF':
                busca = int(busca)
                for dic in dados:
                    if busca == dic['CPF']:
                        beneficiarios.append(dic)
            elif tipo_busca == 'NIS':
                busca = busca.upper()
                for dic in dados:
                    if busca in dic['NIS']:
                        beneficiarios.append(dic)
            elif tipo_busca == 'Nome':
                busca = busca.upper()
                for dic in dados:
                    if busca in dic['NOME']:
                        beneficiarios.append(dic)
            else:
                mensagem = "Nenhum beneficiário encontrato."
    except:
        mensagem = "Dados inválidos."

    return render(request, 'beneficiarios/busca_cestas.html', {'beneficiarios': beneficiarios, 'mensagem': mensagem, 'unique':unique})


@login_required
def beneficiario_details(request, pk):
    sheet = client.open('cesta_basica_emergencial').sheet1
    dados = sheet.get_all_records()
    beneficiarios = []
    try:
       for dic in dados:
            if pk == dic['N']:
                beneficiarios.append(dic)
       else:
            mensagem = "Nenhum beneficiário encontrato."
    except:
        mensagem = "Dados inválidos."

    template_name = 'beneficiarios/beneficiario_details.html'

    return render(request, template_name, {'beneficiarios': beneficiarios, 'mensagem': mensagem})

@login_required
def lista_cestas(request):
    context = {}
    data_i = request.GET.get('datai', None)
    data_f = request.GET.get('dataf', None)
    mensagem = False
    beneficiarios = None

    template_name = 'beneficiarios/lista_cesta.html'

    try:
        if data_i:
            sheet = client.open('cesta_basica_emergencial').sheet1
            dados = sheet.get_all_records()
            beneficiarios = []
            data_i = datetime.datetime.strptime(data_i, '%d/%m/%Y')
            data_f = datetime.datetime.strptime(data_f, '%d/%m/%Y')
            date_generated = [data_i + datetime.timedelta(days=x) for x in range(0, (data_f - data_i).days + 1)]
            context['datai'] = data_i
            context['dataf'] = data_f

            for date in date_generated:
                for dic in dados:
                    data = date.strftime("%d/%m/%Y")
                    if data == dic['DATA']:
                        beneficiarios.append(dic)
    except:
        messages.info(request, 'Usuário não encontrado!')
        mensagem = "Certifique-se que digitou as datas corretas"

    if beneficiarios:
        context['beneficiarios'] = beneficiarios

    if mensagem:
        context['mensagem'] = mensagem

    return render(request, template_name, context)

def export_cestas(request, datai, dataf):
    response = HttpResponse(content_type='text/csv')
    cont = 0
    writer = csv.writer(response)
    writer.writerow(['N', 'DATA', 'CPF', 'NIS', 'NOME', 'ENDERECO', 'LOCALIDADE', 'TELEFONE', 'ORIGEM'
                        , 'AS_SOCIAL', 'TIPO', 'QUANT', 'OBSERVACAO'])
    data_i = datetime.datetime.strptime(datai[:10], '%Y-%m-%d')
    data_f = datetime.datetime.strptime(dataf[:10], '%Y-%m-%d')
    if datai:
        sheet = client.open('cesta_basica_emergencial').sheet1
        dados = sheet.get_all_records()
        beneficiarios = []
        date_generated = [data_i + datetime.timedelta(days=x) for x in range(0, (data_f - data_i).days + 1)]

        for date in date_generated:
            for dic in dados:
                data = date.strftime("%d/%m/%Y")
                if data == dic['DATA']:
                    beneficiarios.append(dic)
                    linha = (dic['N'], dic['DATA'], dic['CPF'], dic['NIS'], dic['NOME'], dic['ENDERECO']
                             , dic['LOCALIDADE'], dic['TELEFONE'], dic['ORIGEM']
                             , dic['AS_SOCIAL'], dic['TIPO'], dic['QUANT'], dic['OBSERVACAO'],)
                    writer.writerow(linha)

    response['Content-Disposition'] = 'attachment; filename="cesta_basica.csv"'

    return response