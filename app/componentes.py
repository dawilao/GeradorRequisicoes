import customtkinter as ctk

# Criar uma classe personalizada para o ComboBox
class CustomComboBox(ctk.CTkComboBox):
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            border_width=1,
            corner_radius=1,
            state="readonly",
            **kwargs  
        )

# Criar uma classe personalizada para Entry
class CustomEntry(ctk.CTkEntry):
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            border_width=1,
            corner_radius=1,
            **kwargs
        )