import time
import threading
import matplotlib.pyplot as plt
from rdt_server import start_server, stop_server
from rdt_client import run_client

server_thread = threading.Thread(target=start_server)
server_thread.start()
time.sleep(1)

tempo_total, acks, retrans, total_bytes, timeout_log, retrans_log = run_client()

stop_server()
server_thread.join()

taxa = (retrans / (acks + retrans)) * 100 if acks + retrans else 0
throughput = (total_bytes * 8 / tempo_total) / 1000

print("\n===== RESULTADOS =====")
print(f"Tempo total: {tempo_total:.3f} s")
print(f"ACKs recebidos: {acks}")
print(f"Retransmissões: {retrans}")
print(f"Taxa de Retransmissão: {taxa:.2f}%")
print(f"Throughput: {throughput:.2f} Kbps")
print("=======================\n")

# Timeout Adaptativo
plt.figure(figsize=(8,4))
plt.plot(timeout_log)
plt.title("Evolução do Timeout Adaptativo")
plt.xlabel("Pacote confirmado")
plt.ylabel("Timeout (s)")
plt.grid(True)
plt.savefig("grafico_timeout.png") 

# Retransmissões por Pacote
plt.figure(figsize=(8,4))
plt.bar(range(len(retrans_log)), retrans_log)
plt.title("Retransmissões por Pacote")
plt.xlabel("Pacote")
plt.ylabel("Retransmissões")
plt.grid(True)
plt.savefig("grafico_retransmissoes.png")