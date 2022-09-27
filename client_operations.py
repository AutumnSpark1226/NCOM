import os
import socket
import sys

from Cryptodome.Cipher import AES  # pip install pycryptodomex
from Cryptodome.Cipher import PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from Cryptodome.Util import Padding

_client_socket = None
_aes_key = None
_iv = None


def connect(host, port, hashed_password):
    global _client_socket
    _client_socket = socket.socket()
    _client_socket.connect((host, port))
    # receive public_key
    public_key = _client_socket.recv(1024)
    # generate _aes_key
    global _aes_key, _iv
    _aes_key = os.urandom(32)
    # generate _iv
    _iv = os.urandom(16)
    # create cipher
    cipher = AES.new(_aes_key, AES.MODE_CBC, _iv)
    # encrypt aes_key
    rsa_public_key = RSA.importKey(public_key)
    oaep_cipher = PKCS1_OAEP.new(rsa_public_key)
    encrypted_aes_key = oaep_cipher.encrypt(_aes_key)
    # send encrypted_aes_key
    _client_socket.send(encrypted_aes_key)
    # encrypt iv
    encrypted_iv = oaep_cipher.encrypt(_iv)
    # send encrypted_iv
    _client_socket.send(encrypted_iv)
    # check encryption
    if not receive_text() == "encryptionOk":
        disconnect()
        raise Exception("encryption error")
    # send password
    send_text(hashed_password)
    # wait for server password check
    password_check_response = receive_text()
    if not password_check_response == "passwordOK":
        disconnect()
        raise Exception("wrong password")
    print("password ok")


def disconnect():
    if not _client_socket:
        raise Exception("client not connected")
    _client_socket.close()


def send_text(text):
    if not _client_socket:
        raise Exception("client not connected")
    padded_text = Padding.pad(text.encode(), 16)
    cipher = AES.new(_aes_key, AES.MODE_CBC, _iv)
    encrypted_text = cipher.encrypt(padded_text)
    _client_socket.send(encrypted_text)


def receive_text(size=1024):
    if not _client_socket:
        raise Exception("client not connected")
    cipher = AES.new(_aes_key, AES.MODE_CBC, _iv)
    encrypted_text = _client_socket.recv(size)
    text = str(Padding.unpad(cipher.decrypt(encrypted_text), 16).decode())
    return text


def send_text_to_other_client(client_data, text):
    header = client_data
    # TODO create header containing metadata
    send_text(header)
    # TODO end to end encryption
    encrypted_text = text
    send_text(encrypted_text)
    status = receive_text()
    return status


def receive_text_from_server_or_other_client():
    header = receive_text()
    # TODO extract information
    text = receive_text()
    # TODO decrypt text in case it's from another client


if __name__ == "__main__":
    connect("bestPCEver", 4444, "A")

# hash: hashed = hashlib.sha512(value).hexdigest().encode()
