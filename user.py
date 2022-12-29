# config
from getpass import getpass

import client_operations

print_cmd_output = True


def main():
    # TODO read configuration
    server_address = input("server address: ")  # TODO url parsing
    # split host and port
    if server_address.__contains__("]") and server_address.__contains__(":") and \
            server_address.rfind(":") > server_address.rfind("]"):
        host = server_address[:server_address.rfind(":")]
        port = int(server_address[(server_address.rfind(":") + 1):])
    elif server_address.__contains__(":") and server_address.rfind(":") > server_address.rfind("]"):
        host = server_address[:server_address.rfind(":")]
        port = int(server_address[(server_address.rfind(":") + 1):])
    else:
        host = server_address
        port = 44444
    password = getpass("Password: ")
    client_operations.connect(host, port, password)
    print(client_operations.receive_text())
    client_operations.send_text("Hi2")
    while True:
        command = input("> ")
        if command == "exit" or command == "quit":
            break
        output = execute_command(command)
        if print_cmd_output:
            print(output)
        log(output)
    client_operations.disconnect()


def execute_command(command):
    return "not supported"
    # TODO WIP


def log(text):
    print("[log] " + text)
    # TODO better logging


if __name__ == "__main__":
    main()
