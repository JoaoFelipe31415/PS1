from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen,ScreenManager
from kivy.lang import Builder
from kivy.core.window import Window
#Variáveis Globais
usuario = None

def contains_number(s):
    return any(c.isdigit() for c in s)

def verifica_senha(string):
    if len(string) < 12:
        return False,"A senha deve ter pelo menos 8 dígitos"
    elif "@" not in string and "#" not in string and "!" not in string:
        return False,"A senha necessita de pelo menos um caracter especial @#!"
    elif not (contains_number(string)):
        return False, "A senha deve ter pelo menor um número"
    else:
        return True,'Forte'
    
    

class Cadastro(Screen):
    pass          
class Cadastro_Fornecedor(Screen):
    def apertou(self):
        self.ids.label_fornecedor.text = ""
        with open("dados_empresas.txt","r") as empresas:
            lista = empresas.readlines()
            id = len(empresas.readlines())
        
        empresa = self.ids.empresa_cadastro.text
        senha = self.ids.empresa_senha_cadastro.text
        categoria = self.ids.categoria_cadastro.text
        cnpj = self.ids.cnpj_cadastro.text
        parada = False
    
        
        for cadastros in lista:
            elemento = cadastros.split(",")
            if (empresa == elemento[1]):
                self.ids.label_fornecedor.text += "Empresa já cadastrada, "
                parada =True     
            if(cnpj == elemento[4][:-1]):
                self.ids.label_fornecedor.text += "Cnpj já cadastrado"
                parada = True
                
        if(parada):
            return 

        with open("dados_empresas.txt","a") as empresas:
            if(id and empresa and senha and categoria and cnpj):
                senha_integridade = verifica_senha(senha)
                if(not senha_integridade[0]):
                    self.ids.label_fornecedor.text = senha_integridade[1]
                    return
                empresas.write(f'{id},{empresa},{senha},{categoria},{cnpj}\n')
                self.manager.transition.direction = 'down'
                self.manager.current = 'login'
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
                clientes.write(f'{id},{usuario},{senha},{cpf},{email}\n')
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
    
    def entrar(self):
        global usuario   
        usuario = self.ids.usuario.text
        senha = self.ids.senha.text
        if(not self.ids.box.active):
            with open("dados_clientes.txt","r") as dados:
                usuarios = dados.readlines()
                for cadastro in usuarios:
                    componentes = cadastro.split(",")
                    nome = componentes[1]
                    password = componentes[2]
                    id = componentes[0]
                    if(usuario == nome and password == senha):
                        self.manager.transition.direction = 'left'
                        self.manager.current = 'cliente'
                        break
        else:
            with open("dados_empresas.txt","r") as dados:
                usuarios = dados.readlines()
                for cadastro in usuarios:
                    componentes = cadastro.split(",")
                    nome = componentes[1]
                    password = componentes[2]
                    id = componentes[0]
                    if(usuario == nome and password == senha):
                        self.manager.transition.direction = 'left'
                        self.manager.current = 'fornecedor'
                        break
    def esqueceu(self):
        pass
        
class Cliente(Screen):
    global usuario
    def on_enter(self):
        self.ids.mensagem.text = f'Olá! Seja bem vindo ao espaço do cliente, {usuario}'
class Fornecedor(Screen):
    global usuario
    def on_enter(self):
        self.ids.mensagem_fornecedor.text = f'Olá! Seja bem vindo ao espaço do fornecedor, {usuario}'
class WindowManager(ScreenManager):
    pass

#Carrega o arquivo kivy
kv = Builder.load_file('sistema.kv')

class MyApp(App):

    def build(self):
        return kv
    

if __name__ == '__main__':
    MyApp().run()