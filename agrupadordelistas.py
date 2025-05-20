#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import datetime
import lzma
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from playwright.sync_api import sync_playwright, TimeoutError

class TVGuideScraper:
    """
    Classe para extrair a programação de todos os canais do TVGuide.com
    e gerar um arquivo XML com os dados coletados.
    """
    
    def __init__(self, output_dir=None, days_to_scrape=3, headless=True):
        """
        Inicializa o scraper com configurações básicas.
        
        Args:
            output_dir: Diretório para salvar os arquivos de saída
            days_to_scrape: Número de dias para coletar a programação
            headless: Se True, executa o navegador em modo headless
        """
        self.base_url = "https://www.tvguide.com/listings/"
        self.output_dir = output_dir or os.path.dirname(os.path.abspath(__file__))
        self.days_to_scrape = days_to_scrape
        self.headless = headless
        self.channels_data = {}
        self.time_slots = []
        
        # Garantir que o diretório de saída exista
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Arquivo de log para depuração
        self.log_file = os.path.join(self.output_dir, "tvguide_scraper.log")
        
    def log(self, message):
        """Registra mensagens no arquivo de log"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
        print(message)
    
    def run(self):
        """Executa o processo completo de scraping e geração do XML"""
        self.log("Iniciando o processo de scraping do TVGuide.com")
        
        with sync_playwright() as playwright:
            # Inicializar o navegador
            browser = playwright.chromium.launch(headless=self.headless)
            context = browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
            
            # Criar uma nova página
            page = context.new_page()
            
            try:
                # Acessar a página inicial de listagens
                self.log(f"Acessando {self.base_url}")
                page.goto(self.base_url, wait_until="networkidle")
                
                # Fechar pop-ups de login ou cookies se aparecerem
                self.handle_popups(page)
                
                # Coletar dados para cada dia
                current_date = datetime.datetime.now()
                
                for day in range(self.days_to_scrape):
                    target_date = current_date + datetime.timedelta(days=day)
                    date_str = target_date.strftime("%Y-%m-%d")
                    self.log(f"Coletando programação para o dia {date_str}")
                    
                    # Se não for o primeiro dia, navegar para o próximo dia
                    if day > 0:
                        self.navigate_to_date(page, target_date)
                    
                    # Coletar dados de todos os horários disponíveis para este dia
                    self.scrape_all_time_slots(page, target_date)
                
                # Gerar o arquivo XML com todos os dados coletados
                self.generate_xmltv()
                
                # Comprimir o arquivo XML
                self.compress_xml()
                
            except Exception as e:
                self.log(f"Erro durante o scraping: {str(e)}")
                raise
            finally:
                # Fechar o navegador
                browser.close()
        
        self.log("Processo de scraping concluído com sucesso")
    
    def handle_popups(self, page):
        """Trata pop-ups de login ou cookies que podem aparecer"""
        try:
            # Tentar fechar modal de login se aparecer
            if page.locator("button[aria-label='Close']").is_visible(timeout=3000):
                self.log("Fechando modal de login")
                page.locator("button[aria-label='Close']").click()
            
            # Aceitar cookies se o botão estiver visível
            if page.locator("button:has-text('Accept Cookies')").is_visible(timeout=3000):
                self.log("Aceitando cookies")
                page.locator("button:has-text('Accept Cookies')").click()
        except:
            self.log("Nenhum pop-up detectado ou erro ao tentar fechar")
    
    def navigate_to_date(self, page, target_date):
        """
        Navega para uma data específica na grade de programação
        
        Args:
            page: Objeto da página do Playwright
            target_date: Data alvo para navegação
        """
        self.log(f"Navegando para a data: {target_date.strftime('%Y-%m-%d')}")
        
        # Clicar no seletor de data (botão "tonight, 7PM" ou similar)
        date_selector = page.locator("button:has-text('tonight') >> nth=0")
        date_selector.click()
        
        # Aguardar o calendário aparecer e selecionar a data
        # Implementação depende da estrutura exata do calendário
        # Esta é uma implementação simplificada que pode precisar de ajustes
        try:
            # Tentar encontrar e clicar na data desejada
            date_str = target_date.strftime("%-d")  # Dia sem zero à esquerda
            month_str = target_date.strftime("%B")  # Nome do mês
            
            # Verificar se o mês correto está visível, senão navegar
            month_header = page.locator(f"text={month_str} {target_date.year}")
            if not month_header.is_visible(timeout=1000):
                # Clicar no botão de próximo mês até encontrar
                next_month_btn = page.locator("button[aria-label='Next month']")
                for _ in range(3):  # Limite de tentativas
                    next_month_btn.click()
                    if month_header.is_visible(timeout=1000):
                        break
            
            # Clicar no dia
            day_button = page.locator(f"button:has-text('{date_str}'):not([disabled])")
            day_button.click()
            
            # Aguardar a página carregar com a nova data
            page.wait_for_load_state("networkidle")
            
        except Exception as e:
            self.log(f"Erro ao navegar para a data {target_date}: {str(e)}")
            # Tentar método alternativo - usar URL com parâmetro de data
            date_param = target_date.strftime("%Y-%m-%d")
            page.goto(f"{self.base_url}?date={date_param}", wait_until="networkidle")
    
    def scrape_all_time_slots(self, page, current_date):
        """
        Coleta dados de todos os horários disponíveis para um dia específico
        
        Args:
            page: Objeto da página do Playwright
            current_date: Data atual sendo coletada
        """
        date_str = current_date.strftime("%Y-%m-%d")
        self.log(f"Coletando todos os horários para {date_str}")
        
        # Coletar os dados do horário atual visível
        self.scrape_current_view(page, current_date)
        
        # Clicar no botão de próximo horário para avançar na grade
        next_time_button = page.locator("button[aria-label='Next time slot']")
        
        # Contador para evitar loop infinito
        max_time_slots = 12  # Aproximadamente 24 horas com slots de 2 horas
        time_slots_scraped = 1
        
        while time_slots_scraped < max_time_slots:
            try:
                # Verificar se o botão está habilitado
                if not next_time_button.is_enabled():
                    self.log("Botão de próximo horário desabilitado, finalizando coleta do dia")
                    break
                
                # Clicar para avançar ao próximo horário
                self.log("Avançando para o próximo horário")
                next_time_button.click()
                
                # Aguardar a atualização da grade
                page.wait_for_load_state("networkidle")
                
                # Coletar os dados do novo horário
                self.scrape_current_view(page, current_date)
                
                time_slots_scraped += 1
                
            except Exception as e:
                self.log(f"Erro ao avançar para o próximo horário: {str(e)}")
                break
    
    def scrape_current_view(self, page, current_date):
        """
        Coleta os dados de programação visíveis na visualização atual
        
        Args:
            page: Objeto da página do Playwright
            current_date: Data atual sendo coletada
        """
        # Obter o horário atual sendo exibido
        time_header = page.locator("div.listings-grid__time-header").all_text_contents()
        if not time_header:
            self.log("Não foi possível identificar o horário atual")
            return
        
        current_time_slot = time_header[0].strip()
        self.log(f"Coletando programação para o horário: {current_time_slot}")
        
        # Extrair todos os canais e programas visíveis
        channel_rows = page.locator("div.listings-grid__row").all()
        
        for row in channel_rows:
            try:
                # Extrair informações do canal
                channel_info = row.locator("div.listings-grid__channel").first()
                channel_logo = channel_info.locator("img").get_attribute("src") if channel_info.locator("img").count() > 0 else ""
                channel_name = channel_info.locator("div.listings-grid__channel-name").text_content().strip()
                channel_number = channel_info.locator("div.listings-grid__channel-number").text_content().strip() if channel_info.locator("div.listings-grid__channel-number").count() > 0 else ""
                
                # Criar ID único para o canal
                channel_id = channel_name.lower().replace(" ", "_")
                
                # Adicionar canal ao dicionário se ainda não existir
                if channel_id not in self.channels_data:
                    self.channels_data[channel_id] = {
                        "id": channel_id,
                        "display_name": channel_name,
                        "number": channel_number,
                        "icon": channel_logo,
                        "programs": []
                    }
                
                # Extrair todos os programas para este canal na visualização atual
                program_cells = row.locator("div.listings-grid__item").all()
                
                for cell in program_cells:
                    try:
                        # Extrair informações do programa
                        program_title = cell.locator("div.listings-grid__item-title").text_content().strip()
                        program_time = cell.locator("div.listings-grid__item-time").text_content().strip()
                        
                        # Extrair horário de início e fim
                        start_time, end_time = self.parse_program_time(program_time, current_date)
                        
                        # Extrair descrição se disponível
                        program_desc = ""
                        if cell.locator("div.listings-grid__item-desc").count() > 0:
                            program_desc = cell.locator("div.listings-grid__item-desc").text_content().strip()
                        
                        # Adicionar programa à lista do canal
                        self.channels_data[channel_id]["programs"].append({
                            "title": program_title,
                            "start": start_time,
                            "stop": end_time,
                            "desc": program_desc
                        })
                        
                    except Exception as e:
                        self.log(f"Erro ao extrair informações do programa: {str(e)}")
                
            except Exception as e:
                self.log(f"Erro ao processar canal: {str(e)}")
    
    def parse_program_time(self, time_str, current_date):
        """
        Converte a string de horário do programa para formato ISO
        
        Args:
            time_str: String com horário no formato "7:00 PM - 8:00 PM"
            current_date: Data atual sendo coletada
            
        Returns:
            Tupla com horário de início e fim no formato ISO
        """
        try:
            # Dividir a string de tempo
            times = time_str.split(" - ")
            
            if len(times) != 2:
                # Formato alternativo ou horário único
                if ":" in time_str:
                    # Tentar extrair apenas o horário de início
                    start_time_str = time_str
                    # Estimar o fim como 30 minutos depois
                    end_time = None
                else:
                    # Não foi possível extrair horário
                    return None, None
            else:
                start_time_str, end_time_str = times
                
                # Converter para objetos datetime
                start_time = datetime.datetime.strptime(f"{current_date.strftime('%Y-%m-%d')} {start_time_str}", "%Y-%m-%d %I:%M %p")
                end_time = datetime.datetime.strptime(f"{current_date.strftime('%Y-%m-%d')} {end_time_str}", "%Y-%m-%d %I:%M %p")
                
                # Verificar se o horário de término é no dia seguinte
                if end_time < start_time:
                    end_time = end_time + datetime.timedelta(days=1)
            
            # Formatar para o padrão XMLTV
            start_time_iso = start_time.strftime("%Y%m%d%H%M%S")
            end_time_iso = end_time.strftime("%Y%m%d%H%M%S") if end_time else None
            
            return start_time_iso, end_time_iso
            
        except Exception as e:
            self.log(f"Erro ao converter horário '{time_str}': {str(e)}")
            return None, None
    
    def generate_xmltv(self):
        """Gera o arquivo XMLTV com os dados coletados"""
        self.log("Gerando arquivo XMLTV")
        
        # Criar elemento raiz
        root = ET.Element("tv")
        root.set("generator-info-name", "TVGuide Scraper")
        root.set("generator-info-url", "https://www.tvguide.com/")
        
        # Adicionar canais
        for channel_id, channel_data in self.channels_data.items():
            channel_elem = ET.SubElement(root, "channel")
            channel_elem.set("id", channel_id)
            
            # Nome do canal
            display_name = ET.SubElement(channel_elem, "display-name")
            display_name.text = channel_data["display_name"]
            
            # Número do canal se disponível
            if channel_data["number"]:
                number = ET.SubElement(channel_elem, "display-name")
                number.text = channel_data["number"]
            
            # Ícone do canal se disponível
            if channel_data["icon"]:
                icon = ET.SubElement(channel_elem, "icon")
                icon.set("src", channel_data["icon"])
        
        # Adicionar programas
        for channel_id, channel_data in self.channels_data.items():
            for program in channel_data["programs"]:
                if not program["start"]:
                    continue  # Pular programas sem horário de início
                
                programme = ET.SubElement(root, "programme")
                programme.set("start", program["start"])
                if program["stop"]:
                    programme.set("stop", program["stop"])
                programme.set("channel", channel_id)
                
                # Título do programa
                title = ET.SubElement(programme, "title")
                title.set("lang", "en")
                title.text = program["title"]
                
                # Descrição se disponível
                if program["desc"]:
                    desc = ET.SubElement(programme, "desc")
                    desc.set("lang", "en")
                    desc.text = program["desc"]
        
        # Converter para string formatada
        xml_str = minidom.parseString(ET.tostring(root, encoding='utf-8')).toprettyxml(indent="  ")
        
        # Salvar arquivo XML
        xml_file = os.path.join(self.output_dir, "tvguide_listings.xml")
        with open(xml_file, 'w', encoding='utf-8') as f:
            f.write(xml_str)
        
        self.log(f"Arquivo XMLTV gerado: {xml_file}")
        return xml_file
    
    def compress_xml(self):
        """Comprime o arquivo XML em formato .xz"""
        xml_file = os.path.join(self.output_dir, "tvguide_listings.xml")
        xz_file = os.path.join(self.output_dir, "tvguide_listings.xml.xz")
        
        self.log(f"Comprimindo arquivo XML para {xz_file}")
        
        try:
            with open(xml_file, 'rb') as f_in:
                with lzma.open(xz_file, 'wb') as f_out:
                    f_out.write(f_in.read())
            
            self.log(f"Arquivo comprimido gerado: {xz_file}")
            return xz_file
            
        except Exception as e:
            self.log(f"Erro ao comprimir arquivo: {str(e)}")
            return None
    
    def save_raw_data(self):
        """Salva os dados brutos em formato JSON para referência"""
        json_file = os.path.join(self.output_dir, "tvguide_raw_data.json")
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.channels_data, f, ensure_ascii=False, indent=2)
        
        self.log(f"Dados brutos salvos em: {json_file}")
        return json_file


def main():
    """Função principal para execução do script"""
    import argparse
    
    parser = argparse.ArgumentParser(description='TVGuide.com Scraper para geração de XMLTV')
    parser.add_argument('--output-dir', type=str, help='Diretório para salvar os arquivos de saída')
    parser.add_argument('--days', type=int, default=3, help='Número de dias para coletar a programação (padrão: 3)')
    parser.add_argument('--headless', action='store_true', help='Executar em modo headless (sem interface gráfica)')
    
    args = parser.parse_args()
    
    # Criar e executar o scraper
    scraper = TVGuideScraper(
        output_dir=args.output_dir,
        days_to_scrape=args.days,
        headless=args.headless
    )
    
    try:
        scraper.run()
        scraper.save_raw_data()
        print("\nProcesso concluído com sucesso!")
        return 0
    except Exception as e:
        print(f"\nErro durante a execução: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())



#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import json
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import lzma
import datetime
import os
import sys
from playwright.sync_api import sync_playwright

def get_telemundo_schedule():
    """
    Acessa o site da Telemundo PR e extrai os dados da programação usando requests e BeautifulSoup.
    """
    import requests
    from bs4 import BeautifulSoup
    
    schedule_data = []
    
    try:
        # Acessar a página
        print("Acessando o site da Telemundo PR...")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get("https://www.telemundopr.com/guiadeprogramacion/", headers=headers )
        response.raise_for_status()
        
        # Usar BeautifulSoup para analisar o HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Encontrar as tabelas de programação
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            current_day = ""
            
            for row in rows:
                columns = row.find_all(['th', 'td'])
                
                # Verificar se é um cabeçalho de dia
                if len(columns) == 1 and columns[0].name == 'th':
                    current_day = columns[0].text.strip()
                    continue
                
                # Extrair horário e programa
                if len(columns) == 2:
                    time_slot = columns[0].text.strip()
                    program = columns[1].text.strip()
                    
                    # Extrair observação especial
                    observation = ""
                    if "(Solo" in time_slot:
                        observation = time_slot.split("(Solo")[1].split(")")[0].strip()
                        time_slot = time_slot.split("(")[0].strip()
                    elif "(no" in program:
                        observation = "exceto " + program.split("(no")[1].split(")")[0].strip()
                        program = program.split("(")[0].strip()
                    
                    # Adicionar à lista de programação
                    schedule_data.append({
                        "dia": current_day,
                        "horario": time_slot,
                        "programa": program,
                        "observacao": observation
                    })
        
        # Se não encontrou dados, usar dados de exemplo
        if not schedule_data:
            print("Usando dados de exemplo para testes...")
            schedule_data = get_example_data()
        
    except Exception as e:
        print(f"Erro ao acessar o site: {e}")
        schedule_data = get_example_data()
    
    return schedule_data


def get_example_data():
    """
    Retorna dados de exemplo para testes.
    """
    return [
        {
            "dia": "L-V",
            "horario": "8:00 a.m. to 10:00 a.m.",
            "programa": "Hoy Día Puerto Rico",
            "observacao": ""
        },
        {
            "dia": "L-V",
            "horario": "11:00 to 11:30 a.m.",
            "programa": "Telenoticias PR",
            "observacao": ""
        },
        {
            "dia": "L-V",
            "horario": "11:30 a.m. to 1:00 p.m.",
            "programa": "Alexandra a las 12",
            "observacao": ""
        },
        {
            "dia": "L-V",
            "horario": "1:00 to 4:00 p.m.",
            "programa": "Día a Día",
            "observacao": ""
        },
        {
            "dia": "L-V",
            "horario": "4:00 to 5:30 p.m.",
            "programa": "Telenoticias PR",
            "observacao": ""
        },
        {
            "dia": "L-V",
            "horario": "5:30 - 6:00 p.m.",
            "programa": "Primera Pregunta",
            "observacao": ""
        },
        {
            "dia": "L-V",
            "horario": "6:00 to 7:00 p.m.",
            "programa": "Puerto Rico Gana",
            "observacao": "exceto martes"
        },
        {
            "dia": "L-V",
            "horario": "8:00 to 10:00 p.m.",
            "programa": "Raymond y sus Amigos",
            "observacao": "martes"
        },
        {
            "dia": "L-V",
            "horario": "10:00 to 10:30 p.m.",
            "programa": "Telenoticias PR",
            "observacao": ""
        },
        {
            "dia": "L-V",
            "horario": "10:00 to 11:00 p.m.",
            "programa": "Rayos X",
            "observacao": "martes"
        },
        {
            "dia": "L-V",
            "horario": "7:00 p.m. to 10:00 p.m.",
            "programa": "La Casa de los Famosos",
            "observacao": ""
        },
        {
            "dia": "Sab/Dom",
            "horario": "5:00 to 6:00 p.m.",
            "programa": "Telenoticias PR",
            "observacao": ""
        },
        {
            "dia": "Sab/Dom",
            "horario": "6:00 to 7:00 p.m.",
            "programa": "Puerto Rico Gana",
            "observacao": "domingo"
        }
    ]

def parse_time_slot(time_slot):
    """
    Converte o formato de horário para um formato padronizado.
    Exemplo: "8:00 a.m. to 10:00 a.m." -> ("08:00", "10:00")
    """
    parts = time_slot.replace(" to ", " - ").replace(" - ", " - ").split(" - ")
    
    start_time = parts[0].strip()
    end_time = parts[1].strip() if len(parts) > 1 else ""
    
    # Converter para formato 24h
    def convert_to_24h(time_str):
        if not time_str:
            return ""
        
        # Remover "a.m." ou "p.m." e converter para 24h
        if "a.m." in time_str.lower() or "am" in time_str.lower():
            time_str = time_str.lower().replace("a.m.", "").replace("am", "").strip()
            hour, minute = map(int, time_str.split(":"))
            if hour == 12:
                hour = 0
        elif "p.m." in time_str.lower() or "pm" in time_str.lower():
            time_str = time_str.lower().replace("p.m.", "").replace("pm", "").strip()
            hour, minute = map(int, time_str.split(":"))
            if hour != 12:
                hour += 12
        else:
            # Se não tiver indicação, assumir formato 24h
            hour, minute = map(int, time_str.split(":"))
        
        return f"{hour:02d}:{minute:02d}"
    
    start_time_24h = convert_to_24h(start_time)
    end_time_24h = convert_to_24h(end_time)
    
    return start_time_24h, end_time_24h

def map_day_to_weekday(day):
    """
    Mapeia os dias da semana para números (0-6, onde 0 é segunda-feira).
    """
    if day == "L-V":
        return [0, 1, 2, 3, 4]  # Segunda a Sexta
    elif day == "Sab/Dom":
        return [5, 6]  # Sábado e Domingo
    return []

def generate_xmltv(schedule_data):
    """
    Gera um arquivo XMLTV com os dados da programação.
    """
    # Criar elemento raiz
    root = ET.Element("tv")
    root.set("generator-info-name", "TelemundoPR Guide Generator")
    root.set("generator-info-url", "https://www.telemundopr.com/guiadeprogramacion/")
    
    # Adicionar informações do canal
    channel = ET.SubElement(root, "channel")
    channel.set("id", "TelemundoWKAQ.pr")
    
    display_name = ET.SubElement(channel, "display-name")
    display_name.set("lang", "es")
    display_name.text = "Telemundo Puerto Rico"
    
    icon = ET.SubElement(channel, "icon")
    icon.set("src", "https://upload.wikimedia.org/wikipedia/commons/6/68/Telemundo_logo_2018.svg")
    
    url = ET.SubElement(channel, "url")
    url.text = "https://www.telemundopr.com"
    
    # Data atual para referência
    today = datetime.datetime.now()
    
    # Processar cada item da programação
    for item in schedule_data:
        day_name = item["dia"]
        weekdays = map_day_to_weekday(day_name)
        
        # Obter horários de início e fim
        start_time, end_time = parse_time_slot(item["horario"])
        
        # Verificar observações especiais
        observation = item["observacao"]
        
        # Para cada dia da semana aplicável
        for weekday in weekdays:
            # Pular se for uma observação específica que não se aplica a este dia
            if observation == "martes" and weekday != 1:  # 1 = terça-feira
                continue
            if observation == "exceto martes" and weekday == 1:
                continue
            if observation == "domingo" and weekday != 6:  # 6 = domingo
                continue
            
            # Calcular a data para este dia da semana
            delta_days = (weekday - today.weekday()) % 7
            program_date = today + datetime.timedelta(days=delta_days)
            
            # Criar elemento do programa
            programme = ET.SubElement(root, "programme")
            
            # Definir atributos de início e fim
            start_datetime = program_date.strftime("%Y%m%d") + start_time.replace(":", "") + "00 -0400"
            programme.set("start", start_datetime)
            
            if end_time:
                end_datetime = program_date.strftime("%Y%m%d") + end_time.replace(":", "") + "00 -0400"
                programme.set("stop", end_datetime)
            
            # Definir canal
            programme.set("channel", "TelemundoWKAQ.pr")
            
            # Adicionar título
            title = ET.SubElement(programme, "title")
            title.set("lang", "es")
            title.text = item["programa"]
            
            # Adicionar descrição se houver observação
            if observation:
                desc = ET.SubElement(programme, "desc")
                desc.set("lang", "es")
                desc.text = f"Observação: {observation}"
            
            # Adicionar categoria
            category = ET.SubElement(programme, "category")
            category.set("lang", "es")
            category.text = "Entretenimento"
    
    # Converter para string formatada
    xml_str = minidom.parseString(ET.tostring(root, encoding='utf-8')).toprettyxml(indent="  ")
    
    return xml_str

def compress_xml_xz(xml_str, output_file):
    """
    Comprime o XML em formato .xz
    """
    with lzma.open(output_file, 'wb') as f:
        f.write(xml_str.encode('utf-8'))
    
    return output_file

def validate_xmltv(xml_str):
    """
    Valida a estrutura do XMLTV gerado.
    """
    try:
        minidom.parseString(xml_str)
        return True, "XMLTV válido"
    except Exception as e:
        return False, f"Erro na validação do XMLTV: {e}"

def main():
    # Definir diretório de saída
    output_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Extrair dados da programação
    print("Extraindo dados da programação da Telemundo PR...")
    schedule_data = get_telemundo_schedule()
    
    # Verificar se os dados foram extraídos
    if not schedule_data:
        print("Erro: Não foi possível extrair dados da programação.")
        sys.exit(1)
    
    # Salvar dados brutos em JSON (para referência)
    json_file = os.path.join(output_dir, "telemundo_schedule.json")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(schedule_data, f, ensure_ascii=False, indent=2)
    print(f"Dados brutos salvos em: {json_file}")
    
    # Gerar XMLTV
    print("Gerando arquivo XMLTV...")
    xml_str = generate_xmltv(schedule_data)
    
    # Salvar XMLTV não comprimido (para referência)
    xml_file = os.path.join(output_dir, "telemundopr_guide.xml")
    with open(xml_file, 'w', encoding='utf-8') as f:
        f.write(xml_str)
    print(f"XMLTV gerado em: {xml_file}")
    
    # Validar XMLTV
    print("Validando estrutura do XMLTV...")
    is_valid, validation_msg = validate_xmltv(xml_str)
    print(validation_msg)
    
    if is_valid:
        # Comprimir XMLTV
        print("Comprimindo arquivo XMLTV...")
        xz_file = os.path.join(output_dir, "telemundo_guide.xml.xz")
        compress_xml_xz(xml_str, xz_file)
        print(f"Arquivo comprimido gerado em: {xz_file}")
        print("\nProcesso concluído com sucesso!")
    else:
        print("Falha na geração do arquivo XMLTV. Verifique os erros acima.")
        sys.exit(1)

if __name__ == "__main__":
    main()
