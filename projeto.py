from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen,ScreenManager
from kivy.lang import Builder
from kivy.core.window import Window
import re
from pathlib import Path
import shutil
from datetime import datetime
from sys import exit

def obter_data_atual():
    # Captura a data e hora atuais
    data_atual = datetime.now()
    
    # Formata a data no formato DD/MM/YYYY
    data_formatada = data_atual.strftime("%d/%m/%Y")
    
    return data_formatada

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def mover_arquivo(origem, destino):
    try:
        # Converte os caminhos em objetos Path
        origem = Path(origem).resolve()
        destino_dir = Path(destino).resolve()
        
        # Verifica se o arquivo de origem existe
        if not origem.is_file():
            raise FileNotFoundError(f"O arquivo de origem não existe: {origem}")
        
        # Gera o caminho do arquivo no destino
        destino_arquivo = destino_dir / origem.name
        
        # Move o arquivo para o destino
        shutil.move(str(origem), str(destino_arquivo))
        
        # Converte o caminho de destino para relativo
        caminho_relativo = Path(destino_arquivo).relative_to(Path(destino_dir).parent)
        
        # Normaliza o caminho para usar barras (/), que são aceitas por todos os sistemas operacionais
        caminho_relativo_normalizado = caminho_relativo.as_posix()
        
        return caminho_relativo_normalizado
    
    except FileNotFoundError as e:
        print(f"Erro: {e}")
    except NotADirectoryError as e:
        print(f"Erro: {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")



def enviar_email(remetente, senha, destinatario, assunto, corpo, caminho_anexo=None):
    # Configurações do servidor SMTP
    servidor = 'smtp.gmail.com'
    porta = 587
    
    # Cria a mensagem
    mensagem = MIMEMultipart()
    mensagem['From'] = remetente
    mensagem['To'] = destinatario
    mensagem['Subject'] = assunto
    
    # Adiciona o corpo ao e-mail
    mensagem.attach(MIMEText(corpo, 'plain'))
    
    if caminho_anexo:
        # Adiciona o anexo
        try:
            with open(caminho_anexo, 'rb') as anexo:
                parte = MIMEBase('application', 'octet-stream')
                parte.set_payload(anexo.read())
                encoders.encode_base64(parte)
                parte.add_header(
                    'Content-Disposition',
                    f'attachment; filename={caminho_anexo}',
                )
                mensagem.attach(parte)
        except FileNotFoundError:
            print(f"Arquivo não encontrado: {caminho_anexo}")
            return
    
    try:
        # Conecta ao servidor SMTP
        with smtplib.SMTP(servidor, porta) as servidor_smtp:
            servidor_smtp.starttls()  # Estabelece uma conexão segura
            servidor_smtp.login(remetente, senha)  # Faz login
            servidor_smtp.send_message(mensagem)  # Envia a mensagem
    except Exception as e:
        print(f"Ocorreu um erro: {e}")



#Variáveis Globais
usuario = None #Nome do usuário
saldo = None #Saldo do usuário
categoria = None #Verificar
cnpj = None 
tipo = None
id = None

loja_categoria = None
empresa = None

def contains_number(s):
    return any(c.isdigit() for c in s)

def validar_cpf(cpf):
    """
    Valida um CPF (Cadastro de Pessoas Físicas) no formato brasileiro.
    
    :param cpf: CPF a ser validado (string).
    :return: True se o CPF for válido, False caso contrário.
    """
    
    cpf = re.sub(r'\D', '', cpf)
    
    if len(cpf) != 11:
        return False
    
    if cpf == cpf[0] * 11:
        return False
    
    def calcular_digito(cpf, pesos):
        soma = sum(int(cpf[i]) * pesos[i] for i in range(len(pesos)))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto
    
    pesos_primeiro_digito = list(range(10, 1, -1))
    digito1 = calcular_digito(cpf[:9], pesos_primeiro_digito)
    
    pesos_segundo_digito = list(range(11, 1, -1))
    digito2 = calcular_digito(cpf[:10], pesos_segundo_digito)
    
    
    return cpf[-2:] == f"{digito1}{digito2}"


def verifica_senha(string):
    if len(string) < 12:
        return False,"A senha deve ter pelo menos 12 dígitos"
    elif "@" not in string and "#" not in string and "!" not in string:
        return False,"A senha necessita de pelo menos um caracter especial @#!"
    elif not (contains_number(string)):
        return False, "A senha deve ter pelo menor um número"
    else:
        return True,'Forte'

import re

def validar_email(email):
    """
    Valida um endereço de e-mail usando uma expressão regular.

    :param email: Endereço de e-mail a ser validado.
    :return: True se o e-mail for válido, False caso contrário.
    """
    # Expressão regular para validação de e-mail
    padrao_email = re.compile(r'''
        ^[a-zA-Z0-9._%+-]+       # Nome do usuário, pode incluir letras, números, pontos, sublinhados, porcentagens, sinais de adição e hífens
        @                       # O símbolo @
        [a-zA-Z0-9.-]+          # Domínio, pode incluir letras, números, pontos e hífens
        \.                      # O ponto antes da extensão do domínio
        [a-zA-Z]{2,}$           # Extensão do domínio (mínimo de 2 letras)
    ''', re.VERBOSE | re.IGNORECASE)
    
    return bool(padrao_email.match(email))

    

class Cadastro(Screen):
    pass          
class Cadastro_Fornecedor(Screen):

    def apertou(self):
        self.ids.label_fornecedor.text = ""
        with open("dados_empresas.txt","r") as empresas:
            lista = empresas.readlines()
            id = len(lista)
        
        empresa = self.ids.empresa_cadastro.text
        senha = self.ids.empresa_senha_cadastro.text
        categoria = self.ids.categoria_cadastro.text
        cnpj = self.ids.cnpj_cadastro.text
        email = self.ids.email_cadastro_fornecedor.text

        
        for cadastros in lista:
            elemento = cadastros.split(",")
            if(empresa == elemento[1]):
                self.ids.label_fornecedor.text += "Empresa já cadastrada, "
                return     
            if(cnpj == elemento[4]):
                self.ids.label_fornecedor.text += "Cnpj já cadastrado, "
                return
            if(email == elemento[5][:-1]):
                self.ids.label_fornecedor.text += "E-mail já cadastrado, "
                return
            if(empresa.lower() in "empresas"):
                self.ids.label_fornecedor.text += "Não é possível registrar esse nome de empresa."
                return
                

                

        with open("dados_empresas.txt","a") as empresas:
            if(empresa and senha and categoria != "Categoria" and cnpj and email):
                senha_integridade = verifica_senha(senha)
                if(not senha_integridade[0]):
                    self.ids.label_fornecedor.text = senha_integridade[1]
                    return
                if(not validar_email(email)):
                    self.ids.label_fornecedor.text = "Email inválido"
                    return
                empresas.write(f'{id},{empresa},{senha},{categoria},{cnpj},{email},0.00\n')
                self.ids.empresa_cadastro.text = ''
                self.ids.empresa_senha_cadastro.text = ''
                self.ids.categoria_cadastro.text = "Categoria"
                self.ids.cnpj_cadastro.text = ''
                self.ids.email_cadastro_fornecedor.text = ''

                self.manager.transition.direction = 'down'
                self.manager.current = 'login'
            elif categoria == "Categoria":
                self.ids.label_fornecedor.text = "Selecione uma categoria"
            else:
                self.ids.label_fornecedor.text = "Preencha todos os campos"

class Cadastro_Cliente(Screen):
    def apertou(self):
        self.ids.label_cliente.text = ""
        with open("dados_clientes.txt","r") as clientes:
            lista = clientes.readlines()
            id = len(lista)
        usuario = self.ids.usuario_cadastro.text
        senha = self.ids.senha_cadastro.text
        cpf = self.ids.cpf_cadastro.text
        email = self.ids.email_cadastro.text
        parada = False
        for cadastros in lista:
            elemento = cadastros.split(",")
            if (usuario == elemento[1]):
                self.ids.label_cliente.text += "Usuario já cadastrado, "
                parada =True     
            if(cpf == elemento[3]):
                self.ids.label_cliente.text += "Cpf já cadastrado, "
                parada = True
                
            if(email == elemento[4][:-1]):
                self.ids.label_cliente.text += "Email já cadastrado, "
                parada = True  
    
            if(parada):
                return
                
        with open("dados_clientes.txt","a") as clientes:
            
            senha_integridade = verifica_senha(senha)
            
            if(usuario and senha and cpf and email):
                if(not senha_integridade[0]):
                    self.ids.label_cliente.text = senha_integridade[1]
                    return
                if(not validar_cpf(cpf)):
                    self.ids.label_cliente.text = "CPF inválido"
                    return 

                if(not validar_email(email)):
                    self.ids.label_cliente.text = "Email inválido"
                    return
                clientes.write(f'{id},{usuario},{senha},{cpf},{email},0\n')
                self.manager.transition.direction = 'down'
                self.manager.current = 'login'
                self.ids.usuario_cadastro.text = ""
                self.ids.senha_cadastro.text = ""
                self.ids.cpf_cadastro.text = ""
                self.ids.email_cadastro.text = ""
                parada = False             
            else:
                
                self.ids.label_cliente.text = "Preencha todos os campos"

class Login(Screen):

    def on_enter(self):
        if 'login_aviso' in self.ids:
            self.ids.login_aviso.text = ''
        else:
            print("login_aviso não encontrado em ids")

    def entrar(self):
        global id
        global cnpj #CNPJ da empresa que logou
        global categoria #Categoria da empresa que logou
        global saldo #Saldo da conta do usuário
        global usuario #Nome do usuário  
        global tipo #Se é fornecedor tipo == True, caso não Tipo == False
        flag = False
        usuario = self.ids.usuario.text
        senha = self.ids.senha.text
        tipo = self.ids.box.active
        if(not tipo):
            with open("dados_clientes.txt","r") as dados:
                usuarios = dados.readlines()
                for cadastro in usuarios:
                    componentes = cadastro.split(",")
                    nome = componentes[1]
                    password = componentes[2]
                    id = componentes[0]
                    saldo = componentes[5][:-1]
                    if(usuario == nome and password == senha):
                        self.manager.transition.direction = 'left'
                        self.manager.current = 'cliente'
                        flag = True
                        break
            if(not flag):
                self.ids.login_aviso.text = f"Credenciais Inválidas"
                return
            else:
                self.ids.login_aviso.text = f""

        else:
            with open("dados_empresas.txt","r") as dados:
                usuarios = dados.readlines()
                for cadastro in usuarios:
                    componentes = cadastro.split(",")
                    nome = componentes[1]
                    id = componentes[0]
                    password = componentes[2]
                    categoria = componentes[3]
                    cnpj = componentes[4]
                    saldo = componentes[6][:-1]
                    if(usuario == nome and password == senha):
                        self.manager.transition.direction = 'left'
                        self.manager.current = 'fornecedor'
                        flag = True
                        break          
            if(not flag):
                self.ids.login_aviso.text = f"Credenciais Inválidas"
                return
            else:
                self.ids.login_aviso.text = f""

        
class Cliente(Screen):
    global usuario
    global saldo
    def on_enter(self):
        novo_saldo = saldo.replace(".",",")
        self.ids.mensagem.text = f'Olá! Seja bem vindo ao espaço do cliente, {usuario}'
        self.ids.nome_usuario.text = f'Usuário: {usuario}'
        self.ids.saldo.text = f'Saldo: R${novo_saldo}'
        self.ids.data.text = obter_data_atual()

    def mostrar_saldo(self):
        string = self.ids.saldo.text
        if "R$" in string:
            self.ids.saldo.text = "Saldo: --------"
        else:
            self.ids.saldo.text = f"Saldo: R$ {saldo.replace(".",",")}"
    def sair(self):
        exit()

class Fornecedor(Screen):
    global usuario
    global saldo
    
    def mostrar_saldo(self):
        string = self.ids.saldo_fornecedor.text
        if "R$" in string:
            self.ids.saldo_fornecedor.text = "Saldo: --------"
        else:
            self.ids.saldo_fornecedor.text = f"Saldo: R$ {saldo.replace(".",",")}"
    
    def sair(self):
        exit()
    
    def on_enter(self):
        self.ids.mensagem_fornecedor.text = f'Olá! Seja bem vindo ao espaço do fornecedor, {usuario}'
        self.ids.nome_usuario_fornecedor.text = f'Usuário: {usuario}'
        self.ids.data_fornecedor.text = obter_data_atual()
        self.ids.saldo_fornecedor.text = f"Saldo: R$ {saldo.replace(".",",")}"


class Esqueceu(Screen):
    def on_enter(self):
        self.ids.aviso_esqueceu.text = f""

    def enviar(self):
        email_capturado = self.ids.email_esqueceu.text
        achou = False
        if(validar_email(email_capturado)):
            if(self.ids.box_esqueceu.active):
                with open("dados_empresas.txt","r") as dados:
                    usuarios = dados.readlines()
                    for cadastro in usuarios:
                        componentes = cadastro.split(",")
                        email_teste = componentes[5][:-1]
                        if(email_capturado == email_teste):
                            achou = True
                            remetente = 'projetops1si@gmail.com'
                            senha = 'jcgiyyjzzwnhaafk'
                            destinatario = email_capturado
                            assunto = 'Recuperação de Login'
                            tamanho_senha = len(componentes[2])
                            primeira_parte = 'x'*(tamanho_senha//2)
                            corpo = f'Seu usuário é {componentes[1]} e sua senha é {primeira_parte}{componentes[2][(tamanho_senha//2):]}'
                            enviar_email(remetente, senha, destinatario, assunto, corpo)
                            self.ids.aviso_esqueceu.text = f"Email enviado"
                            return
            else:
                with open("dados_clientes.txt","r") as dados:
                    usuarios = dados.readlines()
                    for cadastro in usuarios:
                        componentes = cadastro.split(",")
                        email_teste = componentes[4][:-1]
                        if(email_capturado == email_teste):
                            achou = True
                            remetente = 'projetops1si@gmail.com'
                            senha = 'jcgiyyjzzwnhaafk'
                            destinatario = email_capturado
                            assunto = 'Recuperação de Login'
                            tamanho_senha = len(componentes[2])
                            primeira_parte = 'x'*(tamanho_senha//2)
                            corpo = f'Seu usuário é {componentes[1]} e sua senha é {primeira_parte}{componentes[2][(tamanho_senha//2):]}'
                            enviar_email(remetente, senha, destinatario, assunto, corpo)
                            self.ids.aviso_esqueceu.text = f"Email enviado"
                            return     
            
        else:
            self.ids.aviso_esqueceu.text = "Email inválido"

class Loja(Screen):
    def voltar(self):
        global tipo
        if(not tipo):
            self.manager.transition.direction = 'down'
            self.manager.current = 'cliente'
        else:
            self.manager.transition.direction = 'down'
            self.manager.current = 'fornecedor'
    def proximo(self):
        capturado = self.ids.loja_categoria.text
        global loja_categoria
        if(capturado != "Categoria"):
            self.manager.transition.direction = 'up'
            self.manager.current = f'{capturado.lower()}'
            loja_categoria = capturado
        else:
            return

class Medicamentos(Screen):
    def on_enter(self):
        global loja_categoria #Categoria da loja selecionada na tela Loja.
        with open("dados_empresas.txt","r") as arquivo:
            temp  = list()
            lista_de_empresas = arquivo.readlines()
            for linha in lista_de_empresas:
                conteudo = linha.split(",")
                if(conteudo[3] == loja_categoria):
                    temp.append(conteudo[1])
            self.ids.medicamentos_seletor.values = temp
    def proximo(self):
        global empresa
        empresa_capturada = self.ids.medicamentos_seletor.text
        if(empresa_capturada != "Empresas" ):
            empresa = empresa_capturada
            self.manager.transition.direction = 'up'
            self.manager.current = f'painel'

class Alimentos(Screen):
    def on_enter(self):
        global loja_categoria
        with open("dados_empresas.txt","r") as arquivo:
            temp  = list()
            lista_de_empresas = arquivo.readlines()
            for linha in lista_de_empresas:
                conteudo = linha.split(",")
                if(conteudo[3] == loja_categoria):
                    temp.append(conteudo[1])
            self.ids.alimentos_seletor.values = temp
    def proximo(self):
        global empresa
        empresa_capturada = self.ids.alimentos_seletor.text
        if(empresa_capturada != "Empresas" ):
            empresa = empresa_capturada
            self.manager.transition.direction = 'up'
            self.manager.current = f'painel'


class Painel(Screen):
    def on_enter(self):
        self.ids.seletor_painel.text = "Produtos"
        self.ids.imagem_painel.opacity = 0
        self.ids.quantidade_painel.text = ""
        self.ids.saldo_painel.text = f'Seu saldo: R$ {saldo}'
        global loja_categoria
        global empresa
        with open("dados_loja.txt","r+") as loja:
            lista = loja.readlines()
            self.auxiliar_todos = list()
            self.auxiliar = list()
            for produto in lista:
                dados = produto.split(",")
                vendedor = dados[6]
                if(empresa == vendedor):
                    self.auxiliar.append(dados[0])
                    self.auxiliar_todos.append(produto)
            self.ids.seletor_painel.values = self.auxiliar
    
    def mostrar_produto(self,nome):
        self.ids.mostrar_painel.text = "Produtos"
        self.ids.mostrar_painel.text = ""
        self.valor = None
        for produto in self.auxiliar_todos:
            dados = produto.split(",")
            if dados[0] == nome:
                self.valor = dados[2]
                self.ids.mostrar_painel.text = f'Nome: {nome}\nQuantidade: {dados[1]}\nPreço: {dados[2]}\nDescrição: {dados[5]}'
                if(dados[4] != "0"):
                    self.ids.imagem_painel.source = dados[4]
                    self.ids.imagem_painel.opacity = 1
                else:
                    self.ids.imagem_painel.opacity = 0
        
    def retorno(self):
        return loja_categoria.lower()
    
    def comprar(self):
        global saldo
        global tipo
        global usuario
        global id
        try:
            atual = self.ids.seletor_painel.text
            if atual == "Produtos":
                return
           
            #print(self.auxiliar_todos)
            
            for j in range(len(self.auxiliar_todos)):
                dados = self.auxiliar_todos[j].split(",")
                if atual == dados[0]:
                    quantidade = self.ids.quantidade_painel.text
                    if(float(dados[1]) <= 0):
                        self.ids.aviso_painel.text = "Produto indisponível"
                        return
                    if usuario == dados[-2]:
                       self.ids.aviso_painel.text = "Operação inválida"
                       return
                    if(float(quantidade) < 0):
                        self.ids.aviso_painel.text = "Quantidade inválida"
                        return
                    total = float(quantidade) * float(self.valor)
    
                    
                    if(float(saldo) < total):
                        self.ids.aviso_painel.text = "Saldo Insuficiente"
                        return
                    
                    saldo = str(float(saldo) - total) + "0"
                    self.ids.saldo_painel.text = f'Seu saldo: R$ {saldo}'
                    self.ids.aviso_painel.text = "Compra efetuada"
                    
                    with open("dados_loja.txt","r+") as dados:
                        lista = dados.readlines()
                        for i in range(len(lista)):
                            componentes = lista[i].split(",")
                            nome = componentes[0]
                            if(nome == atual):
                                componentes[1] = str(int(componentes[1]) - int(quantidade))
                                lista[i] = ','.join(componentes)
                                self.auxiliar_todos[j] = ','.join(componentes)
                                self.ids.mostrar_painel.text = f'Nome: {nome}\nQuantidade: {componentes[1]}\nPreço: {componentes[2]}\nDescrição: {componentes[5]}'
                                dados.seek(0)
                                dados.writelines(lista)
                                dados.truncate()
                                break
                
                    if(not tipo):
                        with open("dados_clientes.txt","r+") as dados:
                            lista = dados.readlines()
                            linha = lista[int(id)]
                            novo_saldo = float(saldo)
                            componentes = linha.split(",")
                            componentes[-1] = f'{novo_saldo:.2f}\n'
                            linha = ','.join(componentes)
                            lista[int(id)] = linha
                            dados.seek(0)
                            dados.writelines(lista)
                            dados.truncate()
                    else:
                        with open("dados_empresas.txt","r+") as dados:
                            lista = dados.readlines()
                            linha = lista[int(id)]
                            novo_saldo = float(saldo)
                            componentes = linha.split(",")
                            componentes[-1] = f'{novo_saldo:.2f}\n'
                            linha = ','.join(componentes)
                            lista[int(id)] = linha
                            dados.seek(0)
                            dados.writelines(lista)
                            dados.truncate()
                    
                    with open("dados_empresas.txt","r+") as dados:
                        lista = dados.readlines()
                        nome_da_empresa_atual = self.auxiliar_todos[0].split(",")[6]
                        for i in range(len(lista)):
                            componentes = lista[i].split(",")
                            nome = componentes[1]
                            if(nome_da_empresa_atual == nome):
                                componentes[-1] = str(float(componentes[-1]) + total) + "0\n"          
                                lista[i] = ','.join(componentes)
                                dados.seek(0)
                                dados.writelines(lista)
                                dados.truncate()
                                break
                    return
        
        except:                 
            return

                

class Gerenciador(Screen):
    pass        
class Deposito(Screen):
    global usuario
    global saldo
    global cnpj
    
    def on_enter(self):
        self.ids.nome_usuario_fornecedor.text = f'Usuário: {usuario}'
        self.ids.data_fornecedor.text = obter_data_atual()
        self.ids.saldo_fornecedor.text = f"Saldo: R$ {saldo.replace(".",",")}"
    def depositar(self):
        global saldo
        try:
            if cnpj == None:
                with open("dados_clientes.txt",'r+') as dados:
                    lista = dados.readlines()
                    for i in range(len(lista)):
                        componentes = lista[i].split(",")
                        nome = componentes[1]
                        if(nome == usuario):
                            montante = float(self.ids.valor_deposito.text)
                            if montante < 0:
                                return
                            resultado = (float(componentes[-1]) + montante)
                            resultado = f'{resultado:.2f}'
                            componentes[-1] = resultado+"\n"
                            saldo = resultado
                            lista[i] = ",".join(componentes)
                            dados.seek(0)
                            self.ids.saldo_fornecedor.text = f"Saldo: R$ {saldo.replace(".",",")}"
                            #print(lista)
                            dados.writelines(lista)
                            dados.truncate()
                            return
            else:
                with open("dados_empresas.txt",'r+') as dados:
                    lista = dados.readlines()
                    for i in range(len(lista)):
                        componentes = lista[i].split(",")
                        nome = componentes[1]
                        if(nome == usuario):
                            montante = float(self.ids.valor_deposito.text)
                            if montante < 0:
                                return
                            resultado = (float(componentes[-1]) + montante)
                            resultado = f'{resultado:.2f}'
                            componentes[-1] = resultado+"\n"
                            saldo = resultado
                            lista[i] = ",".join(componentes)
                            dados.seek(0)
                            self.ids.saldo_fornecedor.text = f"Saldo: R$ {saldo.replace(".",",")}"
                            #print(lista)
                            dados.writelines(lista)
                            dados.truncate()
                            return
        except:
            return
                            

class CadastrarProduto(Screen):
    def on_enter(self):
        self.ids.nome_produto.text = ""
        self.ids.preco_produto.text = ""
        self.ids.quantidade_produto.text = ""
        self.ids.imagem_produto.text = ""
        self.ids.mensagem_produto.text = ""

    def cadastro_produto(self):
        global usuario
        global cnpj
        global categoria
        with open("dados_loja.txt","r+") as loja:
            nome = self.ids.nome_produto.text
            quantidade = self.ids.quantidade_produto.text
            preco = self.ids.preco_produto.text
            imagem = self.ids.imagem_produto.text
            descricao = self.ids.descricao.text
            produtos = loja.readlines()
            for linha in produtos:
                componentes = linha.split(",")
                nome_atual = componentes[0]
                cpnj_atual = componentes[5][:-1]        
                if nome.upper() == nome_atual and cpnj_atual == cnpj:
                    self.ids.mensagem_produto.text = ("Produto já cadastrado por sua loja")
                    return    
            if(nome == "" or quantidade == "" or preco == "" or descricao == ""):
                self.ids.mensagem_produto.text = "Preencha todos os campos obrigatórios (*)"
                return
            if(not imagem):
                imagem = '0'
            else:
                imagem = mover_arquivo(imagem,'imagens')

            loja.write(f"{nome.upper()},{quantidade},{preco},{categoria},{imagem},{descricao},{usuario},{cnpj}\n")
            self.ids.nome_produto.text = ""
            self.ids.preco_produto.text = ""
            self.ids.quantidade_produto.text = ""
            self.ids.imagem_produto.text = ""
            self.ids.descricao.text = ""
            self.ids.mensagem_produto.text = "Produto cadastrado"

class GerenciarProdutos(Screen):
    def on_enter(self):
        global usuario
        
        self.lista_com_todos_os_produtos = list()
        self.lista_so_com_os_nomes_dos_produtos = list()
        self.ids.empresa_painel.text = f"Gerenciar loja {usuario}"
        print(usuario)
        with open("dados_loja.txt","r+") as dados:
            lista = dados.readlines()
            for i in range(len(lista)):
                componentes = lista[i].split(",")
                nome_empresa = componentes[-2]
                if(nome_empresa == usuario):
                    self.lista_so_com_os_nomes_dos_produtos.append(componentes[0])
                    self.lista_com_todos_os_produtos.append(lista[i])
        self.ids.seletor_painel.values = self.lista_so_com_os_nomes_dos_produtos
    
    def mostrar_produto(self,nome):
        self.ids.mostrar_painel.text = "Produtos"
        self.ids.mostrar_painel.text = ""
        self.valor = None
        for produto in self.lista_com_todos_os_produtos:
            dados = produto.split(",")
            if dados[0] == nome:
                self.valor = dados[2]
                self.ids.mostrar_painel.text = f'Nome: {nome}\nQuantidade: {dados[1]}\nPreço: {dados[2]}\nDescrição: {dados[5]}'
                if(dados[4] != "0"):
                    self.ids.imagem_painel.source = dados[4]
                    self.ids.imagem_painel.opacity = 1
                else:
                    self.ids.imagem_painel.opacity = 0
    
    def alterar(self):
        try:
            novo_preco = self.ids.preco_painel.text
            nova_quantidade = self.ids.quantidade_painel.text
            atual = self.ids.seletor_painel.text
            
            if atual == "Produtos":
                return
            if(float(nova_quantidade) < 0 or float(novo_preco) < 0):
                return
            
            for j in range(len(self.lista_com_todos_os_produtos)):
                dados = self.lista_com_todos_os_produtos[j].split(",")
                nome = dados[0]
                if(nome == atual):
                    dados[1] = nova_quantidade
                    dados[2] = novo_preco
                    with open("dados_loja.txt","r+") as loja:
                        lista = loja.readlines()
                        for i in range(len(lista)):
                            busca = lista[i].split(",")
                            if(busca[0] == nome):
                                lista[i] = ','.join(dados)
                                loja.seek(0)
                                loja.writelines(lista)
                                loja.truncate()
                                self.ids.mostrar_painel.text = f'Nome: {nome}\nQuantidade: {dados[1]}\nPreço: {dados[2]}\nDescrição: {dados[5]}'
                                return


                    


        
        except:
            pass

class CadastroPet(Screen):
    
    def on_enter(self):
        self.ids.pet_cadastro.text = ""
        self.ids.raca_seletor.opacity = 0
        self.ids.raca_seletor.text = "Raça"
        self.ids.pet_seletor.text = "Tipo de Pet"
        self.ids.aviso_pet.text = ""
    
    def verifica(self):
        nome_do_pet = self.ids.pet_cadastro.text
        if(not(bool(nome_do_pet))):
            self.ids.raca_seletor.opacity = 0
            self.ids.raca_seletor.values = []
            self.ids.aviso_pet.text = "Digite um nome para seu Pet"
            return
        return
    

    def mostrar_tipos(self,tipo):
        global usuario
        nome_do_pet = self.ids.pet_cadastro.text
        cachorros = ['Caramelinho','Husky Siberiano']
        gatos = ['Siamês','Maine Coon']

        animais = {'Cachorro':cachorros, 'Gato':gatos}

        
        
        if(bool(nome_do_pet)):
            self.ids.raca_seletor.values = animais[tipo]
            self.ids.raca_seletor.opacity = 1
            self.ids.aviso_pet.text = ""
        else:
            self.ids.raca_seletor.opacity = 0
            self.ids.raca_seletor.values = []
            self.ids.aviso_pet.text = "Digite um nome para seu Pet"
            return
    
    def apertou(self):   
        nome_do_pet = self.ids.pet_cadastro.text
        tipo = self.ids.pet_seletor.text
        
        
        if nome_do_pet == "":
            self.ids.aviso_pet.text = "Digite um nome para seu Pet"
            return
        
        if tipo == "Tipo de Pet":
            self.ids.aviso_pet.text = "Selecione um tipo"
            return
        
        self.ids.aviso_pet.text = ""
        
        raca = self.ids.raca_seletor.text
        if raca == "Raça":
            return

        with open("dados_pets.txt","r+") as dados:
            raca = self.ids.raca_seletor.text
            lista = dados.readlines()
            for i in range(len(lista)):
                componentes = lista[i].split(',')
                nome_dono_busca = componentes[0]
                nome_pet_busca = componentes[1]
                if(nome_pet_busca == nome_do_pet and usuario == nome_dono_busca):
                    return
            string = f'{usuario},{nome_do_pet},{tipo},{raca}\n'
            dados.write(string)
            dados.truncate()

            self.ids.pet_cadastro.text = ""
            self.ids.raca_seletor.opacity = 0
            self.ids.raca_seletor.text = "Raça"
            self.ids.raca_seletor.values = []
            self.ids.pet_seletor.text = "Tipo de Pet"
            
            self.ids.aviso_pet.text = "Cadastro Efetuado"
            return

class GuiaPet(Screen):
    
    
    def on_enter(self):
        self.ids.dica.text = ""
        #self.ids.pet_seletor.text = "Selecione seu Pet"
        self.animais = []
        self.nomes = []
        with open("dados_pets.txt","r") as dados:
            lista = dados.readlines()
            for i in range(len(lista)):
                componentes = lista[i].split(',')
                tutor = componentes[0]
                if (tutor == usuario):
                    self.animais.append(lista[i])
                    self.nomes.append(componentes[1])
        self.ids.pet_seletor.values = self.nomes


    def mostrar_dicas(self,pet):
        
        dica = {'Caramelinho':"Para manter seu Caramelo saudável e feliz, ofereça uma dieta balanceada, exercícios regulares e visitas ao veterinário. Escove seu pelo periodicamente para reduzir a queda e mantenha a higiene dental em dia para evitar problemas dentários comuns",
        
        "Husky Siberiano": "Cuide bem do seu Husky Siberiano oferecendo exercícios intensos e atividades estimulantes, além de uma alimentação adequada. Eles têm uma pelagem espessa que exige escovação frequente para evitar emaranhados e reduzir a queda de pelos",
        
        "Siamês": "Para manter seu Siamês saudável, forneça uma dieta equilibrada, estimule a mente com brinquedos interativos e mantenha as visitas ao veterinário em dia. Escove seu pelo curto regularmente para reduzir a queda e mantenha seus olhos limpos e livres de secreções.",
        
        "Maine Coon":"Cuide bem do seu Maine Coon com escovações regulares para manter a pelagem longa e densa sem nós. Ofereça uma dieta nutritiva, exercícios diários e visitas regulares ao veterinário. Esteja atento à saúde dental e aos cuidados com as orelhas grandes."}
        
        
        id = self.nomes.index(pet)
        raca = self.animais[id].split(",")[3]
        self.ids.dica.text = dica[raca[:-1]]


class WindowManager(ScreenManager):
    pass

#Carrega o arquivo kivy
kv = Builder.load_file('sistema.kv')

class MyApp(App):

    def build(self):
        return kv
    

if __name__ == '__main__':
    MyApp().run()