import codecs
import random
from .models import *
from django.shortcuts import render, redirect
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from django.contrib.auth.decorators import login_required
import datetime
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
import csv
from collections import defaultdict
from bokeh.plotting import figure, show, output_file
from bokeh.embed import components
from bokeh.models import ColumnDataSource
from math import pi
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure
from bokeh.sampledata.autompg import autompg_clean as df
from bokeh.transform import factor_cmap
import calendar
from reportlab.pdfgen import canvas
from xhtml2pdf import pisa
from Beneficiarios.utils import link_callback
import django.template.loader
from io import BytesIO
import time
from bokeh.palettes import Category10, Category20, Category20c, Turbo256
from bokeh.transform import factor_cmap
#from django.contrib.sessions.models import Session
#Session.objects.all().delete()

scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('secret_client.json', scope)
client = gspread.authorize(creds)

ORDEM = ['N', 'STATUS', 'NOME', 'NASCIMENTO', 'NIS', 'CPF', 'RG', 'TELEFONE', 'ENDERECO', 'BAIRRO', 'LOCALIDADE',
         'DATA_SOLICITACAO', 'ORIGEM', 'TECNICO_RESPONSAVEL', 'PROX_ENTREGA', 'PROX_CESTA', '1_MES', '2_MES', '3_MES',
         '1A_RENOVACAO', '4_MES', '5_MES', '6_MES', '2A_RENOVACAO', '7_MES', '8_MES', '9_MES', '3A_RENOVACAO',
         '10_MES', '11_MES', '12_MES', 'OBSERVACOES', 'ULTIMA_ATUALIZACAO']

ORDEM_PROMOVE = ['N', 'ID_BE', 'ESCOLARIDADE', 'TELEFONE2', 'DOCUMENTOS', 'OBSERVACOES', 'ULTIMA_ATUALIZACAO']

meses = ['1_MES', '2_MES', '3_MES', '4_MES', '5_MES', '6_MES', '7_MES', '8_MES',
         '9_MES', '10_MES', '11_MES', '12_MES']

LISTA = ['CONT', 'STATUS', 'DATA', 'NOME', 'CPF', 'NIS', 'BAIRRO', 'ORIGEM', 'QUANTAS']
LISTA_CURSOS = ['CONTADOR', 'CPF', 'NOME', 'CURSO', 'DATA']

mes_english = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
               'October', 'November', 'December']

mes_port = ['JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO', 'JULHO', 'AGOSTO', 'SETEMBRO',
               'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO']

CHECK = ['CPF_CHECK', 'RG_CHECK', 'NIS_CHECK', 'RESIDENCIA_CHECK', 'ESCOLARIDADE_CHECK']

FIELDS_ERROS = ['NIS', 'CPF', 'PROX_ENTREGA', 'PROX_CESTA', 'TODAS_DATAS', 'DATA_SOLICITACAO', '1_MES', '2_MES', '3_MES',
         '1A_RENOVACAO', '4_MES', '5_MES', '6_MES', '2A_RENOVACAO', '7_MES', '8_MES', '9_MES', '3A_RENOVACAO',
         '10_MES', '11_MES', '12_MES']

TODAY = datetime.date.today()
MES_ATUAL = str(TODAY.strftime("%B"))
MES_ATUAL_INDEX = mes_english.index(MES_ATUAL)
PROX_MES = mes_english[MES_ATUAL_INDEX + 1]
first = TODAY.replace(day=1)
lastMonth = first - datetime.timedelta(days=1)
MES_PASSADO = str(lastMonth.strftime("%B"))

lista_beneficiarios = []
lista_matriculados, lista_desistentes, cursos_existentes = [], [], []
mes = None
ano = None
mensagem_pdf = None


def traduzir(mes):
    if mes in mes_english:
        id = mes_english.index(mes)
        mes_traduzido = mes_port[id]
    elif mes in mes_port:
        id = mes_port.index(mes)
        mes_traduzido = mes_english[id]
    else:
        mes_traduzido = 'ERRO'
    return mes_traduzido


def Conta_cestas(beneficiario):
    conta = 0
    ultima_data = ''

    for mes in meses:
        for key in beneficiario:
            if mes == key and '/' in beneficiario[key]:
                conta += 1
                ultima_data = beneficiario[key]
                #print(mes, key, ultima_data)
    return conta, ultima_data


@login_required
def busca_auxlio(request):

    tipo_busca = request.GET.get('tipo_busca', None)
    busca = request.GET.get('busca', None)
    beneficiarios = []
    mensagem = None
    cont = 0

    try:
        if tipo_busca:
            sheet = client.open('Aux_emergencial').sheet1
            dados = sheet.get_all_records()
            if tipo_busca == 'CPF':
                busca = int(busca)
                for dic in dados:
                    if busca == dic['CPF']:
                        beneficiarios.append(dic)
                        cont += 1
                        mensagem = f'Foram encontrados {cont} cadastros com CPF {busca}'
            elif tipo_busca == 'Nome':
                busca = busca.upper()
                for dic in dados:
                    if busca in dic['NOME']:
                        beneficiarios.append(dic)
                        cont += 1
                        mensagem = f'Foram encontrados {cont} cadastros com nome {busca}'
            else:
                mensagem = "Nenhum beneficiário encontrado."
    except:
        mensagem = "Dados inválidos."


    #pp.pprint(beneficiarios)
    return render(request, 'beneficiarios/busca_auxilio.html', {'beneficiarios': beneficiarios, 'mensagem': mensagem})


@login_required
def busca_cestas(request, cpf=None):
    cont_cestas, cont = 0, 0
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
            #print(tipo_busca)
            sheet = client.open('cesta_basica_emergencial').sheet1
            dados = sheet.get_all_records()
            if tipo_busca == 'CPF':
                #busca = int(busca)
                for dic in dados:
                    if busca == dic['CPF']:
                        beneficiarios.append(dic)
                        dic['QTAS_CESTAS'], dic['ULT_CESTA'] = Conta_cestas(dic)
                        cont += 1
                        mensagem = f'Foram encontrados {cont} cadastros com CPF {busca}'
            elif tipo_busca == 'NIS':
                for dic in dados:
                    if str(busca) == str(dic['NIS']):
                        beneficiarios.append(dic)
                        dic['QTAS_CESTAS'], dic['ULT_CESTA'] = Conta_cestas(dic)
            elif tipo_busca == 'Nome':
                busca = busca.upper()
                for dic in dados:
                    if busca in dic['NOME']:
                        beneficiarios.append(dic)
                        dic['QTAS_CESTAS'], dic['ULT_CESTA'] = Conta_cestas(dic)
                        cont += 1
                        mensagem = f'Foram encontrados {cont} cadastros com nome {busca}.'
        else:
            tipo_busca = "Nome"

        if len(beneficiarios) == 0:
            mensagem = "Nenhum beneficiário encontrato."
    except:
        mensagem = "Ocorreu um erro interno, por favor entre em contato com o administrador"

    return render(request, 'beneficiarios/busca_cestas.html', {'beneficiarios': beneficiarios, 'mensagem': mensagem, 'unique':unique,
                                                               'tipo_busca': tipo_busca})


@login_required
def beneficiario_details(request, pk):

    status = Status.objects.all()
    unidades = UnidadeSuas.objects.all()
    uni, sta = [], []
    for u in unidades:
        uni.append(u.unidade)
    for s in status:
        sta.append(s.status)

    sheet = client.open('cesta_basica_emergencial').sheet1
    pks = str(pk)
    cell = sheet.find(pks, None, in_column=1)
    #print(cell.address, cell.row, cell.col, cell.value)
    address = str(cell.address)
    #print(address)
    dados = sheet.get_all_records()
    beneficiarios = []
    if request.method == 'POST':
        historico = client.open('cesta_basica_emergencial').worksheet("historico")
        values_list = historico.col_values(1)
        del (values_list[0])
        values_list = list(map(int, values_list))
        ult_id = max(values_list, key=int)
        novo_id = ult_id + 1

        user = request.user
        data1 = time.strftime('%d/%m/%Y', time.localtime())
        hora1 = time.strftime('%H:%M:%S', time.localtime())
        atualizacao = f'{hora1} de {data1} por {user}'

        updados = dict(request.POST.items())
        #print(updados)
        uplist = []
        for item in ORDEM:
            for key in updados:
                if key == item:
                    if key == 'ULTIMA_ATUALIZACAO':
                        updados[key] = atualizacao
                        historico.update(f'A{novo_id}:D{novo_id}', [[str(novo_id), pks, 0, atualizacao]])
                    uplist.append(updados[key])

        sheet.update(f'{address}:AG{cell.row}', [uplist])
        messages.success(request, 'Cadastro alterado com sucesso')
        return redirect('beneficiarios:busca_cestas')
    try:
       for dic in dados:
            if pk == dic['N']:
                beneficiarios.append(dic)
       else:
            mensagem = "Nenhum beneficiário encontrato."
            messages.info(request, 'Nenhum beneficiário encontrato.')
    except:
        mensagem = "Dados inválidos."

    template_name = 'beneficiarios/beneficiario_details.html'

    return render(request, template_name, {'beneficiario': beneficiarios, 'mensagem': mensagem,
                                           'unidades': uni, 'status': sta})


@login_required
def beneficiario_register(request):

    status = Status.objects.all()
    unidades = UnidadeSuas.objects.all()
    uni, sta = [], []

    for u in unidades:
        uni.append(u.unidade)
    for s in status:
        sta.append(s.status)

    sheet = client.open('cesta_basica_emergencial').sheet1
    values_list = sheet.col_values(1)
    #print(values_list)
    del(values_list[0])

    values_list = list(map(int, values_list))
    ult_id = max(values_list, key=int)
    novo_id = ult_id + 1

    beneficiarios = []
    dic = {}
    if request.method == 'POST':

        historico = client.open('cesta_basica_emergencial').worksheet("historico")
        values_list2 = historico.col_values(1)
        del (values_list2[0])
        values_list2 = list(map(int, values_list2))
        ult_id2 = max(values_list2, key=int)
        novo_id2 = ult_id2 + 1

        user = request.user
        data1 = time.strftime('%d/%m/%Y', time.localtime())
        hora1 = time.strftime('%H:%M:%S', time.localtime())
        atualizacao = f'{hora1} de {data1} por {user}'

        updados = dict(request.POST.items())
        uplist = []
        updados['N'] = novo_id
        for item in ORDEM:
            for key in updados:
                if key == item:
                    if key == 'ULTIMA_ATUALIZACAO':
                        updados[key] = atualizacao
                        historico.update(f'A{novo_id2}:D{novo_id2}', [[str(novo_id2), novo_id, 0, atualizacao]])
                    uplist.append(updados[key])

        sheet.update(f'A{novo_id+1}:AG{novo_id+1}', [uplist])
        messages.success(request, 'Usuário cadastrado com sucesso')
        return redirect('beneficiarios:busca_cestas')

    for key in ORDEM:
        dic[key] = ''
    dic['N'] = novo_id
    beneficiarios.append(dic)
    novo_cadastro = True

    template_name = 'beneficiarios/beneficiario_details.html'

    return render(request, template_name, {'beneficiario': beneficiarios, 'novo': novo_cadastro,
                                           'unidades': uni, 'status': sta})


@login_required
def lista_cestas(request):
    global lista_beneficiarios, mes, ano, mensagem_pdf
    context = {}
    status = request.GET.get('status', None)
    mes = request.GET.get('mes', None)
    ano = request.GET.get('ano', None)
    mensagem = False
    beneficiarios = None
    cont = 0
    template_name = 'beneficiarios/lista_cesta.html'

    if ano and mes:

        if mes != 'TODOS':
            ano = int(ano)
            mes = int(mes)
            a, b = calendar.monthrange(ano, mes)
            data_i = f'1/{mes}/{ano}'
            data_f = f'{b}/{mes}/{ano}'
            context['MES'] = mes_port[mes - 1]
        else:
            ano = int(ano)
            a, b = calendar.monthrange(ano, MES_ATUAL_INDEX + 1)
            data_i = f'1/1/{ano}'
            data_f = f'{b}/{MES_ATUAL_INDEX + 1}/{ano}'
            context['MES'] = mes

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
                    if dic['STATUS'] == status or status == 'TODOS':
                        data = date.strftime("%d/%m/%Y")
                        for m in meses:
                            if data == dic[m]:
                                cont += 1
                                dic['CONT'] = cont
                                dic['DATA'] = data
                                dic['QUANTAS'] = f'{m[0]}º MÊS'
                                beneficiarios.append(dic)
                                #print(dic)

        mensagem = f'De {data_i.strftime("%d/%m/%Y")} até {data_f.strftime("%d/%m/%Y")} foram distribuídas {cont} cestas básicas'

    if beneficiarios:
        context['beneficiarios'] = beneficiarios
        lista_beneficiarios = beneficiarios

    if mensagem:
        context['mensagem'] = mensagem
        mensagem_pdf = mensagem
    context['ANO'] = ano
    context['MES_VALOR'] = mes
    context['STATUS'] = status

    return render(request, template_name, context)


@login_required
def export_csv(request):
    global lista_beneficiarios, mes, ano

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response.write(codecs.BOM_UTF8)
    writer = csv.writer(response)
    writer.writerow(LISTA)

    for linha in lista_beneficiarios:
        row_dados = []
        for i in LISTA:
            if i in linha:
                row_dados.append(linha[i])
        writer.writerow(row_dados)

    file = f'cestas_basicas_mes_{mes}_ano_{ano}.csv'
    response['Content-Disposition'] = f'attachment; filename={file}'

    return response


@login_required
def export_pdf(request):
    template_path = 'beneficiarios/export_pdf.html'
    context = {'beneficiarios': lista_beneficiarios, 'mensagem': mensagem_pdf}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    file = f'cestas_basicas_mes_{mes}_ano_{ano}.pdf'
    response['Content-Disposition'] = f'attachment; filename={file}'
    # find the template and render it.
    template = django.template.loader.get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response, link_callback=link_callback)
    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


def conte_cestas():
    dic_status = defaultdict(list)
    dic_datas = defaultdict(list)
    dic_origens = defaultdict(list)
    dic_bairros = defaultdict(list)
    total_registros, total_ano, PROX_CESTA, CESTA_ATUAL_RECEBEU, CESTA_ATUAL_N_RECEBEU, pk = 0, 0, 0, 0, 0, 0
    atuais_ben_receberam, atuais_ben_n_receberam, proxs_beneficiarios,beneficiarios_desatualizados = [], [], [], []
    mes_atual_pt = traduzir(MES_ATUAL)
    prox_mes_pt = traduzir(PROX_MES)

    sheet = client.open('cesta_basica_emergencial').sheet1
    dados = sheet.get_all_records()

    for linha in dados: #PARA CADA LINHA DO ARQUIVO
        total_registros += 1 #TOTAL DE REGISTROS NO SISTEMA

        STATUS = linha['STATUS']
        if dic_status[STATUS]: #CRIAR DICIONARIO DE STATUS
            cont1 = int(dic_status[STATUS]) + 1
            dic_status[STATUS] = cont1
        else:
            dic_status[STATUS] = 1

        for col in linha: #PARA CADA COLUNA DA LINHA

            if col in meses: #SE A COLUNA ESTA NA TABELA MESES A RECEBER [1_MES 2_MES 3_MES ...]
                DATA = linha[col]
                if '/' in DATA: #SE CAMPO ESTÁ PREENCHIDO
                    DATA_FORMATADA = datetime.datetime.strptime(DATA, '%d/%m/%Y') #DATA NO PADRÃO d/m/Y
                    MES_DATA = datetime.datetime.strftime(DATA_FORMATADA, "%B") #MES DESTA DATA
                    ANO_DATA = datetime.datetime.strftime(DATA_FORMATADA, "%Y") #ANO DESTA DADA
                    ANO = datetime.datetime.strptime('2021', "%Y")
                    ANO = datetime.datetime.strftime(ANO, "%Y") #ANO DE 2021 FORMATADO
                    MES_DATA = str(MES_DATA)
                    if ANO_DATA == ANO: #SE O ANO FOR 2021

                        if linha['N'] != pk:
                            total_ano += 1
                            pk = linha['N']

                        MES_DATA = traduzir(MES_DATA)
                        if dic_datas[MES_DATA]: #CRIAR DICIONARIOS DE MESES
                            dic_datas[MES_DATA].append(DATA)
                        else:
                            dic_datas[MES_DATA] = [DATA]

                        ORIGEM = linha['ORIGEM']
                        if dic_origens[ORIGEM]:
                            dic_origens[ORIGEM].append(1)
                        else:
                            dic_origens[ORIGEM] = [1]

                        BAIRRO = linha['BAIRRO']
                        if dic_bairros[BAIRRO]:
                            dic_bairros[BAIRRO].append(1)
                        else:
                            dic_bairros[BAIRRO] = [1]

        cont, ultima_data = Conta_cestas(linha)
        p_cesta = linha['PROX_CESTA']
        p_cesta = p_cesta.strip('.')
        data_solicitacao = linha['DATA_SOLICITACAO']
        if linha['STATUS'] == 'DEFERIDO':
            #print('Cesta atual: ', CESTA_ATUAL, 'Prox Cesta: ', PROX_CESTA)
            if ultima_data:
                ult_cesta_date = datetime.datetime.strptime(ultima_data, '%d/%m/%Y')
                ult_cesta_date = str(ult_cesta_date.strftime("%B"))

                if "/" in p_cesta:
                    p_cesta = p_cesta.split("/")

                    if MES_ATUAL != ult_cesta_date and mes_atual_pt in linha['PROX_ENTREGA']: #AINDA NÃO RECEBEU ESTE MÊS
                        if int(p_cesta[1]) == int(p_cesta[0]): #RECEBERÁ A ÚLTIMA
                            CESTA_ATUAL_N_RECEBEU += 1
                            atuais_ben_n_receberam.append(linha)
                        elif int(p_cesta[1]) > int(p_cesta[0]): #VAI RECEBER ESTE MÊS E TEM PROXIMO MÊS
                            PROX_CESTA += 1
                            CESTA_ATUAL_N_RECEBEU += 1
                            proxs_beneficiarios.append(linha)
                            atuais_ben_n_receberam.append(linha)

                    elif MES_ATUAL == ult_cesta_date and prox_mes_pt in linha['PROX_ENTREGA']: #JA RECEBEU ESTE MêS E TEM PROXIMO MÊS
                        if int(p_cesta[1]) == int(p_cesta[0]): #A PROXIMA CESTA É A ULTIMA
                            CESTA_ATUAL_RECEBEU += 1
                            atuais_ben_receberam.append(linha)
                            PROX_CESTA += 1
                            proxs_beneficiarios.append(linha)

                    elif MES_ATUAL != ult_cesta_date and prox_mes_pt in linha['PROX_ENTREGA']: #FEZ SOLICITAÇÃO AGORA E TEM PROXIMO MÊS
                            if int(p_cesta[1]) > int(p_cesta[0]):       #PROXIMO MÊS RECEBE A PRIMEIRA CESTA
                                PROX_CESTA += 1
                                proxs_beneficiarios.append(linha)
                    else:
                        beneficiarios_desatualizados.append(linha)
            else:
                if "/" in p_cesta and "/" in data_solicitacao:
                    if mes_atual_pt in linha['PROX_ENTREGA']: #VAI RECEBER A PRIMEIRA ESTE MÊS
                        #print('setembro =', linha['PROX_ENTREGA'], linha['N'])
                        PROX_CESTA += 1
                        CESTA_ATUAL_N_RECEBEU += 1
                        proxs_beneficiarios.append(linha)
                        atuais_ben_n_receberam.append(linha)
                    else:
                        beneficiarios_desatualizados.append(linha)
                        #print('setembro =', linha['PROX_ENTREGA'], linha['N'])

    return total_registros, total_ano, dic_status, dic_datas, proxs_beneficiarios, beneficiarios_desatualizados,\
           atuais_ben_receberam, dic_bairros, dic_origens


@login_required
def relatorios(request):
    total_registros, total_ano, dic_status, dic_datas, proxs_beneficiarios, beneficiarios_desatualizados,\
    atuais_beneficiarios, dic_bairros, dic_origens = conte_cestas()
    template_name = 'beneficiarios/relatorios.html'
    context = {}

    MES_PASSADO_PT = traduzir(MES_PASSADO)
    MES_ATUAL_PT = traduzir(MES_ATUAL)
    PROX_MES_PT = traduzir(PROX_MES)

    context['total_registros'] = total_registros
    context['total_ano'] = total_ano
    context['total_ativos'] = dic_status['DEFERIDO']
    context['total_finalizados'] = dic_status['FINALIZADO']
    context['total_suspensos'] = dic_status['SUSPENSO']
    context['total_indeferidos'] = dic_status['INDEFERIDO']
    context['total_emergenciais'] = dic_status['EMERGENCIAL']
    context['total_ausentes'] = dic_status['AUSENTE']

    context['proxs_beneficiarios'] = proxs_beneficiarios
    context['beneficiarios_desatualizados'] = beneficiarios_desatualizados
    context['atuais_beneficiarios'] = atuais_beneficiarios

    meses, qtd_mes = [], []
    for mes in mes_port:
        if mes in dic_datas:
            meses.append(mes)
            qtd_mes.append(len(dic_datas[mes]))

    bairros, qtd_bairros = [], []
    for bairro in dic_bairros:
        bairros.append(bairro)
        qtd_bairros.append(len(dic_bairros[bairro]))
    if "" in bairros:
        b_index = bairros.index("")
        b_vazios = bairros.pop(b_index)
        qtd_b_vazios = qtd_bairros.pop(b_index)
        mensagem2 = f'Atenção! Existem {qtd_b_vazios} cadastros faltando colocar o bairro {b_vazios}'
        print(mensagem2)
    else:
        mensagem2 =None
    origens, qtd_origens = [], []
    for origem in dic_origens:
        origens.append(origem)
        qtd_origens.append(len(dic_origens[origem]))

    context['total_2021'] = sum(qtd_mes)
    context['total_mes_anterior'] = len(dic_datas[MES_PASSADO_PT])
    context['total_esse_mes'] = len(dic_datas[MES_ATUAL_PT])

    context['total_falta_esse_mes'] = len(atuais_beneficiarios)
    context['total_prox_mes'] = len(proxs_beneficiarios)
    context['total_desatualizados'] = len(beneficiarios_desatualizados)


    # DEFININDO AS CONFIGURAÇÕES DO GRÁFICO 1
    x_axis = 'Distruibuição de Cestas Básicas por mês em 2021.'
    y_axis = 'plotado por https://sasi-igarassu.herokuapp.com/'

    TOOLTIPS = [("Mês", "@x"), ("Total", "@y")]

    plt = figure(x_range=meses, plot_width=800, plot_height=400,
                 toolbar_location="right", x_axis_label=x_axis,
                 y_axis_label=y_axis, tools="pan,wheel_zoom,box_zoom,reset, hover, tap, save",
                 tooltips=TOOLTIPS)

    plt.xaxis.major_label_orientation = pi / 4
    plt.sizing_mode = 'scale_width'

    source = ColumnDataSource(data=dict(x=meses, y=qtd_mes))
    plt.vbar('x', top='y', color="#ffba57", bottom=0, width=0.6, source=source)
    #plt.vbar('x', top='y', color="#ff5252", bottom=0, width=0.6, source=source)
    plt.line(x=meses, y=qtd_mes, color='red', line_width=3)

    # DEFININDO AS CONFIGURAÇÕES DO GRÁFICO 2
    x_axis2 = 'Distruibuição de Cestas Básicas por Unidade SUAS em 2021.'
    y_axis2 = 'plotado por https://sasi-igarassu.herokuapp.com/'

    TOOLTIPS2 = [("Unidade SUAS", "@x"), ("Total", "@y")]

    plt2 = figure(x_range=origens, plot_width=800, plot_height=400,
                 toolbar_location="right", x_axis_label=x_axis2,
                 y_axis_label=y_axis2, tools="pan,wheel_zoom,box_zoom,reset, hover, tap, save",
                 tooltips=TOOLTIPS2)

    plt2.xaxis.major_label_orientation = pi / 4
    plt2.sizing_mode = 'scale_width'
    total_origens = len(origens)

    source2 = ColumnDataSource(data=dict(x=origens, y=qtd_origens, color=Category20[total_origens]))
    plt2.vbar('x', top='y', color='color', bottom=0, width=0.6, source=source2)
    #plt2.line(x=origens, y=qtd_origens, color='red', line_width=3)

    # DEFININDO AS CONFIGURAÇÕES DO GRÁFICO 3
    x_axis3 = 'Distruibuição de Cestas Básicas por Bairros em 2021.'
    y_axis3 = 'plotado por https://sasi-igarassu.herokuapp.com/'

    TOOLTIPS3 = [("Bairro", "@x"), ("Total", "@y")]

    plt3 = figure(x_range=bairros, plot_width=800, plot_height=400,
                  toolbar_location="right", x_axis_label=x_axis3, title=mensagem2,
                  y_axis_label=y_axis3, tools="pan,wheel_zoom,box_zoom,reset, hover, tap, save",
                  tooltips=TOOLTIPS3)

    plt3.xaxis.major_label_orientation = pi / 4
    plt3.sizing_mode = 'scale_width'
    turbo_color = list(Turbo256)
    random.shuffle(turbo_color)
    total_bairros = len(bairros)

    source3 = ColumnDataSource(data=dict(x=bairros, y=qtd_bairros, color=turbo_color[:total_bairros]))
    plt3.vbar('x', top='y', color="color", bottom=0, width=0.6, source=source3)
    #plt3.line(x=bairros, y=qtd_bairros, color='red', line_width=1)

    script, div = components(plt)
    context['script'] = script
    context['div'] = div

    script2, div2 = components(plt2)
    context['script2'] = script2
    context['div2'] = div2

    script3, div3 = components(plt3)
    context['script3'] = script3
    context['div3'] = div3
    #show(plt)

    mensagem = "Em 2021 foram entregues {0} cestas básicas " \
               ". Em {1} foram {2} Cestas, " \
               "no mês atual foram {3} cestas até o momento.".format(context['total_2021'], MES_PASSADO_PT,
                                                             context['total_mes_anterior'], context['total_esse_mes'])

    context['mensagem'] = mensagem


    return render(request, template_name, context)


@login_required
def promove_details(request, pk):

    RG, CPF, NIS, RESIDENCIA, ESCOLARIDADE = False, False, False, False, False
    status = Status.objects.all()
    escolaridade = Escolaridade.objects.all()
    cursos = Curso.objects.all()
    unidades = UnidadeSuas.objects.all()
    esc, cur, uni, sta = [], [], [], []
    for e in escolaridade:
        esc.append(e.nivel)
    for c in cursos:
        cur.append(c.curso)
    for u in unidades:
        uni.append(u.unidade)
    for s in status:
        sta.append(s.status)

    sheet = client.open('cesta_basica_emergencial').sheet1
    promove = client.open('cesta_basica_emergencial').worksheet("Promove")
    cursos = client.open('cesta_basica_emergencial').worksheet("Cursos")
    cursos_desistentes = client.open('cesta_basica_emergencial').worksheet("cursos_desistentes")

    pks = str(pk)
    novo_id2 = False
    try:
        cell = promove.find(pks, None, in_column=2)
        address = str(cell.address)
        #print(cell.address, cell.row, cell.col, cell.value)
    except:
        values_list2 = promove.col_values(1)
        del (values_list2[0])
        values_list2 = list(map(int, values_list2))
        ult_id2 = max(values_list2, key=int)
        novo_id2 = ult_id2 + 1
        #print(ult_id2, novo_id2)

    dados = sheet.get_all_records()
    dados_promove = promove.get_all_records()
    dados_cursos = cursos.get_all_records()
    dados_cursos_desistentes = cursos_desistentes.get_all_records()
    beneficiarios, lista_promove, lista_cursos, lista_cursos_desistentes = [], [], [], []

    # PREPARAÇÕES AÇÕES CURSOS
    for lst in dados_cursos:
        if pk == lst['ID_BE']:
            lista_cursos.append(lst['CURSO'])

    #PREPARAÇÕES AÇÕES CURSOS DESISTÊNTES
    dic_id_desistentes = {}
    for lst in dados_cursos_desistentes:
        if pk == lst['ID_BE']:
            nome_curso = lst['CURSO']
            lista_cursos_desistentes.append(nome_curso)
            dic_id_desistentes[nome_curso] = lst['N']

     ####### MÉTODO POST ######
    if request.method == 'POST':
        updados = dict(request.POST.items())

        #VERIFICAR SE TEM CURSOS MARCADOS
        lista_entrar_cursos, lista_sair_cursos = [], []
        for curso in updados:
            if 'ENTRAR_CURSO' in str(curso):
                lista_entrar_cursos.append(updados[curso])
                #print('MATRICULAR', curso, updados[curso])
            elif 'SAIR_CURSO' in str(curso):
                lista_sair_cursos.append(updados[curso])
                #print('DESISTENTE', curso, updados[curso])

        #ENCONTRAR POSIÇÃO HISTÓRICO
        historico = client.open('cesta_basica_emergencial').worksheet("historico")
        values_list = historico.col_values(1)
        del (values_list[0])
        values_list = list(map(int, values_list))
        ult_id = max(values_list, key=int)
        novo_id = ult_id + 1

        user = request.user
        data1 = time.strftime('%d/%m/%Y', time.localtime())
        hora1 = time.strftime('%H:%M:%S', time.localtime())
        atualizacao = f'{hora1} de {data1} por {user}'

        #VERIFICAR SE JÁ ESTÁ MATRICULADO
        for curso in lista_entrar_cursos:
            if curso not in lista_cursos:
                values_list_cursos = cursos.col_values(1)
                del (values_list_cursos[0])
                values_list_cursos = list(map(int, values_list_cursos))
                ult_id_curso = max(values_list_cursos, key=int)
                novo_id_curso = ult_id_curso+ 1
                cursos.update(f'A{novo_id_curso + 1}:F{novo_id_curso + 1}', [[str(novo_id_curso), pks, updados['NOME'], updados['CPF'], curso, data1]])

        #VERIFICAR SE JÁ DESISTIU DO CURSO
        for curso in lista_sair_cursos:
            if curso not in lista_cursos_desistentes:
                #não faz nada
                values_list_cursos_desistente =cursos_desistentes.col_values(1)
                del (values_list_cursos_desistente[0])
                values_list_cursos_desistente = list(map(int, values_list_cursos_desistente))
                ult_id_curso_desistente = max(values_list_cursos_desistente, key=int)
                novo_id_curso_desistente = ult_id_curso_desistente + 1
                cursos_desistentes.update(f'A{novo_id_curso_desistente + 1}:F{novo_id_curso_desistente + 1}',
                              [[str(novo_id_curso_desistente), pks, updados['NOME'], updados['CPF'], curso, data1]])

        # VERIFICAR SE VOLTOU PRO CURSO
        for curso in lista_cursos_desistentes:
            if curso not in lista_sair_cursos:
                id_desiste = dic_id_desistentes[curso]
                cursos_desistentes.update(f'A{id_desiste + 1}:F{id_desiste + 1}',
                              [[str(id_desiste), '--', '--', '--', '--', data1]])

        documentos = ""
        for doc in CHECK:
            if doc in updados:
                documentos = updados[doc] + ", " + documentos
        #print(updados)
        uplist = []
        for item in ORDEM_PROMOVE:
            if item == "DOCUMENTOS":
                updados[item] = documentos
            if item in updados:
                if item == 'ULTIMA_ATUALIZACAO':
                    updados[item] = atualizacao
                    historico.update(f'A{novo_id}:D{novo_id}', [[str(novo_id), 0, pks, atualizacao]])
                uplist.append(updados[item])
        if novo_id2:
            uplist.insert(0, novo_id2)
            #print(f'A{novo_id2+1}:G{novo_id2+1}')
            promove.update(f'A{novo_id2+1}:G{novo_id2+1}', [uplist])
        else:
            promove.update(f'B{cell.row}:G{cell.row}', [uplist])
        messages.success(request, 'Cadastro alterado com sucesso')
        return redirect('beneficiarios:promove_cursos')

    try:
       for dic in dados:
            if pk == dic['N']:
                beneficiarios.append(dic)
                dic['QTAS_CESTAS'], dic['ULT_CESTA'] = Conta_cestas(dic)
       else:
            mensagem = "Nenhum beneficiário encontrato."
            messages.info(request, 'Nenhum beneficiário encontrato.')
    except:
        mensagem = "Dados inválidos."

    # PRAPARAR AÇÕES DOCUMENTOS
    for lst in dados_promove:
        if pk == lst['ID_BE']:
            beneficiarios[0]['ESCOLARIDADE'] = lst['ESCOLARIDADE']
            beneficiarios[0]['TELEFONE2'] = lst['TELEFONE2']
            beneficiarios[0]['DOCUMENTOS'] = lst['DOCUMENTOS']
            beneficiarios[0]['OBSERVACOES'] = lst['OBSERVACOES']
            beneficiarios[0]['ULTIMA_ATUALIZACAO'] = lst['ULTIMA_ATUALIZACAO']
            if 'RG' in lst['DOCUMENTOS']:
                RG = True
            if 'CPF' in lst['DOCUMENTOS']:
                CPF = True
            if 'NIS' in lst['DOCUMENTOS']:
                NIS = True
            if 'RESIDENCIA' in lst['DOCUMENTOS']:
                RESIDENCIA = True
            if 'ESCOLARIDADE' in lst['DOCUMENTOS']:
                ESCOLARIDADE = True

    template_name = 'beneficiarios/promove_details.html'
    context = {'beneficiario': beneficiarios, 'mensagem': mensagem, 'escolaridades': esc, 'cursos': cur, 'unidades': uni,
               'status': sta, 'cursos_registrados': lista_cursos, 'cursos_desistentes': lista_cursos_desistentes,
               'RG': RG, 'CPF': CPF, 'NIS': NIS, 'RESIDENCIA': RESIDENCIA, 'ESCOLARIDADE': ESCOLARIDADE}

    return render(request, template_name, context)


@login_required
def promove_cursos(request):
    context = {}
    global lista_matriculados, lista_desistentes, cursos_existentes
    lista_matriculados, lista_desistentes, cursos_existentes = [], [], []
    cursos_matriculados = client.open('cesta_basica_emergencial').worksheet("Cursos")
    cursos_desistentes = client.open('cesta_basica_emergencial').worksheet("cursos_desistentes")
    dados_cursos_matriculados = cursos_matriculados.get_all_records()
    dados_cursos_desistentes = cursos_desistentes.get_all_records()
    cursos = Curso.objects.all()

    for c in cursos:
        cursos_existentes.append(c.curso)

    dic_desistentes = {}
    for curso in cursos_existentes:
        cont_matriculado, cont_desistente = 0, 0
        for lst in dados_cursos_desistentes:
            if curso == lst['CURSO']:
                cont_desistente += 1
                lst['CONTADOR'] = cont_desistente
                lista_desistentes.append(lst)
                dic_desistentes[lst['ID_BE']] = lst['CURSO']
        for lst in dados_cursos_matriculados:
            if curso == lst['CURSO']:
                if not lst['ID_BE'] in dic_desistentes or curso != dic_desistentes[lst['ID_BE']]:
                    cont_matriculado += 1
                    lst['CONTADOR'] = cont_matriculado
                    lista_matriculados.append(lst)

    context['cursos'] = cursos_existentes
    context['matriculados'] = lista_matriculados
    context['desistentes'] = lista_desistentes

    template_name = 'beneficiarios/lista_cursos.html'

    return render(request, template_name, context)


@login_required
def export_cursos_pdf(request):
    template_path = 'beneficiarios/lista_cursos_pdf.html'
    context= {}
    context['cursos'] = cursos_existentes
    context['matriculados'] = lista_matriculados
    context['desistentes'] = lista_desistentes
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    file = 'Lista Igarassu Promove.pdf'
    response['Content-Disposition'] = f'attachment; filename={file}'
    # find the template and render it.
    template = django.template.loader.get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response, link_callback=link_callback)
    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


@login_required
def export_cursos_csv(request):
    global lista_matriculados

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response.write(codecs.BOM_UTF8)
    writer = csv.writer(response)
    writer.writerow(LISTA_CURSOS)

    for linha in lista_matriculados:
        row_dados = []
        for i in LISTA_CURSOS:
            if i in linha:
                row_dados.append(linha[i])

        writer.writerow(row_dados)


    file = 'Lista de Matriculados por curso.csv'
    response['Content-Disposition'] = f'attachment; filename={file}'

    return response



def busca_erros(request):

    context= {}
    lista_erros = []
    sheet = client.open('cesta_basica_emergencial').sheet1
    dados = sheet.get_all_records()
    busca = request.GET.get('busca', 'CPF')
    datas_erros = FIELDS_ERROS[5:]

    for linha in dados:
        dic_erros = {}
        if busca in datas_erros:
            data = linha[busca]
            if data != '':
                try:
                    data = datetime.datetime.strptime(data, '%d/%m/%Y')
                except:
                    dic_erros['N'] = linha['N']
                    dic_erros['NOME'] = linha['NOME']
                    dic_erros['FIELD'] = linha[busca]
                    dic_erros['MSG'] = 'Data errada'
        elif busca == "TODAS_DATAS":
            for data_erro in datas_erros:
                data = linha[data_erro]
                if data != '':
                    try:
                        data = datetime.datetime.strptime(data, '%d/%m/%Y')
                    except:
                        dic_erros['N'] = linha['N']
                        dic_erros['NOME'] = linha['NOME']
                        dic_erros['FIELD'] = linha[data_erro]
                        dic_erros['MSG'] = f'Data errada em {data_erro}'
        elif busca == "PROX_ENTREGA":
            p_entrega = linha['PROX_ENTREGA'].upper()
            p_entrega = p_entrega.split('.')
            if len(p_entrega) > 1:
                try:
                    if p_entrega[0] not in mes_port or int(p_entrega[1]) < 2020 and int(p_entrega[1]) > 2021:
                        dic_erros['N'] = linha['N']
                        dic_erros['NOME'] = linha['NOME']
                        dic_erros['FIELD'] = linha['PROX_ENTREGA']
                        dic_erros['MSG'] = 'Prox Entrega errada'
                except:
                    dic_erros['N'] = linha['N']
                    dic_erros['NOME'] = linha['NOME']
                    dic_erros['FIELD'] = linha['PROX_ENTREGA']
                    dic_erros['MSG'] = 'Prox Entrega errada'
        elif busca == "PROX_CESTA":
            p_cesta = linha['PROX_CESTA']
            p_cesta = p_cesta.replace('.', '')
            p_cesta = p_cesta.split('/')
            if len(p_cesta) > 1:
                try:
                    if int(p_cesta[1]) - int(p_cesta[0]) < 0:
                        #print(int(p_cesta[1]) - int(p_cesta[0]), 'no try')
                        dic_erros['N'] = linha['N']
                        dic_erros['NOME'] = linha['NOME']
                        dic_erros['FIELD'] = linha['PROX_CESTA']
                        dic_erros['MSG'] = 'Prox cesta errada'
                except:
                    #print(linha['PROX_CESTA'], p_cesta, p_cesta[1], p_cesta[1], 'no except')
                    dic_erros['N'] = linha['N']
                    dic_erros['NOME'] = linha['NOME']
                    dic_erros['FIELD'] = linha['PROX_CESTA']
                    dic_erros['MSG'] = 'Prox cesta errada'
        elif busca == "CPF":
            cpf = linha['CPF']
            try:
                cpf = str(cpf)
                cpf = cpf.replace('.', '')
                cpf = cpf.replace('-', '')
                digitos_cpf = len(cpf)
                if digitos_cpf != 11 and cpf != '':
                    dic_erros['N'] = linha['N']
                    dic_erros['NOME'] = linha['NOME']
                    dic_erros['FIELD'] = linha['CPF']
                    dic_erros['MSG'] = 'CPF ERRADO'
                    cpf = int(cpf)
            except:
                #print('erro em', linha['N'])
                dic_erros['N'] = linha['N']
                dic_erros['NOME'] = linha['NOME']
                dic_erros['FIELD'] = linha['CPF']
                dic_erros['MSG'] = 'CPF ERRADO'

        elif busca == "NIS":
            try:
                nis = linha['NIS']
                nis = str(nis)
                nis = nis.replace('.', '')
                digitos_nis = len(nis)
                if digitos_nis != 11 and nis != '':
                    dic_erros['N'] = linha['N']
                    dic_erros['NOME'] = linha['NOME']
                    dic_erros['FIELD'] = linha['NIS']
                    dic_erros['MSG'] = 'NIS ERRADO'
                    nis = int(nis)
            except:
                #print('erro em', linha['N'])
                dic_erros['N'] = linha['N']
                dic_erros['NOME'] = linha['NOME']
                dic_erros['FIELD'] = linha['NIS']
                dic_erros['MSG'] = 'NIS ERRADO'

        if len(dic_erros) != 0:
            lista_erros.append(dic_erros)
    context['fields'] = FIELDS_ERROS
    context['field_buscado'] = busca
    context['lista_erros'] = lista_erros
    context['qtd_erros'] = len(lista_erros)
    #print(context)
    return render(request, 'beneficiarios/busca_erros.html', context)

