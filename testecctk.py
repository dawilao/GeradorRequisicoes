import customtkinter as ctk

# Lista de abas permitidas
abas_permitidas = ["E-MAIL"]  # Exemplo, pode vir de uma configuração ou outro lugar

# Criando a janela principal
root = ctk.CTk()

# Criando o Tabview
tabview = ctk.CTkTabview(master=root)
tabview.grid(row=0, column=0, padx=20, pady=20)

# Criando as abas dinamicamente com base nas permissões
for aba in abas_permitidas:
    tabview.add(aba)

# Agora, criamos os frames e outros widgets dentro das abas
if "E-MAIL" in abas_permitidas:
    frame_tab2 = ctk.CTkScrollableFrame(master=tabview.tab("E-MAIL"))
    frame_tab2.grid(row=0, column=0, padx=10, pady=10)
    
    # Adicionando widgets dentro do frame da aba "E-MAIL"
    label_email = ctk.CTkLabel(master=frame_tab2, text="E-mail:")
    label_email.grid(row=0, column=0, padx=5, pady=5)

if "OUTRA ABA" in abas_permitidas:
    frame_tab3 = ctk.CTkScrollableFrame(master=tabview.tab("OUTRA ABA"))
    frame_tab3.grid(row=0, column=0, padx=10, pady=10)

    # Adicionando widgets na outra aba
    label_outra_aba = ctk.CTkLabel(master=frame_tab3, text="Outro conteúdo")
    label_outra_aba.grid(row=0, column=0, padx=5, pady=5)

# Rodando o mainloop
root.mainloop()