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
