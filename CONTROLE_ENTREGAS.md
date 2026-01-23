# Controle de Entregas

## Visão Geral

Módulo de gestão e acompanhamento de prazos de entregas com sistema de alertas automáticos por e-mail.

## Funcionalidades

### Cadastro de Entregas
- Registro de entregas vinculadas a contratos
- Campos: Contrato, Agência, OS, Produto, Data de Entrega, Responsável
- Validação de campos obrigatórios e formato de data (DD/MM/AAAA)
- Edição de entregas cadastradas

### Organização Automática
- Ordenação por urgência: entregas atrasadas aparecem primeiro
- Indicador visual de status por cores:
  - Vermelho: Entregas atrasadas
  - Laranja: Entregas hoje/amanhã ou próximos 2-3 dias
  - Azul: Entregas em 4-7 dias
  - Verde: Entregas com mais de 7 dias

### Sistema de Alertas
- Envio automático de e-mails ao iniciar o programa
- Envio manual através do botão "Enviar Agora"
- Controle de envio diário (um alerta por dia)
- Alertas incluem entregas atrasadas e próximas (até 3 dias)
- E-mails formatados em HTML com tabelas separadas para atrasadas e próximas

### Lixeira
- Exclusão lógica de entregas
- Restauração de entregas excluídas
- Exclusão permanente com confirmação
- Histórico de data de exclusão

### Interface
- Notificações flutuantes modernas (sem bloquear interface)
- Cards compactos otimizados para diferentes tamanhos de janela
- Sidebar com formulário de cadastro scrollable
- Painel principal com lista de entregas independente
- Botão de atualização manual da lista

## Banco de Dados

### Tabela: entregas
- id (INTEGER PRIMARY KEY)
- nome_contrato (TEXT)
- nome_agencia (TEXT)
- os (TEXT)
- descricao_produto (TEXT)
- data_entrega (TEXT)
- usuario (TEXT)
- data_cadastro (TEXT)
- excluido (INTEGER DEFAULT 0)
- data_exclusao (TEXT)

### Tabela: historico_alertas
- id (INTEGER PRIMARY KEY)
- data_envio (TEXT)
- entregas_alertadas (TEXT)
- data_hora_envio (TEXT)

## Configuração de E-mail

Servidor SMTP: smtp.kinghost.net:465 (SSL)
Remetente/Destinatário: dawison@machengenharia.com.br

## Dependências

- customtkinter: Interface gráfica
- sqlite3: Banco de dados
- smtplib: Envio de e-mails
- CTkFloatingNotifications: Sistema de notificações

## Estrutura de Arquivos

```
app/
├── ui_aba_controle_entregas.py       # Interface principal
├── bd/
│   └── prazo_entrega.db           # Banco de dados SQLite
└── CTkFloatingNotifications/      # Módulo de notificações
```

## Uso

A aba "CONTROLE ENTREGAS" deve estar incluída na lista de `abas_permitidas` do usuário para acesso.

```python
abas_permitidas = ['PAGAMENTO', 'E-MAIL', 'AQUISIÇÃO', 'DADOS PAGAMENTOS', 'CONTROLE ENTREGAS']
```
