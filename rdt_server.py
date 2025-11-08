import socket
import porta
import pickle
import random

PACKET_LOSS_PROB = 0.2
ACK_LOSS_PROB = 0.1
CORRUPT_PROB = 0.1

RUNNING = True

def start_server():
    global RUNNING

    meu_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    meu_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    meu_socket.settimeout(0.5)

    meu_socket.bind((porta.ip_server, porta.porta_server))
    print("[Servidor] Iniciado!")

    seq_esperado = 0

    while RUNNING:
        try:
            mensagem_byte, ip_client = meu_socket.recvfrom(1024)
        except socket.timeout:
            continue

        if random.random() < PACKET_LOSS_PROB:
            print("[PERDA] Pacote descartado")
            continue
        
        if random.random() < CORRUPT_PROB:
            mensagem_byte = mensagem_byte[:-1] + b'\x00'
            print("[CORRUPÇÃO] Pacote alterado")

        try:
            checkSum_recebido, dados_data = pickle.loads(mensagem_byte)
            seq_num, dados = pickle.loads(dados_data)
        except:
            print("[ERRO] Pacote ilegível")
            continue
        
        if checkSum_recebido != sum(dados_data) % 256:
            print("[ERRO] Checksum inválido")
            continue
        
        if seq_num == seq_esperado:
            print(f"[PACOTE] seq={seq_num} dados={dados}")
            ack = pickle.dumps((seq_num, "ACK"))

            if random.random() >= ACK_LOSS_PROB:
                meu_socket.sendto(ack, ip_client)
                print(f"[ACK] seq={seq_num} enviado")
            else:
                print(f"[ACK-PERDIDO] seq={seq_num}")

            seq_esperado = 1 - seq_esperado
        else:
            ack = pickle.dumps((1 - seq_esperado, "ACK"))
            meu_socket.sendto(ack, ip_client)
            print(f"[ACK-DUP] enviado")

    meu_socket.close()
    print("[Servidor] Finalizado")


def stop_server():
    global RUNNING
    RUNNING = False
