import socket
import os

SERVER_ADDRESS = '0.0.0.0'
sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def negotiate_port(sock, fName):
    sock.connect(('0.0.0.0', 5698))
    try:
        message = "REQUEST,TCP,{}".format(fName)
        sock.sendall(message.encode('utf-8'))
        resp = sock.recv(1024).decode('utf-8').split(',')

        if resp[0] != 'ERROR':
            return int(resp[2])
        else:
            return "ERROR"
    except Exception as e:
            print(f"Erro no UDP: {e}")
        
def request_file(sock_tcp, fName):
    lenFile = 0
    message = "get,{}".format(fName)
    sock_tcp.sendall(message.encode('utf-8'))

    with open(fName, 'wb') as file:
        try:
            while True:
                data = sock_tcp.recv(1024)
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
            print(f"Erro no TCP: {e}")

    if lenFile > 0:
        ackMessage = "fcp_ack,{}".format(lenFile)
        sock_tcp.sendall(ackMessage.encode('utf-8'))
        print(ackMessage)
    else:
        os.remove(fName)
        print("Problema no envio")

    print("Desconectando...")
    sock_tcp.close() 


fName = input("Escreva o nome do arquivo: ")
TRANSFER_PORT = negotiate_port(sock_udp, fName)
print(TRANSFER_PORT)

if TRANSFER_PORT != "ERROR":
    sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_tcp.settimeout(5)  # Timeout de 5 segundos
    sock_tcp.connect((SERVER_ADDRESS, TRANSFER_PORT))
    request_file(sock_tcp, fName)
else:
    print("Problema na negociação UDP")