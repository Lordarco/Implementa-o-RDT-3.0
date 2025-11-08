import socket
import porta
import pickle
import time

def run_client():

    timeout_log = []
    retransmissoes_por_msg = []

    retransmissoes = 0
    acks_recebidos = 0
    total_bytes = 0

    tempo_inicio = time.time()

    EstimatedRTT = 1.0
    DevRTT = 0.5
    TimeoutInterval = EstimatedRTT + 4 * DevRTT
    alpha = 0.125
    beta = 0.25

    seq_atual = 0
    i = 0

    meu_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    with open("mensagens.txt", "r") as f:
        mensagem = f.read().splitlines()

    while i < len(mensagem):
        retrans_count_msg = 0
        esperando_ack = True

        while esperando_ack:
            dados_data = pickle.dumps((seq_atual, mensagem[i]))
            checksum = sum(dados_data) % 256
            pacote_envio = (checksum, dados_data)

            total_bytes += len(mensagem[i].encode())
            send_time = time.time()
            dados_checksum = pickle.dumps(pacote_envio)

            print(f"[ENVIO] seq={seq_atual}, msg='{mensagem[i]}', timeout={TimeoutInterval:.3f}s")
            meu_socket.sendto(dados_checksum, (porta.ip_server, porta.porta_server))

            try:
                meu_socket.settimeout(TimeoutInterval)
                dados_ack, _ = meu_socket.recvfrom(1024)
                ack_seq, _ = pickle.loads(dados_ack)

                if ack_seq == seq_atual:
                    sample = time.time() - send_time

                    EstimatedRTT = (1 - alpha) * EstimatedRTT + alpha * sample
                    DevRTT = (1 - beta) * DevRTT + beta * abs(sample - EstimatedRTT)
                    TimeoutInterval = EstimatedRTT + 4 * DevRTT

                    print(f"[ACK] seq={ack_seq} SampleRTT={sample:.3f}s Timeout={TimeoutInterval:.3f}s")

                    timeout_log.append(TimeoutInterval)
                    retransmissoes_por_msg.append(retrans_count_msg)
                    acks_recebidos += 1
                    esperando_ack = False
                    seq_atual = 1 - seq_atual
                    i += 1
                else:
                    print("[ACK-DUP] ignorado")

            except socket.timeout:
                retransmissoes += 1
                retrans_count_msg += 1
                print("[TIMEOUT] Retransmitindo...")

    tempo_total = time.time() - tempo_inicio
    print("Todas as mensagens confirmadas!")

    return tempo_total, acks_recebidos, retransmissoes, total_bytes, timeout_log, retransmissoes_por_msg
