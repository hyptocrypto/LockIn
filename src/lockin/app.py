"""
Encrypted Credentials Manager
"""
from re import T
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER 
from lockin.utils import CredentialsManager
from lockin.styles import Styles
from lockin.validators import not_null

class LockIn(toga.App):
    def __init__(self):
        self.manager = CredentialsManager()
        return super().__init__()
    
    def set_selected_service(self, *args, **kwargs):
        self.selected_service = kwargs.get("row").services
        
        
    def save_service(self, *args, **kwargs):
        inputs = [            
            self.service_name_input.value,
            self.service_username_input.value,
            self.service_password_input.value,
            self.encryption_password.value
            ]
        if all([not_null(val) for val in inputs]):
            saved = self.manager.save_service(
                self.service_name_input.value,
                self.service_username_input.value,
                self.service_password_input.value,
                self.encryption_password.value
            )
            if saved:
                self.encrypt_popup.confirm_dialog("Saved!", f"New service saved: {self.service_name_input.value}")
                self.encrypt_popup.close()
                return
        else:
            self.encrypt_popup.error_dialog("Error!", "Empty values not permitted")
            return
        
        self.encrypt_popup.error_dialog("Error!", f"Error saving service: {self.service_name_input.value}")
    
    def fetch_service(self, *args, **kwargs):
        try:
            username, password = self.manager.fetch_service(
                self.selected_service, 
                self.decryption_password.value
            )
        except TypeError:
            self.decrypt_popup.error_dialog("Error!", f"Password ( {self.decryption_password.value} ) incorrect.")
            return
            
        self.decrypt_popup.info_dialog("Success!", f"Username: {username}\nPassword: {password} ")
        self.decrypt_popup.close()
        
        
    
    def encrypt_popup_handler(self, *args, **kwargs):
        self.encrypt_popup = toga.Window(title="New Service", size=(600, 250))
        self.windows.add(self.encrypt_popup)
    
        self.service_name_input = toga.TextInput(placeholder="Service Name", style=Styles.ENCRYPT_TEXT_INPUT_STYLE)
        self.service_username_input = toga.TextInput(placeholder="Username", style=Styles.ENCRYPT_TEXT_INPUT_STYLE)
        self.service_password_input = toga.TextInput(placeholder="Password", style=Styles.ENCRYPT_TEXT_INPUT_STYLE)
        self.encryption_password = toga.TextInput(placeholder="Encryption Password", style=Styles.ENCRYPT_TEXT_INPUT_STYLE)
        self.save_button = toga.Button("Save", style=Styles.SAVE_BUTTON_STYLE, on_press=self.save_service)
             
        self.encrypt_popup.content = toga.Box(
            style=Styles.ENCRYPT_POPUP_WINDOW_STYLE,
            children=[
            self.service_name_input,
            self.service_username_input,
            self.service_password_input,
            self.encryption_password,
            self.save_button
            ]
        )
        self.encrypt_popup.show()
        
    def decrypt_popup_handler(self, *args, **kwargs):
        service = self.selected_service
    
        self.decrypt_popup = toga.Window(title=service, size=(600, 200))
        self.windows.add(self.decrypt_popup)
        
        self.decrypt_label = toga.Label(f"Please enter decryption password.", style=Styles.DECRYPT_LABEL_STYLE)
        self.decryption_password = toga.TextInput(placeholder="Password", style=Styles.DECRYPT_TEXT_INPUT_STYLE)
        self.decrypt_button = toga.Button("Decrypt", style=Styles.DECRYPT_BUTTON_STYLE, on_press=self.fetch_service)
        
        self.decrypt_popup.content = toga.Box(
            style=Pack(width=300, direction=COLUMN),
            children=[
                self.decrypt_label,
                self.decryption_password,
                self.decrypt_button
            ]
        )
        self.decrypt_popup.show()
    
    def startup(self):
        """
        The startup methods acts as the __call__ for a class inheriting from type: toga.aApp.
        """
        
        actions = toga.Group("Actions")
        
        add_new = toga.Command(
            self.encrypt_popup_handler,
            label='Add New',
            tooltip='Add new service',
            icon="resources/add_new.png",
            group=actions,
            section="actions",
            order=2
        )
        delete = toga.Command(
            self.decrypt_popup_handler,
            label='Delete',
            tooltip='Delete selected service',
            icon="resources/delete.png",
            group=actions,
            section="actions",
            order=1
        )
        
        
        service_container = toga.Table(
            style=Pack(font_size=100, font_family="Sans", font_weight="bold"),
            headings=["Services"],
            data=self.manager.list_services(), 
            on_select=self.set_selected_service, 
            on_double_click=self.decrypt_popup_handler, 
            missing_value="N/A"
            )
        
        
        self.main_window = toga.MainWindow(title=self.formal_name, size=(600, 600))
        self.main_window.content = service_container
        self.commands.add(add_new)
        self.main_window.toolbar.add(add_new, delete)
        self.main_window.show()



def main():
    return LockIn()


if __name__ == "__main__":
    main().main_loop()
