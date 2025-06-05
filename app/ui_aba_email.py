import tkinter as tk
import customtkinter as ctk
import pyperclip
import sqlite3

from .componentes import CustomEntry, CustomComboBox
from .CTkFloatingNotifications import NotificationManager, NotifyType
from .utils import arrumar_texto, valida_prefixo, valida_os, verificar_se_numero
from app.ui_tela_principal import root
from .bd.utils_bd import DatabaseManager

class AbaEmail(ctk.CTkFrame):
    def __init__(self, master, tabview="E-mail", nome_completo_usuario=None):
        """
        Inicializa a aba de email com todos os componentes necessários.
        
        Args:
            master (CTkFrame): Frame pai onde a aba será criada
            tabview (CTkTabview): Componente que gerencia as abas da interface
            nome_completo_usuario (str): Nome do usuário logado que será exibido no campo usuário
        """
        super().__init__(master)
        self.tabview = tabview
        self.nome_completo_usuario = nome_completo_usuario
        self.noificacao = NotificationManager(master=None)
        self.pack(fill="both", expand=True)
        
        # Lista de widgets para limpeza
        self.widgets_para_limpar = []
        
        # Variáveis dos widgets
        self.nome_usuario_entry = None
        self.tipo_servico_combobox = None
        self.prefixo_label = None
        self.prefixo_entry = None
        self.agencia_label = None
        self.agencia_entry = None
        self.os_label = None
        self.os_entry = None
        self.endereco_agencia_label = None
        self.endereco_entry = None
        self.nome_fornecedor_entry = None
        self.valor_entry = None
        self.tipo_pagamento_combobox = None
        self.num_orcamento_entry = None
        self.switch_autocopia_var = None
        self.texto_email = None
        
        self.db_paths = [
            r'G:\Meu Drive\17 - MODELOS\PROGRAMAS\Gerador de Requisições\app\bd\dados.db',
            r'app\bd\dados.db'
        ]

        # self.inicializar_banco() -> Para implantar o acesso dados.db na aba
        self._criar_interface()
        self._configurar_eventos()
    
    def inicializar_banco(self):
        """Inicializa o banco de dados"""
        try:
            # Usa o DatabaseManager já existente
            self.db_manager = DatabaseManager()

            # Estabelece conexão usando o gerenciador
            with self.db_manager._get_connection(self.db_paths) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(registros)")
                colunas = [coluna[1] for coluna in cursor.fetchall()]
                if "lido" not in colunas:
                    cursor.execute("ALTER TABLE registros ADD COLUMN lido INTEGER DEFAULT 0")
                    conn.commit()
        
        except sqlite3.Error as e:
            print(f"Erro ao inicializar o banco de dados: {e}")
            self.noificacao.show_notification(
                "Erro ao inicializar o banco de dados.",
                NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF"
            )
    
    def _criar_interface(self):
        """Cria a interface da aba de email."""
        self._set_appearance_mode("system")

        # Configuração do grid
        self.grid_rowconfigure(14, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self._criar_campos_principais()
        self._criar_campos_condicionais()
        self._criar_campos_finais()
        self._criar_botoes()
        self._criar_area_texto()
    
    def _criar_campos_principais(self):
        """Cria os campos principais sempre visíveis."""
        # Campo Usuário
        ctk.CTkLabel(self, text="USUÁRIO:").grid(
            row=0, column=0, sticky="w", padx=(10, 10), pady=(10, 0))
        self.nome_usuario_entry = CustomEntry(self)
        self.nome_usuario_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=(10, 2))
        self.nome_usuario_entry.insert(0, self.nome_completo_usuario)
        self.nome_usuario_entry.configure(state='disabled')
        
        # Campo Tipo de Serviço
        ctk.CTkLabel(self, text="TIPO DE SERVIÇO:").grid(
            row=1, column=0, sticky="w", padx=(10, 10))
        self.tipo_servico_combobox = CustomComboBox(
            self,
            values=["COMPRAS EM GERAL - COM OS", "COMPRAS EM GERAL - SEM OS", "LOCAÇÃO"],
            command=lambda choice: self._adicionar_campos_condicionais()
        )
        self.tipo_servico_combobox.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=2)
        self.tipo_servico_combobox.set("")
        self.widgets_para_limpar.append(self.tipo_servico_combobox)
    
    def _criar_campos_condicionais(self):
        """Cria os campos que aparecem condicionalmente."""
        # Prefixo
        self.prefixo_label = ctk.CTkLabel(self, text="PREFIXO:")
        self.prefixo_entry = CustomEntry(self)
        self.widgets_para_limpar.append(self.prefixo_entry)
        
        # Agência
        self.agencia_label = ctk.CTkLabel(self, text="AGÊNCIA:")
        self.agencia_entry = CustomEntry(self)
        self.widgets_para_limpar.append(self.agencia_entry)
        
        # OS
        self.os_label = ctk.CTkLabel(self, text="OS:")
        self.os_entry = CustomEntry(self)
        self.widgets_para_limpar.append(self.os_entry)
        
        # Endereço
        self.endereco_agencia_label = ctk.CTkLabel(self, text="ENDEREÇO DE ENTREGA:")
        self.endereco_entry = CustomEntry(self, placeholder_text="Opcional")
        self.widgets_para_limpar.append(self.endereco_entry)
    
    def _criar_campos_finais(self):
        """Cria os campos finais sempre visíveis."""
        # Nome Fornecedor
        ctk.CTkLabel(self, text="NOME FORNEC./BENEF.:").grid(
            row=8, column=0, sticky="w", padx=(10, 10))
        self.nome_fornecedor_entry = CustomEntry(self)
        self.nome_fornecedor_entry.grid(row=8, column=1, sticky="ew", padx=(0, 10), pady=2)
        self.widgets_para_limpar.append(self.nome_fornecedor_entry)
        
        # Valor
        ctk.CTkLabel(self, text="VALOR:").grid(
            row=9, column=0, sticky="w", padx=(10, 10))
        self.valor_entry = CustomEntry(self)
        self.valor_entry.grid(row=9, column=1, sticky="ew", padx=(0, 10), pady=2)
        self.widgets_para_limpar.append(self.valor_entry)
        
        # Tipo de Pagamento
        ctk.CTkLabel(self, text="TIPO DE PAGAMENTO:").grid(
            row=10, column=0, sticky="w", padx=(10, 10))
        self.tipo_pagamento_combobox = CustomComboBox(
            self,
            values=["FATURAMENTO", "PIX", "VEXPENSES"],
            command=lambda choice: self._adicionar_campo_pix()
        )
        self.tipo_pagamento_combobox.grid(row=10, column=1, sticky="ew", padx=(0, 10), pady=2)
        self.tipo_pagamento_combobox.set("")
        self.widgets_para_limpar.append(self.tipo_pagamento_combobox)
        
        # Número do Orçamento
        ctk.CTkLabel(self, text="Nº ORÇAM./PEDIDO (SE APLICÁVEL):").grid(
            row=11, column=0, sticky="w", padx=(10, 10))
        self.num_orcamento_entry = CustomEntry(self, placeholder_text="Opcional")
        self.num_orcamento_entry.grid(row=11, column=1, sticky="ew", padx=(0, 10), pady=2)
        self.widgets_para_limpar.append(self.num_orcamento_entry)
    
    def _criar_botoes(self):
        """Cria os botões da interface."""
        # Botão Gerar
        gerar_button = ctk.CTkButton(
            self, 
            text="GERAR", 
            command=self.gerar_texto_email
        )
        gerar_button.grid(row=12, column=0, sticky="ew", padx=(10, 10), pady=10)
        
        # Botão Limpar
        limpar_button = ctk.CTkButton(
            self, 
            text="LIMPAR", 
            width=150, 
            command=self.limpar_dados
        )
        limpar_button.grid(row=12, column=1, sticky="ew", padx=(0, 10), pady=10)
        
        # Switch Auto-Cópia
        self.switch_autocopia_var = tk.BooleanVar(value=True)
        switch_autocopia = ctk.CTkSwitch(
            self,
            text="Auto-Cópia",
            variable=self.switch_autocopia_var,
            onvalue=True,
            offvalue=False
        )
        switch_autocopia.grid(row=13, column=0, columnspan=2, sticky="n", padx=10, pady=10)
    
    def _criar_area_texto(self):
        """Cria a área de texto para exibir o email gerado."""
        self.texto_email = ctk.CTkTextbox(self)
        self.texto_email.grid(row=14, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="nsew")
        self.widgets_para_limpar.append(self.texto_email)
    
    def _configurar_eventos(self):
        """Configura os eventos da interface."""
        root.bind("<Return>", self._on_return_press)
    
    def _adicionar_campos_condicionais(self):
        """Adiciona ou remove campos baseado no tipo de serviço selecionado."""
        tipo_servico = self.tipo_servico_combobox.get()
        
        if tipo_servico in {"COMPRAS EM GERAL - COM OS", "LOCAÇÃO"}:
            # Mostra campos obrigatórios
            self.prefixo_label.grid(row=4, column=0, sticky="w", padx=(10, 10))
            self.prefixo_entry.grid(row=4, column=1, sticky="ew", padx=(0, 10), pady=2)
            self.agencia_label.grid(row=5, column=0, sticky="w", padx=(10, 10))
            self.agencia_entry.grid(row=5, column=1, sticky="ew", padx=(0, 10), pady=2)
            self.os_label.grid(row=6, column=0, sticky="w", padx=(10, 10))
            self.os_entry.grid(row=6, column=1, sticky="ew", padx=(0, 10), pady=2)
        else:
            # Oculta campos
            campos_ocultar = [
                self.prefixo_label, self.prefixo_entry,
                self.os_label, self.os_entry,
                self.agencia_label, self.agencia_entry
            ]
            for widget in campos_ocultar:
                widget.grid_forget()
        
        # Campo endereço específico para locação
        if tipo_servico == "LOCAÇÃO":
            self.endereco_agencia_label.grid(row=7, column=0, sticky="w", padx=(10, 10))
            self.endereco_entry.grid(row=7, column=1, sticky="ew", padx=(0, 10), pady=2)
        else:
            self.endereco_agencia_label.grid_forget()
            self.endereco_entry.grid_forget()
    
    def _adicionar_campo_pix(self):
        """Adiciona campos específicos para pagamento PIX se necessário."""
        # Implementar lógica específica para PIX se necessário
        pass
    
    def _on_return_press(self, event):
        """Manipula o evento de pressionar Enter."""
        self.gerar_texto_email()
    
    def _validar_campos(self):
        """Valida todos os campos obrigatórios."""
        # Coleta dados dos campos
        nome_usuario = arrumar_texto(self.nome_usuario_entry.get().upper())
        tipo_servico = arrumar_texto(self.tipo_servico_combobox.get().upper())
        nome_fornecedor = arrumar_texto(self.nome_fornecedor_entry.get().upper())
        valor = verificar_se_numero(self.valor_entry.get())
        tipo_pagamento = arrumar_texto(self.tipo_pagamento_combobox.get().upper())
        
        # Campos obrigatórios básicos
        campos_obrigatorios = [
            (nome_usuario, "USUÁRIO"),
            (tipo_servico, "TIPO DE SERVIÇO"),
            (nome_fornecedor, "NOME DO FORNECEDOR/BENEFICIÁRIO"),
            (valor, "VALOR"),
            (tipo_pagamento, "TIPO DE PAGAMENTO")
        ]
        
        # Adiciona campos condicionais
        if tipo_servico in {"COMPRAS EM GERAL - COM OS", "LOCAÇÃO"}:
            prefixo = valida_prefixo(self.prefixo_entry.get())
            agencia = arrumar_texto(self.agencia_entry.get().upper())
            os_num = valida_os(self.os_entry.get())
            
            campos_obrigatorios.extend([
                (prefixo, "PREFIXO"),
                (agencia, "AGÊNCIA"),
                (os_num, "OS")
            ])
        
        # Verifica campos vazios
        campos_vazios = [nome for valor, nome in campos_obrigatorios if not valor]
        
        # Validações específicas
        if tipo_servico in {"COMPRAS EM GERAL - COM OS", "LOCAÇÃO"}:
            prefixo = valida_prefixo(self.prefixo_entry.get())
            if prefixo == "Prefixo inválido":
                self.noificacao.show_notification(
                    "Campo PREFIXO\nPrefixo inválido. Use o padrão XXXX/XX.",
                    NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF"
                )
                return False
            
            os_num = valida_os(self.os_entry.get())
            if os_num == "OS_invalida":
                self.noificacao.show_notification(
                    "Campo OS\nPor favor, insira uma OS válida!",
                    NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF"
                )
                return False
        
        if valor == ValueError:
            self.noificacao.show_notification(
                "Campo VALOR\nPor favor, insira um número válido!",
                NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF"
            )
            return False
        
        if campos_vazios:
            self.noificacao.show_notification(
                "Preencha os campos obrigatórios em branco!",
                NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF"
            )
            return False
        
        return True
    
    def _gerar_texto_compras_com_os(self, dados):
        """Gera texto para compras em geral com OS."""
        texto = f"Prezado Fornecedor {dados['nome_fornecedor']},\n\n"
        
        if dados['tipo_pagamento'] == "FATURAMENTO":
            texto += f"Comunico que está autorizado para FATURAMENTO o pedido {dados['os_num']}, no valor de R$ {dados['valor']}.\n\n"
        else:
            pedido = dados['num_orcamento'] if dados['num_orcamento'] else "S/N"
            texto += f"Comunico que está autorizado para pagamento via {dados['tipo_pagamento']} o pedido {pedido}, no valor de R$ {dados['valor']}.\n\n"

        texto += f"SEGUE INFORMAÇÕES PARA NOTA FISCAL:\n{dados['prefixo']} - {dados['agencia']} - {dados['os_num']}\n\n"
        texto += self._get_texto_padrao_fornecedor()

        return texto

    def _gerar_texto_compras_sem_os(self, dados):
        """Gera texto para compras em geral sem OS."""
        texto = "Prezado(a),\n\n"
        pedido = dados['num_orcamento'] if dados['num_orcamento'] else "S/N"
        texto += f"Comunico que está autorizado para pagamento via {dados['tipo_pagamento']} o pedido {pedido}, no valor de R$ {dados['valor']}.\n\n"

        return texto

    def _gerar_texto_locacao(self, dados):
        """Gera texto para locação."""
        texto = f"Prezado Fornecedor {dados['nome_fornecedor']},\n\n"
        pedido = dados['num_orcamento'] if dados['num_orcamento'] else ""

        if pedido:
            texto += f"Comunico que está autorizado a locação de EQUIPAMENTO via {dados['tipo_pagamento']}, referente ao pedido {pedido}, no valor de R$ {dados['valor']}.\n\n"
        else:
            texto += f"Comunico que está autorizado a locação de EQUIPAMENTO via {dados['tipo_pagamento']}, no valor de R$ {dados['valor']}.\n\n"
        
        texto += f"Segue informação referente ao local para entrega do material:\n{dados['endereco']}\n\n"
        texto += f"SEGUE INFORMAÇÕES PARA NOTA FISCAL:\n{dados['prefixo']} - {dados['agencia']} - {dados['os_num']}\n\n"
        texto += self._get_texto_padrao_fornecedor()
        
        return texto

    def _get_texto_padrao_fornecedor(self):
        """Retorna o texto padrão para fornecedores."""
        return (
            "Prezado fornecedor, solicito por gentileza que a partir deste momento todos os e-mails enviados sejam respondidos para todos.\n"
            "Nossa empresa solicita que seja incluída na nota fiscal as informações referentes a obra enviada no corpo do e-mail no momento da autorização da compra.\n"
            "Gostaria de solicitar, por gentileza, o envio da nota fiscal, boleto e ordem de compra para compras faturadas. Para pagamentos à vista, solicito apenas a nota fiscal e a ordem de compra.\n"
            "Por favor, encaminhem todos os documentos para o e-mail, respondendo para todos os envolvidos."
        )

    def gerar_texto_email(self):
        """Gera o texto do email baseado nos dados inseridos."""
        if not self._validar_campos():
            return

        # Coleta todos os dados
        dados = {
            'nome_usuario': arrumar_texto(self.nome_usuario_entry.get().upper()),
            'tipo_servico': arrumar_texto(self.tipo_servico_combobox.get().upper()),
            'nome_fornecedor': arrumar_texto(self.nome_fornecedor_entry.get().upper()),
            'valor': verificar_se_numero(self.valor_entry.get()),
            'tipo_pagamento': arrumar_texto(self.tipo_pagamento_combobox.get().upper()),
            'num_orcamento': arrumar_texto(self.num_orcamento_entry.get().upper()),
        }

        # Adiciona dados condicionais
        if dados['tipo_servico'] in {"COMPRAS EM GERAL - COM OS", "LOCAÇÃO"}:
            dados.update({
                'prefixo': valida_prefixo(self.prefixo_entry.get()),
                'agencia': arrumar_texto(self.agencia_entry.get().upper()),
                'os_num': valida_os(self.os_entry.get()),
            })

            if dados['tipo_servico'] == "LOCAÇÃO":
                dados['endereco'] = arrumar_texto(self.endereco_entry.get().upper())

        # Gera o texto baseado no tipo de serviço
        if dados['tipo_servico'] == "COMPRAS EM GERAL - COM OS":
            texto = self._gerar_texto_compras_com_os(dados)
        elif dados['tipo_servico'] == "COMPRAS EM GERAL - SEM OS":
            texto = self._gerar_texto_compras_sem_os(dados)
        else:  # LOCAÇÃO
            texto = self._gerar_texto_locacao(dados)

        # Exibe o texto gerado
        self.texto_email.delete(1.0, tk.END)
        self.texto_email.insert(tk.END, texto)
        
        # Copia automaticamente se o switch estiver ativo
        if self.switch_autocopia_var.get():
            pyperclip.copy(texto)

    def limpar_dados(self):
        """Limpa todos os campos da aba."""
        for widget in self.widgets_para_limpar:
            if hasattr(widget, 'delete'):
                if isinstance(widget, ctk.CTkTextbox):
                    widget.delete(1.0, tk.END)
                else:
                    widget.delete(0, tk.END)
            elif hasattr(widget, 'set'):
                widget.set("")

        # Oculta campos condicionais
        campos_ocultar = [
            self.prefixo_label, self.prefixo_entry,
            self.os_label, self.os_entry,
            self.agencia_label, self.agencia_entry,
            self.endereco_agencia_label, self.endereco_entry
        ]
        for widget in campos_ocultar:
            widget.grid_forget()
