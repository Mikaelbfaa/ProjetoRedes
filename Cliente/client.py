import socket
import os

TRANSFER_PORT = 6000
SERVER_ADDRESS = '0.0.0.0'

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(5)  # Timeout de 5 segundos
sock.connect((SERVER_ADDRESS, TRANSFER_PORT))


lenFile = 0
message = input("Digite o nome do arquivo que deseja receber: ")
sock.sendall(message.encode('utf-8'))

filename = message.split(',')[1].strip()

with open(filename, 'wb') as file:
    try:
        while True:
            data = sock.recv(1024)
            lenFile += len(data)
            if not data:
                break
            if data.decode('utf-8') == 'ERROR':
                lenFile = -1
                break
            file.write(data)
            print(f"Received {len(data)} bytes")
    
    except socket.timeout:
        print("Timeout: Nenhum dado recebido.")
    except Exception as e:
        print(f"Erro: {e}")

if lenFile > 0:
    ackMessage = "fcp_ack,{}".format(lenFile)
    sock.sendall(ackMessage.encode('utf-8'))
    print(ackMessage)
else:
    os.remove(filename)
    print("Problema no envio")

print("Desconectando...")
sock.close()