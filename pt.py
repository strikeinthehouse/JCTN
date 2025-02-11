import os

# Acessando as variáveis de ambiente do GitHub
email_ia = os.getenv('EMAIL_IA')
senha_ia = os.getenv('SENHA_IA')

# Verificando se as variáveis de ambiente estão presentes
if not email_ia or not senha_ia:
    print("Erro: As variáveis de ambiente EMAIL_IA ou SENHA_IA não estão definidas.")
else:
    # Criando o conteúdo para o arquivo .m3u8
    conteudo = f"#EXTM3U\n#EMAIL={email_ia}\n#SENHA={senha_ia}\n"

    # Salvando o conteúdo no arquivo IA.m3u8
    with open('IA.m3u8', 'w') as arquivo:
        arquivo.write(conteudo)
    
    print("Arquivo IA.m3u8 criado com sucesso!")




import subprocess

# URL do vídeo ou live do YouTube
url = "https://www.youtube.com/@recordnews/live"

# Comando para rodar o haruhi-dl
command = ["haruhi-dl", "-g", url]

# Executando o comando
result = subprocess.run(command, capture_output=True, text=True)

# Exibindo o link gerado para o download
print("Link para download:", result.stdout)




