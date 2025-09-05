"""
Módulo refatorado para a aba de Pagamento
Organizado em classes e métodos para melhor manutenibilidade
"""

import customtkinter as ctk
import tkinter as tk
from datetime import datetime
import pyperclip
from typing import List, Dict, Any, Optional
from os.path import splitext

try:
    from .utils import *
    from .bd.utils_bd import acessa_bd_contratos, acessa_bd_usuarios, conecta_banco_pagamentos
    from .componentes import CustomEntry, CustomComboBox
    from .CTkFloatingNotifications import *
    from .gerador_excel import gerar_excel, DadosRequisicao
except ImportError:
    from utils import *
    from bd.utils_bd import acessa_bd_contratos, acessa_bd_usuarios, conecta_banco_pagamentos
    from componentes import CustomEntry, CustomComboBox
    from CTkFloatingNotifications import *
    from gerador_excel import gerar_excel, DadosRequisicao

class AbaPagamento(ctk.CTkFrame):
    """Classe responsável pela aba de Pagamento"""
    
    def __init__(self, master, tela_para_notifcacao, tabview="PAGAMENTO", nome_completo_usuario=None, contratos=None):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.tabview = tabview
        self.nome_completo_usuario = nome_completo_usuario
        self.contratos = contratos  # Lista de contratos
        self.notificacao = NotificationManager(master=None)

        # Variavel para passar parâmetro da tela principal para o gerador_excel
        self.root = tela_para_notifcacao

        # Listas para widgets que precisam ser limpos
        self.widgets_para_limpar = []
        
        # Variável para controle de edição
        self.editando_item_pagamento = None

        # Variável para controle dos itens_pagamento
        self.itens_pagamento = []

        self.aparece_lista_itens_aba_pagamentos = {
            "RELATÓRIO EXTRA", "ADIANTAMENTO/PAGAMENTO PARCEIRO",
            "REEMBOLSO SEM OS", "SOLICITAÇÃO SEM OS",
            "SOLICITAÇÃO COM OS", "REEMBOLSO COM OS",
            "REEMBOLSO UBER",
        }
        
        # Dados dos usuários
        self.usuarios_gerais, self.usuarios_varios_departamentos = acessa_bd_usuarios()
        
        # Configuração da interface
        self._setup_main_frame()
        self._create_widgets()
        self._configure_layout()
    
    def _setup_main_frame(self):
        """Configura o frame principal da aba"""
        self._set_appearance_mode("system")
        
        # Configuração de grid
        self.grid_rowconfigure(4, weight=1)
        self.grid_rowconfigure(18, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
    
    def _create_widgets(self):
        """Cria todos os widgets da interface"""
        self._create_secao_usuario()
        self._create_secao_servico()
        self._create_secao_contrato()
        self._create_items_frame()
        self._create_secao_aquisicao()
        self._create_secao_fornecedor()
        self._create_secao_valor()
        self._create_secao_pagamento()
        self._create_botoes_de_acao()
        self._create_switches()
        self._create_area_texto()
    
    def _create_secao_usuario(self):
        """Cria a seção de usuário"""
        ctk.CTkLabel(self, text="USUÁRIO:").grid(
            row=0, column=0, sticky="w", padx=(10, 10), pady=(10, 0)
        )
        
        self.nome_usuario_entry = CustomEntry(self)
        self.nome_usuario_entry.grid(
            row=0, column=1, sticky="ew", padx=(0, 10), pady=(10, 2)
        )
        self.nome_usuario_entry.insert(0, self.nome_completo_usuario)
        self.nome_usuario_entry.configure(state='disabled')
    
    def _create_secao_servico(self):
        """Cria a seção de tipo de serviço"""
        ctk.CTkLabel(self, text="TIPO DE SERVIÇO:").grid(
            row=1, column=0, sticky="w", padx=(10, 10)
        )
        
        service_types = [
            "ABASTECIMENTO", "ADIANTAMENTO/PAGAMENTO PARCEIRO", "AQUISIÇÃO COM OS",
            "AQUISIÇÃO SEM OS", "CARRETO", "COMPRA IN LOCO", "ENVIO DE MATERIAL",
            "ESTACIONAMENTO/PEDÁGIO", "HOSPEDAGEM", "ORÇAMENTO APROVADO",
            "PREST. SERVIÇO/MÃO DE OBRA", "REEMBOLSO COM OS", "REEMBOLSO SEM OS",
            "REEMBOLSO UBER", "RELATÓRIO EXTRA", "SOLICITAÇÃO COM OS",
            "SOLICITAÇÃO SEM OS", "TRANSPORTADORA"
        ]
        
        self.tipo_servico_combobox = CustomComboBox(
            self, 
            values=service_types,
            command=self._on_muda_tipo_servico
        )
        self.tipo_servico_combobox.grid(
            row=1, column=1, sticky="ew", padx=(0, 10), pady=2
        )
    
    def _create_secao_contrato(self):
        """Cria a seção de contrato"""
        self.contrato_label = ctk.CTkLabel(self, text="CONTRATO:")
        self.contrato_combobox = CustomComboBox(self, values=self.contratos)
        
        self.opcao_os_parceiro_label = ctk.CTkLabel(self, text="POSSUI OS?")
        self.opcao_os_parceiro_combobox = CustomComboBox(
            self, 
            values=["SIM", "NÃO"],
            command=self._on_muda_os
        )
    
    def _create_items_frame(self):
        """Cria o frame para os itens"""
        self.frame_caixa_itens_pagamento = ctk.CTkFrame(self, border_width=1)
        self.frame_caixa_itens_pagamento.grid_columnconfigure(0, weight=1)
        self.frame_caixa_itens_pagamento.grid_columnconfigure(1, weight=1)
        
        self.frame_lista_itens_pagamento = ctk.CTkFrame(master=self.frame_caixa_itens_pagamento)
        
        # Campos do frame de itens
        self._create_item_fields()
        
        # Botão adicionar item
        self.btn_adicionar_servico_pagamento = ctk.CTkButton(
            master=self.frame_caixa_itens_pagamento,
            text="Adicionar item",
            command=self._add_item_pagamento
        )
        self.btn_adicionar_servico_pagamento.grid(
            row=10, column=1, sticky="ew", padx=(0, 10), pady=5
        )
    
    def _create_item_fields(self):
        """Cria os campos específicos dos itens"""
        self.descricao_do_item_pagamento_label = ctk.CTkLabel(
            master=self.frame_caixa_itens_pagamento, text="DESCRIÇÃO DO ITEM: "
        )
        self.descricao_do_item_pagamento_entry = CustomEntry(
            master=self.frame_caixa_itens_pagamento
        )
        
        # Campo SAÍDA X DESTINO (UBER)
        self.saida_destino_label = ctk.CTkLabel(master=self.frame_caixa_itens_pagamento)
        self.saida_destino_entry = CustomEntry(master=self.frame_caixa_itens_pagamento)
        
        # Campo MOTIVO
        self.motivo_label = ctk.CTkLabel(master=self.frame_caixa_itens_pagamento)
        self.motivo_entry = CustomEntry(master=self.frame_caixa_itens_pagamento)
        
        # Campo VALOR
        self.valor_caixa_itens_label = ctk.CTkLabel(master=self.frame_caixa_itens_pagamento)
        self.valor_caixa_itens_entry = CustomEntry(master=self.frame_caixa_itens_pagamento)
    
    def _create_secao_aquisicao(self):
        """Cria a seção de aquisição"""
        self.tipo_aquisicao_label = ctk.CTkLabel(self, text="TIPO DE AQUISIÇÃO:")
        self.tipo_aquisicao_combobox = CustomComboBox(
            self, command=self._campo_descricao_utilidades
        )
        self.tipo_aquisicao_combobox.set("")
        self.widgets_para_limpar.append(self.tipo_aquisicao_combobox)
        
        # Bind events
        self.tipo_aquisicao_combobox.bind("<FocusOut>", self._restaurar_valores_tipo_aquisicao)
        self.tipo_aquisicao_combobox.bind("<KeyRelease>", self._restaurar_valores_tipo_aquisicao)
        
        # Campos relacionados
        self._create_campos_relacionados_a_aquisicao()
    
    def _create_campos_relacionados_a_aquisicao(self):
        """Cria campos relacionados à aquisição"""
        fields_config = [
            ("DESCRIÇÃO DA SOLICITAÇÃO:", "descricao_utilidades"),
            ("TÉCNICOS:", "tecnicos"),
        ]

        for label_text, attr_name in fields_config:
            label = ctk.CTkLabel(self, text=label_text)
            entry = CustomEntry(self)
            setattr(self, f"{attr_name}_label", label)
            setattr(self, f"{attr_name}_entry", entry)
            self.widgets_para_limpar.append(entry)
        
        # Campos opcionais (sem labels fixos)
        optional_fields = ["prefixo", "agencia", "os"]
        for field in optional_fields:
            label = ctk.CTkLabel(self)
            entry = CustomEntry(self)
            setattr(self, f"{field}_label", label)
            setattr(self, f"{field}_entry", entry)
            self.widgets_para_limpar.append(entry)
    
    def _create_secao_fornecedor(self):
        """Cria a seção de fornecedor"""
        ctk.CTkLabel(self, text="NOME FORNEC./BENEF.:").grid(
            row=8, column=0, sticky="w", padx=(10, 10)
        )
        
        self.nome_fornecedor_entry = CustomEntry(self)
        self.nome_fornecedor_entry.grid(
            row=8, column=1, sticky="ew", padx=(0, 10), pady=2
        )
        self.widgets_para_limpar.append(self.nome_fornecedor_entry)

    def _create_secao_valor(self):
        """Cria a seção de valores"""
        self.valor_label = ctk.CTkLabel(self, text="VALOR:")
        self.valor_entry = CustomEntry(self)
        self.widgets_para_limpar.append(self.valor_entry)
        
        # Competência
        ano_atual = datetime.now().strftime("%Y")
        months = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN",
                 "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"]
        
        self.competencia_label = ctk.CTkLabel(self, text="COMPETÊNCIA:")
        self.competencia_combobox = CustomComboBox(
            self,
            values=[f"{month}/{ano_atual}" for month in months]
        )
        self.widgets_para_limpar.append(self.competencia_combobox)
        
        # Porcentagem
        self.porcentagem_label = ctk.CTkLabel(
            self, text="% DO ADIANTAMENTO \nDO PARCEIRO:"
        )
        self.porcentagem_entry = CustomEntry(self)
        self.widgets_para_limpar.append(self.porcentagem_entry)
    
    def _create_secao_pagamento(self):
        """Cria a seção de pagamento"""
        ctk.CTkLabel(self, text="TIPO DE PAGAMENTO:").grid(
            row=12, column=0, sticky="w", padx=(10, 10)
        )
        
        self.tipo_pagamento_combobox = CustomComboBox(
            self,
            values=["PIX", "VEXPENSES"],
            command=self._adiciona_campo_pix
        )
        self.tipo_pagamento_combobox.grid(
            row=12, column=1, sticky="ew", padx=(0, 10), pady=2
        )
        self.tipo_pagamento_combobox.set("")
        
        # Campos PIX
        self._create_campos_pix()
    
    def _create_campos_pix(self):
        """Cria os campos relacionados ao PIX"""
        self.tipo_chave_pix_label = ctk.CTkLabel(self, text="TIPO DA CHAVE PIX:")
        
        pix_types = ["CHAVE ALEATÓRIA", "CNPJ", "COPIA E COLA", "CPF", 
                    "E-MAIL", "QR CODE", "TELEFONE"]
        
        self.tipo_chave_pix_combobox = CustomComboBox(
            self,
            values=pix_types,
            command=self._esconde_campos_pagamento_qrcode
        )
        self.tipo_chave_pix_combobox.set("")
        self.widgets_para_limpar.append(self.tipo_chave_pix_combobox)
        
        self.chave_pix_label = ctk.CTkLabel(self, text="CHAVE PIX:")
        self.chave_pix_entry = CustomEntry(self)
        self.widgets_para_limpar.append(self.chave_pix_entry)
        
        self.nome_benef_pix_label = ctk.CTkLabel(self, text="NOME DO BENEF. DO PIX:")
        self.nome_benef_pix_entry = CustomEntry(self, placeholder_text="Opcional")
        self.widgets_para_limpar.append(self.nome_benef_pix_entry)
        self.chave_pix_entry.focus()
    
    def _create_botoes_de_acao(self):
        """Cria os botões de ação"""
        self.gerar_button = ctk.CTkButton(
            self, text="GERAR", command=self._gerar_solicitacao
        )
        self.gerar_button.grid(row=16, column=0, sticky="ew", padx=(10, 10), pady=10)
        
        self.limpar_button = ctk.CTkButton(
            self, text="LIMPAR", width=150, command=self._limpar_dados
        )
        self.limpar_button.grid(row=16, column=1, sticky="ew", padx=(0, 10), pady=10)
    
    def _create_switches(self):
        """Cria os switches de configuração"""
        self.switch_autocopia_var = tk.BooleanVar(value=True)
        self.switch_autocopia = ctk.CTkSwitch(
            self, text="Auto-Cópia",
            variable=self.switch_autocopia_var, onvalue=True, offvalue=False
        )
        self.switch_autocopia.grid(row=17, column=0, sticky="n", padx=(0, 10), pady=10)
        
        self.switch_gerar_excel_var = tk.BooleanVar(value=True)
        self.switch_gerar_excel = ctk.CTkSwitch(
            self, text="Gerar Excel",
            variable=self.switch_gerar_excel_var, onvalue=True, offvalue=False
        )
        self.switch_gerar_excel.grid(row=17, column=1, sticky="n", padx=(0, 10), pady=10)
    
    def _create_area_texto(self):
        """Cria a área de texto para solicitação"""
        self.texto_solicitacao = ctk.CTkTextbox(self)
        self.texto_solicitacao.grid(
            row=18, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="nsew"
        )
        self.widgets_para_limpar.append(self.texto_solicitacao)
    
    def _configure_layout(self):
        """Configura o layout após criação dos widgets"""
        # Esta função pode ser expandida para configurações específicas de layout
        pass
    
    # Event handlers
    def _on_muda_tipo_servico(self, choice: str):
        """Handler para mudança no tipo de serviço"""
        self._add_campos()
    
    def _on_muda_os(self, choice: str):
        """Handler para mudança na opção de OS"""
        self._atualizar_exibicao_frame_caixa_itens()
    
    # Métodos de negócio (placeholders - implementar conforme necessário)
    def _add_campos(self):
        """Adiciona campos baseado no tipo de serviço selecionado"""
        # Verificar se há um item em edição
        if self.editando_item_pagamento is not None:
            self._mostra_aviso_edicao()
            return

        tipo_servico = self.tipo_servico_combobox.get()
        self.valor_atual_combobox = tipo_servico

        self._configure_base_labels()
        self._configure_opcoes_contratos(tipo_servico)
        self._reseta_campos_pagamento()
        self._configure_campo_valor()
        self._esconde_campos_condicionais()
        self._limpa_campos_condicionais()
        
        # Configurar campos específicos por tipo de serviço
        self._configure_service_specific_fields(tipo_servico)
        self._configure_pref_age_os()
        self._configure_opcoes_pagamento(tipo_servico)
        self._configure_visibilidade_contrato(tipo_servico)
        self._configure_campos_aquisicao(tipo_servico)

    def _mostra_aviso_edicao(self):
        """Mostra aviso quando há item em edição"""
        # Assumindo que notification_manager é acessível
        if hasattr(self, 'notification_manager'):
            self.notificacao.show_notification(
                "Item em edição!\nSalve-o para alterar o tipo de serviço.",
                "WARNING",  # Assumindo que NotifyType.WARNING é uma string
                bg_color="#404040",
                text_color="#FFFFFF"
            )
        self.tipo_servico_combobox.set(getattr(self, 'valor_atual_combobox', ''))

    def _configure_base_labels(self):
        """Configura labels base"""
        self.prefixo_label.configure(text="PREFIXO:")
        self.agencia_label.configure(text="AGÊNCIA:")
        self.os_label.configure(text="OS ou Nº DO CONTRATO (CAIXA):")

    def _configure_opcoes_contratos(self, tipo_servico: str):
        """Configura opções de contrato baseado no tipo de serviço"""
        # Assumindo que 'contratos' é uma variável acessível
        contratos = getattr(self, 'contratos', [])
        
        if tipo_servico == "ADIANTAMENTO/PAGAMENTO PARCEIRO" and "ESCRITÓRIO" in contratos:
            contrato_sem_escritorio = contratos.copy()
            contrato_sem_escritorio.remove("ESCRITÓRIO")
            self.contrato_combobox.configure(values=contrato_sem_escritorio)
        else:
            self.contrato_combobox.configure(values=contratos)
        self.contrato_combobox.set("")

    def _reseta_campos_pagamento(self):
        """Reseta campos de pagamento"""
        self.tipo_pagamento_combobox.set("")
        
        # Esconder campos PIX
        pix_widgets = [
            self.tipo_chave_pix_label, self.tipo_chave_pix_combobox,
            self.chave_pix_label, self.chave_pix_entry,
            self.nome_benef_pix_label, self.nome_benef_pix_entry
        ]
        
        for widget in pix_widgets:
            widget.grid_forget()
        
        self.tipo_chave_pix_combobox.set("")

    def _configure_campo_valor(self):
        """Configura campo de valor como padrão"""
        self.valor_label.grid(row=11, column=0, sticky="w", padx=(10, 10))
        self.valor_entry.grid(row=11, column=1, sticky="ew", padx=(0, 10), pady=2)

    def _esconde_campos_condicionais(self):
        """Oculta todos os campos condicionais"""
        conditional_widgets = [
            self.competencia_label, self.competencia_combobox,
            self.porcentagem_label, self.porcentagem_entry,
            self.motivo_label, self.motivo_entry,
            self.saida_destino_label, self.saida_destino_entry,
            self.tecnicos_label, self.tecnicos_entry,
            self.descricao_utilidades_label, self.descricao_utilidades_entry,
            self.frame_caixa_itens_pagamento,
            self.opcao_os_parceiro_label, self.opcao_os_parceiro_combobox,
        ]
        
        for widget in conditional_widgets:
            widget.grid_forget()

    def _limpa_campos_condicionais(self):
        """Limpa campos condicionais"""
        self.competencia_combobox.set("")
        self.opcao_os_parceiro_combobox.set("")
        
        clear_entries = [
            self.porcentagem_entry, self.motivo_entry, self.saida_destino_entry,
            self.tecnicos_entry, self.prefixo_entry, self.agencia_entry, self.os_entry
        ]
        
        for entry in clear_entries:
            entry.delete(0, tk.END)

    def _configure_service_specific_fields(self, tipo_servico: str):
        """Configura campos específicos baseado no tipo de serviço"""
        if tipo_servico == "PREST. SERVIÇO/MÃO DE OBRA":
            self._configure_campo_competencia()
        elif tipo_servico in {"ABASTECIMENTO", "ESTACIONAMENTO/PEDÁGIO", "HOSPEDAGEM", 
                             "SOLICITAÇÃO COM OS", "SOLICITAÇÃO SEM OS"}:
            self._configure_campos_tecnicos()
        
        # Configurar campos para serviços com lista de itens
        if hasattr(self, 'aparece_lista_itens_aba_pagamentos'):
            if tipo_servico in self.aparece_lista_itens_aba_pagamentos:
                self._configure_campos_da_lista_de_itens()

    def _configure_campo_competencia(self):
        """Configura campos para prestação de serviço/mão de obra"""
        self.competencia_label.grid(row=9, column=0, sticky="w", padx=(10, 10))
        self.competencia_combobox.grid(row=9, column=1, sticky="ew", padx=(0, 10), pady=2)
        self.porcentagem_label.grid(row=10, column=0, sticky="w", padx=(10, 10))
        self.porcentagem_entry.grid(row=10, column=1, sticky="ew", padx=(0, 10), pady=2)

    def _configure_campos_tecnicos(self):
        """Configura campo de técnicos"""
        self.tecnicos_label.grid(row=2, column=0, sticky="w", padx=(10, 10))
        self.tecnicos_entry.grid(row=2, column=1, sticky="ew", padx=(0, 10), pady=2)

    def _configure_campos_da_lista_de_itens(self):
        """Configura campos da lista de itens"""
        tipo_servico = self.tipo_servico_combobox.get()

        # Posicionamento do frame de itens
        if tipo_servico in {"SOLICITAÇÃO COM OS", "SOLICITAÇÃO SEM OS", "REEMBOLSO COM OS", "REEMBOLSO SEM OS", "REEMBOLSO UBER"}:
            self.frame_caixa_itens_pagamento.grid(row=9, column=0, columnspan=2, sticky="nsew", pady=5)
        elif tipo_servico == "ADIANTAMENTO/PAGAMENTO PARCEIRO":
            self.opcao_os_parceiro_label.grid(row=5, column=0, sticky="w", padx=(10, 10))
            self.opcao_os_parceiro_combobox.grid(row=5, column=1, sticky="ew", padx=(0, 10), pady=2)
        else:
            self.frame_caixa_itens_pagamento.grid(row=6, column=0, columnspan=2, sticky="nsew", pady=5)

        # Limpar lista de itens se existir
        if hasattr(self, 'itens_pagamento') and len(self.itens_pagamento) > 0:
            self.itens_pagamento.clear()
            if hasattr(self, '_atualizar_lista_itens_pagamento'):
                self._atualizar_lista_itens_pagamento()
            self._add_campos()  # Recursão controlada

        self._configure_campos_especificos_de_itens()

    def _configure_campos_especificos_de_itens(self):
        """Configura campos específicos dos itens"""
        # Esconder todos os campos de itens primeiro
        item_widgets = [
            self.descricao_do_item_pagamento_label, self.descricao_do_item_pagamento_entry,
            self.motivo_label, self.motivo_entry,
            self.valor_caixa_itens_label, self.valor_caixa_itens_entry,
            self.saida_destino_label, self.saida_destino_entry,
        ]
        
        for widget in item_widgets:
            widget.grid_forget()
        
        # Limpar campos
        for entry in [self.descricao_do_item_pagamento_entry, self.motivo_entry, self.valor_caixa_itens_entry]:
            entry.delete(0, tk.END)

        tipo_servico = self.tipo_servico_combobox.get()

        if tipo_servico == "ADIANTAMENTO/PAGAMENTO PARCEIRO":
            self._configure_campos_parceiros()
        elif tipo_servico == "RELATÓRIO EXTRA":
            self._configure_relatorio_extra()
        else:
            self._configure_campos_padroes_itens()

    def _configure_campos_parceiros(self):
        """Configura campos para adiantamento de parceiro"""
        self.descricao_do_item_pagamento_label.grid(row=3, column=0, sticky="w", padx=(10, 10))
        self.descricao_do_item_pagamento_entry.grid(row=3, column=1, sticky="ew", padx=(0, 10), pady=2)
        # root.focus() - seria necessário ter acesso ao root
        
        self.competencia_label.grid(row=7, column=0, sticky="w", padx=(10, 10))
        self.competencia_combobox.grid(row=7, column=1, sticky="ew", padx=(0, 10), pady=2)

    def _configure_relatorio_extra(self):
        """Configura campos para relatório extra"""
        self.descricao_do_item_pagamento_label.grid(row=3, column=0, sticky="w", padx=(10, 10))
        self.descricao_do_item_pagamento_entry.grid(row=3, column=1, sticky="ew", padx=(0, 10), pady=2)
        self.descricao_do_item_pagamento_entry.configure(placeholder_text="PREFIXO - AGÊNCIA - OS - VALOR")

    def _configure_campos_padroes_itens(self):
        """Configura campos padrão para itens"""
        # Esconder campo valor principal
        tipo_servico = self.tipo_servico_combobox.get()
        
        self.valor_label.grid_forget()
        self.valor_entry.grid_forget()

        if tipo_servico == "REEMBOLSO UBER":
            self.saida_destino_label.grid(row=3, column=0, sticky="w", padx=(10, 10))
            self.saida_destino_entry.grid(row=3, column=1, sticky="ew", padx=(0, 10), pady=2)
            self.saida_destino_entry.configure(placeholder_text="Informe a saída e o destino")

        self.motivo_label.grid(row=4, column=0, sticky="w", padx=(10, 10))
        self.motivo_entry.grid(row=4, column=1, sticky="ew", padx=(0, 10), pady=2)
        self.motivo_entry.configure(placeholder_text="Informe o motivo")
        
        self.valor_caixa_itens_label.grid(row=5, column=0, sticky="w", padx=(10, 10))
        self.valor_caixa_itens_entry.grid(row=5, column=1, sticky="ew", padx=(0, 10), pady=2)
        self.valor_caixa_itens_entry.configure(placeholder_text="Informe o valor")

        self._configure_labels_dos_itens()

    def _configure_labels_dos_itens(self):
        """Configura textos dos labels dos itens"""
        # Resetar labels
        for label in [self.motivo_label, self.valor_caixa_itens_label]:
            label.configure(text="")

        tipo_servico = self.tipo_servico_combobox.get()

        if tipo_servico in {"REEMBOLSO SEM OS", "SOLICITAÇÃO SEM OS"}:
            self.motivo_label.configure(text="MOTIVO:\t\t      ")
            self.valor_caixa_itens_label.configure(text="VALOR:")
        elif tipo_servico in {"SOLICITAÇÃO COM OS", "REEMBOLSO COM OS"}:
            self.motivo_label.configure(text="MOTIVO:\t\t\t     ")
            self.valor_caixa_itens_label.configure(text="VALOR:")
        elif tipo_servico == "REEMBOLSO UBER":
            self.saida_destino_label.configure(text="SAÍDA X DESTINO:\t\t")
            self.motivo_label.configure(text="MOTIVO:\t\t\t     ")
            self.valor_caixa_itens_label.configure(text="VALOR:")

    def _configure_pref_age_os(self):
        """Configura campos de prefixo, agência e OS"""
        esconde_pref_age_os = {
            "REEMBOLSO SEM OS", "SOLICITAÇÃO SEM OS", "ABASTECIMENTO",
            "ENVIO DE MATERIAL", "AQUISIÇÃO SEM OS", "RELATÓRIO EXTRA",
            "ADIANTAMENTO/PAGAMENTO PARCEIRO", "COMPRA IN LOCO",
        }

        tipo_servico = self.tipo_servico_combobox.get()

        if tipo_servico in esconde_pref_age_os:
            self._esconde_pref_age_os()
        elif tipo_servico in {"REEMBOLSO UBER", "PREST. SERVIÇO/MÃO DE OBRA", 
                             "CARRETO", "TRANSPORTADORA"}:
            self._show_pref_age_os_opcionais()
        else:
            self._show_pref_age_os_obrigatorios()

    def _esconde_pref_age_os(self):
        """Esconde campos de prefixo, agência e OS"""        
        campos = [
            (self.prefixo_label, self.prefixo_entry),
            (self.agencia_label, self.agencia_entry),
            (self.os_label, self.os_entry)
        ]
        
        for label, entry in campos:
            label.grid_forget()
            entry.grid_forget()
            entry.delete(0, tk.END)  # Limpa o conteúdo do campo

    def _show_pref_age_os_opcionais(self):
        """Mostra campos opcionais de prefixo, agência e OS"""
        fields_config = [
            (self.prefixo_label, self.prefixo_entry, 5),
            (self.agencia_label, self.agencia_entry, 6),
            (self.os_label, self.os_entry, 7)
        ]
        
        for label, entry, row in fields_config:
            label.grid(row=row, column=0, sticky="w", padx=(10, 10))
            entry.configure(placeholder_text="Opcional")
            entry.grid(row=row, column=1, sticky="ew", padx=(0, 10), pady=2)

    def _show_pref_age_os_obrigatorios(self):
        """Mostra campos obrigatórios de prefixo, agência e OS"""
        fields_config = [
            (self.prefixo_label, self.prefixo_entry, 5),
            (self.agencia_label, self.agencia_entry, 6),
            (self.os_label, self.os_entry, 7)
        ]
        
        for label, entry, row in fields_config:
            label.grid(row=row, column=0, sticky="w", padx=(10, 10))
            entry.configure(placeholder_text="")
            entry.grid(row=row, column=1, sticky="ew", padx=(0, 10), pady=2)

    def _configure_opcoes_pagamento(self, tipo_servico: str):
        """Configura opções de pagamento baseado no tipo de serviço"""
        self.tipo_pagamento_combobox.set("")  # Limpar seleção
        
        if tipo_servico in {"PREST. SERVIÇO/MÃO DE OBRA", "ABASTECIMENTO", 
                           "ADIANTAMENTO/PAGAMENTO PARCEIRO"}:
            opcoes_pagamento = ["PIX"]
        elif tipo_servico in {"ORÇAMENTO APROVADO", "AQUISIÇÃO SEM OS", "AQUISIÇÃO COM OS",
                             "ENVIO DE MATERIAL", "TRANSPORTADORA"}:
            opcoes_pagamento = ["PIX", "VEXPENSES", "FATURAMENTO"]
        else:
            opcoes_pagamento = ["PIX", "VEXPENSES"]

        self.tipo_pagamento_combobox.configure(values=opcoes_pagamento)

    def _configure_visibilidade_contrato(self, tipo_servico: str):
        """Configura visibilidade do campo contrato"""
        if tipo_servico == "ENVIO DE MATERIAL":
            self.contrato_label.grid_forget()
            self.contrato_combobox.grid_forget()
        else:
            self.contrato_label.grid(row=3, column=0, sticky="w", padx=(10, 10))
            self.contrato_combobox.grid(row=3, column=1, sticky="ew", padx=(0, 10), pady=2)

    def _configure_campos_aquisicao(self, tipo_servico: str):
        """Configura campos de aquisição baseado no tipo de serviço"""
        acquisition_configs = {
            "AQUISIÇÃO COM OS": ["CORRETIVA DIÁRIA", "LOCAÇÃO"],
            "AQUISIÇÃO SEM OS": ["EPI", "CRACHÁ", "FERRAMENTAS", "FARDAMENTO", "ESTOQUE", "UTILIDADES"],
            "COMPRA IN LOCO": ["CORRETIVA DIÁRIA", "SEM OS", "ORÇAMENTO APROVADO"]
        }
        
        if tipo_servico in acquisition_configs:
            self.tipo_aquisicao_combobox.configure(values=acquisition_configs[tipo_servico])
            self.tipo_aquisicao_combobox.set("")
            self.tipo_aquisicao_label.grid(row=2, column=0, sticky="w", padx=(10, 10))
            self.tipo_aquisicao_combobox.grid(row=2, column=1, sticky="ew", padx=(0, 10), pady=2)
        else:
            self.tipo_aquisicao_label.grid_forget()
            self.tipo_aquisicao_combobox.grid_forget()

    def _atualizar_exibicao_frame_caixa_itens(self):
        """Atualiza exibição do frame de itens para ADIANTAMENTO/PAGAMENTO PARCEIRO"""
        tipo_servico = self.tipo_servico_combobox.get()
        possui_os = self.opcao_os_parceiro_combobox.get()

        if tipo_servico == "ADIANTAMENTO/PAGAMENTO PARCEIRO":
            if possui_os in {"SIM", "NÃO"}:
                self.frame_caixa_itens_pagamento.grid(row=6, column=0, columnspan=2, sticky="nsew", pady=5)
                self.focus_set()  # Foca no frame principal da aba
            else:
                self.frame_caixa_itens_pagamento.grid_forget()

            # Atualizar o placeholder do campo de descrição
            if possui_os == "SIM":
                self.descricao_do_item_pagamento_entry.configure(placeholder_text="OS - PREFIXO - AGÊNCIA - PORCENTAGEM")
            else:
                self.descricao_do_item_pagamento_entry.configure(placeholder_text="MOTIVO - PORCENTAGEM")

            # Limpa e atualiza a lista de itens
            if hasattr(self, 'itens_pagamento'):
                self.itens_pagamento.clear()
                if hasattr(self, '_atualizar_lista_itens_pagamento'):
                    self._atualizar_lista_itens_pagamento()
    
    def _add_item_pagamento(self):
        """Adiciona um item de pagamento"""
        global descricao_base
        
        tipo_servico = self.tipo_servico_combobox.get()

        if tipo_servico in {"ADIANTAMENTO/PAGAMENTO PARCEIRO", "RELATÓRIO EXTRA"}:
            entrada = arrumar_texto(self.descricao_do_item_pagamento_entry.get().upper().strip())
            possui_os = self.opcao_os_parceiro_combobox.get()

            descricao_formatada, descricao_base, erro = validar_item_pagamento(entrada, tipo_servico, possui_os)

            if erro:
                self.notificacao.show_notification(
                    f"Campo DESCRIÇÃO DO ITEM\n{erro}",
                    NotifyType.ERROR,
                    bg_color="#404040",
                    text_color="#FFFFFF"
                )
                return

            item = {
                "descricao": descricao_formatada,
                "descricao_base": descricao_base
            }
        elif tipo_servico == "REEMBOLSO UBER":
            saida_e_destino = arrumar_texto(self.saida_destino_entry.get().upper().strip())
            motivo = arrumar_texto(self.motivo_entry.get().upper().strip())
            valor = verificar_se_numero(self.valor_caixa_itens_entry.get())

            # Verificações de campos obrigatórios
            if not motivo and not valor and not saida_e_destino:
                erro = "Campos DESCRIÇÃO DO ITEM, MOTIVO e SAÍDA/DESTINO não podem ser vazios!"
            elif not motivo and not saida_e_destino:
                erro = "Campos MOTIVO e SAÍDA/DESTINO não podem ser vazios!"
            elif not motivo and not valor:
                erro = "Campos DESCRIÇÃO DO ITEM e MOTIVO não podem ser vazios!"
            elif not saida_e_destino and not valor:
                erro = "Campos DESCRIÇÃO DO ITEM e SAÍDA/DESTINO não podem ser vazios!"
            elif not motivo:
                erro = "Campo MOTIVO não pode ser vazio!"
            elif not valor:
                erro = "Campo VALOR não pode ser vazio!"
            elif not saida_e_destino:
                erro = "Campo SAÍDA/DESTINO não pode ser vazio!"
            elif valor is ValueError:
                erro = "Campo VALOR\nPor favor, insira um número válido!"
            else:
                erro = None

            if erro:
                self.notificacao.show_notification(
                    erro,
                    NotifyType.ERROR,
                    bg_color="#404040",
                    text_color="#FFFFFF"
                )
                return

            item = {
                "saida_e_destino": saida_e_destino,
                "motivo": motivo,
                "valor": valor,
                "descricao": f"{saida_e_destino} - {motivo} - R$ {valor}"
            }
        else:
            motivo = arrumar_texto(self.motivo_entry.get().upper().strip())
            valor = verificar_se_numero(self.valor_caixa_itens_entry.get())

            if not motivo and not valor:
                erro = "Campos DESCRIÇÃO DO ITEM e MOTIVO não podem ser vazios!"
            elif not motivo:
                erro = "Campo MOTIVO não pode ser vazio!"
            elif not valor:
                erro = "Campo VALOR não pode ser vazio!"
            elif valor is ValueError:
                erro = "Campo VALOR\nPor favor, insira um número válido!"
            else:
                erro = None

            if erro:
                self.notificacao.show_notification(
                    erro,
                    NotifyType.ERROR,
                    bg_color="#404040",
                    text_color="#FFFFFF"
                )
                return

            item = {
                "motivo": motivo,
                "valor": valor,
                "descricao": f"{motivo} - R$ {valor}"
            }

        # Garante que a lista de itens exista na instância
        if not hasattr(self, "itens_pagamento"):
            self.itens_pagamento = []

        self.itens_pagamento.append(item)

        if tipo_servico in {"ADIANTAMENTO/PAGAMENTO PARCEIRO", "RELATÓRIO EXTRA"}:
            self.descricao_do_item_pagamento_entry.delete(0, tk.END)
            self.descricao_do_item_pagamento_entry.focus()

        if tipo_servico not in {"ADIANTAMENTO/PAGAMENTO PARCEIRO", "RELATÓRIO EXTRA"}:
            self.motivo_entry.delete(0, tk.END)
            self.valor_caixa_itens_entry.delete(0, tk.END)

            if tipo_servico == "REEMBOLSO UBER":
                self.saida_destino_entry.delete(0, tk.END)
                self.saida_destino_entry.focus()
            else:
                self.motivo_entry.focus()

        if hasattr(self, "_atualizar_lista_itens_pagamento"):
            self._atualizar_lista_itens_pagamento()

    def _atualizar_lista_itens_pagamento(self):
        for widget in self.frame_lista_itens_pagamento.winfo_children():
            widget.destroy()

        if len(self.itens_pagamento) > 0:
            self.frame_lista_itens_pagamento.grid(row=11, column=0, columnspan=2, sticky="ew", padx=(10, 10), pady=(0, 10))
        else:
            self.frame_lista_itens_pagamento.grid_forget()

        for index, item in enumerate(self.itens_pagamento):
            self.row_frame_pagamento = ctk.CTkFrame(self.frame_lista_itens_pagamento, width=400)
            self.row_frame_pagamento.grid(row=index, column=0, columnspan=2, sticky="ew", padx=(10, 10), pady=5)

            self.label_itens_gerados_pagamento = ctk.CTkLabel(
                self.row_frame_pagamento,
                text=item["descricao"],
                anchor="w", justify="left", wraplength=340
            )
            self.label_itens_gerados_pagamento.grid(row=0, column=0, padx=2)

            self.btn_editar_item_pagamento = ctk.CTkButton(
                self.row_frame_pagamento, text="Editar", width=30, 
                command=lambda i=index: self._editar_item_pagamento(i)
            )
            self.btn_editar_item_pagamento.grid(row=0, column=1, padx=2)

            self.btn_excluir_item_pagamento = ctk.CTkButton(
                self.row_frame_pagamento, text="❌", width=30, 
                fg_color="red", hover_color="darkred", 
                command=lambda i=index: self._remover_item_pagamento(i)
            )
            self.btn_excluir_item_pagamento.grid(row=0, column=2, padx=2)

    def _editar_item_pagamento(self, index: int):
        self.editando_item_pagamento = index

        item = self.itens_pagamento[index]
        descricao_nova = item["descricao"]

        tipo_servico = self.tipo_servico_combobox.get()

        if tipo_servico in {"ADIANTAMENTO/PAGAMENTO PARCEIRO", "RELATÓRIO EXTRA"}:
            if tipo_servico == "ADIANTAMENTO/PAGAMENTO PARCEIRO":  # para remover o texto "ADIANTAMENTO DE"
                descricao_nova = descricao_nova.replace("ADIANTAMENTO DE ", "").strip()
            
            self.descricao_do_item_pagamento_entry.delete(0, tk.END)
            self.descricao_do_item_pagamento_entry.insert(0, descricao_nova)
            
            self.descricao_do_item_pagamento_entry.focus()
        elif tipo_servico == "REEMBOLSO UBER":
            self.saida_destino_entry.delete(0, tk.END)
            self.saida_destino_entry.insert(0, item.get("saida_e_destino", ""))

            self.motivo_entry.delete(0, tk.END)
            self.motivo_entry.insert(0, item.get("motivo", ""))

            self.valor_caixa_itens_entry.delete(0, tk.END)
            self.valor_caixa_itens_entry.insert(0, str(item.get("valor", "")))

            self.saida_destino_entry.focus()
        else:
            self.motivo_entry.delete(0, tk.END)
            self.motivo_entry.insert(0, item.get("motivo", ""))

            self.valor_caixa_itens_entry.delete(0, tk.END)
            self.valor_caixa_itens_entry.insert(0, str(item.get("valor", "")))

            self.motivo_entry.focus()

        self.btn_adicionar_servico_pagamento.configure(text="Salvar", command=lambda: self._salvar_edicao_pagamento(index))

        self._atualizar_lista_itens_pagamento()

    def _salvar_edicao_pagamento(self, index: int):
        global descricao_base

        tipo_servico = self.tipo_servico_combobox.get()

        if tipo_servico in {"ADIANTAMENTO/PAGAMENTO PARCEIRO", "RELATÓRIO EXTRA"}:
            entrada = arrumar_texto(self.descricao_do_item_pagamento_entry.get().upper().strip())
            possui_os = self.opcao_os_parceiro_combobox.get()

            descricao_formatada, descricao_base, erro = validar_item_pagamento(entrada, tipo_servico, possui_os)

            if erro:
                self.notificacao.show_notification(f"Campo DESCRIÇÃO DO ITEM\n{erro}", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
                return
            
            item_editado = {
                "descricao": descricao_formatada,
                "descricao_base": descricao_base
            }

        elif tipo_servico == "REEMBOLSO UBER":
            saida_e_destino = arrumar_texto(self.saida_destino_entry.get().upper().strip())
            motivo = arrumar_texto(self.motivo_entry.get().upper().strip())
            valor = verificar_se_numero(self.valor_caixa_itens_entry.get())

            # Verificações de campos obrigatórios
            if not motivo and not valor and not saida_e_destino:
                erro = "Campos DESCRIÇÃO DO ITEM, MOTIVO e SAÍDA/DESTINO não podem ser vazios!"
            elif not motivo and not saida_e_destino:
                erro = "Campos MOTIVO e SAÍDA/DESTINO não podem ser vazios!"
            elif not motivo and not valor:
                erro = "Campos DESCRIÇÃO DO ITEM e MOTIVO não podem ser vazios!"
            elif not saida_e_destino and not valor:
                erro = "Campos DESCRIÇÃO DO ITEM e SAÍDA/DESTINO não podem ser vazios!"
            elif not motivo:
                erro = "Campo MOTIVO não pode ser vazio!"
            elif not valor:
                erro = "Campo VALOR não pode ser vazio!"
            elif not saida_e_destino:
                erro = "Campo SAÍDA/DESTINO não pode ser vazio!"
            elif valor is ValueError:
                erro = "Campo VALOR\nPor favor, insira um número válido!"
            else:
                erro = None

            # Exibição de erro, se houver
            if erro:
                self.notificacao.show_notification(
                    erro, 
                    NotifyType.ERROR,
                    bg_color="#404040", 
                    text_color="#FFFFFF"
                )
                return

            # Adiciona dicionário com dados completos
            item_editado = {
                "saida_e_destino": saida_e_destino,
                "motivo": motivo,
                "valor": valor,
                "descricao": f"{saida_e_destino} - {motivo} - R$ {valor}"
            }
        else:
            motivo = arrumar_texto(motivo_entry.get().upper().strip())
            valor = verificar_se_numero(valor_caixa_itens_entry.get())

            # Verificações de campos obrigatórios
            if not motivo and not valor:
                erro = "Campos DESCRIÇÃO DO ITEM e MOTIVO não podem ser vazios!"
            elif not motivo:
                erro = "Campo MOTIVO não pode ser vazio!"
            elif not valor:
                erro = "Campo VALOR não pode ser vazio!"
            elif valor is ValueError:
                erro = "Campo VALOR\nPor favor, insira um número válido!"
            else:
                erro = None

            # Exibição de erro, se houver
            if erro:
                self.notificacao.show_notification(
                    erro, 
                    NotifyType.ERROR, 
                    bg_color="#404040", 
                    text_color="#FFFFFF"
                )
                return

            # Adiciona dicionário com dados completos
            item_editado = {
                "motivo": motivo,
                "valor": valor,
                "descricao": f"{motivo} - R$ {valor}"
            } 

        self.itens_pagamento[index] = item_editado

        if tipo_servico in {"ADIANTAMENTO/PAGAMENTO PARCEIRO", "RELATÓRIO EXTRA"}:
            self.descricao_do_item_pagamento_entry.delete(0, tk.END)

        if tipo_servico not in {"ADIANTAMENTO/PAGAMENTO PARCEIRO", "RELATÓRIO EXTRA"}:
            if tipo_servico == "REEMBOLSO UBER":
                self.saida_destino_entry.delete(0, tk.END)
            self.valor_caixa_itens_entry.delete(0, tk.END)
            self.motivo_entry.delete(0, tk.END)

        self.btn_adicionar_servico_pagamento.configure(text="Adicionar", command=self._add_item_pagamento)

        self.editando_item_pagamento = None  # Reabilita o botão de excluir

        self.descricao_do_item_pagamento_entry.focus()

        self._atualizar_lista_itens_pagamento()

    def _remover_item_pagamento(self, index: int):
        if self.editando_item_pagamento is None:  # Só permite excluir se não estiver editando
            del self.itens_pagamento[index]
            self._atualizar_lista_itens_pagamento()
        else:
            self.notificacao.show_notification("Item em edição!\nSalve-o para habilitar a exclusão.", NotifyType.WARNING, bg_color="#404040", text_color="#FFFFFF")
            pass

    def _campo_descricao_utilidades(self, choice: str = None):
        """Gerencia campo de descrição de utilidades"""
        tipo_servico = self.tipo_servico_combobox.get()
        tipo_aquisicao = self.tipo_aquisicao_combobox.get()

        if tipo_aquisicao == "UTILIDADES":
            self.descricao_utilidades_label.grid(row=4, column=0, sticky="w", padx=(10, 10))
            self.descricao_utilidades_entry.grid(row=4, column=1, sticky="ew", padx=(0, 10), pady=2)
        else:
            self.descricao_utilidades_label.grid_forget()
            self.descricao_utilidades_entry.grid_forget()
            self.descricao_utilidades_entry.delete(0, tk.END)

        if tipo_servico == "AQUISIÇÃO SEM OS":
            self._esconde_pref_age_os()
        else:
            self._show_pref_age_os_obrigatorios()    

    def _restaurar_valores_tipo_aquisicao(self, event):
        """Restaura valores do tipo de aquisição"""
        # Implementar lógica específica
        pass
    
    def _adiciona_campo_pix(self, choice: str):
        """Adiciona campos PIX quando necessário"""
        tipo_pagamento = self.tipo_pagamento_combobox.get()

        # Mostrar ou esconder campos para PIX
        if tipo_pagamento == 'PIX':
            self.tipo_chave_pix_label.grid(row=13, column=0, sticky="w", padx=(10, 10))
            self.tipo_chave_pix_combobox.grid(row=13, column=1, sticky="ew", padx=(0, 10), pady=2)
            self.chave_pix_label.grid(row=14, column=0, sticky="w", padx=(10, 10))
            self.chave_pix_entry.grid(row=14, column=1, sticky="ew", padx=(0, 10), pady=2)
            self.nome_benef_pix_label.grid(row=15, column=0, sticky="w", padx=(10, 10))
            self.nome_benef_pix_entry.grid(row=15, column=1, sticky="ew", padx=(0, 10), pady=2)
        else:
            self.tipo_chave_pix_label.grid_forget()
            self.tipo_chave_pix_combobox.grid_forget()
            self.tipo_chave_pix_combobox.set("")
            self.chave_pix_label.grid_forget()
            self.chave_pix_entry.grid_forget()
            self.chave_pix_entry.delete(0, tk.END)
            self.nome_benef_pix_label.grid_forget()
            self.nome_benef_pix_entry.grid_forget()
            self.nome_benef_pix_entry.delete(0, tk.END)

    def _esconde_campos_pagamento_qrcode(self, choice: str):
        """Esconde campos específicos para QR Code"""
        tipo_chave = self.tipo_chave_pix_combobox.get()

        if tipo_chave == "QR CODE":
            self.chave_pix_label.grid_forget()
            self.chave_pix_entry.grid_forget()
            self.nome_benef_pix_label.grid_forget()
            self.nome_benef_pix_entry.grid_forget()

            self.chave_pix_entry.delete(0, tk.END)
            self.nome_benef_pix_entry.delete(0, tk.END)
        else:
            self.chave_pix_label.grid(row=14, column=0, sticky="w", padx=(10, 10))
            self.chave_pix_entry.grid(row=14, column=1, sticky="ew", padx=(0, 10), pady=2)
            self.nome_benef_pix_label.grid(row=15, column=0, sticky="w", padx=(10, 10))
            self.nome_benef_pix_entry.grid(row=15, column=1, sticky="ew", padx=(0, 10), pady=2)
    
    def _gerar_solicitacao(self):
        """Gera a solicitação de pagamento"""
        tipo_servico = self.tipo_servico_combobox.get()

        nome_usuario = arrumar_texto(self.nome_usuario_entry.get().upper())
        tipo_servico = arrumar_texto(self.tipo_servico_combobox.get().upper())
        nome_fornecedor = arrumar_texto(self.nome_fornecedor_entry.get().upper())
        prefixo = valida_prefixo(self.prefixo_entry.get())
        agencia = arrumar_texto(self.agencia_entry.get().upper())
        os_num = valida_os(self.os_entry.get())
        
        if tipo_servico == "ENVIO DE MATERIAL":
            contrato = "ESCRITÓRIO"
        else:
            contrato = arrumar_texto(self.contrato_combobox.get().upper())

        motivo = arrumar_texto(self.motivo_entry.get().upper())
        
        if tipo_servico in {
            "REEMBOLSO SEM OS", "SOLICITAÇÃO SEM OS",
            "SOLICITAÇÃO COM OS", "REEMBOLSO COM OS",
            "REEMBOLSO UBER",
        }:
            total_valor = sum(float(str(item.get("valor", 0)).replace(".", "").replace(",", ".")) for item in self.itens_pagamento)
            valor_tab1 = verificar_se_numero(str(total_valor).replace(".", ","))
        else:
            valor_tab1 = verificar_se_numero(self.valor_entry.get())

        tecnicos = arrumar_texto(self.tecnicos_entry.get().upper())
        competencia = arrumar_texto(self.competencia_combobox.get().upper())
        porcentagem = valida_porcentagem(self.porcentagem_entry.get().upper())
        tipo_aquisicao = arrumar_texto(self.tipo_aquisicao_combobox.get().upper())
        descricao_utilidades = arrumar_texto(self.descricao_utilidades_entry.get().upper())

        tipo_pagamento = arrumar_texto(self.tipo_pagamento_combobox.get().upper())
        if tipo_pagamento == "PIX":
            tipo_chave_pix = arrumar_texto(self.tipo_chave_pix_combobox.get())
            chave_pix = arrumar_texto(self.chave_pix_entry.get())
            nome_benef_pix = arrumar_texto(self.nome_benef_pix_entry.get().upper())

        departamento, sigla_contrato = acessa_bd_contratos(contrato)
        print(f"Departamento: {departamento}, Sigla: {sigla_contrato}")

        # Verificar se algum campo obrigatório está vazio
        campos_obrigatorios = [
            (nome_usuario, "USUÁRIO"),
            (tipo_servico, "TIPO DE SERVIÇO"),
            (nome_fornecedor, "NOME DO FORNECEDOR/BENEFICIÁRIO"),
            (contrato, "CONTRATO"),
            (valor_tab1, "VALOR"),
            (tipo_pagamento, "TIPO DE PAGAMENTO")
        ]

        if tipo_servico == "ABASTECIMENTO":
            campos_obrigatorios.append((tecnicos, "TÉCNICOS"))
        elif tipo_servico == "PREST. SERVIÇO/MÃO DE OBRA":
            campos_obrigatorios.extend([
                (competencia, "COMPETÊNCIA"),
                (porcentagem, "% DO ADIANTAMENTO DO PARCEIRO")
            ])
        elif tipo_servico in {"AQUISIÇÃO COM OS", "COMPRA IN LOCO"}:
            if tipo_servico == "AQUISIÇÃO COM OS":
                campos_obrigatorios.extend([
                    (tipo_aquisicao, "TIPO DE AQUISIÇÃO"),
                    (prefixo, "PREFIXO"),
                    (agencia, "AGÊNCIA"),
                    (os_num, "OS")
                ])
            else:
                campos_obrigatorios.append((tipo_aquisicao, "TIPO DE AQUISIÇÃO"))
                if tipo_aquisicao != "SEM OS":
                    campos_obrigatorios.extend([
                        (prefixo, "PREFIXO"),
                        (agencia, "AGÊNCIA"),
                        (os_num, "OS")
                    ])
        elif tipo_servico == "AQUISIÇÃO SEM OS":
            campos_obrigatorios.append((tipo_aquisicao, "TIPO DE AQUISIÇÃO"))
            if tipo_aquisicao == "UTILIDADES":
                campos_obrigatorios.append((descricao_utilidades, "DESCRIÇÃO UTILIDADES"))
        elif tipo_servico == "ENVIO DE MATERIAL":
            campos_obrigatorios.remove((contrato, "CONTRATO"))
        elif tipo_servico in {"ESTACIONAMENTO/PEDÁGIO", "HOSPEDAGEM"}:
            campos_obrigatorios.extend([
                (tecnicos, "TÉCNICOS"),
                (prefixo, "PREFIXO"),
                (agencia, "AGÊNCIA"),
                (os_num, "OS")
            ])        
        elif tipo_servico in {"ORÇAMENTO APROVADO"}:
            campos_obrigatorios.extend([
                (prefixo, "PREFIXO"),
                (agencia, "AGÊNCIA"),
                (os_num, "OS")
            ])
        elif tipo_servico in self.aparece_lista_itens_aba_pagamentos:
            campos_obrigatorios.append((self.itens_pagamento if self.itens_pagamento else None, "DESCRIÇÃO DO ITEM"))
            
            if tipo_servico == "ADIANTAMENTO/PAGAMENTO PARCEIRO":
                campos_obrigatorios.append((competencia, "COMPETÊNCIA"))

            if tipo_servico in {
                "REEMBOLSO SEM OS", "SOLICITAÇÃO SEM OS",
                "SOLICITAÇÃO COM OS", "REEMBOLSO COM OS",
                "REEMBOLSO UBER"
            }:
                campos_obrigatorios = [campo for campo in campos_obrigatorios if campo != (valor_tab1, "VALOR")]

            if tipo_servico in {"REEMBOLSO COM OS", "SOLICITAÇÃO COM OS"}:
                campos_obrigatorios.extend([
                    (prefixo, "PREFIXO"),
                    (agencia, "AGÊNCIA"),
                    (os_num, "OS")
                ])
            
            if tipo_servico in {"SOLICITAÇÃO SEM OS", "SOLICITAÇÃO COM OS"}:
                campos_obrigatorios.append((tecnicos, "TÉCNICOS"))

        if tipo_pagamento == "PIX" and tipo_chave_pix != "QR CODE":
            campos_obrigatorios.extend([
                (tipo_chave_pix, "TIPO DA CHAVE PIX"),
                (chave_pix, "CHAVE PIX")
            ])

        if contrato in {"ESCRITÓRIO", "ATA BB CURITIBA", "CAIXA BAHIA", "CAIXA CURITIBA", "CAIXA MANAUS", "INFRA CURITIBA"}:
            campos_obrigatorios = [
                item for item in campos_obrigatorios
                if item not in [(prefixo, "PREFIXO"), (agencia, "AGÊNCIA"), (os_num, "OS")]
            ]

        # Verificar campos vazios
        campos_vazios = [nome for valor, nome in campos_obrigatorios if not valor]

        if campos_vazios:
            if campos_vazios == ["DESCRIÇÃO DO ITEM"]:
                self.notificacao.show_notification("Campo DESCRIÇÃO DO ITEM\nPor favor, adicione um item à lista.", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
                return
            else:
                self.notificacao.show_notification("Preencha os campos em branco!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
                return

        if prefixo == "Prefixo inválido":
            self.notificacao.show_notification("Campo PREFIXO\nPrefixo inválido. Use o padrão XXXX/XX.", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
            return     

        if os_num == "OS_invalida":
            self.notificacao.show_notification("Campo OS\nPor favor, insira uma OS válida!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
            return
        
        if valor_tab1 is ValueError:
            self.notificacao.show_notification("Campo VALOR\nPor favor, insira um número válido!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
            return
        
        if porcentagem == ValueError:
            self.notificacao.show_notification("Campo PORCENTAGEM\nPor favor, insira um número válido!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
            return
        elif porcentagem == "RangeError":
            self.notificacao.show_notification("Campo PORCENTAGEM\nPor favor, insira um número entre 1 e 100.", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
            return
            
        if self.identifica_preenchimento_pref_os_age(prefixo, agencia, os_num):
            return

        # Definindo o nome do arquivo
        data_atual = datetime.now().strftime("%d.%m.%Y")
        
        if os_num == "":
            nome_arquivo = f"{valor_tab1} - {data_atual} - OC {nome_fornecedor} - {tipo_servico} - {sigla_contrato}.xlsx"
        else:
            nome_arquivo = f"{valor_tab1} - {data_atual} - OC {nome_fornecedor} - {os_num} - {agencia} - {prefixo} - {tipo_servico} - {sigla_contrato}.xlsx"    
        
        nome_arquivo = re.sub(r'[<>:"/\\|?*\x00]', ".", nome_arquivo)

        nome_arquivo_sem_ext, ext = splitext(nome_arquivo)

        # Gerar texto da solicitação
        if tipo_servico == "PREST. SERVIÇO/MÃO DE OBRA":
            texto = (
                f"Solicito o pagamento para {nome_fornecedor}, referente à obra: "
                f"{prefixo} - {agencia} - {os_num}, para {contrato}.\n\n"
                if prefixo
                else
                f"Solicito o pagamento para {nome_fornecedor}, para {contrato}.\n\n"
            )
            texto += f"SERVIÇO: {tipo_servico}\n\n"
            texto += f"COMPETÊNCIA: {competencia}\n\n"
            texto += f"PORCENTAGEM DO ADIANTAMENTO: {porcentagem}%\n\n"
            texto += f"VALOR: R$ {valor_tab1}\n\n"
        elif tipo_servico == "AQUISIÇÃO COM OS":
            texto = (
                f"Solicito o pagamento para {nome_fornecedor}, referente à obra: "
                f"{prefixo} - {agencia} - {os_num}, para {contrato}.\n\n"
            )
            texto += f"SERVIÇO: {tipo_servico} - {tipo_aquisicao}\n\n"
            texto += f"VALOR: R$ {valor_tab1}\n\n"

        elif tipo_servico == "COMPRA IN LOCO":
            if tipo_aquisicao != "SEM OS":
                texto = (
                    f"Solicito o pagamento para {nome_fornecedor}, referente à obra: "
                    f"{prefixo} - {agencia} - {os_num}, para {contrato}.\n\n"
                )
                texto += f"SERVIÇO: {tipo_servico} - {tipo_aquisicao}\n\n"
                texto += f"VALOR: R$ {valor_tab1}\n\n"
            else:
                texto = (
                    f"Solicito o pagamento para {nome_fornecedor}, para {contrato}.\n\n"
                )
                texto += f"SERVIÇO: {tipo_servico} - {tipo_aquisicao}\n\n"
                texto += f"VALOR: R$ {valor_tab1}\n\n"

        elif tipo_servico == "AQUISIÇÃO SEM OS":
            texto = f"Solicito o pagamento para {nome_fornecedor}, para {contrato}.\n\n"
            
            if descricao_utilidades:
                texto += f"SERVIÇO: {tipo_servico} - {tipo_aquisicao}: {descricao_utilidades}\n\n"
            else:
                texto += f"SERVIÇO: {tipo_servico} - {tipo_aquisicao}\n\n"

            texto += f"VALOR: R$ {valor_tab1}\n\n"
        
        elif tipo_servico in {"REEMBOLSO COM OS", "SOLICITAÇÃO COM OS"}:
            texto = (
                f"Solicito o pagamento para {nome_fornecedor}, referente à obra: "
                f"{prefixo} - {agencia} - {os_num}, para {contrato}.\n\n"
            )
            texto += f"SERVIÇO: {tipo_servico}\n\n"

            if tecnicos:
                texto += f"TÉCNICOS: {tecnicos}\n\n"

            if len(self.itens_pagamento) == 1:
                item = self.itens_pagamento[0]
                texto += f"MOTIVO: {item['motivo']}\n\n"
                texto += f"*VALOR: R$ {valor_tab1}*\n\n"
            else:
                texto += "MOTIVOS:\n"
                for idx, item in enumerate(self.itens_pagamento, start=1):
                    texto += f"{idx}. {item['motivo']} (R$ {item['valor']})\n"
                texto += f"\n*VALOR TOTAL: R$ {valor_tab1}*\n\n"
        
        elif tipo_servico in {"REEMBOLSO SEM OS", "SOLICITAÇÃO SEM OS"}:
            texto = f"Solicito o pagamento para {nome_fornecedor}, para {contrato}.\n\n"
            texto += f"SERVIÇO: {tipo_servico}\n\n"

            if tecnicos:
                texto += f"TÉCNICOS: {tecnicos}\n\n"

            if len(self.itens_pagamento) == 1:
                item = self.itens_pagamento[0]
                texto += f"MOTIVO: {item['motivo']}\n\n"
                texto += f"*VALOR: R$ {valor_tab1}*\n\n"
            else:
                texto += "MOTIVOS:\n"
                for idx, item in enumerate(self.itens_pagamento, start=1):
                    texto += f"{idx}. {item['motivo']} (R$ {item['valor']})\n"
                texto += f"\n*VALOR TOTAL: R$ {valor_tab1}*\n\n"
        
        elif tipo_servico == "ABASTECIMENTO":
            texto = (
                f"Solicito o pagamento ao fornecedor {nome_fornecedor}, referente ao "
                f"abastecimento dos técnicos {tecnicos}, para {contrato}.\n\n"
            )
            texto += f"SERVIÇO: {tipo_servico}\n\n"
            texto += f"VALOR: R$ {valor_tab1}\n\n"
        
        elif tipo_servico == "ESTACIONAMENTO/PEDÁGIO":
            texto = (
                f"Solicito o pagamento ao fornecedor {nome_fornecedor}, pelo estacionamento/pedágio "
                f"dos técnicos {tecnicos}, referente à obra: {prefixo} - {agencia} - {os_num}, "
                f"para {contrato}.\n\n"
            )
            texto += f"SERVIÇO: {tipo_servico}\n\n"
            texto += f"VALOR: R$ {valor_tab1}\n\n"
        
        elif tipo_servico == "REEMBOLSO UBER":
            if len(self.itens_pagamento) == 1:
                item = self.itens_pagamento[0]
                texto = (
                    f"Solicito reembolso referente ao deslocamento de {nome_fornecedor}, para {item['saida_e_destino']}, "
                    f"referente à obra: {prefixo} - {agencia} - {os_num}, para {contrato}.\n\n"
                    if prefixo
                    else f"Solicito reembolso referente ao deslocamento de {nome_fornecedor}, para {item['saida_e_destino']}, "
                    f"para {contrato}.\n\n"
                )
                texto += f"SERVIÇO: {tipo_servico}\n\n"
                texto += f"MOTIVO: {item['motivo']}\n\n"
                texto += f"*VALOR: R$ {valor_tab1}*\n\n"
            else:
                texto = (
                    f"Solicito reembolso referente ao deslocamento de {nome_fornecedor} "
                    f"referente à obra: {prefixo} - {agencia} - {os_num}, para {contrato}.\n\n"
                    if prefixo
                    else f"Solicito reembolso referente ao deslocamento de {nome_fornecedor} para {contrato}.\n\n"
                )
                texto += f"SERVIÇO: {tipo_servico}\n\n"
                texto += "DESLOCAMENTOS:\n"
                for idx, item in enumerate(self.itens_pagamento, start=1):
                    texto += f"{idx}. {item['saida_e_destino']} - {item['motivo']} (R$ {item['valor']})\n"
                texto += f"\n*VALOR TOTAL: R$ {valor_tab1}*\n\n"
        
        elif tipo_servico == "HOSPEDAGEM":
            texto = (
                f"Solicito o pagamento ao fornecedor {nome_fornecedor} pela hospedagem dos "
                f"técnicos {tecnicos} referente à obra: {prefixo} - {agencia} - {os_num}, "
                f"para {contrato}.\n\n"
            )
            texto += f"SERVIÇO: {tipo_servico}\n\n"
            texto += f"VALOR: R$ {valor_tab1}\n\n"
        
        elif tipo_servico == "ENVIO DE MATERIAL":
            texto = f"Solicito o pagamento ao fornecedor {nome_fornecedor}.\n\n"
            texto += f"SERVIÇO: {tipo_servico}\n\n"
            texto += f"VALOR: R$ {valor_tab1}\n\n"
        
        elif tipo_servico == "RELATÓRIO EXTRA":
            texto = f"Solicito o pagamento ao fornecedor {nome_fornecedor} pela confecção de relatório(s) técnico(s) relacionado(s) abaixo, para o {contrato}:\n\n"
            texto += f"SERVIÇO: CONFECÇÃO DE {tipo_servico}\n\n"

            for item in self.itens_pagamento:
                texto += f"{item["descricao"]}\n"

            texto += "\n"
            texto += f"VALOR: R$ {valor_tab1}\n\n"
        
        elif tipo_servico == "ADIANTAMENTO/PAGAMENTO PARCEIRO":
            if self.opcao_os_parceiro_combobox.get() == "SIM":
                if len(self.itens_pagamento) == 1:
                    texto = (
                        f"Solicito o pagamento para {nome_fornecedor}, referente à obra listada abaixo, para {contrato}:\n\n"
                    )
                else:
                    texto = (
                        f"Solicito o pagamento para {nome_fornecedor}, referente as obras listadas abaixo, para {contrato}:\n\n"
                    )
                texto += f"SERVIÇO: {tipo_servico}\n\n"
                texto += f"COMPETÊNCIA: {competencia}\n\n"
                
                for item in self.itens_pagamento:
                    texto += f"{item["descricao"]}\n"
                
                texto += f"\nVALOR: R$ {valor_tab1}\n\n"
            else:
                texto = (
                    f"Solicito o pagamento para {nome_fornecedor}, referente ao listado abaixo, para {contrato}:\n\n"
                )
                texto += f"SERVIÇO: {tipo_servico}\n\n"
                texto += f"COMPETÊNCIA: {competencia}\n\n"

                for item in self.itens_pagamento:
                    texto += f"{item["descricao"]}\n"

                texto += f"\nVALOR: R$ {valor_tab1}\n\n"
        
        elif contrato == "ESCRITÓRIO" and tipo_aquisicao:
            texto = f"Solicito o pagamento para {nome_fornecedor}, para {contrato}.\n\n"
            texto += f"SERVIÇO: {tipo_servico} - {tipo_aquisicao}\n\n"
            texto += f"VALOR: R$ {valor_tab1}\n\n"
        
        else:
            texto = (
                f"Solicito o pagamento ao fornecedor {nome_fornecedor}, referente à obra: "
                f"{prefixo} - {agencia} - {os_num}, para {contrato}.\n\n"
                if prefixo
                else f"Solicito o pagamento ao fornecedor {nome_fornecedor}, para {contrato}.\n\n"
            )
            texto += f"SERVIÇO: {tipo_servico}\n\n"
            texto += f"VALOR: R$ {valor_tab1}\n\n"

        if tipo_pagamento == "FATURAMENTO":
            texto = (
                f"Assunto: {nome_arquivo_sem_ext}\n\n"
                "Prezado(a),\n\n"
                "Solicito autorização para compra referente aos materiais descritos na "
                "ordem de compra e orçamento em anexo."
            )
        elif tipo_pagamento == "PIX":
            if tipo_chave_pix == "QR CODE":
                texto += f"Pagamento PIX via {tipo_chave_pix}"
            else:
                texto += f"Segue PIX {tipo_chave_pix} ⬇\n\n{chave_pix}"
                texto += f"\n\n{nome_benef_pix}" if nome_benef_pix else ""
        else:
            texto += "Pagamento via VEXPENSES"

        # Exibir texto na caixa de texto
        self.texto_solicitacao.delete(1.0, tk.END)
        self.texto_solicitacao.insert(tk.END, texto)

        # Insere os dados no BD
        conecta_banco_pagamentos(nome_usuario, tipo_servico, nome_fornecedor, prefixo, agencia, os_num, 
            contrato, motivo, valor_tab1, tipo_pagamento, tecnicos, competencia,
            porcentagem, tipo_aquisicao)

        # Copiar automaticamente o texto gerado caso o switch esteja ativo
        if self.switch_autocopia_var.get():
            pyperclip.copy(texto)

        if self.switch_gerar_excel_var.get():
            descricao_itens = ""
            valor_itens = ""

            if tipo_servico in {"RELATÓRIO EXTRA", "ADIANTAMENTO/PAGAMENTO PARCEIRO"} and self.itens_pagamento:
                descricao_itens = "\n".join(item["descricao"] for item in self.itens_pagamento)

                if self.opcao_os_parceiro_combobox.get() == "SIM" and len(self.itens_pagamento) == 1:
                    partes = [parte.strip() for parte in descricao_base.split('-')]

                    os_num = partes[0]
                    prefixo = partes[1]
                    agencia = partes[2]

                    print(f"Prefixo: {prefixo}, Agência: {agencia}, OS: {os_num}")
            
            if tipo_servico in {
                "REEMBOLSO SEM OS", "SOLICITAÇÃO SEM OS",
                "SOLICITAÇÃO COM OS", "REEMBOLSO COM OS", "REEMBOLSO UBER"
            }:
                if tipo_servico == "REEMBOLSO UBER":
                    descricao_itens = "\n".join(
                        f"{item['saida_e_destino']} - {item['motivo']}" for item in self.itens_pagamento
                    )
                elif tipo_servico in {"SOLICITAÇÃO SEM OS", "SOLICITAÇÃO COM OS"}:
                    descricao_itens = "\n".join(
                        f"{item['motivo']} - TÉCNICOS: {tecnicos}" for item in self.itens_pagamento
                    )
                else:
                    descricao_itens = "\n".join(item["motivo"] for item in self.itens_pagamento)

                valor_itens = "\n".join(str(item["valor"]) for item in self.itens_pagamento)

            # Criando uma instância do dataclass DadosRequisicao
            dados = DadosRequisicao(
                root=self.root,
                nome_arquivo=nome_arquivo,
                tipo_servico=tipo_servico,
                nome_fornecedor=nome_fornecedor,
                os_num=os_num,
                prefixo=prefixo,
                agencia=agencia,
                contrato=contrato,
                nome_usuario=nome_usuario,
                tipo_pagamento=tipo_pagamento,
                departamento=departamento,
                valor=valor_tab1,
                tecnicos=tecnicos,
                usuarios_varios_departamentos=self.usuarios_varios_departamentos,
                usuarios_gerais=self.usuarios_gerais,
                motivo=motivo,
                descricao_itens=descricao_itens,
                valor_itens=valor_itens,
            )

            gerar_excel(dados)

    def identifica_preenchimento_pref_os_age(self, prefixo, agencia, os_num):
        ''''''
        campos_preenchidos = {
            "PREFIXO": bool(prefixo),
            "AGÊNCIA": bool(agencia),
            "OS": bool(os_num),
        }

        faltantes = [campo for campo, preenchido in campos_preenchidos.items() if not preenchido]
        preenchidos = [campo for campo, preenchido in campos_preenchidos.items() if preenchido]

        def formatar_lista(lista):
            """Formata uma lista para usar 'e' antes do último item."""
            if len(lista) > 1:
                return f"{', '.join(lista[:-1])} e {lista[-1]}"
            return lista[0]

        if len(preenchidos) == 1:
            self.notificacao.show_notification(
                f"Campo {preenchidos[0]} está preenchido\nPor favor, insira {formatar_lista(faltantes)}.",
                NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF"
            )
            return True
        elif len(preenchidos) == 2:
            self.notificacao.show_notification(
                f"Os campos {formatar_lista(preenchidos)} estão preenchidos\nPor favor, insira {faltantes[0]}.",
                NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF"
            )
            return True

    def _limpar_dados(self):
        """Limpa todos os dados dos campos"""
        if self.editando_item_pagamento is None:
            # Limpar os widgets da Tab 1
            for widget in self.widgets_para_limpar:
                if isinstance(widget, ctk.CTkEntry):
                    widget.delete(0, tk.END)
                elif isinstance(widget, ctk.CTkTextbox):
                    widget.delete("0.0", tk.END)
                elif isinstance(widget, ctk.CTkComboBox):
                    widget.set("")

                self.itens_pagamento.clear()
                self._atualizar_lista_itens_pagamento()
                self._add_campos()
        else:
            self.notificacao.show_notification("Item em edição!\nSalve-o para habilitar a limpeza dos campos.", NotifyType.WARNING, bg_color="#404040", text_color="#FFFFFF")
            pass 

# Classe de utilidade para facilitar a criação
class AbaPagamentoManager:
    """Gerenciador para a aba de pagamento"""
    
    @staticmethod
    def create_payment_tab(tabview, nome_completo_usuario: str) -> AbaPagamento:
        """Cria e retorna uma instância da aba de pagamento"""
        return AbaPagamento(tabview, nome_completo_usuario)


# Exemplo de uso:
if __name__ == "__main__":
    # Este código seria usado em seu aplicativo principal
    # tabview = ctk.CTkTabview(master=root)
    # payment_tab = AbaPagamentoManager.create_payment_tab(tabview, "Nome do Usuário")
    pass