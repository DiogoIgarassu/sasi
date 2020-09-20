from django.shortcuts import render
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from django.contrib.auth.decorators import login_required

scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('secret_client.json', scope)
client = gspread.authorize(creds)


@login_required
def busca_auxlio(request):
    sheet = client.open('Aux_emergencial').sheet1
    dados = sheet.get_all_records()

    tipo_busca = request.GET.get('tipo_busca', None)
    busca = request.GET.get('busca', None)
    beneficiarios = []
    mensagem = None

    try:
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
    sheet = client.open('cesta_basica_emergencial').sheet1
    dados = sheet.get_all_records()
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
