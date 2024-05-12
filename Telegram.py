import requests
import json
import os
import mysql.connector
from mysql.connector import Error
from datetime import datetime

class TelegramBot:
    def __init__(self):
        iTOKEN = '6711233009:AAE7zKPUZzXzu3ulH2WjD0ctAZdQSoOLLv8'
        self.iURL = f'https://api.telegram.org/bot{iTOKEN}/'
        self.connection = self.create_connection(host="127.0.0.1", user="root", password="sport8799", database="bot")
        self.estamos_a_caminho = False
        self.primeira_mensagem = True

    def create_connection(self, host, user, password, database):
        try:
            connection = mysql.connector.connect(host=host,
                                                 user=user,
                                                 password=password,
                                                 database=database)
            if connection.is_connected():
                print("Conectado ao servidor MySQL com sucesso.")
                return connection
        except Error as e:
            print(f"Erro ao conectar ao MySQL: {e}")
            return None

    def Iniciar(self):
        iUPDATE_ID = None
        while True:
            iATUALIZACAO = self.ler_novas_mensagens(iUPDATE_ID)
            IDADOS = iATUALIZACAO["result"]
            if IDADOS:
                for dado in IDADOS:
                    iUPDATE_ID = dado['update_id']
                    mensagem = dado["message"]["text"].strip()  
                    chat_id = dado["message"]["from"]["id"]
                    nome_usuario = dado["message"]["from"].get("first_name", "")  
                    hora_enviada = datetime.utcfromtimestamp(dado["message"]["date"]).strftime('%Y-%m-%d %H:%M:%S')
                    
                    resposta = self.gerar_respostas(mensagem)
                    self.responder(resposta, chat_id)
                    
                    if resposta.startswith('Pedido Confirmado!'):
                        self.salvar_pedido(mensagem, chat_id, nome_usuario, hora_enviada)

    def ler_novas_mensagens(self, iUPDATE_ID):
        iLINK_REQ = f'{self.iURL}getUpdates?timeout=5'
        if iUPDATE_ID:
            iLINK_REQ = f'{iLINK_REQ}&offset={iUPDATE_ID + 1}'
        iRESULT = requests.get(iLINK_REQ)
        return json.loads(iRESULT.content)

    def gerar_respostas(self, mensagem):
        print('mensagem do cliente: ' + str(mensagem))
        
        if mensagem.lower() == 'oi':  
            self.estamos_a_caminho = False 
            self.primeira_mensagem = True  
            return f'''Olá! 😊 Seja bem-vindo à Pizzaria MammaMia! Por favor, escolha o número correspondente ao item desejado no menu:{os.linesep}1️⃣ - Pizza Calabresa 🍕 R$32,00{os.linesep}2️⃣ - Pizza Napolitana 🍕 R$35,00{os.linesep}3️⃣ - Pizza 4 Queijos 🍕 R$40,00{os.linesep}4️⃣ - Pizza Margherita 🍕 R$35,00'''

        if not self.estamos_a_caminho:
            self.estamos_a_caminho = True
            self.primeira_mensagem = True
            return f'''Olá! 😊 Seja bem-vindo à Pizzaria MammaMia! Por favor, escolha o número correspondente ao item desejado no menu:{os.linesep}1️⃣ - Pizza Calabresa 🍕 R$32,00{os.linesep}2️⃣ - Pizza Napolitana 🍕 R$35,00{os.linesep}3️⃣ - Pizza 4 Queijos 🍕 R$40,00{os.linesep}4️⃣ - Pizza Margherita 🍕 R$35,00'''

        if mensagem in ('1', '2', '3', '4'):
            self.estamos_a_caminho = True
            return f'''Pedido Confirmado! 🎉🍕 Digite seu endereço para entrega e estaremos a caminho! 🚚'''

        if mensagem.lower() == 'menu':
            return f'''Olá! 😊 Bem-vindo de volta! Aqui está o nosso cardápio:{os.linesep}1️⃣ - Pizza Calabresa 🍕 R$32,00{os.linesep}2️⃣ - Pizza Napolitana 🍕 R$35,00{os.linesep}3️⃣ - Pizza 4 Queijos 🍕 R$40,00{os.linesep}4️⃣ - Pizza Margherita 🍕 R$35,00'''

        if mensagem.lower() == 's' or mensagem.lower() == 'n':
            return mensagem.lower()

        if mensagem.strip() and self.estamos_a_caminho:
            if self.primeira_mensagem:
                self.primeira_mensagem = False
                return f'''Olá! 😊 Bem-vindo de volta! Deseja fazer um novo pedido? Digite "menu" para ver o cardápio novamente.{os.linesep}Caso tenha informado seu endereço recentemente, só aguardar a entrega!'''
            return ''

        if mensagem.strip():
            self.estamos_a_caminho = False

        return '''Olá! 😊 Bem-vindo de volta! Deseja fazer um novo pedido? Digite "menu" para ver o cardápio novamente, ou insira o código do item desejado.'''

    def salvar_pedido(self, mensagem, chat_id, nome_usuario, hora_enviada):
        try:
            cursor = self.connection.cursor()
            confirmado = True

            insert_query = """INSERT INTO pedidos (chat_id, nome_usuario, item, hora_enviada, confirmado) VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(insert_query, (chat_id, nome_usuario, mensagem, hora_enviada, confirmado))
            self.connection.commit()
            print("Pedido salvo no banco de dados.")
        except Error as e:
            print(f"Erro ao salvar pedido: {e}")
        finally:
            if self.connection.is_connected():
                cursor.close()

    def responder(self, resposta, chat_id):
        iLINK_REQ = f'{self.iURL}sendMessage?chat_id={chat_id}&text={resposta}'
        requests.get(iLINK_REQ)
        print("respondi: " + str(resposta))


bot = TelegramBot()
print("Bot iniciado. Pronto para receber mensagens.")
_ = bot.Iniciar()
