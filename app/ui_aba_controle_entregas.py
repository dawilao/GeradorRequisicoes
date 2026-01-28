import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
import os
import time

try:
    from .bd.utils_bd import DatabaseManager as DBManager
    from .bd.utils_bd import acessa_bd_contratos
    from .CTkFloatingNotifications import NotificationManager, NotifyType
except ImportError:
    from bd.utils_bd import DatabaseManager as DBManager
    from bd.utils_bd import acessa_bd_contratos
    from CTkFloatingNotifications import NotificationManager, NotifyType

class DatabaseManagerEntregas:
    """Gerenciador de banco de dados SQLite para Entregas"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.criar_tabelas()
    
    def get_connection(self):
        """Cria uma conexão com o banco de dados"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        return sqlite3.connect(self.db_path)
    
    def criar_tabelas(self):
        """Cria as tabelas necessárias se não existirem"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabela de entregas (usa nome do contrato diretamente)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entregas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_contrato TEXT NOT NULL,
                nome_agencia TEXT NOT NULL,
                os TEXT NOT NULL,
                descricao_produto TEXT,
                data_entrega TEXT NOT NULL,
                usuario TEXT NOT NULL,
                data_cadastro TEXT NOT NULL,
                excluido INTEGER DEFAULT 0,
                data_exclusao TEXT,
                requisicao_omie TEXT
            )
        ''')
        
        # Adicionar colunas excluido, data_exclusao e requisicao_omie se não existirem (migração)
        cursor.execute("PRAGMA table_info(entregas)")
        colunas = [col[1] for col in cursor.fetchall()]
        if 'excluido' not in colunas:
            cursor.execute("ALTER TABLE entregas ADD COLUMN excluido INTEGER DEFAULT 0")
        if 'data_exclusao' not in colunas:
            cursor.execute("ALTER TABLE entregas ADD COLUMN data_exclusao TEXT")
        if 'requisicao_omie' not in colunas:
            cursor.execute("ALTER TABLE entregas ADD COLUMN requisicao_omie TEXT")
        
        # Tabela de histórico de alertas de e-mail
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historico_alertas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_envio TEXT NOT NULL,
                entregas_alertadas TEXT NOT NULL,
                data_hora_envio TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def inserir_entrega(self, nome_contrato, nome_agencia, os, descricao_produto, data_entrega, usuario, requisicao_omie=None):
        """Insere uma nova entrega no banco de dados"""
        conn = self.get_connection()
        cursor = conn.cursor()
        data_cadastro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute('''
            INSERT INTO entregas (nome_contrato, nome_agencia, os, descricao_produto, data_entrega, usuario, data_cadastro, requisicao_omie)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nome_contrato, nome_agencia, os, descricao_produto, data_entrega, usuario, data_cadastro, requisicao_omie))
        
        conn.commit()
        conn.close()
    
    def obter_entregas(self):
        """Retorna todas as entregas não excluídas"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, nome_contrato, nome_agencia, os, descricao_produto, data_entrega, usuario, requisicao_omie
            FROM entregas
            WHERE excluido = 0
            ORDER BY data_entrega ASC
        ''')
        entregas = cursor.fetchall()
        conn.close()
        return entregas
    
    def obter_entregas_excluidas(self):
        """Retorna todas as entregas na lixeira"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, nome_contrato, nome_agencia, os, descricao_produto, data_entrega, usuario, data_exclusao, requisicao_omie
            FROM entregas
            WHERE excluido = 1
            ORDER BY data_exclusao DESC
        ''')
        entregas = cursor.fetchall()
        conn.close()
        return entregas
    
    def deletar_entrega(self, entrega_id):
        """Move uma entrega para a lixeira (exclusão lógica)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        data_exclusao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            UPDATE entregas 
            SET excluido = 1, data_exclusao = ?
            WHERE id = ?
        """, (data_exclusao, entrega_id))
        conn.commit()
        conn.close()
    
    def restaurar_entrega(self, entrega_id):
        """Restaura uma entrega da lixeira"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE entregas 
            SET excluido = 0, data_exclusao = NULL
            WHERE id = ?
        """, (entrega_id,))
        conn.commit()
        conn.close()
    
    def deletar_permanentemente(self, entrega_id):
        """Remove uma entrega permanentemente do banco de dados"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM entregas WHERE id = ?", (entrega_id,))
        conn.commit()
        conn.close()
    
    def atualizar_entrega(self, entrega_id, nome_contrato, nome_agencia, os, descricao_produto, data_entrega, requisicao_omie=None):
        """Atualiza uma entrega existente no banco de dados"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE entregas 
            SET nome_contrato = ?, nome_agencia = ?, os = ?, descricao_produto = ?, data_entrega = ?, requisicao_omie = ?
            WHERE id = ?
        ''', (nome_contrato, nome_agencia, os, descricao_produto, data_entrega, requisicao_omie, entrega_id))
        conn.commit()
        conn.close()
    
    def verificar_alerta_enviado_hoje(self):
        """Verifica se já foi enviado um alerta hoje"""
        conn = self.get_connection()
        cursor = conn.cursor()
        hoje = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("SELECT id FROM historico_alertas WHERE data_envio = ?", (hoje,))
        resultado = cursor.fetchone()
        conn.close()
        return resultado is not None
    
    def registrar_envio_alerta(self, entregas_ids):
        """Registra o envio de um alerta no histórico"""
        conn = self.get_connection()
        cursor = conn.cursor()
        hoje = datetime.now().strftime("%Y-%m-%d")
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entregas_str = ",".join(map(str, entregas_ids))
        
        cursor.execute('''
            INSERT INTO historico_alertas (data_envio, entregas_alertadas, data_hora_envio)
            VALUES (?, ?, ?)
        ''', (hoje, entregas_str, agora))
        
        conn.commit()
        conn.close()


class EmailManager:
    """Gerenciador de envio de e-mails"""
    
    def __init__(self, smtp_server="smtp.kinghost.net", smtp_port=465, db_manager=None):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email_remetente = "dawison@machengenharia.com.br"
        self.senha = "Mach@123"
        self.email_destinatario = "setordecompras@machengenharia.com.br"
        self.db_manager = db_manager
    
    def verificar_entregas_proximas(self, entregas):
        """Verifica se há entregas atrasadas ou nos próximos 3 dias"""
        hoje = datetime.now().date()
        limite = hoje + timedelta(days=3)
        entregas_alertar = []
        
        for entrega in entregas:
            try:
                data_entrega = datetime.strptime(entrega[5], "%Y-%m-%d").date()
                # Incluir entregas atrasadas ou próximas (até 3 dias)
                if data_entrega <= limite:
                    entregas_alertar.append(entrega)
            except ValueError:
                continue
        
        return entregas_alertar
    
    def enviar_alerta(self, entregas_proximas, force_send=False):
        """Envia e-mail de alerta sobre entregas próximas"""
        if not entregas_proximas:
            return False, "Nenhuma entrega próxima para alertar."
        
        # Verificar se já foi enviado alerta hoje
        if self.db_manager and self.db_manager.verificar_alerta_enviado_hoje() and not force_send:
            return False, "Já foi enviado um alerta hoje. Próximo envio será amanhã."
        
        try:
            # Separar entregas atrasadas das próximas
            hoje = datetime.now().date()
            entregas_atrasadas = []
            entregas_proximas_real = []
            
            for entrega in entregas_proximas:
                data_entrega = datetime.strptime(entrega[5], "%Y-%m-%d").date()
                if data_entrega < hoje:
                    entregas_atrasadas.append(entrega)
                else:
                    entregas_proximas_real.append(entrega)
            
            total_alertas = len(entregas_atrasadas) + len(entregas_proximas_real)
            
            mensagem = MIMEMultipart()
            mensagem['From'] = self.email_remetente
            mensagem['To'] = self.email_destinatario
            mensagem['Subject'] = f"⚠️ ALERTA: {total_alertas} Entrega(s) - {len(entregas_atrasadas)} Atrasada(s)"
            
            corpo = """
            <html>
                <head>
                    <style>
                        body { font-family: Arial, sans-serif; color: #333; }
                        .header { background-color: #ff6b6b; color: white; padding: 20px; text-align: center; border-radius: 5px; }
                        .header-atrasadas { background-color: #d32f2f; color: white; padding: 15px; text-align: center; border-radius: 5px; margin-top: 20px; }
                        .header-proximas { background-color: #ff9800; color: white; padding: 15px; text-align: center; border-radius: 5px; margin-top: 20px; }
                        .content { padding: 20px; }
                        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                        th { background-color: #4CAF50; color: white; padding: 12px; text-align: left; font-weight: bold; }
                        .th-atrasado { background-color: #d32f2f !important; }
                        .th-proximo { background-color: #ff9800 !important; }
                        td { padding: 10px; border-bottom: 1px solid #ddd; }
                        tr:hover { background-color: #f5f5f5; }
                        .urgente { color: #d32f2f; font-weight: bold; }
                        .atrasado { background-color: #ffebee !important; }
                        .footer { margin-top: 30px; padding: 15px; background-color: #f5f5f5; border-radius: 5px; font-size: 12px; color: #666; }
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>⚠️ ALERTA DE ENTREGAS</h1>
                        <p>Total: """ + f"{total_alertas}" + """ entrega(s) | Atrasadas: """ + f"{len(entregas_atrasadas)}" + """ | Próximas: """ + f"{len(entregas_proximas_real)}" + """</p>
                    </div>
                    <div class="content">
            """
            
            # Seção de entregas ATRASADAS
            if entregas_atrasadas:
                corpo += """
                        <div class="header-atrasadas">
                            <h2>🚨 ENTREGAS ATRASADAS (""" + f"{len(entregas_atrasadas)}" + """)</h2>
                        </div>
                        <table>
                            <thead>
                                <tr>
                                    <th class="th-atrasado">Contrato</th>
                                    <th class="th-atrasado">Agência</th>
                                    <th class="th-atrasado">OS</th>
                                    <th class="th-atrasado">Requisição OMIE</th>
                                    <th class="th-atrasado">Produto</th>
                                    <th class="th-atrasado">Responsável</th>
                                    <th class="th-atrasado">Data de Entrega</th>
                                    <th class="th-atrasado">Dias Atrasados</th>
                                </tr>
                            </thead>
                            <tbody>
                """
                
                for entrega in entregas_atrasadas:
                    data_formatada = datetime.strptime(entrega[5], "%Y-%m-%d").strftime("%d/%m/%Y")
                    produto = entrega[4] if entrega[4] else "Não especificado"
                    requisicao_omie = entrega[7] if len(entrega) > 7 and entrega[7] else "-"
                    data_entrega = datetime.strptime(entrega[5], "%Y-%m-%d").date()
                    dias_atrasados = (hoje - data_entrega).days
                    
                    corpo += f"""
                                    <tr class="atrasado">
                                        <td><strong>{entrega[1]}</strong></td>
                                        <td>{entrega[2]}</td>
                                        <td>{entrega[3]}</td>
                                        <td>{requisicao_omie}</td>
                                        <td>{produto}</td>
                                        <td>{entrega[6]}</td>
                                        <td class="urgente">{data_formatada}</td>
                                        <td class="urgente">{dias_atrasados} dia(s)</td>
                                    </tr>
                    """
                
                corpo += """
                            </tbody>
                        </table>
                """
            
            # Seção de entregas PRÓXIMAS
            if entregas_proximas_real:
                corpo += """
                        <div class="header-proximas">
                            <h2>⏰ ENTREGAS PRÓXIMAS (3 dias ou menos) - """ + f"{len(entregas_proximas_real)}" + """</h2>
                        </div>
                        <table>
                            <thead>
                                <tr>
                                    <th class="th-proximo">Contrato</th>
                                    <th class="th-proximo">Agência</th>
                                    <th class="th-proximo">OS</th>
                                    <th class="th-proximo">Requisição OMIE</th>
                                    <th class="th-proximo">Produto</th>
                                    <th class="th-proximo">Responsável</th>
                                    <th class="th-proximo">Data de Entrega</th>
                                    <th class="th-proximo">Dias Restantes</th>
                                </tr>
                            </thead>
                            <tbody>
                """
                
                for entrega in entregas_proximas_real:
                    data_formatada = datetime.strptime(entrega[5], "%Y-%m-%d").strftime("%d/%m/%Y")
                    produto = entrega[4] if entrega[4] else "Não especificado"
                    requisicao_omie = entrega[7] if len(entrega) > 7 and entrega[7] else "-"
                    data_entrega = datetime.strptime(entrega[5], "%Y-%m-%d").date()
                    dias_restantes = (data_entrega - hoje).days
                    
                    classe_urgencia = "urgente" if dias_restantes <= 1 else ""
                    texto_dias = "HOJE!" if dias_restantes == 0 else f"{dias_restantes} dia(s)"
                    
                    corpo += f"""
                                    <tr>
                                        <td><strong>{entrega[1]}</strong></td>
                                        <td>{entrega[2]}</td>
                                        <td>{entrega[3]}</td>
                                        <td>{requisicao_omie}</td>
                                        <td>{produto}</td>
                                        <td>{entrega[6]}</td>
                                        <td class="{classe_urgencia}">{data_formatada}</td>
                                        <td class="{classe_urgencia}">{texto_dias}</td>
                                    </tr>
                    """
                
                corpo += """
                            </tbody>
                        </table>
                """
            
            corpo += """
                        <div class="footer">
                            <p><strong>⚠️ ATENÇÃO:</strong> Este é um e-mail automático do sistema de gestão de entregas.</p>
                            <p><strong>Entregas atrasadas</strong> requerem ação imediata!</p>
                            <p><strong>Entregas próximas</strong> devem ser priorizadas para evitar atrasos.</p>
                            <p>Por favor, verifique os prazos e tome as ações necessárias.</p>
                        </div>
                    </div>
                </body>
            </html>
            """
            
            mensagem.attach(MIMEText(corpo, 'html'))
            
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as servidor:
                servidor.login(self.email_remetente, self.senha)
                servidor.send_message(mensagem)
            
            # Registrar envio no histórico
            if self.db_manager:
                entregas_ids = [entrega[0] for entrega in entregas_proximas]
                self.db_manager.registrar_envio_alerta(entregas_ids)
            
            print("E-mail de alerta enviado com sucesso!")
            return True, f"Alerta enviado com sucesso para {len(entregas_proximas)} entrega(s)!"
            
        except Exception as e:
            erro_msg = f"Erro ao enviar e-mail: {str(e)}"
            print(erro_msg)
            return False, erro_msg


class EntregaCard(ctk.CTkFrame):
    """Card individual para exibição de entrega"""
    
    def __init__(self, master, entrega_data, callback_delete, callback_edit, **kwargs):
        cor_status = self.obter_cor_status(entrega_data[5])
        
        super().__init__(master, corner_radius=10, fg_color=("gray95", "gray20"), **kwargs)
        
        self.entrega_id = entrega_data[0]
        self.entrega_data = entrega_data
        self.callback_delete = callback_delete
        self.callback_edit = callback_edit
        
        self.grid_columnconfigure(1, weight=1)
        
        # Barra lateral colorida de status
        frame_status = ctk.CTkFrame(self, width=6, corner_radius=8, fg_color=cor_status)
        frame_status.grid(row=0, column=0, sticky="ns", padx=(3, 0), pady=3)
        frame_status.grid_propagate(False)
        
        # Frame principal de conteúdo
        frame_conteudo = ctk.CTkFrame(self, fg_color="transparent")
        frame_conteudo.grid(row=0, column=1, sticky="ew", padx=8, pady=6)
        frame_conteudo.grid_columnconfigure(0, weight=1)
        
        # Linha 1: Contrato (título principal)
        titulo = ctk.CTkLabel(frame_conteudo, text=entrega_data[1].upper(), 
                             font=ctk.CTkFont(size=13, weight="bold"),
                             anchor="w")
        titulo.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # Linha 2: Agência e OS lado a lado
        frame_linha2 = ctk.CTkFrame(frame_conteudo, fg_color="transparent")
        frame_linha2.grid(row=1, column=0, sticky="w", pady=1)
        
        label_agencia = ctk.CTkLabel(frame_linha2, text=f"Agência: {entrega_data[2].upper()}",
                                     font=ctk.CTkFont(size=11))
        label_agencia.grid(row=0, column=0, sticky="w", padx=(0, 12))
        
        label_os = ctk.CTkLabel(frame_linha2, text=f"OS: {entrega_data[3]}",
                               font=ctk.CTkFont(size=11))
        label_os.grid(row=0, column=1, sticky="w")
        
        # Linha 3: Requisição OMIE (se existir)
        if len(entrega_data) > 7 and entrega_data[7]:
            label_req_omie = ctk.CTkLabel(frame_conteudo, 
                                         text=f"Requisição OMIE: {entrega_data[7]}",
                                         font=ctk.CTkFont(size=11),
                                         anchor="w")
            label_req_omie.grid(row=2, column=0, sticky="w", pady=1)
        
        # Linha 4: Produto (se existir)
        if entrega_data[4]:
            label_produto = ctk.CTkLabel(frame_conteudo, 
                                        text=f"Produto: {entrega_data[4].upper()}",
                                        font=ctk.CTkFont(size=11),
                                        anchor="w")
            label_produto.grid(row=3, column=0, sticky="w", pady=1)
        
        # Linha 5: Data de entrega com destaque
        data_formatada = datetime.strptime(entrega_data[5], "%Y-%m-%d").strftime("%d/%m/%Y")
        dias_restantes = self.calcular_dias_restantes(entrega_data[5])
        cor_texto_data = self.obter_cor_texto_data(entrega_data[5])
        
        frame_data = ctk.CTkFrame(frame_conteudo, fg_color="transparent")
        frame_data.grid(row=4, column=0, sticky="w", pady=(5, 2))
        
        label_data = ctk.CTkLabel(frame_data, text=f"Entrega: {data_formatada}",
                                 font=ctk.CTkFont(size=12, weight="bold"),
                                 text_color=cor_texto_data)
        label_data.grid(row=0, column=0, sticky="w", padx=(0, 8))
        
        label_status = ctk.CTkLabel(frame_data, text=dias_restantes,
                                   font=ctk.CTkFont(size=11, weight="bold"),
                                   text_color=cor_texto_data)
        label_status.grid(row=0, column=1, sticky="w")
        
        # Linha 6: Usuário
        usuario = ctk.CTkLabel(frame_conteudo, text=f"Cadastrado por: {entrega_data[6].upper()}", 
                              font=ctk.CTkFont(size=9),
                              text_color="gray")
        usuario.grid(row=5, column=0, sticky="w", pady=(3, 0))
        
        # Frame para botões à direita
        frame_botoes = ctk.CTkFrame(self, fg_color="transparent")
        frame_botoes.grid(row=0, column=2, padx=6, pady=6)
        
        btn_edit = ctk.CTkButton(frame_botoes, text="Editar", width=65, height=28,
                                command=self.editar, fg_color="#ff9800", hover_color="#f57c00",
                                font=ctk.CTkFont(size=11, weight="bold"))
        btn_edit.grid(row=0, column=0, pady=(0, 4))
        
        btn_delete = ctk.CTkButton(frame_botoes, text="Excluir", width=65, height=28,
                                   command=self.deletar, fg_color="#f44336", hover_color="#d32f2f",
                                   font=ctk.CTkFont(size=11, weight="bold"))
        btn_delete.grid(row=1, column=0)
    
    def obter_cor_status(self, data_entrega_str):
        """Retorna a cor de status baseada na urgência da entrega"""
        try:
            data_entrega = datetime.strptime(data_entrega_str, "%Y-%m-%d").date()
            hoje = datetime.now().date()
            diferenca = (data_entrega - hoje).days
            
            # Vermelho forte para atrasados
            if diferenca < 0:
                return "#d32f2f"
            # Laranja/vermelho para hoje e amanhã
            elif diferenca <= 1:
                return "#ff5722"
            # Laranja para próximos 2-3 dias
            elif diferenca <= 3:
                return "#ff9800"
            # Azul para futuro próximo (4-7 dias)
            elif diferenca <= 7:
                return "#2196F3"
            # Verde para futuro distante
            return "#4CAF50"
        except:
            return "gray"
    
    def obter_cor_texto_data(self, data_entrega_str):
        """Retorna a cor do texto da data baseada na urgência"""
        try:
            data_entrega = datetime.strptime(data_entrega_str, "%Y-%m-%d").date()
            hoje = datetime.now().date()
            diferenca = (data_entrega - hoje).days
            
            if diferenca < 0:
                return "#d32f2f"  # Vermelho para atrasados
            elif diferenca <= 1:
                return "#ff5722"  # Laranja forte para hoje/amanhã
            elif diferenca <= 3:
                return "#ff9800"  # Laranja para próximos
            return None  # Cor padrão para os demais
        except:
            return None
    
    def verificar_alerta(self, data_entrega_str):
        """Método legado - redireciona para obter_cor_status"""
        return self.obter_cor_status(data_entrega_str)
    
    def calcular_dias_restantes(self, data_entrega_str):
        """Calcula e retorna texto com dias restantes"""
        try:
            data_entrega = datetime.strptime(data_entrega_str, "%Y-%m-%d").date()
            hoje = datetime.now().date()
            diferenca = (data_entrega - hoje).days
            
            if diferenca < 0:
                return f"ATRASADO {abs(diferenca)} DIA(S)"
            elif diferenca == 0:
                return "ENTREGA HOJE!"
            elif diferenca == 1:
                return "AMANHÃ"
            elif diferenca <= 3:
                return f"{diferenca} DIAS"
            else:
                return f"{diferenca} DIAS"
        except:
            return "Data inválida"
    
    def editar(self):
        """Inicia o modo de edição"""
        self.callback_edit(self.entrega_data)
    
    def deletar(self):
        """Confirma e deleta a entrega"""
        resposta = messagebox.askyesno("Confirmar Exclusão", 
                                      "Deseja realmente excluir esta entrega?")
        if resposta:
            self.callback_delete(self.entrega_id)


class EntregaCardLixeira(ctk.CTkFrame):
    """Card individual para exibição de entrega na lixeira"""
    
    def __init__(self, master, entrega_data, callback_restaurar, callback_deletar_permanente, **kwargs):
        super().__init__(master, corner_radius=10, fg_color=("gray90", "gray25"), **kwargs)
        
        self.entrega_id = entrega_data[0]
        self.entrega_data = entrega_data
        self.callback_restaurar = callback_restaurar
        self.callback_deletar_permanente = callback_deletar_permanente
        
        self.grid_columnconfigure(1, weight=1)
        
        # Barra lateral cinza para indicar inativo
        frame_status = ctk.CTkFrame(self, width=6, corner_radius=8, fg_color="#9E9E9E")
        frame_status.grid(row=0, column=0, sticky="ns", padx=(3, 0), pady=3)
        frame_status.grid_propagate(False)
        
        # Frame principal de conteúdo
        frame_conteudo = ctk.CTkFrame(self, fg_color="transparent")
        frame_conteudo.grid(row=0, column=1, sticky="ew", padx=8, pady=6)
        frame_conteudo.grid_columnconfigure(0, weight=1)
        
        # Título
        titulo = ctk.CTkLabel(frame_conteudo, text=entrega_data[1].upper(), 
                             font=ctk.CTkFont(size=13, weight="bold"),
                             text_color="gray",
                             anchor="w")
        titulo.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # Agência e OS
        frame_linha2 = ctk.CTkFrame(frame_conteudo, fg_color="transparent")
        frame_linha2.grid(row=1, column=0, sticky="w", pady=1)
        
        label_agencia = ctk.CTkLabel(frame_linha2, text=f"Agência: {entrega_data[2].upper()}",
                                     font=ctk.CTkFont(size=11),
                                     text_color="gray")
        label_agencia.grid(row=0, column=0, sticky="w", padx=(0, 12))
        
        label_os = ctk.CTkLabel(frame_linha2, text=f"OS: {entrega_data[3]}",
                               font=ctk.CTkFont(size=11),
                               text_color="gray")
        label_os.grid(row=0, column=1, sticky="w")
        
        # Requisição OMIE (se existir)
        if len(entrega_data) > 8 and entrega_data[8]:
            label_req_omie = ctk.CTkLabel(frame_conteudo, 
                                         text=f"Requisição OMIE: {entrega_data[8]}",
                                         font=ctk.CTkFont(size=11),
                                         text_color="gray",
                                         anchor="w")
            label_req_omie.grid(row=2, column=0, sticky="w", pady=1)
        
        # Produto (se existir)
        if entrega_data[4]:
            label_produto = ctk.CTkLabel(frame_conteudo, 
                                        text=f"Produto: {entrega_data[4].upper()}",
                                        font=ctk.CTkFont(size=11),
                                        text_color="gray",
                                        anchor="w")
            label_produto.grid(row=3, column=0, sticky="w", pady=1)
        
        # Data de entrega
        data_formatada = datetime.strptime(entrega_data[5], "%Y-%m-%d").strftime("%d/%m/%Y")
        label_data = ctk.CTkLabel(frame_conteudo, text=f"Entrega: {data_formatada}",
                                 font=ctk.CTkFont(size=11),
                                 text_color="gray")
        label_data.grid(row=4, column=0, sticky="w", pady=(5, 2))
        
        # Data de exclusão
        if len(entrega_data) > 7 and entrega_data[7]:
            try:
                data_exclusao = datetime.strptime(entrega_data[7], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
                label_exclusao = ctk.CTkLabel(frame_conteudo, text=f"Excluído em: {data_exclusao}",
                                             font=ctk.CTkFont(size=9),
                                             text_color="darkgray")
                label_exclusao.grid(row=5, column=0, sticky="w", pady=(3, 0))
            except:
                pass
        
        # Frame para botões à direita
        frame_botoes = ctk.CTkFrame(self, fg_color="transparent")
        frame_botoes.grid(row=0, column=2, padx=6, pady=6)
        
        btn_restaurar = ctk.CTkButton(frame_botoes, text="Restaurar", width=70, height=28,
                                     command=self.restaurar, fg_color="#4CAF50", hover_color="#388E3C",
                                     font=ctk.CTkFont(size=10, weight="bold"))
        btn_restaurar.grid(row=0, column=0, pady=(0, 4))
        
        btn_delete = ctk.CTkButton(frame_botoes, text="Excluir", width=70, height=28,
                                   command=self.deletar_permanente, fg_color="#f44336", hover_color="#d32f2f",
                                   font=ctk.CTkFont(size=10, weight="bold"))
        btn_delete.grid(row=1, column=0)
    
    def restaurar(self):
        """Restaura a entrega"""
        self.callback_restaurar(self.entrega_id)
    
    def deletar_permanente(self):
        """Deleta permanentemente a entrega"""
        self.callback_deletar_permanente(self.entrega_id)


class AbaPrazoEntregas(ctk.CTkFrame):
    """Aba de gerenciamento de prazos de entregas"""
    
    def __init__(self, master, tela_para_notifcacao, tabview="CONTROLE ENTREGAS", nome_completo_usuario=None, contratos=None):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        
        self.root = tela_para_notifcacao
        self.tabview = tabview
        self.notification_manager = NotificationManager(self.root)

        self.nome_completo_usuario = nome_completo_usuario or "Usuário"
        
        # Caminho do banco de dados
        db_path = r"G:\Meu Drive\17 - MODELOS\PROGRAMAS\Gerador de Requisições\app\bd\prazo_entrega.db"
        
        # Inicializar gerenciadores
        self.db = DatabaseManagerEntregas(db_path)
        self.email_manager = EmailManager(db_manager=self.db)

        # Lista de contratos
        self.contratos = contratos
        
        # Controle de edição
        self.entrega_em_edicao = None  # Armazena o ID da entrega sendo editada
        
        # Modo de visualização
        self.modo_lixeira = False
        
        # Controle de pesquisa
        self.filtro_tipo = None  # 'os', 'contrato', 'requisicao_omie'
        self.filtro_termo = None
        
        # Criar interface
        self.criar_interface()
        
        # Carregar entregas
        self.carregar_entregas()
        
        # Verificar e enviar alertas automaticamente ao abrir o programa
        self.verificar_e_enviar_alertas_inicializacao()
    
    def validar_entrada_numerica(self, texto):
        """Valida se a entrada contém apenas números, ponto, barra ou está vazia"""
        if texto == "":
            return True
        # Permitir apenas números, ponto (.) e barra (/)
        caracteres_permitidos = set("0123456789./")
        return all(char in caracteres_permitidos for char in texto)
    
    def criar_interface(self):
        """Cria a interface gráfica"""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Painel lateral (Cadastro) - Scrollable para acessar todos os botões
        self.painel_cadastro = ctk.CTkScrollableFrame(self, width=320, corner_radius=0)
        self.painel_cadastro.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
        # ========== SEÇÃO: FORMULÁRIO DE CADASTRO ==========
        frame_form = ctk.CTkFrame(self.painel_cadastro, fg_color=("gray85", "gray25"), corner_radius=10)
        frame_form.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        
        titulo = ctk.CTkLabel(frame_form, text="CADASTRO DE ENTREGA", 
                             font=ctk.CTkFont(size=16, weight="bold"))
        titulo.grid(row=0, column=0, padx=15, pady=(15, 10))
        
        # Se contratos não foi passado, usar lista vazia
        if not self.contratos:
            self.contratos = []
        
        # Campo Contrato
        ctk.CTkLabel(frame_form, text="Contrato:", 
                    font=ctk.CTkFont(size=11, weight="bold")).grid(row=1, column=0, padx=15, pady=(8, 2), sticky="w")
        self.combo_contrato = ctk.CTkComboBox(frame_form, 
                                              values=self.contratos,
                                              width=260)
        self.combo_contrato.grid(row=2, column=0, padx=15, pady=(0, 8))
        
        # Campo Nome da Agência
        ctk.CTkLabel(frame_form, text="Agência:", 
                    font=ctk.CTkFont(size=11, weight="bold")).grid(row=3, column=0, padx=15, pady=(8, 2), sticky="w")
        self.entry_agencia = ctk.CTkEntry(frame_form, width=260, height=32)
        self.entry_agencia.grid(row=4, column=0, padx=15, pady=(0, 8))
        
        # Campo OS
        ctk.CTkLabel(frame_form, text="OS:", 
                    font=ctk.CTkFont(size=11, weight="bold")).grid(row=5, column=0, padx=15, pady=(8, 2), sticky="w")
        
        # Criar validação para aceitar apenas números, ponto e barra
        vcmd = (self.register(self.validar_entrada_numerica), '%P')
        self.entry_os = ctk.CTkEntry(frame_form, width=260, height=32, 
                                     placeholder_text="Ex: 123 ou 123/456 ou 123.456",
                                     validate="key", validatecommand=vcmd)
        self.entry_os.grid(row=6, column=0, padx=15, pady=(0, 8))
        
        # Campo Descrição do Produto
        ctk.CTkLabel(frame_form, text="Produto:", 
                    font=ctk.CTkFont(size=11, weight="bold")).grid(row=7, column=0, padx=15, pady=(8, 2), sticky="w")
        self.entry_descricao = ctk.CTkEntry(frame_form, width=260, height=32)
        self.entry_descricao.grid(row=8, column=0, padx=15, pady=(0, 8))
        
        # Campo Requisição OMIE
        ctk.CTkLabel(frame_form, text="Requisição OMIE:", 
                    font=ctk.CTkFont(size=11, weight="bold")).grid(row=9, column=0, padx=15, pady=(8, 2), sticky="w")
        
        # Criar validação para aceitar apenas números
        vcmd_omie = (self.register(lambda texto: texto == "" or texto.isdigit()), '%P')
        self.entry_req_omie = ctk.CTkEntry(frame_form, width=260, height=32, 
                                           placeholder_text="Digite apenas números",
                                           validate="key", validatecommand=vcmd_omie)
        self.entry_req_omie.grid(row=10, column=0, padx=15, pady=(0, 8))
        
        # Campo Data de Entrega
        ctk.CTkLabel(frame_form, text="Data de Entrega:", 
                    font=ctk.CTkFont(size=11, weight="bold")).grid(row=11, column=0, padx=15, pady=(8, 2), sticky="w")
        self.entry_data = ctk.CTkEntry(frame_form, width=260, height=32, placeholder_text="DD/MM/AAAA")
        self.entry_data.grid(row=12, column=0, padx=15, pady=(0, 8))
        
        # Campo Usuário (somente leitura)
        ctk.CTkLabel(frame_form, text="Responsável:", 
                    font=ctk.CTkFont(size=11, weight="bold")).grid(row=13, column=0, padx=15, pady=(8, 2), sticky="w")
        self.entry_usuario = ctk.CTkEntry(frame_form, width=260, height=32)
        self.entry_usuario.insert(0, self.nome_completo_usuario)
        self.entry_usuario.configure(state="disabled")
        self.entry_usuario.grid(row=14, column=0, padx=15, pady=(0, 12))
        
        # Botões de ação
        self.btn_cadastrar = ctk.CTkButton(frame_form, text="CADASTRAR", 
                                     command=self.cadastrar_ou_salvar_entrega, 
                                     height=40, width=260,
                                     font=ctk.CTkFont(size=13, weight="bold"))
        self.btn_cadastrar.grid(row=15, column=0, padx=15, pady=(5, 10))
        
        self.btn_cancelar = ctk.CTkButton(frame_form, text="CANCELAR", 
                                         command=self.cancelar_edicao, 
                                         height=36, width=260,
                                         fg_color="gray", hover_color="darkgray",
                                         font=ctk.CTkFont(size=12, weight="bold"))
        self.btn_cancelar.grid(row=16, column=0, padx=15, pady=(0, 15))
        self.btn_cancelar.grid_remove()  # Ocultar inicialmente
        
        # ========== SEÇÃO: ALERTAS AUTOMÁTICOS ==========
        frame_alertas = ctk.CTkFrame(self.painel_cadastro, fg_color=("gray85", "gray25"), corner_radius=10)
        frame_alertas.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")
        
        titulo_alertas = ctk.CTkLabel(frame_alertas, text="ALERTAS AUTOMÁTICOS", 
                                      font=ctk.CTkFont(size=13, weight="bold"))
        titulo_alertas.grid(row=0, column=0, padx=15, pady=(12, 8))
        
        self.label_status = ctk.CTkLabel(frame_alertas, 
                                        text="E-mails enviados ao abrir o programa",
                                        font=ctk.CTkFont(size=10),
                                        text_color="#4CAF50",
                                        wraplength=260)
        self.label_status.grid(row=1, column=0, padx=15, pady=(0, 10))
        
        btn_email = ctk.CTkButton(frame_alertas, text="Enviar Agora", 
                                 command=self.enviar_alertas_thread, 
                                 height=36, width=260,
                                 fg_color="#ff9800", hover_color="#f57c00",
                                 font=ctk.CTkFont(size=12, weight="bold"))
        btn_email.grid(row=2, column=0, padx=15, pady=(0, 12))
        
        # ========== SEÇÃO: GERENCIAMENTO ==========
        frame_gerenciamento = ctk.CTkFrame(self.painel_cadastro, fg_color=("gray85", "gray25"), corner_radius=10)
        frame_gerenciamento.grid(row=2, column=0, padx=15, pady=(0, 15), sticky="ew")
        
        titulo_gerenciamento = ctk.CTkLabel(frame_gerenciamento, text="GERENCIAMENTO", 
                                           font=ctk.CTkFont(size=13, weight="bold"))
        titulo_gerenciamento.grid(row=0, column=0, padx=15, pady=(12, 10))
        
        self.btn_lixeira = ctk.CTkButton(frame_gerenciamento, text="Lixeira", 
                                        command=self.alternar_lixeira, 
                                        height=36, width=260,
                                        fg_color="#757575", hover_color="#616161",
                                        font=ctk.CTkFont(size=12, weight="bold"))
        self.btn_lixeira.grid(row=1, column=0, padx=15, pady=(0, 12))
        
        # Painel principal (Visualização)
        self.painel_principal = ctk.CTkFrame(self, corner_radius=0)
        self.painel_principal.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.painel_principal.grid_rowconfigure(1, weight=1)
        self.painel_principal.grid_columnconfigure(0, weight=1)
        
        # Frame para título e botão de atualizar
        frame_topo = ctk.CTkFrame(self.painel_principal, fg_color="transparent")
        frame_topo.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        frame_topo.grid_columnconfigure(0, weight=1)
        
        self.titulo_lista = ctk.CTkLabel(frame_topo, text=f"({len(self.db.obter_entregas())}) Entregas Cadastradas", 
                                   font=ctk.CTkFont(size=24, weight="bold"))
        self.titulo_lista.grid(row=0, column=0, sticky="w")
        
        # Frame de pesquisa
        self.frame_pesquisa = ctk.CTkFrame(frame_topo, fg_color="transparent")
        self.frame_pesquisa.grid(row=0, column=1, padx=(10, 0))
        
        ctk.CTkLabel(self.frame_pesquisa, text="Pesquisar:", 
                    font=ctk.CTkFont(size=11)).grid(row=0, column=0, padx=(0, 5))
        
        self.combo_tipo_pesquisa = ctk.CTkComboBox(self.frame_pesquisa, 
                                                    values=["OS", "Contrato", "Requisição OMIE"],
                                                    width=140, height=35,
                                                    command=self.atualizar_placeholder_pesquisa)
        self.combo_tipo_pesquisa.set("OS")
        self.combo_tipo_pesquisa.grid(row=0, column=1, padx=(0, 5))
        
        self.entry_pesquisa = ctk.CTkEntry(self.frame_pesquisa, width=200, height=35,
                                           placeholder_text="Digite a OS")
        self.entry_pesquisa.grid(row=0, column=2, padx=(0, 5))
        self.entry_pesquisa.bind("<Return>", lambda e: self.pesquisar())
        
        btn_pesquisar = ctk.CTkButton(self.frame_pesquisa, text="Buscar", 
                                     command=self.pesquisar,
                                     width=80, height=35,
                                     fg_color="#4CAF50", hover_color="#388E3C")
        btn_pesquisar.grid(row=0, column=3, padx=(0, 5))
        
        btn_limpar = ctk.CTkButton(self.frame_pesquisa, text="Limpar", 
                                  command=self.limpar_pesquisa,
                                  width=80, height=35,
                                  fg_color="#757575", hover_color="#616161")
        btn_limpar.grid(row=0, column=4, padx=(0, 5))
        
        # Botão Atualizar
        btn_atualizar = ctk.CTkButton(self.frame_pesquisa, text="Atualizar", 
                                     command=self.atualizar_entregas,
                                     width=100, height=35,
                                     fg_color="#1f6aa5", hover_color="#144870")
        btn_atualizar.grid(row=0, column=5)
        
        self.scrollable_frame = ctk.CTkScrollableFrame(self.painel_principal, corner_radius=0)
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
    
    def atualizar_placeholder_pesquisa(self, escolha):
        """Atualiza o campo de pesquisa conforme o tipo selecionado"""
        # Destruir widget atual
        if hasattr(self, 'entry_pesquisa'):
            self.entry_pesquisa.destroy()
        
        if escolha == "Contrato":
            # Usar ComboBox com lista de contratos
            self.entry_pesquisa = ctk.CTkComboBox(self.frame_pesquisa, 
                                                  values=self.contratos if self.contratos else ["Nenhum contrato"],
                                                  width=200, height=35)
            if self.contratos:
                self.entry_pesquisa.set("Selecione um contrato")
        else:
            # Usar Entry normal com placeholder
            placeholders = {
                "OS": "Digite a OS",
                "Requisição OMIE": "Digite o número da requisição"
            }
            self.entry_pesquisa = ctk.CTkEntry(self.frame_pesquisa, width=200, height=35,
                                              placeholder_text=placeholders.get(escolha, "Digite o termo"))
        
        self.entry_pesquisa.grid(row=0, column=2, padx=(0, 5))
        self.entry_pesquisa.bind("<Return>", lambda e: self.pesquisar())
    
    def validar_data(self, data_str):
        """Valida e converte data de DD/MM/AAAA para AAAA-MM-DD"""
        try:
            data_obj = datetime.strptime(data_str, "%d/%m/%Y")
            return data_obj.strftime("%Y-%m-%d")
        except ValueError:
            return None
    
    def cadastrar_ou_salvar_entrega(self):
        """Cadastra uma nova entrega ou salva alterações de uma entrega em edição"""
        contrato_nome = self.combo_contrato.get()
        nome_agencia = self.entry_agencia.get().strip()
        os = self.entry_os.get().strip()
        descricao_produto = self.entry_descricao.get().strip()
        requisicao_omie = self.entry_req_omie.get().strip()
        data_entrega_input = self.entry_data.get().strip()
        
        # Se OS estiver vazia, definir como "SEM OS"
        if not os:
            os = "SEM OS"
        
        # Se Requisição OMIE estiver vazia, definir como None
        if not requisicao_omie:
            requisicao_omie = None
        
        if not all([contrato_nome, nome_agencia, data_entrega_input]):
            self.notification_manager.show_notification(
                "Os campos Contrato, Agência e Data devem ser preenchidos!",
                notify_type=NotifyType.ERROR,
                duration=5000
            )
            return
        
        data_entrega = self.validar_data(data_entrega_input)
        if not data_entrega:
            self.notification_manager.show_notification(
                "Data inválida! Use o formato DD/MM/AAAA",
                notify_type=NotifyType.ERROR,
                duration=5000
            )
            return
        
        try:
            if self.entrega_em_edicao:
                # Modo edição - atualizar entrega existente
                self.db.atualizar_entrega(self.entrega_em_edicao, contrato_nome, nome_agencia, 
                                         os, descricao_produto, data_entrega, requisicao_omie)
                self.notification_manager.show_notification(
                    "Entrega atualizada com sucesso!",
                    notify_type=NotifyType.SUCCESS,
                    duration=4000
                )
                self.cancelar_edicao()
            else:
                # Modo cadastro - inserir nova entrega
                self.db.inserir_entrega(contrato_nome, nome_agencia, os, descricao_produto, 
                                       data_entrega, self.nome_completo_usuario, requisicao_omie)
                self.notification_manager.show_notification(
                    "Entrega cadastrada com sucesso!",
                    notify_type=NotifyType.SUCCESS,
                    duration=4000
                )
                
                # Limpar campos
                self.entry_agencia.delete(0, 'end')
                self.entry_os.delete(0, 'end')
                self.entry_descricao.delete(0, 'end')
                self.entry_req_omie.delete(0, 'end')
                self.entry_data.delete(0, 'end')
            
            self.carregar_entregas()
            
        except Exception as e:
            self.notification_manager.show_notification(
                f"Erro ao processar entrega: {str(e)}",
                notify_type=NotifyType.ERROR,
                duration=6000
            )
    
    def calcular_prioridade_entrega(self, entrega):
        """Calcula a prioridade de uma entrega baseada na data de entrega
        Retorna um valor numérico onde menor = mais urgente"""
        try:
            data_entrega = datetime.strptime(entrega[5], "%Y-%m-%d").date()
            hoje = datetime.now().date()
            diferenca = (data_entrega - hoje).days
            
            # Atrasados: valores negativos (mais atrasado = mais urgente)
            # Próximos: valores positivos pequenos
            # Futuros: valores positivos maiores
            return diferenca
        except:
            return 9999  # Datas inválidas vão para o final
    
    def carregar_entregas(self):
        """Carrega e exibe todas as entregas ordenadas por urgência ou lixeira"""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        if self.modo_lixeira:
            entregas = self.db.obter_entregas_excluidas()
            mensagem_vazio = "Nenhuma entrega na lixeira."
        else:
            entregas = self.db.obter_entregas()
            mensagem_vazio = "Nenhuma entrega cadastrada ainda."
        
        # Aplicar filtro de pesquisa
        if self.filtro_tipo and self.filtro_termo:
            entregas_filtradas = []
            termo_lower = self.filtro_termo.lower()
            
            for entrega in entregas:
                if self.filtro_tipo == "os":
                    # Campo OS está no índice 3
                    if termo_lower in entrega[3].lower():
                        entregas_filtradas.append(entrega)
                elif self.filtro_tipo == "contrato":
                    # Campo nome_contrato está no índice 1
                    if termo_lower in entrega[1].lower():
                        entregas_filtradas.append(entrega)
                elif self.filtro_tipo == "requisicao_omie":
                    # Campo requisicao_omie está no índice 7 (entregas normais) ou 8 (lixeira)
                    idx_req = 8 if self.modo_lixeira else 7
                    if len(entrega) > idx_req and entrega[idx_req]:
                        if termo_lower in str(entrega[idx_req]).lower():
                            entregas_filtradas.append(entrega)
            
            entregas = entregas_filtradas
            if not entregas:
                tipo_nome = {"os": "OS", "contrato": "Contrato", "requisicao_omie": "Requisição OMIE"}
                mensagem_vazio = f"Nenhuma entrega encontrada para {tipo_nome.get(self.filtro_tipo, 'termo')}: '{self.filtro_termo}'."
        
        if not entregas:
            label_vazio = ctk.CTkLabel(self.scrollable_frame, 
                                      text=mensagem_vazio,
                                      font=ctk.CTkFont(size=14))
            label_vazio.grid(row=0, column=0, pady=50)
            return
        
        if self.modo_lixeira:
            # Modo lixeira - não ordenar, manter por data de exclusão
            for idx, entrega in enumerate(entregas):
                card = EntregaCardLixeira(self.scrollable_frame, entrega, 
                                         self.restaurar_entrega_callback, 
                                         self.deletar_permanentemente_callback)
                card.grid(row=idx, column=0, padx=8, pady=3, sticky="ew")
        else:
            # Modo normal - ordenar por prioridade (urgência)
            entregas_ordenadas = sorted(entregas, key=self.calcular_prioridade_entrega)
            for idx, entrega in enumerate(entregas_ordenadas):
                card = EntregaCard(self.scrollable_frame, entrega, self.deletar_entrega, self.iniciar_edicao)
                card.grid(row=idx, column=0, padx=8, pady=3, sticky="ew")
    
    def deletar_entrega(self, entrega_id):
        """Move uma entrega para a lixeira"""
        try:
            self.db.deletar_entrega(entrega_id)
            self.carregar_entregas()
            self.notification_manager.show_notification(
                "Entrega movida para a lixeira! Acesse a lixeira para restaurar ou excluir permanentemente.",
                notify_type=NotifyType.INFO,
                duration=5000
            )
        except Exception as e:
            self.notification_manager.show_notification(
                f"Erro ao mover entrega para lixeira: {str(e)}",
                notify_type=NotifyType.ERROR,
                duration=6000
            )
    
    def pesquisar(self):
        """Aplica filtro de pesquisa por OS, Contrato ou Requisição OMIE"""
        termo_pesquisa = self.entry_pesquisa.get()
        if isinstance(termo_pesquisa, str):
            termo_pesquisa = termo_pesquisa.strip()
        tipo_pesquisa = self.combo_tipo_pesquisa.get()
        
        if termo_pesquisa and termo_pesquisa not in ["Selecione um contrato", "Nenhum contrato"]:
            self.filtro_termo = termo_pesquisa
            
            # Mapear tipo de pesquisa
            if tipo_pesquisa == "OS":
                self.filtro_tipo = "os"
            elif tipo_pesquisa == "Contrato":
                self.filtro_tipo = "contrato"
            elif tipo_pesquisa == "Requisição OMIE":
                self.filtro_tipo = "requisicao_omie"
            
            self.carregar_entregas()
            
            # Atualizar título para indicar pesquisa ativa
            if not self.modo_lixeira:
                self.titulo_lista.configure(text=f"Resultados para {tipo_pesquisa}: {termo_pesquisa}")
        else:
            self.notification_manager.show_notification(
                f"Digite um termo para pesquisar por {tipo_pesquisa}.",
                notify_type=NotifyType.WARNING,
                duration=3000
            )
    
    def limpar_pesquisa(self):
        """Remove o filtro de pesquisa e recarrega todas as entregas"""
        self.filtro_tipo = None
        self.filtro_termo = None
        
        # Limpar campo de pesquisa baseado no tipo de widget
        if hasattr(self, 'entry_pesquisa'):
            if isinstance(self.entry_pesquisa, ctk.CTkComboBox):
                # ComboBox: resetar para placeholder
                if self.contratos:
                    self.entry_pesquisa.set("Selecione um contrato")
            else:
                # Entry: limpar texto
                self.entry_pesquisa.delete(0, 'end')
        
        self.carregar_entregas()
        # Restaurar título original
        if not self.modo_lixeira:
            self.titulo_lista.configure(text=f"({len(self.db.obter_entregas())}) Entregas Cadastradas")
    
    def atualizar_entregas(self):
        """Atualiza a lista de entregas"""
        self.carregar_entregas()
        self.notification_manager.show_notification(
            "Lista de entregas atualizada!",
            notify_type=NotifyType.INFO,
            duration=2000
        )
        # Feedback no console também
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Lista de entregas atualizada")
    
    def iniciar_edicao(self, entrega_data):
        """Inicia o modo de edição preenchendo o formulário com os dados da entrega"""
        # Armazenar ID da entrega em edição
        self.entrega_em_edicao = entrega_data[0]
        
        # Preencher campos com dados da entrega
        self.combo_contrato.set(entrega_data[1])
        self.entry_agencia.delete(0, 'end')
        self.entry_agencia.insert(0, entrega_data[2])
        self.entry_os.delete(0, 'end')
        self.entry_os.insert(0, entrega_data[3])
        self.entry_descricao.delete(0, 'end')
        self.entry_descricao.insert(0, entrega_data[4] if entrega_data[4] else "")
        self.entry_req_omie.delete(0, 'end')
        self.entry_req_omie.insert(0, entrega_data[7] if len(entrega_data) > 7 and entrega_data[7] else "")
        self.entry_data.delete(0, 'end')
        # Converter data de AAAA-MM-DD para DD/MM/AAAA
        data_formatada = datetime.strptime(entrega_data[5], "%Y-%m-%d").strftime("%d/%m/%Y")
        self.entry_data.insert(0, data_formatada)
        
        # Alterar aparência do botão e mostrar botão cancelar
        self.btn_cadastrar.configure(text="SALVAR", fg_color="#ff9800", hover_color="#f57c00")
        self.btn_cancelar.grid()  # Mostrar botão cancelar
        
        # Scroll para o topo do painel de cadastro
        self.painel_cadastro.focus_set()
    
    def cancelar_edicao(self):
        """Cancela o modo de edição e limpa o formulário"""
        # Resetar controle de edição
        self.entrega_em_edicao = None
        
        # Limpar campos
        self.combo_contrato.set(self.contratos[0] if self.contratos else "")
        self.entry_agencia.delete(0, 'end')
        self.entry_os.delete(0, 'end')
        self.entry_descricao.delete(0, 'end')
        self.entry_req_omie.delete(0, 'end')
        self.entry_data.delete(0, 'end')
        
        # Restaurar aparência do botão e ocultar botão cancelar
        self.btn_cadastrar.configure(text="CADASTRAR", fg_color=["#3B8ED0", "#1F6AA5"], hover_color=["#36719F", "#144870"])
        self.btn_cancelar.grid_remove()  # Ocultar botão cancelar
    
    def alternar_lixeira(self):
        """Alterna entre visualização normal e lixeira"""
        self.modo_lixeira = not self.modo_lixeira
        
        # Limpar pesquisa ao trocar de modo
        self.filtro_tipo = None
        self.filtro_termo = None
        
        # Limpar campo de pesquisa baseado no tipo de widget
        if hasattr(self, 'entry_pesquisa'):
            if isinstance(self.entry_pesquisa, ctk.CTkComboBox):
                if self.contratos:
                    self.entry_pesquisa.set("Selecione um contrato")
            else:
                self.entry_pesquisa.delete(0, 'end')
        
        if self.modo_lixeira:
            self.titulo_lista.configure(text=f"Lixeira - {len(self.db.obter_entregas_excluidas())} entrega(s)")
            self.btn_lixeira.configure(text="Entregas", fg_color="#2196F3", hover_color="#1976D2")
        else:
            self.titulo_lista.configure(text=f"({len(self.db.obter_entregas())}) Entregas Cadastradas")
            self.btn_lixeira.configure(text="Lixeira", fg_color="#757575", hover_color="#616161")
        
        self.carregar_entregas()
    
    def restaurar_entrega_callback(self, entrega_id):
        """Callback para restaurar uma entrega da lixeira"""
        try:
            self.db.restaurar_entrega(entrega_id)
            self.carregar_entregas()
            self.notification_manager.show_notification(
                "Entrega restaurada com sucesso!",
                notify_type=NotifyType.SUCCESS,
                duration=4000
            )
        except Exception as e:
            self.notification_manager.show_notification(
                f"Erro ao restaurar entrega: {str(e)}",
                notify_type=NotifyType.ERROR,
                duration=6000
            )
    
    def deletar_permanentemente_callback(self, entrega_id):
        """Callback para deletar permanentemente uma entrega"""
        resposta = messagebox.askyesno(
            "Confirmar Exclusão Permanente", 
            "Esta ação não pode ser desfeita!\n\nDeseja realmente excluir esta entrega permanentemente?",
            icon="warning"
        )
        if resposta:
            try:
                self.db.deletar_permanentemente(entrega_id)
                self.carregar_entregas()
                self.notification_manager.show_notification(
                    "Entrega excluída permanentemente!",
                    notify_type=NotifyType.SUCCESS,
                    duration=4000
                )
            except Exception as e:
                self.notification_manager.show_notification(
                    f"Erro ao excluir permanentemente: {str(e)}",
                    notify_type=NotifyType.ERROR,
                    duration=6000
                )
    
    def enviar_alertas_thread(self):
        """Envia alertas de e-mail em uma thread separada (acionamento manual)"""
        def enviar():
            entregas = self.db.obter_entregas()
            entregas_proximas = self.email_manager.verificar_entregas_proximas(entregas)
            
            if entregas_proximas:
                sucesso, mensagem = self.email_manager.enviar_alerta(entregas_proximas)
                if sucesso:
                    self.notification_manager.show_notification(
                        mensagem,
                        notify_type=NotifyType.SUCCESS,
                        duration=5000
                    )
                else:
                    # Pergunta ao usuário se deseja enviar mesmo assim
                    if messagebox.askyesno("Confirmação", "Alerta já enviado hoje. Deseja enviar mesmo assim?"):
                        sucesso, mensagem = self.email_manager.enviar_alerta(entregas_proximas, force_send=True)
                        if sucesso:
                            # Enviar e-mail mesmo assim
                            self.notification_manager.show_notification(
                                mensagem,
                                notify_type=NotifyType.SUCCESS,
                                duration=5000
                            )

                        else:
                            self.notification_manager.show_notification(
                                mensagem,
                                notify_type=NotifyType.WARNING,
                                duration=6000
                            )
            else:
                self.notification_manager.show_notification(
                    "Não há entregas próximas para alertar.",
                    notify_type=NotifyType.INFO,
                    duration=4000
                )
        
        thread = threading.Thread(target=enviar, daemon=True)
        thread.start()
    
    def verificar_e_enviar_alertas_inicializacao(self):
        """Verifica e envia alertas automaticamente ao abrir o programa"""
        def enviar_automatico():
            try:
                agora = datetime.now()
                print(f"[{agora.strftime('%Y-%m-%d %H:%M:%S')}] Verificando necessidade de envio de alertas...")
                
                # Verificar se já foi enviado hoje
                if self.db.verificar_alerta_enviado_hoje():
                    print("[INFO] Alerta já foi enviado hoje. Próximo envio será amanhã.")
                    self.label_status.configure(
                        text="✅ Alerta já enviado hoje\nPróximo envio: amanhã",
                        text_color="#4CAF50"
                    )
                    return
                
                # Buscar entregas próximas
                entregas = self.db.obter_entregas()
                entregas_proximas = self.email_manager.verificar_entregas_proximas(entregas)
                
                if entregas_proximas:
                    print(f"[INFO] Encontradas {len(entregas_proximas)} entrega(s) próxima(s). Enviando alerta...")
                    sucesso, mensagem = self.email_manager.enviar_alerta(entregas_proximas)
                    
                    if sucesso:
                        print(f"[SUCESSO] {mensagem}")
                        self.label_status.configure(
                            text=f"✅ Alerta enviado com sucesso\n{len(entregas_proximas)} entrega(s) próxima(s)",
                            text_color="#4CAF50"
                        )
                    else:
                        print(f"[ERRO] {mensagem}")
                        self.label_status.configure(
                            text="❌ Erro ao enviar alerta\nVerifique os logs",
                            text_color="#f44336"
                        )
                else:
                    print("[INFO] Não há entregas próximas para alertar hoje.")
                    self.label_status.configure(
                        text="ℹ️ Sem entregas próximas hoje",
                        text_color="#2196F3"
                    )
                    
            except Exception as e:
                erro_msg = f"Erro na verificação automática: {str(e)}"
                print(f"[ERRO] {erro_msg}")
                self.label_status.configure(
                    text="❌ Erro na verificação automática",
                    text_color="#f44336"
                )
        
        # Executar em thread separada para não bloquear a interface
        thread = threading.Thread(target=enviar_automatico, daemon=True)
        thread.start()
