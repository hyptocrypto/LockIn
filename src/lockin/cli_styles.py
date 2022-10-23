from prompt_toolkit.styles import Style
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter


class TermColors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def prompt_factory_warn(text: str, completer: WordCompleter = None):
    warning_style = Style.from_dict({"text": "#ecf542"})
    msg = [("class:text", text)]
    return prompt(msg, style=warning_style, completer=completer)


def prompt_factory_danger(text: str, completer: WordCompleter = None):
    warning_style = Style.from_dict({"text": "#fc2626"})
    msg = [("class:text", text)]
    return prompt(msg, style=warning_style, completer=completer)


class CliStyles:
    def _style_text(style: TermColors, text: str):
        return f"{style}{text}{TermColors.ENDC}"

    _success_line = _style_text(
        TermColors.OKBLUE, "<<<<<<<<<<-------------->>>>>>>>>>\n"
    )
    _error_line = _style_text(TermColors.FAIL, "------------------------------\n")

    def _wrap_success(_success_line, text: str):
        return f"""
        {_success_line}
        {text}
        {_success_line}
        """

    def list_services(services: list, _success_line=_success_line):
        print(f"    {_success_line}")
        for s in services:
            print(f"     {s}")
        print(f"    {_success_line}")

    def _wrap_error(_error_line, text: str):
        return f"""
        {_error_line}
        {text}
        {_error_line}
        """

    help_text = f"""
     {_style_text(TermColors.UNDERLINE, "F")} or {_style_text(TermColors.UNDERLINE, "Fetch")} to fetch record
     {_style_text(TermColors.UNDERLINE, "N")} or {_style_text(TermColors.UNDERLINE, "New")} to add new record
     {_style_text(TermColors.UNDERLINE, "D")} or {_style_text(TermColors.UNDERLINE, "Delete")} to delete record
     {_style_text(TermColors.UNDERLINE, "L")} or {_style_text(TermColors.UNDERLINE, "List")} to list all records
     {_style_text(TermColors.UNDERLINE, "E")} or {_style_text(TermColors.UNDERLINE, "Edit")} to edit a record
     {_style_text(TermColors.UNDERLINE, "C")} or {_style_text(TermColors.UNDERLINE, "Clear")} to clear the screen
    """
    ascii_art = (
        r"""
        __               __   ____    
       / /   ____  _____/ /__/  _/___ 
      / /   / __ \/ ___/ //_// // __ \
     / /___/ /_/ / /__/ ,< _/ // / / /
    /_____/\____/\___/_/|_/___/_/ /_/
   ----------------------------------
    """
        + help_text
    )

    credentials_resp_format = _wrap_success(
        _success_line,
        """
        Service: {}\n
        Username: {}\n
        Password: {}\n
        """,
    )

    save_success_resp = _wrap_success(
        _success_line,
        """
        Service '{}' saved.
        """,
    )

    edit_success_resp = _wrap_success(
        _success_line,
        """
        Service '{}' updated.
        """,
    )

    delete_success_resp = _wrap_success(
        _success_line,
        """
        Service '{}' deleted.
        """,
    )

    invalid_selection = _wrap_error(
        _error_line,
        """
        Error: Selection '{}' is not valid.\n
        """,
    )

    service_not_found = _wrap_error(
        _error_line,
        """
        Error: Service '{}' not found.\n
        """,
    )

    service_already_exists = _wrap_error(
        _error_line,
        """
        Error: Service '{}' already exists.\n
        """,
    )

    password_invalid = _wrap_error(
        _error_line,
        """
        Error: Password '{}' is not valid.\n
        """,
    )

    service_name_prompt = """
    Enter Service Name: 
    """
    username_prompt = """
    Enter Service Username: 
    """
    password_prompt = """
    Enter Service Password: 
    """

    edit_service_name_prompt = """
    Enter New Service Name (Enter to leave unchanged): 
    """
    edit_username_prompt = """
    Enter New Service Username (Enter to leave unchanged): 
    """
    edit_password_prompt = """
    Enter New Service Password (Enter to leave unchanged): 
    """

    service_name_edit_prompt = """
    Edit Service:
    """

    service_name_delete_prompt = """
    Enter Service Name to Delete:
    """

    encryption_pass_prompt = """
    Note: Remember your encryption password. Without it you can not decrypt the credentials.
    Enter Encryption Password: 
    """

    decryption_pass_prompt = """
    Enter Decryption Password: 
    """
