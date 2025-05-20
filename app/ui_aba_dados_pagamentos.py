import sqlite3
import re
import pyperclip
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, scrolledtext
from datetime import datetime

import app.componentes as componentes
from .CTkDatePicker import CTkDatePicker
from .CTkFloatingNotifications import *
from app.ui_tela_principal import root

CAMINHO_BD = r'G:\Meu Drive\17 - MODELOS\PROGRAMAS\Gerador de Requisições\app\bd\dados.db'
notification_manager = NotificationManager(root)  # passando a instância da janela principal

class AbaDadosPagamentos(ctk.CTkFrame):
    def __init__(self, master, tabview="DADOS PAGAMENTOS", **kwargs):
        super().__init__(master, **kwargs)
        self.tabview = tabview
        self.estado_anterior = None  # Adicionado para rastrear mudanças de estado da janela
        self.pack(fill="both", expand=True, padx=2, pady=2)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.registro_atual = None
        self.lido_atual = None
        self.ultimo_fullscreen = root.attributes('-fullscreen')  # Salva o estado inicial

        self.inicializar_banco()
        self._construir_widgets()

    def inicializar_banco(self):
        with sqlite3.connect(CAMINHO_BD) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(registros)")
            colunas = [coluna[1] for coluna in cursor.fetchall()]
            if "lido" not in colunas:
                cursor.execute("ALTER TABLE registros ADD COLUMN lido INTEGER DEFAULT 0")
                conn.commit()

    def _construir_widgets(self):
        self._set_appearance_mode("system")
        root.bind("<Configure>", self._on_configure)  # Adiciona o listener

        self.label_data = ctk.CTkLabel(self, text="Data:")
        self.label_data.grid(row=0, column=0, sticky="e", padx=(10, 10), pady=(10, 0))
        self.data_entry = CTkDatePicker(self, self.tabview)
        self.data_entry.grid(row=0, column=1, sticky="w", padx=(10, 10), pady=(10, 0))
        
        self.botao_exibir = ctk.CTkButton(self, text="Exibir Registros", command=self.busca_por_data)
        self.botao_exibir.grid(row=1, column=1, sticky="w", padx=(10, 10), pady=10)

        self.saida_texto = ctk.CTkTextbox(self, width=500, height=100)
        self.saida_texto.grid(row=3, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="nsew")

        self.botao_marcar_lido = ctk.CTkButton(self, text="Marcar como Lido", command=self.marcar_como_lido)
        self.botao_marcar_nao_lido = ctk.CTkButton(self, text="Marcar como Não Lido", command=self.marcar_como_nao_lido)
        self.botao_deletar = ctk.CTkButton(self, text="Deletar Registro", command=self.deletar_registro)

    def _on_configure(self, event):
        estado = root.state()

        if estado != self.estado_anterior:
            self.estado_anterior = estado
            print(f"Estado da janela mudou para: {estado}")

            # Detecta janela maximizada no Windows
            if estado == 'zoomed':
                if hasattr(self, 'frame_listagem') and self.frame_listagem is not None:
                    if hasattr(self, 'registros_exibidos'):
                        self.exibir_registros_em_frame(self.registros_exibidos)
            else:
                if hasattr(self, 'frame_listagem') and self.frame_listagem is not None:
                    if hasattr(self, 'registros_exibidos'):
                        self.exibir_registros_em_frame(self.registros_exibidos)

    def quebra_linhas(self, texto, tamanho=83):
        try:
            estado = root.state()
            if estado == 'zoomed':
                tamanho = 9999  # Se maximizada, não quebra a linha
        except Exception:
            print("Erro ao verificar o estado da janela. Erro: ", str(e))
            pass

        return '\n'.join([texto[i:i+tamanho] for i in range(0, len(texto), tamanho)])

    def exibir_registros_em_frame(self, registros, titulo="Escolha um registro"):
        # Salva os registros exibidos para poder redesenhar depois
        self.registros_exibidos = registros

        # Remove frame anterior, se existir
        if hasattr(self, 'frame_listagem') and self.frame_listagem is not None:
            self.frame_listagem.destroy()
            self.frame_listagem = None

        if not registros:
            notification_manager.show_notification(
                f"Nenhum registro encontrado.",
                NotifyType.ERROR,
                bg_color="#404040", text_color="#FFFFFF"
            )
            return

        # Cria o frame de listagem na linha 2
        h = 340 if root.state() == 'zoomed' else 250
        if hasattr(self, 'frame_listagem') and self.frame_listagem is not None:
            self.frame_listagem.destroy()
            self.frame_listagem = None
        self.frame_listagem = ctk.CTkFrame(self, height=h)
        self.frame_listagem.grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=(0, 10))
        self.frame_listagem.grid_rowconfigure(0, weight=1)
        self.frame_listagem.grid_columnconfigure(0, weight=1)

        # Frame rolável para os registros
        self.scroll_frame = ctk.CTkScrollableFrame(master=self.frame_listagem, height=h)
        self.scroll_frame.pack(expand=True, fill="both", padx=2, pady=2)

        registros_texto = []

        for registro in registros:
            prefixo_status = '✅' if registro[-1] else '❎'
            
            if registro[5] == "":
                texto_base = f"{prefixo_status} {registro[3]}: {registro[10]} - {registro[8]}"
            else:
                texto_base = f"{prefixo_status} {registro[3]}: {registro[10]} - {registro[5]} - {registro[6]} - {registro[7]} - {registro[8]}"

            if registro[3] in {"AQUISIÇÃO SEM OS", "REEMBOLSO SEM OS", "ABASTECIMENTO", "SOLICITAÇÃO SEM OS"}:
                texto_completo = f"{texto_base}  ({registro[2]} - {registro[18][:5]})"
            else:
                texto_completo = f"{texto_base} ({registro[18][:5]})"

            registros_texto.append(self.quebra_linhas(texto_completo))

        self.opcoes = []
        for idx, texto in enumerate(registros_texto):
            botao = ctk.CTkButton(
                self.scroll_frame,
                text=texto,
                anchor="w",
                width=900,
                command=lambda i=idx: self.mostrar_dados_selecionados(i, registros))
            botao.pack(fill='x', padx=5, pady=2)
            self.opcoes.append(botao)

    def mostrar_dados_selecionados(self, index, registros):
        self.registro_atual = registros[index][0]
        self.lido_atual = registros[index][-1]

        with sqlite3.connect(CAMINHO_BD) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM registros WHERE rowid = ?", (self.registro_atual,))
            dados = cursor.fetchone()

        self.preencher_campos(dados)

        self.botao_marcar_lido.grid_forget()
        self.botao_marcar_nao_lido.grid_forget()
        self.botao_deletar.grid_forget()

        if self.lido_atual:
            self.botao_marcar_nao_lido.grid(row=4, column=0, sticky="w", padx=(10, 10), pady=(0, 10))
        else:
            self.botao_marcar_lido.grid(row=4, column=0, sticky="w", padx=(10, 10), pady=(0, 10))

        self.botao_deletar.grid(row=4, column=1, sticky="e", padx=(10, 10), pady=(0, 10))

        # Fecha o frame de listagem após seleção
        if hasattr(self, 'frame_listagem') and self.frame_listagem is not None:
            self.frame_listagem.destroy()
            self.frame_listagem = None

    def exibir_dados(self):
        with sqlite3.connect(CAMINHO_BD) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT rowid, * FROM registros ORDER BY id DESC, data_criacao DESC, hora_criacao DESC")
            registros = cursor.fetchall()

        self.exibir_registros_em_frame(registros)

    def busca_por_data(self):
        data = self.data_entry.get_date()

        self.saida_texto.delete("1.0", "end")

        if not data:
            notification_manager.show_notification(
                f"Por favor, selecione uma data.",
                NotifyType.ERROR,
                bg_color="#404040",text_color="#FFFFFF"
            )
            return

        with sqlite3.connect(CAMINHO_BD) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT rowid, * FROM registros WHERE data_criacao = ? ORDER BY id DESC", (data,))
            registros = cursor.fetchall()

        self.exibir_registros_em_frame(registros, titulo=f"Registros em {data}")

    def mostrar_dados_selecionados(self, index, registros):
        self.registro_atual = registros[index][0]
        self.lido_atual = registros[index][-1]

        with sqlite3.connect(CAMINHO_BD) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM registros WHERE rowid = ?", (self.registro_atual,))
            dados = cursor.fetchone()

        self.preencher_campos(dados)

        self.botao_marcar_lido.grid_forget()
        self.botao_marcar_nao_lido.grid_forget()
        self.botao_deletar.grid_forget()

        if self.lido_atual:
            self.botao_marcar_nao_lido.grid(row=4, column=0, sticky="w", padx=(10, 10), pady=(0, 10))
        else:
            self.botao_marcar_lido.grid(row=4, column=0, sticky="w", padx=(10, 10), pady=(0, 10))

        self.botao_deletar.grid(row=4, column=1, sticky="e", padx=(10, 10), pady=(0, 10))

    def preencher_campos(self, dados):
        nome_usuario, tipo_servico, nome_fornecedor, prefixo, agencia, os_num, contrato, motivo, valor, tipo_pagamento, tecnicos, saida_destino, competencia, porcentagem, tipo_aquisicao, data_criacao, hora_criacao, lido = dados[1:]

        if os_num == "":
            agencia = os_num = prefixo = "**"

        if re.search(r"\breembolso\b", tipo_servico.strip(), re.IGNORECASE):
            tipo_servico = 'REEMBOLSO'

        texto_gerado = f"{nome_usuario}\t{valor.replace('.', '')}\t{data_criacao}\t{nome_fornecedor.upper()}\t{os_num}\t{agencia}\t{prefixo}\t{tipo_servico}\t{contrato}\t{tipo_pagamento.upper()}"
        self.saida_texto.delete("1.0", "end")
        self.saida_texto.insert("end", texto_gerado)
        pyperclip.copy(texto_gerado)

    def marcar_como_lido(self):
        if self.registro_atual:
            with sqlite3.connect(CAMINHO_BD) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE registros SET lido = 1 WHERE rowid = ?", (self.registro_atual,))
                conn.commit()
            messagebox.showinfo("Sucesso", "Registro marcado como lido!")
            self.botao_marcar_lido.grid_forget()
            self.botao_marcar_nao_lido.grid(row=4, column=0, sticky="w", padx=(10, 10), pady=(0, 10))

    def marcar_como_nao_lido(self):
        if self.registro_atual:
            with sqlite3.connect(CAMINHO_BD) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE registros SET lido = 0 WHERE rowid = ?", (self.registro_atual,))
                conn.commit()
                notification_manager.show_notification(
                    f"Registro marcado como não lido!",
                    NotifyType.SUCCESS,
                    bg_color="#404040",text_color="#FFFFFF"
                )
            self.botao_marcar_nao_lido.grid_forget()
            self.botao_marcar_lido.grid(row=4, column=0, sticky="w", padx=(10, 10), pady=(0, 10))

    def deletar_registro(self):
        if self.registro_atual:
            resposta = messagebox.askyesno("Confirmar", "Tem certeza que deseja deletar este registro?")
            if resposta:
                with sqlite3.connect(CAMINHO_BD) as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM registros WHERE rowid = ?", (self.registro_atual,))
                    conn.commit()
                    notification_manager.show_notification(
                        f"Registro deletado com sucesso!",
                        NotifyType.SUCCESS,
                        bg_color="#404040",text_color="#FFFFFF"
                    )
                self.botao_marcar_lido.grid_forget()
                self.botao_marcar_nao_lido.grid_forget()
                self.botao_deletar.grid_forget()
