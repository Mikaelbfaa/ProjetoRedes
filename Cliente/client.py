import socket

TRANSFER_PORT = 6000
SERVER_ADDRESS = '0.0.0.0'

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(5)  # Timeout de 5 segundos
sock.connect((SERVER_ADDRESS, TRANSFER_PORT))

message = input("Digite o nome do arquivo que deseja receber: ")
sock.sendall(message.encode('utf-8'))

with open(message, 'wb') as file:
    try:
        while True:
            data = sock.recv(1024)
            if not data:
                break
            file.write(data)
            print(f"Received {len(data)} bytes")
    except socket.timeout:
        print("Timeout: Nenhum dado recebido.")
    except Exception as e:
        print(f"Erro: {e}")

print("Arquivo recebido. Fechando conexão.")
sock.close()