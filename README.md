# Gerador de Requisições

Sistema para geração automatizada de requisições de pagamento, e-mail, aquisição e dados de pagamentos. Desenvolvido para agilizar processos administrativos e reduzir erros manuais.

## 📋 Funcionalidades

- **Pagamento**: Geração de requisições para adiantamentos, reembolsos e pagamentos a parceiros
- **E-mail**: Criação automática de e-mails formatados para fornecedores
- **Aquisição**: Requisições para compras e aquisições com suporte a múltiplos itens
- **Dados Pagamentos**: Gerenciamento de informações de pagamento
- Validação de campos obrigatórios e formatação automática
- Integração com banco de dados SQLite para contratos e usuários
- Exportação para planilhas Excel
- Interface gráfica moderna com CustomTkinter

## 📁 Estrutura do Projeto

```
GeradorRequisicoes/
├── app/
│   ├── ui_tela_principal.py      # Interface principal
│   ├── ui_tela_login.py          # Tela de login
│   ├── ui_aba_pagamento.py       # Aba de pagamentos
│   ├── ui_aba_email.py           # Aba de e-mails
│   ├── ui_aba_aquisicao.py       # Aba de aquisições
│   ├── ui_aba_dados_pagamentos.py # Aba de dados de pagamentos
│   ├── gerador_excel.py          # Exportação para Excel
│   ├── utils.py                  # Funções auxiliares
│   ├── bd/                       # Scripts e banco de dados
│   └── assets/                   # Recursos (ícones, etc.)
├── .venv/                        # Ambiente virtual (não versionado)
├── requirements.txt              # Dependências do projeto
├── .gitignore                    # Arquivos ignorados pelo Git
└── README.md                     # Este arquivo
```

## 🛠️ Tecnologias Utilizadas

- **Python 3.13+**
- **CustomTkinter** - Interface gráfica moderna
- **OpenPyXL** - Manipulação de planilhas Excel
- **Pillow** - Processamento de imagens
- **PyWin32** - APIs do Windows
- **SQLite** - Banco de dados

## 📦 Instalação

### Pré-requisitos

- Python 3.13 ou superior
- Windows (devido ao PyWin32)

### 🧑‍💻 Para Desenvolvedores (Execução via Código)

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/dawilao/GeradorRequisicoes.git
   cd GeradorRequisicoes
   ```

2. **Crie um ambiente virtual:**
   ```bash
   python -m venv .venv
   ```

3. **Ative o ambiente virtual:**
   ```bash
   # Windows PowerShell
   .venv\Scripts\activate

   # Windows Command Prompt
   .venv\Scripts\activate.bat
   ```

4. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

### Configuração do PowerShell (se necessário)

Se encontrar erro de política de execução:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 🚀 Execução

### Ambiente de Desenvolvimento
```bash
# Certifique-se que o ambiente virtual está ativado
(.venv) python app/ui_tela_login.py
```

### ▶️ Para Usuários Finais (Ambiente Corporativo)

Se você não tem conhecimento em programação, utilize a versão pronta do programa:

1. Acesse a página de releases:
   👉 [github.com/dawilao/GeradorRequisicoes/releases](https://github.com/dawilao/GeradorRequisicoes/releases/latest)
2. Baixe o arquivo mais recente com extensão `.exe`.
3. Execute o arquivo baixado normalmente (não requer instalação do Python).
4. O programa abrirá com a interface gráfica — basta fazer login e utilizar as abas disponíveis.

> ⚠️ **Importante**: mantenha o arquivo `.exe` e a pasta `bd` juntos, caso o banco de dados não esteja embutido na versão.

## 🔧 Desenvolvimento

### Ambiente Virtual

O projeto utiliza ambiente virtual para isolamento de dependências. A pasta `.venv` não é versionada e deve ser criada localmente em cada máquina.

### Adicionando Novas Dependências

1. Ative o ambiente virtual
2. Instale o pacote: `pip install nome-do-pacote`
3. Atualize o requirements.txt: `pip freeze > requirements.txt`

### Padrão de Commits

Este projeto segue o padrão [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - Nova funcionalidade
- `fix:` - Correção de bug
- `chore:` - Tarefas de manutenção
- `docs:` - Documentação
- `refactor:` - Refatoração de código

## 🔍 Abas Disponíveis

- **PAGAMENTO**: Requisições de adiantamento, reembolso e pagamentos a parceiros
- **E-MAIL**: Geração de e-mails formatados para fornecedores
- **AQUISIÇÃO**: Requisições de compra com múltiplos itens
- **DADOS PAGAMENTOS**: Gerenciamento de informações de pagamento

## 🐛 Solução de Problemas

### Erro de Política de Execução (PowerShell)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Erro de Compatibilidade do Pillow
```bash
pip install --upgrade Pillow
```

### Verificar Ambiente Virtual
```bash
where python  # Deve apontar para .venv\Scripts\python.exe
pip list      # Verificar pacotes instalados
```

### Dependências do Sistema

⚠️ **Atenção**: o programa depende de caminhos específicos para o banco de dados.  
Se for executado fora do ambiente original, certifique-se de que os arquivos `contratos.db` e `login.db` estejam localizados em:

- `app/bd/` (recomendado para uso local)
- `G:\Meu Drive\17 - MODELOS\PROGRAMAS\Gerador de Requisições\app\bd\` (ambiente corporativo)

Você pode ajustar esses caminhos diretamente no código Python, se necessário.

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature: `git checkout -b feature/nova-funcionalidade`
3. Commit suas mudanças: `git commit -m 'feat: adiciona nova funcionalidade'`
4. Push para a branch: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request

## Créditos

Parte do código é baseada no repositório de [maxverwiebe](https://github.com/maxverwiebe), que não possui licença explícita.  
EN: This project includes code based on [maxverwiebe](https://github.com/maxverwiebe)'s repository, which does not have an explicit license.

## Licença

Distribuído sob a [Licença MIT](https://opensource.org/licenses/MIT).

## Autor

Desenvolvido por **Dawison Nascimento**  
- 💼 [LinkedIn](https://www.linkedin.com/in/dawison-nascimento)  
- 💻 [GitHub](https://github.com/dawilao)  
- 📧 daw_afk@tutamail.com | dawison@machengenharia.com.br  
- 📱 WhatsApp: +44 7979 217469
