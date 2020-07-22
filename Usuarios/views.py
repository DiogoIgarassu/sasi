from django.shortcuts import render, redirect, get_object_or_404
from .forms import user_form, beneficiario_form
from .models import Usuario, Beneficiario, Beneficio, Estoque_beneficio
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import io
import csv

@login_required
def buscar_usuarios(request):
    dados = {}
    busca_cpf = request.GET.get('busca_cpf', None)
    busca_nome = request.GET.get('busca_nome', None)

    if busca_cpf:
        usuario = Usuario.objects.filter(CPF=busca_cpf)
    elif busca_nome:
        usuario = Usuario.objects.filter(nome__icontains=busca_nome)
    else:
        usuario = ''

    dados['usuarios'] = usuario
    return render(request, 'usuarios/busca_usuario.html', dados)

@login_required
def buscar_beneficiarios(request):
    dados = {}
    busca_cpf = request.GET.get('busca_cpf', None)
    beneficiario = ''
    usuario = ''
    mensagem = False
    try:
        if busca_cpf:

            usuario = Usuario.objects.filter(CPF=busca_cpf)
            usuario_id = Usuario.objects.get(CPF=busca_cpf)
            beneficiario = Beneficiario.objects.filter(nome_id=usuario_id.pk).order_by('-data_beneficio')
            if not usuario:
                mensagem = "Usuário não localizado com CPF informado!"
    except:
        messages.info(request, 'Usuário não encontrado!')
        mensagem = "CPF inválido ou Usuário não existe"

    dados['beneficiarios'] = beneficiario
    dados['usuarios'] = usuario
    if mensagem:
        dados['mensagem'] = mensagem

    return render(request, 'usuarios/busca_beneficiario.html', dados)

@login_required
def all_usuarios(request):
    dados = {}
    usuario = Usuario.objects.all().order_by('-created_at')[:50]
    dados['usuarios'] = usuario

    return render(request, 'usuarios/lista_usuarios.html', dados)

@login_required
def all_beneficiarios(request):
    dados = {}

    beneficiarios = Beneficiario.objects.all().order_by('-data_beneficio')[:50]
    usuarios = Usuario.objects.all()
    dados['beneficiarios'] = beneficiarios
    dados['usuarios'] = usuarios

    return render(request, 'usuarios/lista_beneficiarios.html', dados)

@login_required
def add_usuarios(request):
    data = {}
    form = user_form(request.POST or None)

    if form.is_valid():
        usuario = form.save(commit=False)
        usuario.user = request.user
        usuario.save()
        messages.success(request, 'Cadastro criado com sucesso')
        return redirect('usuarios:index')

    data['frase'] = "Adicionar Novo Usuário"
    data['form'] = form
    return render(request, 'usuarios/form_usuarios.html', data)

@login_required
def add_beneficiario(request, cpf):
    data = {}

    usuario = Usuario.objects.get(CPF=cpf)
    beneficio = Beneficio.objects.get(pk=1)

    form = beneficiario_form(request.POST or None)

    if form.is_valid():
        inclusao = form.save(commit=False)
        inclusao.user = request.user
        inclusao.tipo_beneficio = beneficio
        inclusao.nome = usuario
        inclusao.is_active = True
        inclusao.save()
        messages.success(request, 'BenefÍcio entregue com sucesso')
        return redirect('usuarios:busca_beneficiarios')

    data['frase'] = "Adicionar Novo Usuário"
    data['form'] = form
    return render(request, 'usuarios/form_beneficiarios.html', data)


@login_required
def up_usuario(request, pk):
    dados = {}
    usuario = Usuario.objects.get(pk=pk)
    form = user_form(request.POST or None, instance=usuario)

    if form.is_valid():
        form.save()
        messages.success(request, 'Os dados foram alterados com sucesso')
        return redirect('usuarios:index')

    dados['form'] = form
    dados['usuario'] = usuario
    return render(request, 'usuarios/form_usuarios.html', dados)

@login_required
def up_beneficiario(request, pk):
    dados = {}
    beneficiario = Beneficiario.objects.get(pk=pk)
    form = beneficiario_form(request.POST or None, instance=beneficiario)

    if form.is_valid():
        form.save()
        messages.success(request, 'Os dados foram alterados com sucesso')
        return redirect('usuarios:busca_beneficiarios')

    dados['form'] = form
    dados['beneficiario'] = beneficiario
    return render(request, 'usuarios/form_beneficiarios.html', dados)

@login_required
def del_usuario(request, pk):
    usuario = Usuario.objects.get(pk=pk)
    usuario.delete()
    return redirect('usuarios:index')

@login_required
def beneficiario(request):
    dados = {}
    busca_cpf = request.GET.get('busca_cpf', None)
    busca_nome = request.GET.get('busca_nome', None)

    if busca_cpf:
        usuario = Usuario.objects.filter(CPF=busca_cpf)
    elif busca_nome:
        usuario = Usuario.objects.filter(nome__icontains=busca_nome)
    else:
        usuario = ''

    dados['usuarios'] = usuario

    return render(request, 'usuarios/busca_usuario.html', dados)


@login_required
def upload_dados(request):
    template = 'usuarios/upload_dados.html'
    
    prompt = {'order': 'A ods dos CSV é CPF, NIS, nome, nascimento, nome_mae, endereco e bairro'}

    if request.method == 'GET':
        return render(request, template, prompt)

    csv_file = request.FILES['file']
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'Please upload a .csv file.')

    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    next(io_string)
    for column in csv.reader(io_string, delimiter=',', quotechar="|"):
        _, created = Usuario.objects.update_or_create(
            CPF=column[0],
            NIS=column[1],
            nome=column[2],
            nascimento=column[3],
            nome_mae=column[4],
            endereco="Sem Endereço",
            bairro="Sem Endereço",
            cidade='Igarassu',
            observacoes=column[5],
            user=request.user,
            status='OFF'
        )
    context = {}
    return render(request, template, context)