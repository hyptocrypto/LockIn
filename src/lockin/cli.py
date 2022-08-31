import subprocess
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from manager import CredentialsManager
from styles import CliStyles
from exceptions import ServiceNotFound


def copy_to_clipboard(txt):
    task = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE, close_fds=True)
    task.communicate(input=txt.encode("utf-8"))


def fetch_service(client: CredentialsManager):
    services = WordCompleter(client.list_services(), ignore_case=True)
    chosen_service = prompt(CliStyles.service_name_prompt, completer=services)
    decryption_password = prompt(CliStyles.decryption_pass_prompt)
    try:
        username, password = client.fetch_service(chosen_service, decryption_password)
        print(
            CliStyles.credentials_resp_format.format(chosen_service, username, password)
        )
        copy_to_clipboard(password)  # Add password to clipboard for convenience
    except TypeError:
        print(CliStyles.password_invalid.format(decryption_password))
    except ServiceNotFound:
        print(CliStyles.service_not_found.format(chosen_service))


def new_service():
    pass


def delete_service():
    pass


def edit_service():
    pass


def list_services():
    pass


if __name__ == "__main__":
    client = CredentialsManager()
    print(CliStyles.ascii_art)
    while True:
        action = prompt("")
        print("\033[1A" + "\033[K", end="")  # Clear user input
        if action.lower() == "help":
            print(CliStyles.ascii_art)
            continue
        if action.lower()[0] not in "fndleq":
            print(CliStyles.invalid_selection.format(action))
            continue
        match action.lower():
            case "f":
                fetch_service(client)
            case "n":
                pass
            case "l":
                pass
            case "e":
                pass
            case "q":
                break
