from site import check_enableusersite
from toga.style import Pack
from toga.style.pack import COLUMN, CENTER


class Styles:
    ENCRYPT_POPUP_WINDOW_STYLE = Pack(
        direction=COLUMN, width=300, alignment=CENTER, padding_left=150
    )

    SAVE_BUTTON_STYLE = Pack(padding_bottom=10, height=30)

    ENCRYPT_TEXT_INPUT_STYLE = Pack(height=50, padding_top=20, padding_bottom=20)

    DECRYPT_BUTTON_STYLE = Pack(
        width=150, padding_left=225, padding_bottom=10, height=30
    )

    DECRYPT_TEXT_INPUT_STYLE = Pack(
        height=40, width=290, padding_left=160, padding_top=20, padding_bottom=20
    )

    DECRYPT_LABEL_STYLE = Pack(font_size=20, padding_top=20, padding_left=153)


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


class CliStyles:
    def _style_text(style: TermColors, text: str):
        return f"{style}{text}{TermColors.ENDC}"

    help_text = f"""
    {_style_text(TermColors.UNDERLINE, "Fetch")} or {_style_text(TermColors.UNDERLINE, "F")} to fetch record
    {_style_text(TermColors.UNDERLINE, "New")} or {_style_text(TermColors.UNDERLINE, "N")} to add new record
    {_style_text(TermColors.UNDERLINE, "Delete")} or {_style_text(TermColors.UNDERLINE, "D")} to delete record
    {_style_text(TermColors.UNDERLINE, "List")} or {_style_text(TermColors.UNDERLINE, "L")} to list all records
    {_style_text(TermColors.UNDERLINE, "Edit")} or {_style_text(TermColors.UNDERLINE, "E")} to edit a record
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

    credentials_resp_format = (
        f"{_style_text(TermColors.OKBLUE, "<<<<<<<<<<-------------->>>>>>>>>>")}"
        +
        """
        \n
        Service: {}\n
        Username: {}\n
        Password: {}
        \n
        """
        +
        f"{_style_text(TermColors.OKBLUE, "<<<<<<<<<<-------------->>>>>>>>>>")}"
        )

    invalid_selection = f"""
    {_style_text(TermColors.FAIL, "------------------------------\n")}
    Error: Selection '{}' is not valid.\n
    {_style_text(TermColors.FAIL, "------------------------------\n")}
    """

    service_name_prompt = """
    Enter Service Name: 
    """

    decryption_pass_prompt = """
    Enter Decryption Password: 
    """

    service_not_found = f"""
    {_style_text(TermColors.FAIL, "------------------------------\n")}
    Error: Service '{}' not found.\n
    {_style_text(TermColors.FAIL, "------------------------------\n")}
    """

    service_already_exists = f"""
    {_style_text(TermColors.FAIL, "------------------------------\n")}
    Error: Service '{}' already exists.\n
    {_style_text(TermColors.FAIL, "------------------------------\n")}
    """

    password_invalid = f"""
    {_style_text(TermColors.FAIL, "------------------------------\n")}
    Error: Password '{}' is invalid.\n
    {_style_text(TermColors.FAIL, "------------------------------\n")}
    """
