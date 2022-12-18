# config
import client_operations

print_cmd_output = True


def main():
    # TODO read configuration
    server_address = input("server ip: ")
    client_operations.connect("bestPCEver", 44444, "A")
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
