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


class CliStyles:
    ascii_art = r"""
        __               __   ____    
       / /   ____  _____/ /__/  _/___ 
      / /   / __ \/ ___/ //_// // __ \
     / /___/ /_/ / /__/ ,< _/ // / / /
    /_____/\____/\___/_/|_/___/_/ /_/
   ----------------------------------
    
    Fetch or F to fetch record
    New or N to add a new record
    Delete or D to delete a record
    List or L to list all records
    Edit or E to edit a record
    """

    credentials_resp_format = """
    \n
    <<<<<<<<<<-------------->>>>>>>>>>
    Service: {}\n
    Username: {}\n
    Password: {}
    <<<<<<<<<<-------------->>>>>>>>>>
    \n
    """

    service_name_prompt = """
    Enter Service Name: 
    """

    decryption_pass_prompt = """
    Enter Decryption Password: 
    """

    service_not_found = """
    ------------------------------\n
    Error: Service '{}' not found.\n
    ------------------------------\n
    """

    service_already_exists = """
    ------------------------------\n
    Error: Service '{}' already exists.\n
    ------------------------------\n
    """

    password_invalid = """
    ------------------------------\n
    Error: Password '{}' is invalid.\n
    ------------------------------\n
    """
