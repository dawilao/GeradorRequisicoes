# Gerador de Texto de Compras

Ferramenta para automatizar a criação de textos utilizados em solicitações de pagamento, e-mails e aquisições. Desenvolvida para agilizar processos administrativos e reduzir erros manuais.

## Funcionalidades

- Geração de textos padrões para:
  - Pagamentos, com validação de campos obrigatórios.
  - E-mails a fornecedores, com dados de pagamento e entrega.
  - Aquisições, com suporte a múltiplos itens.
- Validação de prefixos, porcentagens, números de OS e outros campos.
- Integração com banco de dados SQLite para gerenciamento de contratos e usuários.
- Exportação para planilhas Excel.
- Interface gráfica com CustomTkinter.

## Estrutura

- app/
  - ui_tela_principal.py — Interface principal.
  - ui_tela_login.py — Tela de login.
  - utils.py — Funções auxiliares.
  - bd/ — Scripts e banco de dados.

## Requisitos

- Python 3.8+
- Bibliotecas: customtkinter, sqlite3, pyperclip

## Uso

### ▶️ Para Usuários Finais (Ambiente Corporativo)

Se você não tem conhecimento em programação, utilize a versão pronta do programa:

1. Acesse a página de releases:
   👉 [github.com/dawilao/GeradorRequisicoes/releases](https://github.com/dawilao/GeradorRequisicoes/releases)
2. Baixe o arquivo mais recente com extensão `.exe`.
3. Execute o arquivo baixado normalmente (não requer instalação do Python).
4. O programa abrirá com a interface gráfica — basta fazer login e utilizar as abas disponíveis para gerar os textos desejados.

> ⚠️ Dica: mantenha o arquivo `.exe` e a pasta `bd` juntos, caso o banco de dados não esteja embutido na versão.

---

### 🧑‍💻 Para Desenvolvedores (Execução via Código)

Se você deseja rodar ou modificar o código-fonte:

1. Clone o repositório:
    ```bash
   git clone https://github.com/dawilao/GeradorRequisicoes.git
2. Instale as dependências necessárias:
    ```bash
   pip install customtkinter pyperclip
3. Execute o arquivo principal:
    ```bash
    python app/ui_tela_login.py

⚠️ Atenção: o programa depende de caminhos fixos para o banco de dados.  
Se for executado fora do VSCode ou da estrutura original, certifique-se de que os arquivos `contratos.db` e `login.bd` estejam localizados em um dos seguintes caminhos:

- `app/bd/` (recomendado para uso local)
- `G:\Meu Drive\17 - MODELOS\PROGRAMAS\Gerador de Requisições\app\bd\` (utilizado em ambiente corporativo)

Você também pode ajustar esses caminhos diretamente no código Python, caso necessário.

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
