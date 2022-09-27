import socket
import sys

import Cryptodome.Cipher.PKCS1_OAEP  # pip install pycryptodomex
from Cryptodome.Cipher import AES
from Cryptodome.PublicKey import RSA
from Cryptodome.Util import Padding

_server_socket = None

# config
_hashed_password = "A"


def start(port):
    global _server_socket
    host = socket.gethostname()
    _server_socket = socket.socket()
    _server_socket.bind((host, port))
    _server_socket.listen()


def stop():
    global _server_socket
    if not _server_socket:
        raise Exception("server not running")
    _server_socket.close()
    _server_socket = None


def accept_client():
    if not _server_socket:
        raise Exception("server not running")
    connection, client_address = _server_socket.accept()
    # generate rsa key
    key = RSA.generate(4096)
    # save private_key
    private_key = key.exportKey('PEM')
    rsa_private_key = RSA.importKey(private_key)
    oaep_cipher = Cryptodome.Cipher.PKCS1_OAEP.new(rsa_private_key)
    # save public_key
    public_key = key.publickey().exportKey('PEM')
    # send public_key
    connection.send(public_key)
    # receive encrypted aes_key
    encrypted_aes_key = connection.recv(1024)
    # decrypt aes_key
    aes_key = oaep_cipher.decrypt(encrypted_aes_key)
    # receive iv
    encrypted_iv = connection.recv(1024)
    # decrypt iv
    iv = oaep_cipher.decrypt(encrypted_iv)
    # create secure_connection
    secure_connection = tuple((connection, aes_key, iv))
    # send text to check encryption
    send_text(secure_connection, "encryptionOk")
    # receive hashed_client_password
    hashed_client_password = receive_text(secure_connection)
    # check if hashed_client_password and _hashed_password are equal
    if hashed_client_password == _hashed_password:
        send_text(secure_connection, "passwordOK")
        print("password ok")
        # TODO key and certificate check / generation
        secure_connection = tuple((connection, aes_key, iv))
        client_metadata = "WIP"
        return secure_connection, client_address, client_metadata
    else:
        connection.close()
        raise Exception("password error")


def send_text(secure_connection, text):
    if not _server_socket:
        raise Exception("server not running")
    padded_text = Padding.pad(text.encode(), 16)
    cipher = AES.new(secure_connection[1], AES.MODE_CBC, secure_connection[2])
    encrypted_text = cipher.encrypt(padded_text)
    secure_connection[0].send(encrypted_text)


def receive_text(secure_connection, size=1024):
    if not _server_socket:
        raise Exception("server not running")
    cipher = AES.new(secure_connection[1], AES.MODE_CBC, secure_connection[2])
    encrypted_text = secure_connection[0].recv(size)
    text = str(Padding.unpad(cipher.decrypt(encrypted_text), 16).decode())
    return text


def main():
    # TODO read config files
    start(4444)
    # TODO start thread to handle communication
    while True:
        conn, address, client_metadata = accept_client()
        # TODO store client metadata


if __name__ == '__main__':
    main()
