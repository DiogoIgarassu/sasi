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


scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('secret_client.json', scope)
client = gspread.authorize(creds)

ORDEM = ['N', 'STATUS', 'NOME', 'NIS', 'CPF', 'RG', 'TELEFONE', 'ENDERECO', 'BAIRRO', 'DATA_SOLICITACAO',
         'ORIGEM', 'TECNICO_RESPONSAVEL', 'PROX_ENTREGA', 'PROX_CESTA', '1_MES', '2_MES', '3_MES', '1A_RENOVACAO',
         '4_MES', '5_MES', '6_MES', '2A_RENOVACAO', '7_MES', '8_MES', '9_MES', '3A_RENOVACAO',
         '10_MES', '11_MES', '12_MES', 'OBSERVACOES']

meses = ['1_MES', '2_MES', '3_MES', '4_MES', '5_MES', '6_MES', '7_MES', '8_MES',
         '9_MES', '10_MES', '11_MES', '12_MES']

LISTA = ['CONT', 'DATA', 'NOME', 'CPF', 'NIS', 'BAIRRO', 'ORIGEM', 'QUANTAS']

lista_beneficiarios = []
mes = None
ano = None
mensagem_pdf = None


def Conta_cestas(beneficiario):
    conta = 0
    ultima_data = ''

    for mes in meses:
        for key in beneficiario:
            if mes == key and '/' in beneficiario[key]:
                conta += 1
                ultima_data = beneficiario[key]

    return conta, ultima_data

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
    cont_cestas = 0
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
            print(tipo_busca)
            sheet = client.open('cesta_basica_emergencial').sheet1
            dados = sheet.get_all_records()
            if tipo_busca == 'CPF':
                #busca = int(busca)
                for dic in dados:
                    if busca == dic['CPF']:
                        dic['CPF'] = dic['CPF'].replace('.', '').replace('-', '')
                        beneficiarios.append(dic)
                        dic['QTAS_CESTAS'], dic['ULT_CESTA'] = Conta_cestas(dic)
            elif tipo_busca == 'NIS':
                print("aqui 1", busca)
                #busca = busca.upper()
                for dic in dados:
                    if int(busca) == int(dic['NIS']):
                        dic['CPF'] = dic['CPF'].replace('.', '').replace('-', '')
                        beneficiarios.append(dic)
                        dic['QTAS_CESTAS'], dic['ULT_CESTA'] = Conta_cestas(dic)
            elif tipo_busca == 'Nome':
                busca = busca.upper()
                for dic in dados:
                    if busca in dic['NOME']:
                        dic['CPF'] = dic['CPF'].replace('.', '').replace('-', '')
                        beneficiarios.append(dic)
                        dic['QTAS_CESTAS'], dic['ULT_CESTA'] = Conta_cestas(dic)
    except:
        mensagem = "Dados inválidos."
    if len(beneficiarios) == 0:
        mensagem = "Nenhum beneficiário encontrato."

    return render(request, 'beneficiarios/busca_cestas.html', {'beneficiarios': beneficiarios, 'mensagem': mensagem, 'unique':unique})


@login_required
def beneficiario_details(request, pk):
    #print('método: ', request.method)
    sheet = client.open('cesta_basica_emergencial').sheet1
    pks = str(pk)
    cell = sheet.find(pks, None, in_column=1)
    #print(cell.address, cell.row, cell.col, cell.value)
    address = str(cell.address)
    #print(address)
    dados = sheet.get_all_records()
    beneficiarios = []
    if request.method == 'POST':
        updados = dict(request.POST.items())
        #print(updados)
        uplist = []
        for item in ORDEM:
            for key in updados:
                if key == item:
                    uplist.append(updados[key])
        sheet.update(f'{address}:AD56', [uplist])
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

    return render(request, template_name, {'beneficiario': beneficiarios, 'mensagem': mensagem})


@login_required
def beneficiario_register(request):
    #print('método: ', request.method)
    sheet = client.open('cesta_basica_emergencial').sheet1
    values_list = sheet.col_values(1)
    del(values_list[0])

    values_list = list(map(int, values_list))
    ult_id = max(values_list, key=int)
    novo_id = ult_id + 1

    beneficiarios = []
    dic = {}
    if request.method == 'POST':
        updados = dict(request.POST.items())
        uplist = []
        updados['N'] = novo_id
        for item in ORDEM:
            for key in updados:
                if key == item:
                    uplist.append(updados[key])

        sheet.update(f'A{novo_id+1}:AD56', [uplist])
        messages.success(request, 'Usuário cadastrado com sucesso')
        return redirect('beneficiarios:busca_cestas')
    for key in ORDEM:
        dic[key] = ''
    dic['N'] = novo_id
    beneficiarios.append(dic)
    novo_cadastro = True
    template_name = 'beneficiarios/beneficiario_details.html'

    return render(request, template_name, {'beneficiario': beneficiarios, 'novo': novo_cadastro})


@login_required
def lista_cestas(request):
    global lista_beneficiarios, mes, ano, mensagem_pdf
    context = {}
    status = request.GET.get('status', None)
    mes = request.GET.get('mes', None)
    #print(mes)
    ano = request.GET.get('ano', None)
    mensagem = False
    beneficiarios = None
    cont = 0
    template_name = 'beneficiarios/lista_cesta.html'

    if ano and mes:
        ano = int(ano)
        mes = int(mes)
        a, b = calendar.monthrange(ano, mes)
        data_i = f'1/{mes}/{ano}'
        data_f = f'{b}/{mes}/{ano}'

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
                    for m in meses:
                        if data == dic[m]:
                            cont += 1
                            dic['CONT'] = cont
                            dic['DATA'] = data
                            dic['QUANTAS'] = f'{m[0]}º MÊS'
                            dic['CPF'] = dic['CPF'].replace('.', '').replace('-', '')
                            beneficiarios.append(dic)
                            #print(dic)

        mensagem = f'De {data_i.strftime("%d/%m/%Y")} até {data_f.strftime("%d/%m/%Y")} foram distribuídas {cont} cestas básicas'

    if beneficiarios:
        context['beneficiarios'] = beneficiarios
        lista_beneficiarios = beneficiarios

    if mensagem:
        context['mensagem'] = mensagem
        mensagem_pdf = mensagem

    return render(request, template_name, context)


def export_csv(request):
    global lista_beneficiarios, mes, ano

    response = HttpResponse(content_type='text/csv', charset="utf-8")
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
    total = 0
    PROX_CESTA = 0
    proxs_beneficiarios = []
    sheet = client.open('cesta_basica_emergencial').sheet1
    dados = sheet.get_all_records()
    for linha in dados: #PARA CADA LINHA DO ARQUIVO
        total += 1
        STATUS = linha['STATUS']
        if dic_status[STATUS]: #CRIAR DICIONARIO DE STATUS
            cont1 = int(dic_status[STATUS]) + 1
            dic_status[STATUS] = cont1
        else:
            dic_status[STATUS] = 1
        for col in linha: #PARA CADA COLUNA DA LINHA
            if col in meses: #SE A COLUNA ESTA NA TABELA MESES
                DATA = linha[col]
                if '/' in DATA: #SE CAMPO ESTÁ PREENCHIDO
                    DATAT = datetime.datetime.strptime(DATA, '%d/%m/%Y')
                    MES_DATA = datetime.datetime.strftime(DATAT, "%B")
                    ANO_DATA = datetime.datetime.strftime(DATAT, "%Y")
                    ANO = datetime.datetime.strptime('2021', "%Y")
                    ANO = datetime.datetime.strftime(ANO, "%Y")
                    MES_DATA = str(MES_DATA)
                    if ANO_DATA == ANO: #SE O ANO FOR 2021
                        #print()
                        if dic_datas[MES_DATA]: #CRIAR DICIONARIOS DE MESES
                            dic_datas[MES_DATA].append(DATA)
                        else:
                            dic_datas[MES_DATA] = [DATA]

        cont, ultima_data = Conta_cestas(linha)
        p_cesta_date = datetime.datetime.strptime(ultima_data, '%d/%m/%Y')
        #p_cesta_date = p_cesta_date.replace(day=1)
        p_cesta_date = str(p_cesta_date.strftime("%B"))
        today = datetime.date.today()
        mes_atual = str(today.strftime("%B"))
        p_cesta = linha['PROX_CESTA']
        if "/" in p_cesta:
            p_cesta = p_cesta.split("/")
            if mes_atual == p_cesta_date:
                if int(p_cesta[1]) == int(p_cesta[0]):
                    PROX_CESTA += 1
                    proxs_beneficiarios.append(linha)
            if mes_atual != p_cesta_date:
                    if int(p_cesta[1]) > int(p_cesta[0]):
                        PROX_CESTA += 1
                        proxs_beneficiarios.append(linha)

    return total, dic_status, dic_datas, proxs_beneficiarios

@login_required
def relatorios(request):
    total, dic_status, dic_datas, proxs_beneficiarios = conte_cestas()
    template_name = 'beneficiarios/relatorios.html'
    context = {}
    today = datetime.date.today()
    first = today.replace(day=1)
    lastMonth = first - datetime.timedelta(days=1)
    mes_passado = str(lastMonth.strftime("%B"))
    mes_atual = str(first.strftime("%B"))

    context['total'] = total
    context['total_ativos'] = dic_status['DEFERIDO']
    context['total_finalizados'] = dic_status['FINALIZADO']
    context['total_suspensos'] = dic_status['SUSPENSO']
    context['total_indeferidos'] = dic_status['INDEFIRIDO']
    context['total_emergenciais'] = dic_status['EMERGENCIAL']
    context['proxs_beneficiarios'] = proxs_beneficiarios

    meses, qtd_mes = [], []
    ordem_mes = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
                 'October', 'November', 'December']
    for mes in ordem_mes:
        if mes in dic_datas:
            meses.append(mes)
            qtd_mes.append(len(dic_datas[mes]))

    context['total_2021'] = sum(qtd_mes)
    context['total_mes_anterior'] = len(dic_datas[mes_passado])
    context['total_esse_mes'] = len(dic_datas[mes_atual])
    context['total_prox_mes'] = len(proxs_beneficiarios)

    # DEFININDO NOME DO EIXO X E Y
    x_axis = 'Distruibuição de Cestas Básicas por mês em 2021.'
    y_axis = 'plotado por https://sasi-igarassu.herokuapp.com/'

    TOOLTIPS = [("Cidade", "@x"), ("Total", "@y")]


    # DEFININDO AS CONFIGURAÇÕES DO GRÁFICO 1
    plt = figure(x_range=meses, plot_width=800, plot_height=400, title="tipo",
                 toolbar_location="right", x_axis_label=x_axis,
                 y_axis_label=y_axis, tools="pan,wheel_zoom,box_zoom,reset, hover, tap, save",
                 tooltips=TOOLTIPS)

    plt.xaxis.major_label_orientation = pi / 4
    plt.sizing_mode = 'scale_width'

    source = ColumnDataSource(data=dict(x=meses, y=qtd_mes))
    plt.vbar('x', top='y', color="#ffba57", bottom=0, width=0.6, source=source)
    #plt.vbar('x', top='y', color="#ff5252", bottom=0, width=0.6, source=source)
    plt.line(x=meses, y=qtd_mes, color='red', line_width=3)

    #print(meses)
    #print(lista_total)
    script, div = components(plt)
    context['script'] = script
    context['div'] = div
    show(plt)

    mensagem = "Em 2021 foram entregues {0} cestas básicas " \
               ". Em {1} foram {2} Cestas, " \
               "no mês atual foram até o momento {3} cestas.".format(context['total_2021'], mes_passado,
                                                             context['total_mes_anterior'], context['total_prox_mes'])

    context['mensagem'] = mensagem


    return render(request, template_name, context)


