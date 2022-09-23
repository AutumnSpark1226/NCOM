def main():
    # TODO read configuration
    server_adress = input("server ip: ")
    # TODO connect and authenticate
    while True:
        command = input("> ")
        if command == "exit" or command == "quit":
            break
        output = execute_command(command)
        if print_cmd_output:
            print(output)
        log(output)
    # TODO disconnect


def execute_command(command):
   # TODO WIP

def log():
   # TODO simple logging utility

if __name__ == "__main__":
    main()
