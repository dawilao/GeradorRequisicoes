import tkinter as tk
import customtkinter as ctk
import pyperclip

from .CTkFloatingNotifications import *
from .CTkDatePicker import *
from .componentes import CustomEntry, CustomComboBox
from .utils import arrumar_texto, valida_prefixo, valida_os


class AbaAquisicao(ctk.CTkFrame):
    def __init__(self, master, tabview="AQUISIÇÃO", nome_completo_usuario=None, contratos=None):
        super().__init__(master)
        self.tabview = tabview
        self.nome_completo_usuario = nome_completo_usuario
        self.notificacao = NotificationManager(master=None)
        self.pack(fill="both", expand=True)

        # Lista de widgets para limpeza
        self.widgets_para_limpar = []
        
        # Lista para armazenar serviços
        self.servicos = []
        self.editando_item = None

        # Lista de contratos
        self.contratos = contratos

        self._criar_widgets()
        self._configurar_layout()

    def _criar_widgets(self):
        """Cria a interface da aba Aquisição."""        
        self._set_appearance_mode("system")

        # Configurando a coluna do frame para expandir
        self.grid_rowconfigure(20, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)        

        # Cria todos os widgets
        # Usuario
        ctk.CTkLabel(self, text="USUÁRIO:").grid(row=0, column=0, sticky="w", padx=(10, 10), pady=(10, 0))
        self.nome_usuario_entry = CustomEntry(self)
        self.nome_usuario_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=(10, 2))
        self.nome_usuario_entry.insert(0, self.nome_completo_usuario)
        self.nome_usuario_entry.configure(state='disabled')

        # Tipo
        ctk.CTkLabel(self, text="TIPO:").grid(row=1, column=0, sticky="w", padx=(10, 10))
        self.tipo_aquisicao_combobox = CustomComboBox(self, values=[
            "COMPRA",
            "LOCAÇÃO",
        ], command=lambda choice: self.add_campos())
        self.tipo_aquisicao_combobox.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=2)
        self.tipo_aquisicao_combobox.set("")

        # Contratos
        ctk.CTkLabel(self, text="CONTRATO:").grid(row=2, column=0, sticky="w", padx=(10, 10))
        self.contrato_combobox = CustomComboBox(self, values=self.contratos, command=lambda choice: self.add_campos())
        self.contrato_combobox.grid(row=2, column=1, sticky="ew", padx=(0, 10), pady=2)
        self.contrato_combobox.set("")

        # Criando os campos de entrada
        self.descricao_locacao_label = ctk.CTkLabel(self, text="DESCRIÇÃO:")
        self.descricao_locacao_entry = CustomEntry(self)
        self.widgets_para_limpar.append(self.descricao_locacao_entry)

        # -------------------------------
        # Frame para os itens
        # -------------------------------
        self.frame_caixa_itens = ctk.CTkFrame(self, border_width=1)

        self.frame_caixa_itens.grid_columnconfigure(0, weight=1)
        self.frame_caixa_itens.grid_columnconfigure(1, weight=1)

        # Inicializando o frame antes de manipulá-lo
        self.frame_lista_itens = ctk.CTkFrame(self.frame_caixa_itens)

        # Criando os campos de entrada
        self.descricao_compra_label = ctk.CTkLabel(self.frame_caixa_itens, text="DESCRIÇÃO DO ITEM:")
        self.descricao_compra_entry = CustomEntry(self.frame_caixa_itens)
        self.descricao_compra_label.grid(row=3, column=0, sticky="w", padx=(10, 10))
        self.descricao_compra_entry.grid(row=3, column=1, sticky="ew", padx=(0, 10), pady=2)

        self.quantidade_label = ctk.CTkLabel(self.frame_caixa_itens, text="QUANTIDADE:")
        self.quantidade_entry = CustomEntry(self.frame_caixa_itens)
        self.quantidade_label.grid(row=4, column=0, sticky="w", padx=(10, 10))
        self.quantidade_entry.grid(row=4, column=1, sticky="ew", padx=(0, 10), pady=2)

        self.altura_label = ctk.CTkLabel(self.frame_caixa_itens, text=f"ALTURA:", anchor="w", justify="left")
        self.altura_entry = CustomEntry(self.frame_caixa_itens, placeholder_text="Opcional")
        self.altura_label.grid(row=5, column=0, sticky="w", padx=(10, 10))
        self.altura_entry.grid(row=5, column=1, sticky="ew", padx=(0, 10), pady=2)

        self.largura_label = ctk.CTkLabel(self.frame_caixa_itens, text=f"LARGURA:", anchor="w", justify="left")
        self.largura_entry = CustomEntry(self.frame_caixa_itens, placeholder_text="Opcional")
        self.largura_label.grid(row=6, column=0, sticky="w", padx=(10, 10))
        self.largura_entry.grid(row=6, column=1, sticky="ew", padx=(0, 10), pady=2)

        self.comprimento_label = ctk.CTkLabel(self.frame_caixa_itens, text=f"COMPRIMENTO:                ", anchor="w", justify="left")
        self.comprimento_entry = CustomEntry(self.frame_caixa_itens, placeholder_text="Opcional")
        self.comprimento_label.grid(row=7, column=0, sticky="w", padx=(10, 10))
        self.comprimento_entry.grid(row=7, column=1, sticky="ew", padx=(0, 10), pady=2)

        self.espessura_label = ctk.CTkLabel(self.frame_caixa_itens, text="ESPESSURA:")
        self.espessura_entry = CustomEntry(self.frame_caixa_itens, placeholder_text="Opcional")
        self.espessura_label.grid(row=8, column=0, sticky="w", padx=(10, 10))
        self.espessura_entry.grid(row=8, column=1, sticky="ew", padx=(0, 10), pady=2)

        self.link_label = ctk.CTkLabel(self.frame_caixa_itens, text="LINK:")
        self.link_entry = CustomEntry(self.frame_caixa_itens, placeholder_text="Opcional")
        self.link_label.grid(row=9, column=0, sticky="w", padx=(10, 10))
        self.link_entry.grid(row=9, column=1, sticky="ew", padx=(0, 10), pady=2) 

        # Botão para adicionar serviço
        self.btn_adicionar_servico = ctk.CTkButton(self.frame_caixa_itens, text="Adicionar item", command=self.adicionar_item)
        # -------------------------------
        # Fim do frame para os itens
        # -------------------------------

        self.data_label = ctk.CTkLabel(self, text="DATA DA LOCAÇÃO:")
        self.data_entry = CTkDatePicker(self, tabview="AQUISIÇÃO")
        self.data_entry.set_date_format("%d/%m/%Y")
        self.data_entry.set_allow_manual_input(False)
        self.widgets_para_limpar.append(self.data_entry)

        self.prazo_label = ctk.CTkLabel(self, text="PRAZO:")
        self.prazo_entry = CTkDatePicker(self, tabview="AQUISIÇÃO")
        self.prazo_entry.set_date_format("%d/%m/%Y")
        self.prazo_entry.set_allow_manual_input(False)
        self.widgets_para_limpar.append(self.prazo_entry)

        self.servico_label = ctk.CTkLabel(self, text="SERVIÇO:")
        self.servico_entry = CustomEntry(self)
        self.widgets_para_limpar.append(self.servico_entry)

        #row = 6
        self.periodo_locacao_label = ctk.CTkLabel(self, text="PERÍODO DE LOCAÇÃO:")
        self.periodo_locacao_combobox = CustomComboBox(self, values=[
            "DIÁRIA", "SEMANAL", "QUINZENAL", "MENSAL"
        ])
        self.periodo_locacao_combobox.set("")
        self.widgets_para_limpar.append(self.periodo_locacao_combobox)

        #row = 7
        self.quantidade_locacao_label = ctk.CTkLabel(self, text="QUANTIDADE DE PERÍODOS:")
        self.quantidade_locacao_entry = CustomEntry(self, placeholder_text="Apenas números")
        self.widgets_para_limpar.append(self.quantidade_locacao_entry)

        #row = 8

        #row = 9

        #row = 10

        #row = 11
        self.prefixo_label = ctk.CTkLabel(self, text="PREFIXO:")
        self.prefixo_entry = CustomEntry(self)
        self.widgets_para_limpar.append(self.prefixo_entry)

        #row = 12
        self.agencia_label = ctk.CTkLabel(self, text="AGÊNCIA:")
        self.agencia_entry = CustomEntry(self)
        self.widgets_para_limpar.append(self.agencia_entry)

        #row = 13
        self.os_label = ctk.CTkLabel(self, text="OS:")
        self.os_entry = CustomEntry(self)
        self.widgets_para_limpar.append(self.os_entry)

        self.opcao_entrega_label = ctk.CTkLabel(self, text="OPÇÃO DE ENTREGA:")
        self.opcao_entrega_combobox = CustomComboBox(self, values=[
            "ENTREGA",
            "RETIRADA",
        ], command=lambda choice: self.add_campos())
        self.opcao_entrega_combobox.set("")
        self.widgets_para_limpar.append(self.opcao_entrega_combobox)

        #row = 14
        self.endereco_agencia_label = ctk.CTkLabel(self, text="ENDEREÇO DE ENTREGA:")
        self.endereco_agencia_entry = CustomEntry(self)
        self.widgets_para_limpar.append(self.endereco_agencia_entry)

        self.local_retirada_label = ctk.CTkLabel(self, text="LOCAL DE RETIRADA:")
        self.local_retirada_entry = CustomEntry(self, placeholder_text="Opcional")
        self.widgets_para_limpar.append(self.local_retirada_entry)

        #row = 15
        self.nome_responsavel_label = ctk.CTkLabel(self, text="NOME DO RESPONSÁVEL:")
        self.nome_responsavel_entry = CustomEntry(self)
        self.widgets_para_limpar.append(self.nome_responsavel_entry)

        #row = 16
        self.contato_responsavel_agencia_label = ctk.CTkLabel(self, text="CONTATO DO RESPONSÁVEL:")
        self.contato_responsavel_entry = CustomEntry(self)
        self.widgets_para_limpar.append(self.contato_responsavel_entry)

        self.observacoes_label = ctk.CTkLabel(self, text="OBSERVAÇÕES:")
        self.observacoes_entry = CustomEntry(self, placeholder_text="Opcional")
        self.widgets_para_limpar.append(self.observacoes_entry)

        #row = 17
        self.gerar_button = ctk.CTkButton(self, text="GERAR", command=self.gerar_texto_aquisicao)
        self.gerar_button.grid(row=21, column=0, sticky="ew", padx=(10, 10), pady=10)

        # root.bind("<Return>", on_return_press)

        self.limpar_button = ctk.CTkButton(self, text="LIMPAR", width=150, command=self.limpar_dados)
        self.limpar_button.grid(row=21, column=1, sticky="ew", padx=(0, 10), pady=10)

        #row = 18
        self.switch_autocopia_frame_var = tk.BooleanVar(value=True)
        self.switch_autocopia_frame = ctk.CTkSwitch(self, text="Auto-Cópia",
                                        variable=self.switch_autocopia_frame_var, onvalue=True, offvalue=False)
        self.switch_autocopia_frame.grid(row=22, column=0, columnspan=2, sticky="n", padx=10, pady=10)

        #row = 19
        self.texto_aquisicao = ctk.CTkTextbox(self)
        self.texto_aquisicao.grid(row=23, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="nsew")
        self.widgets_para_limpar.append(self.texto_aquisicao)

    def _configurar_layout(self):
        # Configura o layout dos widgets
        pass

    def add_campos(self):
        tipo_aquisicao = self.tipo_aquisicao_combobox.get()
        contrato = self.contrato_combobox.get()
 
        if tipo_aquisicao == "COMPRA":
            self.data_label.grid_forget()
            self.data_entry.grid_forget()
            self.frame_caixa_itens.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=5)       
            self.btn_adicionar_servico.grid(row=10, column=1, sticky="ew", padx=(0, 10), pady=5)
            self.prazo_label.grid(row=12, column=0, sticky="w", padx=(10, 10))
            self.prazo_entry.grid(row=12, column=1, sticky="ew", padx=(0, 10), pady=2)
            self.servico_label.grid_forget()
            self.servico_entry.grid_forget()
            self.periodo_locacao_label.grid_forget()
            self.periodo_locacao_combobox.grid_forget()
            self.quantidade_locacao_label.grid_forget()
            self.quantidade_locacao_entry.grid_forget()
            self.prefixo_label.grid(row=13, column=0, sticky="w", padx=(10, 10))
            self.prefixo_entry.grid(row=13, column=1, sticky="ew", padx=(0, 10), pady=2)
            self.prefixo_entry.configure(placeholder_text="Opcional")
            self.agencia_label.grid(row=14, column=0, sticky="w", padx=(10, 10))
            self.agencia_entry.grid(row=14, column=1, sticky="ew", padx=(0, 10), pady=2)
            self.agencia_entry.configure(placeholder_text="Opcional")
            self.os_label.grid(row=15, column=0, sticky="w", padx=(10, 10))
            self.os_entry.grid(row=15, column=1, sticky="ew", padx=(0, 10), pady=2)
            self.os_entry.configure(placeholder_text="Opcional")
            self.opcao_entrega_label.grid(row=16, column=0, sticky="w", padx=(10, 10))
            self.opcao_entrega_combobox.grid(row=16, column=1, sticky="ew", padx=(0, 10), pady=2)
            self.nome_responsavel_label.grid(row=18, column=0, sticky="w", padx=(10, 10))
            self.nome_responsavel_entry.grid(row=18, column=1, sticky="ew", padx=(0, 10), pady=2)
            self.contato_responsavel_agencia_label.grid(row=19, column=0, sticky="w", padx=(10, 10))
            self.contato_responsavel_entry.grid(row=19, column=1, sticky="ew", padx=(0, 10), pady=2)
            self.observacoes_label.grid(row=20, column=0, sticky="w", padx=(10, 10))
            self.observacoes_entry.grid(row=20, column=1, sticky="ew", padx=(0, 10), pady=2)
        elif tipo_aquisicao == "LOCAÇÃO":
            self.frame_caixa_itens.grid_forget()
            self.prazo_label.grid_forget()
            self.prazo_entry.grid_forget()
            self.descricao_locacao_label.grid(row=3, column=0, sticky="w", padx=(10, 10))
            self.descricao_locacao_entry.grid(row=3, column=1, sticky="ew", padx=(0, 10), pady=2)
            self.data_label.grid(row=4, column=0, sticky="w", padx=(10, 10))
            self.data_entry.grid(row=4, column=1, sticky="ew", padx=(0, 10), pady=2)
            self.servico_label.grid(row=5, column=0, sticky="w", padx=(10, 10))
            self.servico_entry.grid(row=5, column=1, sticky="ew", padx=(0, 10), pady=2)
            self.periodo_locacao_label.grid(row=6, column=0, sticky="w", padx=(10, 10))
            self.periodo_locacao_combobox.grid(row=6, column=1, sticky="ew", padx=(0, 10), pady=2)
            self.quantidade_locacao_label.grid(row=7, column=0, sticky="w", padx=(10, 10))
            self.quantidade_locacao_entry.grid(row=7, column=1, sticky="ew", padx=(0, 10), pady=2)
            self.prefixo_label.grid(row=8, column=0, sticky="w", padx=(10, 10))
            self.prefixo_entry.grid(row=8, column=1, sticky="ew", padx=(0, 10), pady=2)
            self.prefixo_entry.configure(placeholder_text="")
            self.agencia_label.grid(row=9, column=0, sticky="w", padx=(10, 10))
            self.agencia_entry.grid(row=9, column=1, sticky="ew", padx=(0, 10), pady=2)
            self.agencia_entry.configure(placeholder_text="")
            self.os_label.grid(row=10, column=0, sticky="w", padx=(10, 10))
            self.os_entry.grid(row=10, column=1, sticky="ew", padx=(0, 10), pady=2)
            self.os_entry.configure(placeholder_text="")
            self.opcao_entrega_label.grid(row=11, column=0, sticky="w", padx=(10, 10))
            self.opcao_entrega_combobox.grid(row=11, column=1, sticky="ew", padx=(0, 10), pady=2)
            self.nome_responsavel_label.grid(row=18, column=0, sticky="w", padx=(10, 10))
            self.nome_responsavel_entry.grid(row=18, column=1, sticky="ew", padx=(0, 10), pady=2)
            self.contato_responsavel_agencia_label.grid(row=19, column=0, sticky="w", padx=(10, 10))
            self.contato_responsavel_entry.grid(row=19, column=1, sticky="ew", padx=(0, 10), pady=2)
            self.observacoes_label.grid(row=20, column=0, sticky="w", padx=(10, 10))
            self.observacoes_entry.grid(row=20, column=1, sticky="ew", padx=(0, 10), pady=2)
    
        if contrato == "ESCRITÓRIO":
            self.prefixo_label.grid_forget()
            self.prefixo_entry.grid_forget()
            self.prefixo_entry.delete(0, tk.END)
            self.os_label.grid_forget()
            self.os_entry.grid_forget()
            self.os_entry.delete(0, tk.END)
            self.agencia_label.grid_forget()
            self.agencia_entry.grid_forget()
            self.agencia_entry.delete(0, tk.END)

        if self.opcao_entrega_combobox.get() == "":
            self.local_retirada_label.grid_forget()
            self.local_retirada_entry.grid_forget()
            self.endereco_agencia_label.grid_forget()
            self.endereco_agencia_entry.grid_forget()
        elif self.opcao_entrega_combobox.get() == "ENTREGA":
            self.local_retirada_label.grid_forget()
            self.local_retirada_entry.grid_forget()
            self.endereco_agencia_label.grid(row=17, column=0, sticky="w", padx=(10, 10))
            self.endereco_agencia_entry.grid(row=17, column=1, sticky="ew", padx=(0, 10), pady=2)
        elif self.opcao_entrega_combobox.get() == "RETIRADA":
            self.endereco_agencia_label.grid_forget()
            self.endereco_agencia_entry.grid_forget()
            self.local_retirada_label.grid(row=17, column=0, sticky="w", padx=(10, 10))
            self.local_retirada_entry.grid(row=17, column=1, sticky="ew", padx=(0, 10), pady=2)

    # Lista para armazenar serviços e quantidades
    # Exemplo: [("Abertura de porta", 1, "2m", "1m", "3m", "2cm", "http://exemplo.com")]

    # Função para adicionar serviços à lista
    def adicionar_item(self):
        servico = self.descricao_compra_entry.get().strip().upper()
        quantidade = self.quantidade_entry.get().strip().upper()
        altura = self.altura_entry.get().strip().upper()
        largura = self.largura_entry.get().strip().upper()
        comprimento = self.comprimento_entry.get().strip().upper()
        espessura = self.espessura_entry.get().strip().upper()
        link = self.link_entry.get().strip().upper()

        if servico and not quantidade:
            self.notificacao.show_notification(
                "Campo QUANTIDADE\nPreencha o campo!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF"
            )
            return
        elif not servico and quantidade:
            self.notificacao.show_notification(
                "Campo DESCRIÇÃO\nPreencha o campo!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF"
            )
            return
        elif not servico and not quantidade:
            self.notificacao.show_notification(
                "Campos DESCRIÇÃO e QUANTIDADE\nPreencha os campos!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF"
            )
            return
        else:
            self.servicos.append([
                servico, quantidade, altura, largura, comprimento, espessura, link
            ])
            self.descricao_compra_entry.delete(0, "end")

            self.quantidade_entry.delete(0, "end")

            self.altura_entry.delete(0, "end")
            self.altura_entry.focus()  # Foca em outro elemento para atualizar o placeholder

            self.largura_entry.delete(0, "end")
            self.largura_entry.focus()

            self.comprimento_entry.delete(0, "end")
            self.comprimento_entry.focus()

            self.espessura_entry.delete(0, "end")
            self.espessura_entry.focus()

            self.link_entry.delete(0, "end")
            self.link_entry.focus()

            self.descricao_compra_entry.focus()

            self.atualizar_lista_itens()

    def atualizar_lista_itens(self):
        for widget in self.frame_lista_itens.winfo_children():
            widget.destroy()

        if len(self.servicos) > 0:
            self.frame_lista_itens.grid(row=11, column=0, columnspan=2, sticky="ew", padx=(10, 10), pady=5)
        else:
            self.frame_lista_itens.grid_forget()

        for index, (nome_item, quantidade, altura, largura, comprimento, espessura, link) in enumerate(self.servicos):
            row_frame = ctk.CTkFrame(self.frame_lista_itens, width=400)
            row_frame.grid(row=index, column=0, columnspan=2, sticky="ew", padx=10, pady=2)

            detalhes = f"Descrição: {nome_item}, Quantidade: {quantidade}"
            if altura:
                detalhes += f", Altura: {altura}"
            if largura:
                detalhes += f", Largura: {largura}"
            if comprimento:
                detalhes += f", Comprimento: {comprimento}"
            if espessura:
                detalhes += f", Espessura: {espessura}"
            if link:
                detalhes += f", Link: {link}"

            label_servico_gerado = ctk.CTkLabel(
                row_frame, 
                text=detalhes,
                anchor="w", justify="left", wraplength=340
            )
            label_servico_gerado.grid(row=0, column=0, padx=2)

            btn_editar = ctk.CTkButton(
                row_frame, text="Editar", width=30, 
                command=lambda i=index: self.editar_item(i)
            )
            btn_editar.grid(row=0, column=1, padx=2)

            btn_excluir = ctk.CTkButton(
                row_frame, text="❌", width=30, 
                fg_color="red", hover_color="darkred", 
                command=lambda i=index: self.remover_item(i)
            )
            btn_excluir.grid(row=0, column=2, padx=2)

    # Função para editar um serviço
    def editar_item(self, index):
        self.editando_item = index
        servico_atual, quantidade_atual, altura_atual, largura_atual, \
        comprimento_atual, espessura_atual, link_atual = self.servicos[index]

        # Preenche os campos de entrada com os valores do item selecionado
        self.descricao_compra_entry.delete(0, "end")
        self.descricao_compra_entry.insert(0, servico_atual)

        self.quantidade_entry.delete(0, "end")
        self.quantidade_entry.insert(0, str(quantidade_atual))

        self.altura_entry.delete(0, "end")
        self.altura_entry.insert(0, altura_atual)
        self.altura_entry.focus()

        self.largura_entry.delete(0, "end")
        self.largura_entry.insert(0, largura_atual)
        self.largura_entry.focus()

        self.comprimento_entry.delete(0, "end")
        self.comprimento_entry.insert(0, comprimento_atual)
        self.comprimento_entry.focus()

        self.espessura_entry.delete(0, "end")
        self.espessura_entry.insert(0, espessura_atual)
        self.espessura_entry.focus()

        self.link_entry.delete(0, "end")
        self.link_entry.insert(0, link_atual)
        self.link_entry.focus()

        self.descricao_compra_entry.focus()

        self.btn_adicionar_servico.configure(text="Salvar", command=lambda: self.salvar_edicao(index))

        # Desabilita o botão de excluir
        self.atualizar_lista_itens()

    # Função para salvar a edição
    def salvar_edicao(self, index):
        novo_servico = self.descricao_compra_entry.get().strip()
        nova_quantidade = self.quantidade_entry.get().strip()
        nova_altura = self.altura_entry.get().strip()
        nova_largura = self.largura_entry.get().strip()
        novo_comprimento = self.comprimento_entry.get().strip()
        nova_espessura = self.espessura_entry.get().strip()
        novo_link = self.link_entry.get().strip()

        if novo_servico and not nova_quantidade:
            self.notificacao.show_notification(
                "Campo QUANTIDADE\nA quantidade não pode ser nula!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF"
            )
            return
        elif not novo_servico and nova_quantidade:
            self.notificacao.show_notification(
                "Campo DESCRIÇÃO\nO campo deve ser preenchido!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF"
            )
            return
        elif not novo_servico and not nova_quantidade:
            self.notificacao.show_notification(
                "Campos DESCRIÇÃO e QUANTIDADE\nOs campos devem ser preenchidos!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF"
            )
            return
        else:
            self.servicos[index] = (novo_servico, nova_quantidade, nova_altura, nova_largura, novo_comprimento, nova_espessura, novo_link)

            # Limpa os campos após a edição
            self.descricao_compra_entry.delete(0, "end")
            self.quantidade_entry.delete(0, "end")
            self.altura_entry.delete(0, "end")
            self.largura_entry.delete(0, "end")
            self.comprimento_entry.delete(0, "end")
            self.espessura_entry.delete(0, "end")
            self.link_entry.delete(0, "end")

            # Restaura o texto do botão para "Adicionar item"
            self.btn_adicionar_servico.configure(text="Adicionar item", command=self.adicionar_item)

            # Reabilita o botão de excluir
            self.editando_item = None  # Desmarca a edição

            self.descricao_compra_entry.focus()

            self.atualizar_lista_itens()

    # Função para remover um serviço da lista
    def remover_item(self, index):
        if self.editando_item is None:  # Só permite excluir se não estiver editando
            del self.servicos[index]
            self.atualizar_lista_itens()
        else:
            self.notificacao.show_notification("Item em edição!\nSalve-o para habilitar a exclusão.", NotifyType.WARNING, bg_color="#404040", text_color="#FFFFFF")

    def gerar_texto_aquisicao(self):
        nome_usuario = arrumar_texto(self.nome_usuario_entry.get().upper())
        tipo_aquisicao = arrumar_texto(self.tipo_aquisicao_combobox.get().upper())
        contrato = arrumar_texto(self.contrato_combobox.get().upper())
        descricao = arrumar_texto(self.descricao_locacao_entry.get().upper())
        prazo = arrumar_texto(self.prazo_entry.get_date().upper())
        data = arrumar_texto(self.data_entry.get_date().upper())
        servico = arrumar_texto(self.servico_entry.get().upper())
        periodo_locacao = arrumar_texto(self.periodo_locacao_combobox.get().upper())
        quantidade_periodo_locacao = arrumar_texto(self.quantidade_locacao_entry.get().upper())
        prefixo = valida_prefixo(self.prefixo_entry.get())
        agencia = arrumar_texto(self.agencia_entry.get().upper())
        os_num = valida_os(self.os_entry.get())
        opcao_entrega = arrumar_texto(self.opcao_entrega_combobox.get().upper())
        endereco_agencia = arrumar_texto(self.endereco_agencia_entry.get().upper())
        local_retirada = arrumar_texto(self.local_retirada_entry.get().upper())
        nome_responsavel = arrumar_texto(self.nome_responsavel_entry.get().upper())
        contato_responsavel = arrumar_texto(self.contato_responsavel_entry.get().upper())
        observacoes = arrumar_texto(self.observacoes_entry.get().upper())

        # Verificar se algum campo obrigatório está vazio
        campos_obrigatorios = [
            (nome_usuario, "USUÁRIO"),
            (tipo_aquisicao, "TIPO DE SERVIÇO"),
            (contrato, "CONTRATO")
        ]

        if tipo_aquisicao == "COMPRA":
            # Adiciona os campos comuns para os dois tipos
            campos_obrigatorios.extend([
                (self.servicos if self.servicos else None, "DESCRIÇÃO E QUANTIDADE"),
                (prazo, "PRAZO"),
                (opcao_entrega, "OPÇÃO DE ENTREGA"),
                (nome_responsavel, "NOME DO RESPONSÁVEL"),
                (contato_responsavel, "CONTATO DO RESPONSÁVEL")
            ])
            
            if opcao_entrega == "ENTREGA":
                campos_obrigatorios.append((endereco_agencia, "ENDEREÇO"))

        elif tipo_aquisicao == "LOCAÇÃO":
            # Adiciona os campos comuns para os dois tipos
            campos_obrigatorios.extend([
                (data, "DATA DA LOCAÇÃO"),
                (periodo_locacao, "PERÍODO DE LOCAÇÃO"),
                (quantidade_periodo_locacao, "QUANTIDADE DE PERÍODOS"),
                (prefixo, "PREFIXO"),
                (agencia, "AGÊNCIA"),
                (os_num, "OS"),
                (opcao_entrega, "OPÇÃO DE ENTREGA"),
                (nome_responsavel, "NOME DO RESPONSÁVEL"),
                (contato_responsavel, "CONTATO DO RESPONSÁVEL")
            ])
            
            if opcao_entrega == "ENTREGA":
                campos_obrigatorios.append((endereco_agencia, "ENDEREÇO"))

        if contrato == "ESCRITÓRIO":
            campos_obrigatorios = [
                item for item in campos_obrigatorios
                if item not in [(prefixo, "PREFIXO"), (agencia, "AGÊNCIA"), (os_num, "OS")]
            ]

        # Verificar campos vazios
        campos_vazios = [nome for valor, nome in campos_obrigatorios if not valor]

        if campos_vazios:
            if campos_vazios == ["DESCRIÇÃO E QUANTIDADE"]:
                self.notificacao.show_notification("Item(ns) não adicionado(s)", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
                return
            else:
                self.notificacao.show_notification("Preencha os campos obrigatórios em branco!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
                return

        if prefixo == "Prefixo inválido":
            self.notificacao.show_notification("Campo PREFIXO\nPrefixo inválido. Use o padrão XXXX/XX.", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
            return  

        if os_num == "OS_invalida":
            self.notificacao.show_notification("Campo OS\nPor favor, insira uma OS válida!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
            return

        if quantidade_periodo_locacao:
            if quantidade_periodo_locacao.isdigit():
                quantidade_periodo_locacao = int(quantidade_periodo_locacao)

            if not isinstance(quantidade_periodo_locacao, int) or quantidade_periodo_locacao < 1:
                self.notificacao.show_notification("Campo QUANTIDADE DE PERÍODOS\nPor favor, insira um número válido!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
                return

        if tipo_aquisicao == "COMPRA":
            texto = f"*SOLICITAÇÃO DE AQUISIÇÃO - {tipo_aquisicao}*\n\n"
            texto += f"▪ *Contrato:* {contrato}\n"
            texto += f"▪ *Prazo para aquisição:* {prazo}\n"

            if self.servicos:  # Verifica se a lista não está vazia
                if len(self.servicos) == 1:  # Apenas um item, mantém o formato original
                    servico, quantidade, altura, largura, comprimento, espessura, link = self.servicos[0]
                    texto += f"▪ *Descrição da aquisição:* {servico}\n"
                    texto += f"▪ *Altura:* {altura}\n" if altura else ""
                    texto += f"▪ *Largura:* {largura}\n" if largura else ""
                    texto += f"▪ *Comprimento:* {comprimento}\n" if comprimento else ""
                    texto += f"▪ *Espessura:* {espessura}\n" if espessura else ""
                    texto += f"▪ *Quantidade:* {quantidade}\n"
                    texto += f"▪ *Link:* {link}\n" if link else ""
                else:  # Mais de um item, gera uma lista formatada
                    texto += "▪ *Itens da solicitação:*\n"
                    for idx, (servico, quantidade, altura, largura, comprimento, espessura, link) in enumerate(self.servicos, start=1):
                        texto += f"   {idx}. {servico} - {quantidade} unidade(s)\n"
                        if altura:
                            texto += f"      - *Altura:* {altura}\n"
                        if largura:
                            texto += f"      - *Largura:* {largura}\n"
                        if comprimento:
                            texto += f"      - *Comprimento:* {comprimento}\n"
                        if espessura:
                            texto += f"      - *Espessura:* {espessura}\n"
                        if link:
                            texto += f"      - *Link:* {link}\n"

            texto += f"▪ *Prefixo, Agência e OS:* {prefixo} - {agencia} - {os_num}\n" if os_num else ""
            
            if opcao_entrega == "ENTREGA":
                texto += f"▪ *Entrega ou Retirada:* ENTREGA\n"
                texto += f"▪ *Endereço da Entrega:* {endereco_agencia}\n"
            else: 
                texto += "▪ *Entrega ou Retirada:* RETIRADA\n"

                if local_retirada:
                    texto += f"▪ *Local de Retirada:* {local_retirada}\n"
                    
            texto += f"▪ *Nome do responsável:* {nome_responsavel}\n"
            texto += f"▪ *Contato do responsável:* {contato_responsavel}\n"
            texto += f"▪ *Observações:* {observacoes}\n" if observacoes else ""
        else:        
            texto = f"*SOLICITAÇÃO DE AQUISIÇÃO - {tipo_aquisicao}*\n\n"
            texto += f"▪ *Contrato:* {contrato}\n"
            texto += f"▪ *Descrição da locação:* {descricao}\n"
            texto += f"▪ *Data da locação:* {data}\n"
            texto += f"▪ *Serviço:* {servico}\n"
            
            if periodo_locacao == "DIÁRIA":
                if quantidade_periodo_locacao == 1:
                    texto += f"▪ *Período da locação:* {quantidade_periodo_locacao} {periodo_locacao}\n"
                else:
                    texto += f"▪ *Período da locação:* {quantidade_periodo_locacao} {periodo_locacao}S\n"
            elif periodo_locacao == "SEMANAL":
                if quantidade_periodo_locacao == 1:
                    texto += f"▪ *Período da locação:* {quantidade_periodo_locacao} SEMANA\n"
                else:
                    texto += f"▪ *Período da locação:* {quantidade_periodo_locacao} SEMANAS\n"
            elif periodo_locacao == "QUINZENAL":
                if quantidade_periodo_locacao == 1:
                    texto += f"▪ *Período da locação:* {quantidade_periodo_locacao} QUINZENA\n"
                else:
                    texto += f"▪ *Período da locação:* {quantidade_periodo_locacao} QUINZENAS\n"
            else:
                if quantidade_periodo_locacao == 1:
                    texto += f"▪ *Período da locação:* {quantidade_periodo_locacao} MÊS\n"
                else:
                    texto += f"▪ *Período da locação:* {quantidade_periodo_locacao} MESES\n"
            
            texto += f"▪ *Prefixo, Agência e OS:* {prefixo} - {agencia} - {os_num}\n" if os_num else f""
            
            if opcao_entrega == "ENTREGA":
                texto += f"▪ *Entrega ou Retirada:* ENTREGA\n"
                texto += f"▪ *Endereço da Entrega:* {endereco_agencia}\n"
            else: 
                texto += "▪ *Entrega ou Retirada:* RETIRADA\n"

                if local_retirada:
                    texto += f"▪ *Local de Retirada:* {local_retirada}\n"

            texto += f"▪ *Nome do responsável:* {nome_responsavel}\n"
            texto += f"▪ *Contato do responsável:* {contato_responsavel}\n"
            texto += f"▪ *Observações:* {observacoes}\n" if observacoes else ""

        # Exibir texto na caixa de texto
        self.texto_aquisicao.delete(1.0, tk.END)
        self.texto_aquisicao.insert(tk.END, texto)

        # Copiar automaticamente o texto gerado caso o switch esteja ativo
        if self.switch_autocopia_frame_var.get():
            pyperclip.copy(texto)

    def limpar_dados(self):
        if self.editando_item is None:
            # Limpar os widgets da Tab 1
            for widget in self.widgets_para_limpar:
                if isinstance(widget, ctk.CTkEntry):
                    widget.delete(0, tk.END)
                elif isinstance(widget, ctk.CTkTextbox):
                    widget.delete("0.0", tk.END)
                elif isinstance(widget, ctk.CTkComboBox):
                    widget.set("")
                elif isinstance(widget, CTkDatePicker):
                    widget.set("")

                self.servicos.clear()
                self.atualizar_lista_itens()
                self.add_campos()
        else:
            notification_manager = NotificationManager(root)  # passando a instância da janela principal
            notification_manager.show_notification("Item em edição!\nSalve-o para habilitar a limpeza dos campos.", NotifyType.WARNING, bg_color="#404040", text_color="#FFFFFF")
            pass 

    def _on_return_press(self, event):
        """Manipula o evento de pressionar Enter."""
        self.gerar_texto_aquisicao()
