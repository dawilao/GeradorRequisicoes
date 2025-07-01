# Sistema de Filas para Requisições - Guia de Uso

## 📋 Resumo

Este sistema resolve problemas de concorrência quando múltiplos usuários fazem requisições simultaneamente. Em vez de escrever diretamente no banco de dados, as requisições são salvas como arquivos JSON em uma fila, que depois é processada manualmente por usuários autorizados.

## 🔧 Como Funciona

### Para Usuários Comuns:
1. **Continue usando o sistema normalmente** - nada muda na interface
2. **Requisições são salvas automaticamente na fila** como arquivos JSON
3. **Veja o status da fila** na aba "Dados Pagamentos"

### Para Usuários Autorizados (Aba "Dados Pagamentos"):
1. **Clique em "Atualizar Status"** para verificar requisições pendentes
2. **Veja o status da fila** no label de status
3. **Clique em "Ver Detalhes"** para ver informações completas das requisições
4. **Clique em "Processar Fila"** quando houver requisições pendentes
5. **Confirme o processamento** na janela que aparecer
6. **Acompanhe o progresso** na janela de processamento

## 👥 Usuários Autorizados

Apenas os seguintes usuários podem processar a fila:

- ✅ **TAIANE MARQUES**
- ✅ **AMANDA SAMPAIO**
- ✅ **DAWISON NASCIMENTO**
- ✅ **TÁCIO BARBOSA**
- ✅ **ROSANA SILVA**
- ✅ **MIGUEL MARQUES**

## 📁 Estrutura de Arquivos

```
app/bd/
├── fila_requisicoes/          # Pasta com requisições em fila
│   ├── req_*.json            # Arquivos de requisições pendentes
├── processar_fila.py         # Script do processador
└── utils_bd.py              # Funções atualizadas
```

## 🖥️ Scripts de Comando

### `processar_fila.bat`
- Processa todas as requisições pendentes
- Requer autorização do usuário
- Mostra progresso e estatísticas

### `ver_status_fila.bat`
- Mostra status da fila sem processar
- Lista as últimas 10 requisições
- Não requer autorização

## 🎛️ Interface da Aba "Dados Pagamentos"

### Controles Disponíveis:
- 🔄 **"Atualizar Status"**: Verifica manualmente o status atual da fila
- 🔴 **"Processar Fila"**: Processa todas as requisições pendentes
- 📋 **"Ver Detalhes"**: Mostra lista detalhada das requisições na fila

### Indicadores Visuais:
- 🟢 **Verde**: Fila vazia (todos processados)
- 🟡 **Amarelo**: Poucas requisições (≤5)
- 🟠 **Laranja**: Requisições moderadas (≤20)
- 🔴 **Vermelho**: Muitas requisições (>20) - ATENÇÃO!

### Botões Principais:
- **"Processar Fila (X)"**: Mostra quantidade de requisições e processa quando clicado
- **"Ver Detalhes"**: Abre janela com informações completas de cada requisição
- **"Atualizar Status"**: Atualiza as informações sem processamento automático

## 🔄 Fluxo de Processamento

### 1. Requisição Normal:
```
Usuário faz requisição → Arquivo JSON salvo → Aguarda processamento
```

### 2. Processamento da Fila:
```
Usuário autorizado → Clica "Processar Fila" → Confirma → 
Requisições são lidas → Inseridas no banco → Marcadas como processadas
```

### 3. Fallback (Emergência):
```
Se a fila falhar → Sistema usa método original automaticamente
```

## ⚠️ Situações de Emergência

### Se a Fila Não Funcionar:
- O sistema **automaticamente** usa o método original
- **Nenhuma requisição é perdida**
- **Usuário é informado** sobre o fallback

### Se Houver Muitas Requisições Pendentes:
1. **Processe imediatamente** se for usuário autorizado
2. **Contate um usuário autorizado** se não tiver permissão
3. **Monitore regularmente** o status da fila

## 📊 Monitoramento

### Status Manual:
- **Atualização apenas quando solicitada** pelo usuário
- **Controle total** sobre quando verificar/processar
- **Sem atualizações automáticas** que possam interferir
- **Indicadores visuais claros** com notificações

### Logs e Histórico:
- **Requisições processadas** ficam marcadas nos arquivos JSON
- **Informações de quem processou** e quando
- **Histórico completo** mantido nos arquivos

## 🛠️ Manutenção

### Limpeza Automática:
- Arquivos processados são **mantidos para auditoria**
- **Não é necessário** remover arquivos manualmente
- Sistema **gerencia automaticamente** o espaço

### Backup:
- **Arquivos JSON** servem como backup das requisições
- **Múltiplas cópias** em diferentes locais
- **Recuperação fácil** em caso de problemas

## 🚀 Vantagens do Novo Sistema

### ✅ Para Usuários:
- **Maior confiabilidade** - zero conflitos de concorrência
- **Interface familiar** - nada muda na experiência
- **Feedback visual** - status claro da fila
- **Fallback automático** - nunca perde requisições

### ✅ Para Administradores:
- **Controle de acesso** - apenas usuários autorizados processam
- **Processamento manual** - maior controle sobre quando processar
- **Monitoramento fácil** - status visível na interface
- **Rastreabilidade completa** - cada requisição tem ID único

### ✅ Para o Sistema:
- **Zero conflitos** de escrita simultânea
- **Tolerância a falhas** - cada requisição é independente
- **Escalabilidade** - suporta muitos usuários simultâneos
- **Recuperação granular** - pode reprocessar requisições específicas

## 📞 Suporte

### Em caso de problemas:
1. **Verifique o status da fila** na interface
2. **Contate um usuário autorizado** para processar
3. **Use os scripts .bat** para diagnóstico
4. **Documente o erro** e contate o suporte técnico

### Usuários de suporte técnico:
- **TAIANE MARQUES** - Administradora principal
- **DAWISON NASCIMENTO** - Suporte técnico
- **MIGUEL MARQUES** - Suporte técnico
