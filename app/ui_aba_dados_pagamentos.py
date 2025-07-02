import sqlite3
import re
import pyperclip
import tkinter as tk
import customtkinter as ctk
import os
from tkinter import messagebox, scrolledtext
from datetime import datetime

try:
    from . import componentes
    from .CTkDatePicker import CTkDatePicker
    from .CTkFloatingNotifications import *
    from .bd.processar_fila import obter_info_fila_para_interface, processar_fila_completa, verificar_autorizacao
    from .bd.utils_bd import verificar_status_fila
    from .salva_erros import salvar_erro
except ImportError:
    try:
        import app.componentes as componentes
        from app.CTkDatePicker import CTkDatePicker
        from app.CTkFloatingNotifications import *
        from app.bd.processar_fila import obter_info_fila_para_interface, processar_fila_completa, verificar_autorizacao
        from app.bd.utils_bd import verificar_status_fila
        from app.salva_erros import salvar_erro
    except ImportError:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        import componentes
        from CTkDatePicker import CTkDatePicker
        from CTkFloatingNotifications import *
        from bd.processar_fila import obter_info_fila_para_interface, processar_fila_completa, verificar_autorizacao
        from bd.utils_bd import verificar_status_fila
        from salva_erros import salvar_erro

# CAMINHO_BD = r'G:\Meu Drive\17 - MODELOS\PROGRAMAS\Gerador de Requisições\app\bd\dados.db'
CAMINHO_BD = r'app\bd\dados.db'

def formatar_valor_brasileiro(valor):
    """
    Formata um valor numérico para o formato brasileiro (x,xx).
    
    Args:
        valor: Valor a ser formatado (int, float ou string)
        
    Returns:
        str: Valor formatado no padrão brasileiro
    """
    if isinstance(valor, (int, float)):
        return f"{valor:.2f}".replace('.', ',')
    else:
        # Se já for string, garantir que use vírgula decimal
        return str(valor).replace('.', ',')

class AbaDadosPagamentos(ctk.CTkFrame):
    def __init__(self, master, nome_completo_usuario, root, tabview="DADOS PAGAMENTOS", **kwargs):
        super().__init__(master, **kwargs)
        self.pack(fill="both", expand=True, padx=2, pady=2)
        
        self.tabview = tabview
        self.nome_usuario = nome_completo_usuario
        self.estado_anterior = None  # Adicionado para rastrear mudanças de estado da janela
        self.root = root
        self.notificacao = NotificationManager(self.root)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.registro_atual = None
        self.lido_atual = None
        self.ultimo_fullscreen = self.root.attributes('-fullscreen')  # Salva o estado inicial

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
        self.root.bind("<Configure>", self._on_configure)  # Adiciona o listener

        # Frame para controles de pesquisa por data
        self.frame_pesquisa = ctk.CTkFrame(self)
        self.frame_pesquisa.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 5))
        self.frame_pesquisa.grid_columnconfigure(0, weight=0)
        self.frame_pesquisa.grid_columnconfigure(1, weight=0)
        self.frame_pesquisa.grid_columnconfigure(2, weight=0)
        self.frame_pesquisa.grid_columnconfigure(3, weight=1)

        self.label_data = ctk.CTkLabel(self.frame_pesquisa, text="Pesquisar por Data:", font=ctk.CTkFont(size=12, weight="bold"))
        self.label_data.grid(row=0, column=0, sticky="w", padx=(10, 5), pady=10)
        
        self.data_entry = CTkDatePicker(self.frame_pesquisa, self.tabview)
        self.data_entry.grid(row=0, column=1, sticky="w", padx=(5, 10), pady=10)
        
        self.botao_exibir = ctk.CTkButton(
            self.frame_pesquisa, 
            text="🔍 Buscar Registros", 
            command=self.busca_por_data,
            fg_color="#1f538d",
            hover_color="#1e4a7d",
            width=140
        )
        self.botao_exibir.grid(row=0, column=2, sticky="w", padx=(5, 10), pady=10)

        # Frame para informações e controle da fila de requisições
        self.frame_fila = ctk.CTkFrame(self)
        self.frame_fila.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 0))
        self.frame_fila.grid_columnconfigure(0, weight=1)
        self.frame_fila.grid_columnconfigure(1, weight=0)
        self.frame_fila.grid_columnconfigure(2, weight=0)
        self.frame_fila.grid_rowconfigure(0, weight=0)
        self.frame_fila.grid_rowconfigure(1, weight=0)
        
        # Label para mostrar status da fila
        self.label_status_fila = ctk.CTkLabel(self.frame_fila, text="Verificando fila...", font=ctk.CTkFont(size=12))
        self.label_status_fila.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        # Botão para atualizar status da fila
        self.botao_atualizar_fila = ctk.CTkButton(
            self.frame_fila, 
            text="Atualizar Status", 
            command=self.atualizar_status_fila_manual,
            width=120
        )
        self.botao_atualizar_fila.grid(row=0, column=1, sticky="w", padx=(10, 5), pady=5)
        
        # Botão para processar fila (sempre visível nesta aba restrita)
        self.botao_processar_fila = ctk.CTkButton(
            self.frame_fila, 
            text="Processar Fila", 
            command=self.processar_fila_requisicoes,
            fg_color="#ff6b6b",  # Cor vermelha para destacar
            hover_color="#ff5252",
            width=120
        )
        self.botao_processar_fila.grid(row=0, column=2, sticky="w", padx=(5, 5), pady=5)
        
        # Botão para mostrar detalhes da fila
        self.botao_detalhes_fila = ctk.CTkButton(
            self.frame_fila, 
            text="Ver Detalhes", 
            command=self.mostrar_detalhes_fila,
            width=100
        )
        self.botao_detalhes_fila.grid(row=0, column=3, sticky="w", padx=(5, 5), pady=5)
        
        # Atualizar status da fila na inicialização (sem auto-refresh)
        self.atualizar_status_fila_manual()

        self.saida_texto = ctk.CTkTextbox(self, width=500, height=75)
        self.saida_texto.grid(row=4, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="nsew")

        self.botao_marcar_lido = ctk.CTkButton(self, text="Marcar como Lido", command=self.marcar_como_lido)
        self.botao_marcar_nao_lido = ctk.CTkButton(self, text="Marcar como Não Lido", command=self.marcar_como_nao_lido)
        self.botao_deletar = ctk.CTkButton(self, text="Deletar Registro", command=self.deletar_registro)

    def _on_configure(self, event):
        estado = self.root.state()

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
            estado = self.root.state()
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
            self.notificacao.show_notification(
                f"Nenhum registro encontrado.",
                NotifyType.ERROR,
                bg_color="#404040", text_color="#FFFFFF"
            )
            return

        # Cria o frame de listagem na linha 3
        h = 340 if self.root.state() == 'zoomed' else 235
        if hasattr(self, 'frame_listagem') and self.frame_listagem is not None:
            self.frame_listagem.destroy()
            self.frame_listagem = None
        self.frame_listagem = ctk.CTkFrame(self, height=h)
        self.frame_listagem.grid(row=3, column=0, columnspan=3, sticky="ew", padx=10, pady=(0, 10))
        self.frame_listagem.grid_rowconfigure(0, weight=1)
        self.frame_listagem.grid_columnconfigure(0, weight=1)

        # Frame rolável para os registros
        self.scroll_frame = ctk.CTkScrollableFrame(master=self.frame_listagem, height=h)
        self.scroll_frame.pack(expand=True, fill="both", padx=2, pady=2)

        registros_texto = []

        for registro in registros:
            # Com rowid incluído no SELECT, os índices ficam deslocados em +1
            # Campo 'lido' está na última coluna
            lido_status = registro[-1]
            
            if len(registro) > 19:
                hora_criacao = registro[-4] if len(registro) > 1 else "00:00"  # Fallback
            else:
                hora_criacao = registro[-2] if len(registro) > 16 else "00:00"  # Fallback para hora_criacao
            
            prefixo_status = '[OK]' if lido_status else '[NAO LIDO]'
            
            if registro[5] == "":
                texto_base = f"{prefixo_status} {registro[3]}: {registro[10]} - {registro[8]}"
            else:
                texto_base = f"{prefixo_status} {registro[3]}: {registro[10]} - {registro[5]} - {registro[6]} - {registro[7]} - {registro[8]}"

            if registro[3] in {"AQUISIÇÃO SEM OS", "REEMBOLSO SEM OS", "ABASTECIMENTO", "SOLICITAÇÃO SEM OS"}:
                texto_completo = f"{texto_base}  ({registro[2]} - {hora_criacao[:5]})"
            else:
                texto_completo = f"{texto_base} ({hora_criacao[:5]})"

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
            self.notificacao.show_notification(
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
        # Com rowid incluído, o campo 'lido' está na posição 19
        if len(registros[index]) > 19:
            self.lido_atual = registros[index][19]  # Campo 'lido' na posição correta
        else:
            self.lido_atual = registros[index][-1]  # Fallback para formato antigo

        with sqlite3.connect(CAMINHO_BD) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM registros WHERE rowid = ?", (self.registro_atual,))
            dados = cursor.fetchone()

        self.preencher_campos(dados)

        self.botao_marcar_lido.grid_forget()
        self.botao_marcar_nao_lido.grid_forget()
        self.botao_deletar.grid_forget()

        if self.lido_atual:
            self.botao_marcar_nao_lido.grid(row=5, column=0, sticky="w", padx=(10, 10), pady=(0, 10))
        else:
            self.botao_marcar_lido.grid(row=5, column=0, sticky="w", padx=(10, 10), pady=(0, 10))

        self.botao_deletar.grid(row=5, column=1, sticky="e", padx=(10, 10), pady=(0, 10))

    def preencher_campos(self, dados):
        # Extrair dados considerando as novas colunas (data_processamento e hora_processamento)
        # Estrutura: id, nome_usuario, tipo_servico, nome_fornecedor, prefixo, agencia, os_num, 
        #           contrato, motivo, valor, tipo_pagamento, tecnicos, saida_destino, competencia, 
        #           porcentagem, tipo_aquisicao, data_criacao, hora_criacao, lido, data_processamento, hora_processamento
        
        if len(dados) >= 19:  # Com as novas colunas
            nome_usuario, tipo_servico, nome_fornecedor, prefixo, agencia, os_num, contrato, motivo, valor, tipo_pagamento, tecnicos, saida_destino, competencia, porcentagem, tipo_aquisicao, data_criacao, hora_criacao, lido = dados[1:19]
            # dados[19] e dados[20] são data_processamento e hora_processamento (opcionais)
        else:  # Formato antigo (compatibilidade)
            nome_usuario, tipo_servico, nome_fornecedor, prefixo, agencia, os_num, contrato, motivo, valor, tipo_pagamento, tecnicos, saida_destino, competencia, porcentagem, tipo_aquisicao, data_criacao, hora_criacao, lido = dados[1:]

        if os_num == "":
            agencia = os_num = prefixo = "**"

        if re.search(r"\breembolso\b", tipo_servico.strip(), re.IGNORECASE):
            tipo_servico = 'REEMBOLSO'

        # Formatar valor corretamente usando função auxiliar
        valor_formatado = formatar_valor_brasileiro(valor)

        texto_gerado = f"{nome_usuario}\t{valor_formatado}\t{data_criacao}\t{nome_fornecedor.upper()}\t{os_num}\t{agencia}\t{prefixo}\t{tipo_servico}\t{contrato}\t{tipo_pagamento.upper()}"
        self.saida_texto.delete("1.0", "end")
        self.saida_texto.insert("end", texto_gerado)
        pyperclip.copy(texto_gerado)

    def marcar_como_lido(self):
        if self.registro_atual:
            with sqlite3.connect(CAMINHO_BD) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE registros SET lido = 1 WHERE rowid = ?", (self.registro_atual,))
                conn.commit()
            
            # Notificação de sucesso
            self.notificacao.show_notification(
                f"Registro marcado como lido!",
                NotifyType.SUCCESS,
                bg_color="#404040", text_color="#FFFFFF"
            )
            
            # Atualizar interface
            self.lido_atual = 1  # Atualizar estado local
            self.botao_marcar_lido.grid_forget()
            self.botao_marcar_nao_lido.grid(row=5, column=0, sticky="w", padx=(10, 10), pady=(0, 10))
            
            # Recarregar dados para refletir mudança
            self.busca_por_data()

    def marcar_como_nao_lido(self):
        if self.registro_atual:
            with sqlite3.connect(CAMINHO_BD) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE registros SET lido = 0 WHERE rowid = ?", (self.registro_atual,))
                conn.commit()
            
            # Notificação de sucesso
            self.notificacao.show_notification(
                f"Registro marcado como não lido!",
                NotifyType.SUCCESS,
                bg_color="#404040", text_color="#FFFFFF"
            )
            
            # Atualizar interface
            self.lido_atual = 0  # Atualizar estado local
            self.botao_marcar_nao_lido.grid_forget()
            self.botao_marcar_lido.grid(row=5, column=0, sticky="w", padx=(10, 10), pady=(0, 10))
            
            # Recarregar dados para refletir mudança
            self.busca_por_data()

    def deletar_registro(self):
        if self.registro_atual:
            resposta = messagebox.askyesno("Confirmar", "Tem certeza que deseja deletar este registro?")
            if resposta:
                with sqlite3.connect(CAMINHO_BD) as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM registros WHERE rowid = ?", (self.registro_atual,))
                    conn.commit()
                    self.notificacao.show_notification(
                        f"Registro deletado com sucesso!",
                        NotifyType.SUCCESS,
                        bg_color="#404040",text_color="#FFFFFF"
                    )
                self.botao_marcar_lido.grid_forget()
                self.botao_marcar_nao_lido.grid_forget()
                self.botao_deletar.grid_forget()
                self.busca_por_data()

    def atualizar_status_fila_manual(self):
        """
        Atualiza o status da fila de requisições manualmente (sem auto-refresh).
        
        Esta função é chamada apenas quando o usuário clica no botão "Atualizar Status"
        ou quando a interface é inicializada, garantindo controle total sobre quando
        verificar o status da fila.
        """
        try:
            # Obter informações da fila
            info_fila = obter_info_fila_para_interface()
            
            # Atualizar texto do label com emoji e status
            texto_status = f"{info_fila['icone']} Fila: {info_fila['status']}"
            self.label_status_fila.configure(text=texto_status)
            
            # Atualizar texto do botão com a quantidade de requisições pendentes
            if info_fila['total_pendentes'] > 0:
                self.botao_processar_fila.configure(text=f"Processar Fila ({info_fila['total_pendentes']})")
            else:
                self.botao_processar_fila.configure(text="Processar Fila (0)")
                
            # Exibir notificação sobre o status
            if info_fila['total_pendentes'] == 0:
                self.notificacao.show_notification(
                    "Fila vazia - todos os registros processados",
                    NotifyType.INFO,
                    bg_color="#404040", text_color="#FFFFFF"
                )
            elif info_fila['total_pendentes'] > 20:
                self.notificacao.show_notification(
                    f"ATENÇÃO: {info_fila['total_pendentes']} requisições pendentes!",
                    NotifyType.WARNING,
                    bg_color="#404040", text_color="#FFFFFF"
                )
            else:
                self.notificacao.show_notification(
                    f"{info_fila['icone']} {info_fila['total_pendentes']} requisições na fila",
                    NotifyType.INFO,
                    bg_color="#404040", text_color="#FFFFFF"
                )
            
        except Exception as e:
            print(f"Erro ao atualizar status da fila: {e}")
            self.label_status_fila.configure(text="Erro ao verificar fila")
            self.botao_processar_fila.configure(text="Processar Fila (?)")
            self.notificacao.show_notification(
                f"Erro ao verificar fila: {str(e)}",
                NotifyType.ERROR,
                bg_color="#404040", text_color="#FFFFFF"
            )
            salvar_erro(self.nome_usuario, f"Erro ao atualizar status da fila: {e}")

    def processar_fila_requisicoes(self):
        """
        Processa a fila de requisições com confirmação do usuário.
        
        Como esta aba já possui controle de acesso restrito, não é necessário
        verificar autorização novamente. Apenas solicita confirmação e processa.
        """
        try:
            # Atualizar status antes de processar
            self.atualizar_status_fila_manual()
            
            # Obter status atual da fila
            status_fila = verificar_status_fila()
            
            if 'erro' in status_fila:
                messagebox.showerror("Erro", "Erro ao verificar status da fila:\n" + status_fila['erro'])
                salvar_erro(self.nome_usuario, f"Erro ao verificar status da fila: {status_fila['erro']}")
                return
                
            pendentes = status_fila['pendentes']
            
            if pendentes == 0:
                messagebox.showinfo("Fila Vazia", "Não há requisições pendentes para processar.")
                return
            
            # Confirmar processamento com o usuário
            resposta = messagebox.askyesno(
                "Confirmar Processamento",
                f"Processar {pendentes} requisições pendentes na fila?\n\n"
                f"Esta operação irá:\n"
                f"• Ler todos os arquivos JSON da fila\n"
                f"• Inserir os dados no banco principal\n"
                f"• Marcar os arquivos como processados\n\n"
                f"Deseja continuar?"
            )
            
            if not resposta:
                return
            
            # Mostrar janela de progresso
            janela_progresso = self.criar_janela_progresso()
            
            # Executar processamento em thread separada para não travar a interface
            import threading
            thread_processamento = threading.Thread(
                target=self.executar_processamento_fila,
                args=(janela_progresso, pendentes)
            )
            thread_processamento.start()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar fila: {e}")
            salvar_erro(self.nome_usuario, f"Erro ao processar fila: {e}")

    def criar_janela_progresso(self):
        """
        Cria janela de progresso para mostrar o status do processamento.
        
        Returns:
            dict: Dicionário com referências aos widgets da janela de progresso
        """
        # Criar janela de progresso
        janela = ctk.CTkToplevel(self.root)
        janela.title("Processando Fila")
        janela.geometry("400x200")
        janela.resizable(False, False)
        
        # Centralizar janela
        janela.transient(self.root)
        janela.grab_set()
        
        # Label de status
        label_status = ctk.CTkLabel(janela, text="Iniciando processamento...", font=ctk.CTkFont(size=14))
        label_status.pack(pady=20)
        
        # Barra de progresso
        progress_bar = ctk.CTkProgressBar(janela, width=300)
        progress_bar.pack(pady=10)
        progress_bar.set(0)
        
        # Label de detalhes
        label_detalhes = ctk.CTkLabel(janela, text="", font=ctk.CTkFont(size=12))
        label_detalhes.pack(pady=10)
        
        # Botão para fechar (inicialmente desabilitado)
        botao_fechar = ctk.CTkButton(janela, text="Fechar", command=janela.destroy, state="disabled")
        botao_fechar.pack(pady=20)
        
        return {
            'janela': janela,
            'label_status': label_status,
            'progress_bar': progress_bar,
            'label_detalhes': label_detalhes,
            'botao_fechar': botao_fechar
        }

    def executar_processamento_fila(self, widgets_progresso, total_requisicoes):
        """
        Executa o processamento da fila em thread separada.
        
        Args:
            widgets_progresso (dict): Widgets da janela de progresso
            total_requisicoes (int): Total de requisições a processar
        """
        try:
            try:
                from .bd.processar_fila import obter_arquivos_pendentes, processar_requisicao_individual, marcar_como_processado
            except ImportError:
                try:
                    from app.bd.processar_fila import obter_arquivos_pendentes, processar_requisicao_individual, marcar_como_processado
                except ImportError:
                    import sys
                    import os
                    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
                    from bd.processar_fila import obter_arquivos_pendentes, processar_requisicao_individual, marcar_como_processado
            
            # Atualizar status inicial
            widgets_progresso['label_status'].configure(text="Obtendo arquivos da fila...")
            
            # Obter arquivos pendentes
            arquivos_pendentes = obter_arquivos_pendentes()
            
            if not arquivos_pendentes:
                widgets_progresso['label_status'].configure(text="✅ Nenhuma requisição pendente encontrada")
                widgets_progresso['botao_fechar'].configure(state="normal")
                return
            
            processadas = 0
            erros = 0
            
            # Processar cada arquivo
            for i, caminho_arquivo in enumerate(arquivos_pendentes):
                try:
                    # Atualizar progresso
                    progresso = i / len(arquivos_pendentes)
                    widgets_progresso['progress_bar'].set(progresso)
                    
                    # Carregar dados do arquivo
                    import json
                    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                        requisicao = json.load(f)
                    
                    id_req = requisicao.get('id', 'unknown')[:8]
                    usuario = requisicao.get('nome_usuario', 'N/A')
                    
                    # Atualizar status
                    widgets_progresso['label_status'].configure(
                        text=f"Processando requisição {i+1}/{len(arquivos_pendentes)}"
                    )
                    widgets_progresso['label_detalhes'].configure(
                        text=f"ID: {id_req} | Usuário: {usuario}"
                    )
                    
                    # Processar requisição
                    if processar_requisicao_individual(requisicao):
                        marcar_como_processado(caminho_arquivo)
                        processadas += 1
                    else:
                        erros += 1
                        
                except Exception as e:
                    erros += 1
                    print(f"Erro ao processar arquivo {caminho_arquivo}: {e}")
            
            # Finalizar processamento
            widgets_progresso['progress_bar'].set(1.0)
            
            if erros == 0:
                widgets_progresso['label_status'].configure(text="Processamento concluído com sucesso!")
                widgets_progresso['label_detalhes'].configure(
                    text=f"{processadas} requisições processadas"
                )
                
                # Mostrar notificação de sucesso
                self.root.after(0, lambda: self.notificacao.show_notification(
                    f"Fila processada com sucesso! {processadas} requisições",
                    NotifyType.SUCCESS,
                    bg_color="#404040", text_color="#FFFFFF"
                ))
            else:
                widgets_progresso['label_status'].configure(text="⚠️ Processamento concluído com erros")
                widgets_progresso['label_detalhes'].configure(
                    text=f"✅ {processadas} processadas | ❌ {erros} erros"
                )
                
                # Mostrar notificação de aviso
                self.root.after(0, lambda: self.notificacao.show_notification(
                    f"Fila processada com {erros} erros. {processadas} requisições processadas",
                    NotifyType.WARNING,
                    bg_color="#404040", text_color="#FFFFFF"
                ))
                salvar_erro(self.nome_usuario, f"Fila processada com {erros} erros. {processadas} requisições processadas")

            # Habilitar botão de fechar
            widgets_progresso['botao_fechar'].configure(state="normal")
            
            # Atualizar status da fila na interface principal após 2 segundos
            self.root.after(2000, self.atualizar_status_fila_manual)

        except Exception as e:
            # Erro durante processamento
            widgets_progresso['label_status'].configure(text="❌ Erro durante processamento")
            widgets_progresso['label_detalhes'].configure(text=f"Erro: {str(e)}")
            widgets_progresso['botao_fechar'].configure(state="normal")

            # Mostrar notificação de erro
            self.root.after(0, lambda: self.notificacao.show_notification(
                f"Erro ao processar fila: {str(e)}",
                NotifyType.ERROR,
                bg_color="#404040", text_color="#FFFFFF"
            ))
            salvar_erro(self.nome_usuario, f"Erro ao processar fila: {str(e)}")

    def mostrar_detalhes_fila(self):
        """
        Mostra uma janela com detalhes das requisições na fila.

        Exibe informações detalhadas sobre as requisições pendentes,
        incluindo usuário, timestamp e tipo de serviço.
        """
        try:
            try:
                from .bd.processar_fila import obter_arquivos_pendentes
            except ImportError:
                try:
                    from app.bd.processar_fila import obter_arquivos_pendentes
                except ImportError:
                    import sys
                    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
                    from bd.processar_fila import obter_arquivos_pendentes

            # Obter arquivos pendentes
            arquivos_pendentes = obter_arquivos_pendentes()
            
            if not arquivos_pendentes:
                messagebox.showinfo("Fila Vazia", "Não há requisições pendentes na fila.")
                return
            
            # Criar janela de detalhes
            janela_detalhes = ctk.CTkToplevel(self.root)
            janela_detalhes.title(f"Detalhes da Fila - {len(arquivos_pendentes)} requisições")
            janela_detalhes.geometry("800x600")
            janela_detalhes.resizable(True, True)
            
            # Centralizar janela
            janela_detalhes.transient(self.root)
            
            # Frame principal com scroll
            frame_scroll = ctk.CTkScrollableFrame(janela_detalhes)
            frame_scroll.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Título
            titulo = ctk.CTkLabel(
                frame_scroll, 
                text=f"Requisições Pendentes na Fila ({len(arquivos_pendentes)})",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            titulo.pack(pady=(0, 20))
            
            # Listar requisições
            for i, caminho_arquivo in enumerate(arquivos_pendentes, 1):
                try:
                    import json
                    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                        dados = json.load(f)
                    
                    # Frame para cada requisição
                    frame_req = ctk.CTkFrame(frame_scroll)
                    frame_req.pack(fill="x", pady=5, padx=5)
                    
                    # Informações principais
                    id_req = dados.get('id', 'unknown')[:8]
                    usuario = dados.get('nome_usuario', 'N/A')
                    tipo_servico = dados.get('tipo_servico', 'N/A')
                    fornecedor = dados.get('nome_fornecedor', 'N/A')
                    valor = dados.get('valor', 0)
                    timestamp = dados.get('timestamp', 'N/A')[:19].replace('T', ' ')
                    
                    # Label principal
                    texto_principal = f"{i:2d}. ID: {id_req} | {usuario} | {tipo_servico}"
                    label_principal = ctk.CTkLabel(
                        frame_req, 
                        text=texto_principal,
                        font=ctk.CTkFont(size=12, weight="bold"),
                        anchor="w"
                    )
                    label_principal.pack(fill="x", padx=10, pady=(10, 5))
                    
                    # Formatar valor para exibição usando função auxiliar
                    valor_exibicao = formatar_valor_brasileiro(valor)
                    
                    # Label secundário
                    texto_secundario = f"     Fornecedor: {fornecedor} | Valor: R$ {valor_exibicao} | Data: {timestamp}"
                    label_secundario = ctk.CTkLabel(
                        frame_req, 
                        text=texto_secundario,
                        font=ctk.CTkFont(size=10),
                        anchor="w",
                        text_color="gray"
                    )
                    label_secundario.pack(fill="x", padx=10, pady=(0, 10))
                    
                except Exception as e:
                    # Frame para erro
                    frame_erro = ctk.CTkFrame(frame_scroll)
                    frame_erro.pack(fill="x", pady=5, padx=5)
                    
                    label_erro = ctk.CTkLabel(
                        frame_erro, 
                        text=f"{i:2d}. ❌ Erro ao ler arquivo: {os.path.basename(caminho_arquivo)}",
                        font=ctk.CTkFont(size=12),
                        anchor="w"
                    )
                    label_erro.pack(fill="x", padx=10, pady=10)
            
            # Botão para fechar
            botao_fechar = ctk.CTkButton(
                janela_detalhes, 
                text="Fechar", 
                command=janela_detalhes.destroy
            )
            botao_fechar.pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao mostrar detalhes da fila: {e}")
            salvar_erro(self.nome_usuario, f"Erro ao mostrar detalhes da fila: {e}")
