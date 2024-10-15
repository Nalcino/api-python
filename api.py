from flask import Flask, request
import serial
import threading
import requests
import time

app = Flask(__name__)

# Configure a porta serial
ser = serial.Serial('COM3', 9600, timeout=1)  # Substitua 'COM3' pela sua porta serial

# Dicionário para armazenar os usuários cadastrados
users = {}

@app.route('/api', methods=['POST'])
def receive_uid():
    uid = request.form['uid']
    
    # Verificar se o UID já está cadastrado
    if uid in users:
        return {'message': 'UID já cadastrado', 'name': users[uid]}, 200

    return {'message': 'UID não cadastrado'}, 200

def read_serial():
    while True:
        if ser.in_waiting > 0:
            try:
                raw_data = ser.readline()  # Lê os bytes brutos
                print(f"Dados brutos recebidos: {raw_data}")  # Log dos dados brutos
                uid = raw_data.decode(errors='replace').strip()  # Tente decodificar
                if uid:  # Verifica se uid não está vazio
                    print(f"UID do Arduino: {uid}")
                    # Enviar o UID para a API
                    requests.post('http://localhost:5000/api', data={'uid': uid})
            except Exception as e:
                print(f"Erro ao ler da serial: {e}")

def get_uid_from_rfid():
    print("Aproxime o cartão RFID...")
    while True:
        if ser.in_waiting > 0:
            try:
                uid = ser.readline().decode(errors='replace').strip()
                if uid:  # Verifica se uid não está vazio
                    time.sleep(1)  # Adiciona um atraso de 1 segundo
                    return uid
            except Exception as e:
                print(f"Erro ao ler da serial: {e}")

def handle_user_input():
    while True:
        print("\nEscolha uma opção:")
        print("1. Registrar usuário")
        print("2. Acessar usuário")
        print("3. Deletar usuário")
        print("4. Listar usuários")
        print("5. Sair")

        choice = input("Digite o número da opção: ")

        if choice == '1':
            name = input("Digite o nome do usuário: ")
            uid = get_uid_from_rfid()  # Captura o UID ao aproximar o cartão
            if uid in users:
                print("Este UID já está cadastrado. Tente outro cartão.")
            else:
                users[uid] = name  # Cadastra o nome no dicionário
                print(f"Usuário '{name}' cadastrado com sucesso.")

        elif choice == '2':
            uid = get_uid_from_rfid()  # Captura o UID ao aproximar o cartão
            if uid in users:
                print(f"Acesso concedido. Usuário: {users[uid]}")
            else:
                print("Usuário não encontrado.")

        elif choice == '3':
            uid = get_uid_from_rfid()  # Captura o UID ao aproximar o cartão
            if uid in users:
                del users[uid]
                print("Usuário deletado com sucesso.")
            else:
                print("Usuário não encontrado.")

        elif choice == '4':
            if users:
                print("Usuários cadastrados:")
                for uid, name in users.items():
                    print(f"UID: {uid}, Nome: {name}")
            else:
                print("Nenhum usuário cadastrado.")

        elif choice == '5':
            print("Saindo...")
            break

        else:
            print("Opção inválida. Tente novamente.")

if __name__ == '__main__':
    # Rodar a leitura da serial em uma thread separada
    serial_thread = threading.Thread(target=read_serial)
    serial_thread.start()
    
    # Iniciar o servidor Flask em uma thread separada
    flask_thread = threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 5000})
    flask_thread.start()

    # Gerenciar entrada do usuário
    handle_user_input()