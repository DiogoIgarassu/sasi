from django.shortcuts import render
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint
from django.contrib.auth.decorators import login_required
import re


scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('secret_client.json', scope)
client = gspread.authorize(creds)

sheet = client.open('Aux_emergencial').sheet1
pp = pprint.PrettyPrinter()
dados = sheet.get_all_records()


@login_required
def busca_auxlio(request):
    tipo_busca = request.GET.get('tipo_busca', None)
    busca = request.GET.get('busca', None)
    beneficiarios = []
    mensagem = None
    print(tipo_busca)
    print(busca)


    try:
        if tipo_busca == 'CPF':
            busca = int(busca)
            for dic in dados:
                if busca == dic['CPF']:
                    beneficiarios.append(dic)
        elif tipo_busca == 'Nome':
            busca = busca.upper()
            print(busca)
            for dic in dados:
                if busca in dic['NOME']:
                    beneficiarios.append(dic)
        else:
            mensagem = "Nenhum beneficiário encontrato."
    except:
        mensagem = "Dados inválidos."


    #pp.pprint(beneficiarios)
    return render(request, 'beneficiarios/busca_auxilio.html', {'beneficiarios': beneficiarios, 'mensagem': mensagem})

