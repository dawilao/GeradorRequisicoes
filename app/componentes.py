"""
Módulo componentes.py

Este módulo define componentes personalizados baseados no CustomTkinter,
como CustomComboBox e CustomEntry, com estilos pré-definidos para uso em interfaces gráficas.
"""

import customtkinter as ctk

class CustomComboBox(ctk.CTkComboBox):
    """
    ComboBox personalizada baseada em CTkComboBox.

    Define uma aparência padrão com borda e raio específicos, 
    e com estado somente leitura para evitar edições manuais.
    """
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            border_width=1,
            corner_radius=1,
            state="readonly",
            **kwargs
        )

class CustomEntry(ctk.CTkEntry):
    """
    Campo de entrada personalizado baseado em CTkEntry.

    Define uma aparência padrão com borda e raio arredondado.
    """
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            border_width=1,
            corner_radius=1,
            **kwargs
        )
