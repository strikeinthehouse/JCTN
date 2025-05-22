#!/bin/bash
# Script de instalação das dependências para o SBT+ Downloader

echo "Instalando dependências para o SBT+ Downloader..."

# Instalar Python e pip se não estiverem instalados
if ! command -v python3 &> /dev/null; then
    echo "Instalando Python..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip
fi

# Instalar dependências do Selenium
echo "Instalando Selenium e dependências..."
pip3 install selenium webdriver-manager

# Instalar yt-dlp
echo "Instalando yt-dlp..."
pip3 install yt-dlp

# Instalar Streamlink
echo "Instalando Streamlink..."
pip3 install streamlink

# Instalar Chrome e ChromeDriver
if ! command -v google-chrome &> /dev/null; then
    echo "Instalando Google Chrome..."
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
    sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
    sudo apt-get update
    sudo apt-get install -y google-chrome-stable
fi

# Verificar se tudo foi instalado corretamente
echo "Verificando instalações..."
python3 --version
pip3 --version
python3 -c "import selenium; print(f'Selenium versão: {selenium.__version__}')"
yt-dlp --version
streamlink --version

echo "Instalação concluída!"
echo "Para executar o downloader, use: python3 sbt_plus_downloader.py"
echo "Para ver as opções disponíveis, use: python3 sbt_plus_downloader.py --help"
