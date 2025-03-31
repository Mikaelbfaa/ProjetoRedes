import socket
import os
import configparser

def negotiate_port(fName):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(5)
        message = "REQUEST,TCP,{}".format(fName)
        sock.sendto(message.encode(), (SERVER_ADDRESS, UDP_TRANSFER_PORT))
        
        try:
            resp, _ = sock.recvfrom(1024)
            parts = resp.decode().split(',')

            if parts[0] == 'RESPONSE':
                return int(parts[2])
            else:
                return "ERROR"
        except Exception as e:
                print("Erro no UDP: {}".format(e))
        
def request_file(sock_tcp, fName):
    lenFile = 0
    message = "get,{}".format(fName)
    try:
        sock_tcp.sendall(message.encode())
        with open(fName, 'wb') as file:
            while data := sock_tcp.recv(1024):
                lenFile += len(data)
                if data == b'ERROR':
                    lenFile = -1
                    break
                file.write(data)
        
    except socket.timeout:
        print("Timeout: Nenhum dado recebido.")
    except Exception as e:
        print(f"Erro no TCP: {e}")

    send_ack(sock_tcp, lenFile, fName)
    print("Download concluído com {} bytes".format(lenFile) if os.path.exists(fName) else "Falha no download")

def send_ack(sock_tcp, lenFile, fName):
    if lenFile > 0:
        ackMessage = "fcp_ack,{}".format(lenFile)
        sock_tcp.sendall(ackMessage.encode())
        print(ackMessage)
    else:
        os.remove(fName)
        print("Problema no envio")

    print("Desconectando...")
    sock_tcp.close() 


if __name__ == '__main__':

    config = configparser.ConfigParser()
    config.read('../config.ini')

    SERVER_ADDRESS = config['SERVER_CONFIG']['SERVER_ADRESS']
    UDP_TRANSFER_PORT = int(config['SERVER_CONFIG']['UDP_PORT'])

    fName = input("Escreva o nome do arquivo: ").strip()
    TRANSFER_PORT = negotiate_port(fName)

    if TRANSFER_PORT != "ERROR":
        sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_tcp.settimeout(5)  # Timeout de 5 segundos
        sock_tcp.connect((SERVER_ADDRESS, TRANSFER_PORT))
        request_file(sock_tcp, fName)
    else:
        print("Problema na negociação UDP")