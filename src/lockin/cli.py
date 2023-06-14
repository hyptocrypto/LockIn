#!venv/bin/python

import os
import subprocess
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from manager import CredentialsManager
from cli_styles import CliStyles, prompt_factory_danger, prompt_factory_warn
from exceptions import ServiceNotFound
from loader import Loader


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


def new_service(client: CredentialsManager):
    service_name = prompt(CliStyles.service_name_prompt)
    username = prompt(CliStyles.username_prompt)
    password = prompt(CliStyles.password_prompt)
    encryption_password = prompt_factory_warn(CliStyles.encryption_pass_prompt)
    saved = client.save_service(
        service_name=service_name,
        service_username=username,
        service_password=password,
        encryption_password=encryption_password,
    )
    if saved:
        print(CliStyles.save_success_resp.format(service_name))


def delete_service(client: CredentialsManager):
    services = WordCompleter(client.list_services(), ignore_case=True)
    service_name = prompt_factory_danger(
        CliStyles.service_name_delete_prompt, completer=services
    )
    encryption_password = prompt(CliStyles.decryption_pass_prompt)
    deleted = client.delete_service(
        service_name=service_name, encryption_password=encryption_password
    )

    if deleted:
        print(CliStyles.delete_success_resp.format(service_name))
    else:
        print(CliStyles.password_invalid.format(encryption_password))


def edit_service(client: CredentialsManager):
    services = WordCompleter(client.list_services(), ignore_case=True)
    service_name = prompt_factory_warn(
        CliStyles.service_name_edit_prompt, completer=services
    )
    encryption_password = prompt(CliStyles.decryption_pass_prompt)
    new_service_name = prompt(CliStyles.edit_service_name_prompt) or service_name
    new_service_username = prompt(CliStyles.edit_username_prompt)
    new_service_password = prompt(CliStyles.edit_password_prompt)
    try:
        edited = client.edit_service(
            service_name=service_name,
            encryption_password=encryption_password,
            update_name=new_service_name,
            update_username=new_service_username,
            update_password=new_service_password,
        )
    except TypeError:
        print(CliStyles.password_invalid.format(encryption_password))
    except ServiceNotFound:
        print(CliStyles.service_not_found.format(service_name))

    if edited:
        print(CliStyles.edit_success_resp.format(new_service_name))
    else:
        print("Error")


def list_services(client: CredentialsManager):
    CliStyles.list_services(client.list_services())


def clear():
    os.system("clear")
    print(CliStyles.ascii_art)


if __name__ == "__main__":
    with Loader("Attempting to connect to network share....."):
        client = CredentialsManager()
    print(CliStyles.ascii_art)
    while True:
        action = prompt("")
        print("\033[1A" + "\033[K", end="")  # Clear user input
        if action and action.lower()[0] not in "fndleqc":
            print(CliStyles.invalid_selection.format(action))
            continue
        match action.lower():
            case "f":
                try:
                    clear()
                    fetch_service(client)
                except KeyboardInterrupt:
                    pass
            case "n":
                try:
                    clear()
                    new_service(client)
                except KeyboardInterrupt:
                    pass
            case "e":
                try:
                    clear()
                    edit_service(client)
                except KeyboardInterrupt:
                    pass
            case "d":
                try:
                    clear()
                    delete_service(client)
                except KeyboardInterrupt:
                    pass
            case "c":
                os.system("clear")
                print(CliStyles.ascii_art)
            case "l":
                clear()
                list_services(client)
            case "q":
                break
