# config
send_cmd_output = True


def main():
    # TODO read configuration
    # TODO connect and authenticate
    while True:
        # TODO receive command
        command = "nothing"
        # TODO add break
        cmd_output = execute_command(command)
        if not send_cmd_output:
            cmd_output = 'command output not sent'
        # TODO send cmd_output
    # TODO disconnect


def execute_command(command):
    # TODO execute command
    return "not supported"


if __name__ == '__main__':
    main()
