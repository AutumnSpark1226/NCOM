import hashlib
import socket

import Cryptodome.Cipher.PKCS1_OAEP  # pip install pycryptodomex
from Cryptodome.Cipher import AES
from Cryptodome.PublicKey import RSA
from Cryptodome.Util import Padding

_server_socket = None

# TODO read config files
def start(port):
    global _server_socket
    host = socket.gethostname()
    _server_socket = socket.socket()
    _server_socket.bind((host, port))
    _server_socket.listen()


def stop():
    if not _server_socket:
        raise Exception("server not running")
    _server_socket.close()


def accept_client():
    if not _server_socket:
        raise Exception("server not running")
    connection, client_address = _server_socket.accept()
    # generate rsa key
    key = RSA.generate(2048)
    # save private_key
    private_key = key.exportKey('PEM')
    rsa_private_key = RSA.importKey(private_key)
    oaep_cipher = Cryptodome.Cipher.PKCS1_OAEP.new(rsa_private_key)
    # save public_key
    public_key = key.publickey().exportKey('PEM')
    # hash public key
    hashed_public_key = hashlib.sha512(public_key).hexdigest().encode()
    # send public_key
    connection.send(public_key)
    # receive encrypted aes_key
    rsa_encrypted = connection.recv(1024)
    # decrypt aes_key
    aes_key = oaep_cipher.decrypt(rsa_encrypted)
    # receive iv
    rsa_encrypted = connection.recv(1024)
    # decrypt iv
    iv = oaep_cipher.decrypt(rsa_encrypted)
    # create cipher
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    # encrypt hashed_public_key
    encrypted_hashed_public_key = cipher.encrypt(hashed_public_key)
    # send encrypted_hashed_public_key
    connection.send(encrypted_hashed_public_key)
    # receive encrypted_hashed_public_key2
    encrypted_hashed_public_key2 = connection.recv(1024)
    # decrypt hashed_public_key2
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    hashed_public_key2 = cipher.decrypt(encrypted_hashed_public_key2).decode()
    # check if hashed_public_key and hashed_public_key2 are equal (they should be)
    if hashed_public_key2 == hashed_public_key.decode():
        secure_connection = tuple((connection, aes_key, iv))
        return secure_connection, client_address
    else:
        connection.close()
        raise Exception("encryption or client error")


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


if __name__ == '__main__':
    # simple echo server to test the communication
    start(4444)
    conn, address = accept_client()
    while True:
        test_message = receive_text(conn)
        if test_message == 'disconnect':
            break
        print("received: " + test_message)
        send_text(conn, test_message)
    conn[0].close()
    stop()
