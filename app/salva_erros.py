from datetime import datetime
import os
import traceback

def salvar_erro(root, usuario, e):
    agora = datetime.now()
    data_hora_str = agora.strftime("%Y-%m-%d_%H-%M-%S")
    data_hora_legivel = agora.strftime("%d/%m/%Y %H:%M:%S")
    erro_str = str(e)
    erro_trace = traceback.format_exc()

    nome_arquivo_erro = f"{data_hora_str}_{usuario}_{type(e).__name__}.txt"
    nome_arquivo_erro = nome_arquivo_erro.replace(" ", "_").replace(":", "-").replace("\\", "_").replace("/", "_")

    pasta_erros = r"G:\Meu Drive\17 - MODELOS\PROGRAMAS\Gerador de Requisições\app\errors"
    os.makedirs(pasta_erros, exist_ok=True)
    caminho_erro = os.path.join(pasta_erros, nome_arquivo_erro)

    conteudo_erro = (
        f"Usuário: {usuario}\n"
        f"Data/Hora: {data_hora_legivel}\n"
        f"Tipo de erro: {type(e).__name__}\n"
        f"Mensagem: {erro_str}\n\n"
        f"Traceback:\n{erro_trace}\n"
    )

    try:
        with open(caminho_erro, "w", encoding="utf-8") as f:
            f.write(conteudo_erro)
        return True  # ou "Arquivo salvo"
    except Exception as erro_salvando:
        # Aqui você pode retornar o erro, logar em outro lugar, ou apenas retornar False
        return f"Erro ao salvar arquivo de erro: {erro_salvando}"