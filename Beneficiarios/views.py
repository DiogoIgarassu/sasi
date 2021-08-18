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

scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('secret_client.json', scope)
client = gspread.authorize(creds)


def Conta_cestas(beneficiario):
    conta = 0
    ultima_data = ''
    meses = ['1_MES', '2_MES', '3_MES', '4_MES', '5_MES', '6_MES', '7_MES', '8_MES',
             '9_MES', '10_MES', '11_MES', '12_MES']
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
            sheet = client.open('cesta_basica_emergencial').sheet1
            dados = sheet.get_all_records()
            if tipo_busca == 'CPF':
                #busca = int(busca)
                for dic in dados:
                    if busca == dic['CPF']:
                        beneficiarios.append(dic)
            elif tipo_busca == 'NIS':
                #busca = busca.upper()
                for dic in dados:
                    if busca in dic['NIS']:
                        beneficiarios.append(dic)
            elif tipo_busca == 'Nome':
                busca = busca.upper()
                for dic in dados:
                    if busca in dic['NOME']:
                        beneficiarios.append(dic)
                        dic['QTAS_CESTAS'], dic['ULT_CESTA'] = Conta_cestas(dic)
            else:
                mensagem = "Nenhum beneficiário encontrato."
    except:
        mensagem = "Dados inválidos."

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
        ORDEM = ['N', 'STATUS', 'NOME', 'NIS', 'CPF', 'RG', 'TELEFONE', 'ENDERECO', 'BAIRRO', 'DATA_SOLICITACAO',
                 'ORIGEM',	'TECNICO_RESPONSAVEL', 'PROX_ENTREGA', 'PROX_CESTA', '1_MES', '2_MES',	'3_MES', '1A_RENOVACAO',
                 '4_MES', '5_MES', '6_MES', '2A_RENOVACAO', '7_MES', '8_MES', '9_MES', '3A_RENOVACAO',
                 '10_MES', '11_MES', '12_MES', 'OBSERVACOES']
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
    values_list= list(map(int, values_list))
    ult_id = max(values_list, key=int)
    novo_id = ult_id + 1
    #pos_col = f'A{novo_id + 1}'
    beneficiarios = []
    dic = {}
    ORDEM = ['N', 'STATUS', 'NOME', 'NIS', 'CPF', 'RG', 'TELEFONE', 'ENDERECO', 'BAIRRO', 'DATA_SOLICITACAO',
             'ORIGEM', 'TECNICO_RESPONSAVEL', 'PROX_ENTREGA', 'PROX_CESTA', '1_MES', '2_MES', '3_MES', '1A_RENOVACAO',
             '4_MES', '5_MES', '6_MES', '2A_RENOVACAO', '7_MES', '8_MES', '9_MES', '3A_RENOVACAO',
             '10_MES', '11_MES', '12_MES', 'OBSERVACOES']
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

dic_meses_eme = defaultdict(list)
dic_meses_eve = defaultdict(list)
dic_meses_total = defaultdict(list)
dic_count = defaultdict(list)

def conte_por_mes(mes, tipo):
    global dic_meses_eme, dic_meses_eve, dic_meses_total, dic_count

    if tipo == 'eme':
        dic_count = dic_meses_eme
    elif tipo == 'eve':
        dic_count = dic_meses_eve

    if mes == 1:
        if dic_count[1]:
            cont1 = int(dic_count[1]) + 1
            cont2 = int(dic_meses_total[1]) + 1
            dic_count[1] = cont1
            dic_meses_total[1] = cont2
        else:
            dic_count[1] = 1
            if dic_meses_total[1]:
                cont2 = int(dic_meses_total[1]) + 1
                dic_meses_total[1] = cont2
            else:
                dic_meses_total[1] = 1
    elif mes == 2:
        if dic_count[2]:
            cont1 = int(dic_count[2]) + 1
            cont2 = int(dic_meses_total[2]) + 1
            dic_count[2] = cont1
            dic_meses_total[2] = cont2
        else:
            dic_count[2] = 1
            if dic_meses_total[2]:
                cont2 = int(dic_meses_total[2]) + 1
                dic_meses_total[2] = cont2
            else:
                dic_meses_total[2] = 1
    elif mes == 3:
        if dic_count[3]:
            cont1 = int(dic_count[3]) + 1
            cont2 = int(dic_meses_total[3]) + 1
            dic_count[3] = cont1
            dic_meses_total[3] = cont2
        else:
            dic_count[3] = 1
            if dic_meses_total[3]:
                cont2 = int(dic_meses_total[3]) + 1
                dic_meses_total[3] = cont2
            else:
                dic_meses_total[3] = 1
    elif mes == 4:
        if dic_count[4]:
            cont1 = int(dic_count[4]) + 1
            cont2 = int(dic_meses_total[4]) + 1
            dic_count[4] = cont1
            dic_meses_total[4] = cont2
        else:
            dic_count[4] = 1
            if dic_meses_total[4]:
                cont2 = int(dic_meses_total[4]) + 1
                dic_meses_total[4] = cont2
            else:
                dic_meses_total[4] = 1
    elif mes == 5:
        if dic_count[5]:
            cont1 = int(dic_count[5]) + 1
            cont2 = int(dic_meses_total[5]) + 1
            dic_count[5] = cont1
            dic_meses_total[5] = cont2
        else:
            dic_count[5] = 1
            if dic_meses_total[5]:
                cont2 = int(dic_meses_total[5]) + 1
                dic_meses_total[5] = cont2
            else:
                dic_meses_total[5] = 1
    elif mes == 6:
        if dic_count[6]:
            cont1 = int(dic_count[6]) + 1
            cont2 = int(dic_meses_total[6]) + 1
            dic_count[6] = cont1
            dic_meses_total[6] = cont2
        else:
            dic_count[6] = 1
            if dic_meses_total[6]:
                cont2 = int(dic_meses_total[6]) + 1
                dic_meses_total[6] = cont2
            else:
                dic_meses_total[6] = 1
    elif mes == 7:
        if dic_count[7]:
            cont1 = int(dic_count[7]) + 1
            cont2 = int(dic_meses_total[7]) + 1
            dic_count[7] = cont1
            dic_meses_total[7] = cont2
        else:
            dic_count[7] = 1
            if dic_meses_total[7]:
                cont2 = int(dic_meses_total[7]) + 1
                dic_meses_total[7] = cont2
            else:
                dic_meses_total[7] = 1
    elif mes == 8:
        if dic_count[8]:
            cont1 = int(dic_count[8]) + 1
            cont2 = int(dic_meses_total[8]) + 1
            dic_count[8] = cont1
            dic_meses_total[8] = cont2
        else:
            dic_count[8] = 1
            if dic_meses_total[8]:
                cont2 = int(dic_meses_total[8]) + 1
                dic_meses_total[8] = cont2
            else:
                dic_meses_total[8] = 1
    elif mes == 9:
        if dic_count[9]:
            cont1 = int(dic_count[9]) + 1
            cont2 = int(dic_meses_total[9]) + 1
            dic_count[9] = cont1
            dic_meses_total[9] = cont2
        else:
            dic_count[9] = 1
            if dic_meses_total[9]:
                cont2 = int(dic_meses_total[9]) + 1
                dic_meses_total[9] = cont2
            else:
                dic_meses_total[9] = 1
    elif mes == 10:
        if dic_count[10]:
            cont1 = int(dic_count[10]) + 1
            cont2 = int(dic_meses_total[10]) + 1
            dic_count[10] = cont1
            dic_meses_total[10] = cont2
        else:
            dic_count[10] = 1
            if dic_meses_total[10]:
                cont2 = int(dic_meses_total[10]) + 1
                dic_meses_total[10] = cont2
            else:
                dic_meses_total[10] = 1
    elif mes == 11:
        if dic_count[1]:
            cont1 = int(dic_count[1]) + 1
            cont2 = int(dic_meses_total[11]) + 1
            dic_count[11] = cont1
            dic_meses_total[11] = cont2
        else:
            dic_count[11] = 1
            if dic_meses_total[11]:
                cont2 = int(dic_meses_total[11]) + 1
                dic_meses_total[11] = cont2
            else:
                dic_meses_total[11] = 1
    elif mes == 12:
        if dic_count[12]:
            cont1 = int(dic_count[12]) + 1
            cont2 = int(dic_meses_total[12]) + 1
            dic_count[12] = cont1
            dic_meses_total[12] = cont2
        else:
            dic_count[12] = 1
            if dic_meses_total[12]:
                cont2 = int(dic_meses_total[12]) + 1
                dic_meses_total[12] = cont2
            else:
                dic_meses_total[12] = 1

    if tipo == 'eme':
        dic_meses_eme = dic_count
    elif tipo == 'eve':
        dic_meses_eve = dic_count


    return dic_meses_eve, dic_meses_eme, dic_meses_total





@login_required
def relatorios(request):
    sheet = client.open('cesta_basica_emergencial').sheet1
    dados = sheet.get_all_records()
    template_name = 'beneficiarios/relatorios.html'
    eventual_count = 0
    emergencial_count = 0
    total_count = 0
    context = {}
    data_atual = datetime.date.today()
    mes_atual = data_atual.month

    global dic_meses_total, dic_meses_eme, dic_meses_eve
    dic_meses_total = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0}
    dic_meses_eme = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0}
    dic_meses_eve = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0}

    for dic in dados:
        data_benef = dic['DATA']
        data_benef = datetime.datetime.strptime(data_benef, '%d/%m/%Y')
        mes = data_benef.month
        if 'EVENTUAL' == dic['TIPO']:
            eventual_count += 1
            total_count += 1
            conte_por_mes(mes, 'eve')
        elif 'EMERGENCIAL' == dic['TIPO']:
            emergencial_count += 1
            total_count += 1
            conte_por_mes(mes, 'eme')

    '''print(dic_meses_total, 'Dicionario total')
    print(dic_meses_eme, 'Dicionario emergencial')
    print(dic_meses_eve, 'Dicionario eventual')'''
    context['total'] = total_count
    context['total_eme'] = emergencial_count
    context['total_eve'] = eventual_count
    mes_aterior = mes - 1
    context['total_anterior'] = dic_meses_total[mes_aterior]
    context['eme_anterior'] = dic_meses_eme[mes_aterior]
    context['eve_anterior'] = dic_meses_eve[mes_aterior]
    context['total_atual'] = dic_meses_total[mes]
    context['eme_atual'] = dic_meses_eme[mes]
    context['eve_atual'] = dic_meses_eve[mes]

    # DEFININDO NOME DO EIXO X E Y
    x_axis = 'Distruibuição de Cestas Básicas por mês em 2020.'
    y_axis = 'plotado por https://sasi-igarassu.herokuapp.com/'

    TOOLTIPS = [("Cidade", "@x"), ("Total", "@y")]

    meses = ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ']

    # DEFININDO AS CONFIGURAÇÕES DO GRÁFICO 1
    plt = figure(x_range=meses, plot_width=800, plot_height=450, title="tipo",
                 toolbar_location="right", x_axis_label=x_axis,
                 y_axis_label=y_axis, tools="pan,wheel_zoom,box_zoom,reset, hover, tap, save",
                 tooltips=TOOLTIPS)

    plt.xaxis.major_label_orientation = pi / 4
    plt.sizing_mode = 'scale_width'

    lista_total = []
    for mes in dic_meses_total:
        lista_total.append(mes)
    source = ColumnDataSource(data=dict(x=meses, y=lista_total))
    plt.vbar('x', top='y', color="#ffba57", bottom=0, width=0.6, source=source)
    plt.vbar('x', top='y', color="#ff5252", bottom=0, width=0.6, source=source)
    plt.line(x=meses, y=lista_total, color='red', legend_label='MORTOS', line_width=3)

    #print(meses)
    #print(lista_total)
    script, div = components(plt)
    context['script'] = script
    context['div'] = div

    plt2 = figure(x_range=['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ']
                  , plot_width=800, plot_height=800, title="tipo",
                 toolbar_location="right", x_axis_label=x_axis,
                 y_axis_label=y_axis, tools="pan,wheel_zoom,box_zoom,reset, hover, tap, save",
                 tooltips=TOOLTIPS)

    plt2.line(x=['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ'],
              y=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], color='red', legend_label='MORTOS', line_width=3)




    mensagem = "Em 2020 foram {0} Cestas eventuais e {1} cestas " \
               "emergenciais. Em julho foram {2} Cestas, " \
               "no mês atual foram até o momento {3}".format(eventual_count, emergencial_count,
                                                             dic_meses_total[7], dic_meses_total[mes_atual])

    context['mensagem'] = mensagem


    # create some example data
    output_file('vbar.html')

    p = figure(plot_width=400, plot_height=400)
    p.vbar(x=[1, 2, 3], width=0.5, bottom=0,
           top=[1.2, 2.5, 3.7], color="firebrick")
    script2, div2 = components(p)
    show(p)
    context['script2'] = script2
    context['div2'] = div2
    return render(request, template_name, context)

