"""Cliente para transferência de arquivos via UDP/TCP.

Realiza a negociação de porta via UDP e transfere arquivos via TCP.
Configurações do servidor são lidas de um arquivo `config.ini`.
"""

import socket
import os
import configparser

def negotiate_port(fName):
    """
    Negocia uma porta TCP com o servidor via UDP.

    Args:
        fName (str): Nome do arquivo solicitado.

    Returns:
        int: Porta TCP para conexão.
        str: "ERROR" se a negociação falhar.

    Raises:
        Exception: Exceção genérica em caso de falha na comunicação UDP.
    """
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
    """
    Solicita e recebe um arquivo via TCP através do comando 'get,{fName}
    O arquivo é então salvo em blocos de 1024 bytes
    Ao receber o arquivo inteiro é enviado um ack para o servidor. 

    Args:
        sock_tcp (socket.socket): Socket TCP conectado ao servidor.
        fName (str): Nome do arquivo a ser baixado.
    """
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
    """
    Envia confirmação (ACK) ao servidor após o download.
    Descarta arquivos caso tenha um problema na transmissão
    Após o envio do ACK, fecha a conexão.

    Args:
        sock_tcp (socket.socket): Socket TCP conectado.
        lenFile (int): Tamanho do arquivo recebido em bytes.
        fName (str): Nome do arquivo.
    """
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