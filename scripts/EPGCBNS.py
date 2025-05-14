tvg-id="CBN.SaoPaulo" tvg-name="CBN São Paulo"
tvg-id="CBN.RioDeJaneiro" tvg-name="CBN Rio de Janeiro"

"""
Script para gerar EPG (Electronic Program Guide) em formato XMLTV
para as rádios CBN São Paulo e CBN Rio de Janeiro, a partir da grade de programação
disponível em https://cbn.globo.com/grade-de-programacao/

Dependências: playwright, pytz
É necessário instalar os navegadores para o Playwright com: playwright install
"""
import xml.etree.ElementTree as ET
import datetime
import pytz
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import re

def get_program_data_from_page_playwright(page, channel_id, channel_name):
    """
    Extrai os dados da programação da página.
    IMPORTANTE: Esta função atualmente usa DADOS FICTÍCIOS (DUMMY DATA).
    A lógica de extração real (parsing do HTML) precisa ser implementada
    usando seletores HTML/CSS corretos para a página da CBN.
    Adapte os seletores e a lógica de parsing abaixo conforme a estrutura real do site.
    """
    print(f"INFO: Tentando extrair programação para {channel_name}.")
    print(f"AVISO: A extração de dados real (parsing) PRECISA SER IMPLEMENTADA/AJUSTADA.")
    print(f"       Atualmente, dados fictícios (dummy) serão usados para {channel_name}.")
    
    programs_raw = []
    
    # ----- INÍCIO DA SEÇÃO DE EXTRAÇÃO DE DADOS (PRECISA DE IMPLEMENTAÇÃO REAL) -----
    # Exemplo de como você poderia tentar extrair os dados com Playwright:
    # (Estes seletores são fictícios e precisam ser adaptados!)
    # try:
    #     program_items_selector = "div.component.programacaoHorizontal" # Seletor do container de cada programa
    #     items = page.locator(program_items_selector)
    #     print(f"INFO: Encontrados {items.count()} itens de programa para {channel_name} com o seletor '{program_items_selector}'.")
    #     for i in range(items.count()):
    #         item = items.nth(i)
    #         # Extrair horário, título e apresentador de dentro do 'item'
    #         # Exemplo (seletores fictícios):
    #         time_str = item.locator("div.programacaoHorizontal__horario").inner_text(timeout=1000).strip()
    #         title = item.locator("div.programmation__title").inner_text(timeout=1000).strip()
    #         presenter_elements = item.locator("div.programmation__presenter")
    #         presenter = presenter_elements.first.inner_text(timeout=1000).strip() if presenter_elements.count() > 0 else "N/A"
    
    #         if re.match(r"\d{2}h\d{2}", time_str) and title:
    #             programs_raw.append({"time_str": time_str, "title": title, "presenter": presenter})
    #         else:
    #             print(f"AVISO: Item ignorado para {channel_name} devido a formato inválido: Hora='{time_str}', Título='{title}'")
    # except PlaywrightTimeoutError:
    #     print(f"ERRO: Timeout ao tentar extrair detalhes de um item para {channel_name}.")
    # except Exception as e:
    #     print(f"ERRO: Exceção ao extrair detalhes de um item para {channel_name}: {e}")
    # ----- FIM DA SEÇÃO DE EXTRAÇÃO DE DADOS -----

    # Usando dados fictícios (dummy data) porque a extração real não está implementada acima:
    if not programs_raw: # Se a extração real falhou ou não foi implementada
        print(f"INFO: Usando dados fictícios para {channel_name}.")
        if channel_id == "CBN.SaoPaulo":
            programs_raw = [
                {"time_str": "00h00", "title": "CBN Madrugada SP (Fictício)", "presenter": "Apresentador SP1"},
                {"time_str": "05h00", "title": "CBN Primeiras Notícias SP (Fictício)", "presenter": "Apresentador SP2"},
                {"time_str": "06h00", "title": "CBN São Paulo (Fictício)", "presenter": "Apresentador SP3"},
                {"time_str": "10h00", "title": "Manhã CBN SP (Fictício)", "presenter": "Apresentador SP4"},
                {"time_str": "14h00", "title": "Tarde CBN SP (Fictício)", "presenter": "Apresentador SP5"},
                {"time_str": "19h00", "title": "Noite CBN SP (Fictício)", "presenter": "Apresentador SP6"},
                {"time_str": "23h00", "title": "Fim de Expediente SP (Fictício)", "presenter": "Apresentador SP7"}
            ]
        elif channel_id == "CBN.RioDeJaneiro":
            programs_raw = [
                {"time_str": "00h00", "title": "CBN Madrugada RJ (Fictício)", "presenter": "Apresentador RJ1"},
                {"time_str": "05h00", "title": "CBN Primeiras Notícias RJ (Fictício)", "presenter": "Apresentador RJ2"},
                {"time_str": "06h00", "title": "CBN Rio (Fictício)", "presenter": "Apresentador RJ3"},
                {"time_str": "10h00", "title": "Manhã CBN RJ (Fictício)", "presenter": "Apresentador RJ4"},
                {"time_str": "14h00", "title": "Tarde CBN RJ (Fictício)", "presenter": "Apresentador RJ5"},
                {"time_str": "19h00", "title": "Noite CBN RJ (Fictício)", "presenter": "Apresentador RJ6"},
                {"time_str": "23h00", "title": "Fim de Expediente RJ (Fictício)", "presenter": "Apresentador RJ7"}
            ]

    if not programs_raw:
        print(f"AVISO: Nenhum programa (nem fictício) foi carregado para {channel_name}. Verifique a lógica.")
        return []

    programs_raw.sort(key=lambda p: p["time_str"]) # Ordenar por horário
    
    processed_programs = []
    try:
        tz = pytz.timezone("America/Sao_Paulo")
    except pytz.exceptions.UnknownTimeZoneError:
        class SimpleTZ(datetime.tzinfo):
            def utcoffset(self, dt): return datetime.timedelta(hours=-3)
            def dst(self, dt): return datetime.timedelta(0)
            def tzname(self, dt): return "BRT-3"
        tz = SimpleTZ()
        print("AVISO: pytz.timezone('America/Sao_Paulo') falhou. Usando fallback de timezone simples (-3h).")
        
    today_local = datetime.datetime.now(tz).date()

    for i, prog_info in enumerate(programs_raw):
        try:
            start_hour = int(prog_info["time_str"][:2])
            start_minute = int(prog_info["time_str"][3:5])
        except (ValueError, TypeError, IndexError):
            print(f"ERRO: Formato de hora inválido '{prog_info.get('time_str')}' para '{prog_info.get('title')}'. Programa ignorado.")
            continue

        start_dt_local = datetime.datetime(today_local.year, today_local.month, today_local.day, start_hour, start_minute, 0, tzinfo=tz)
        
        stop_dt_local = None
        if i + 1 < len(programs_raw):
            next_prog_info = programs_raw[i+1]
            try:
                stop_hour = int(next_prog_info["time_str"][:2])
                stop_minute = int(next_prog_info["time_str"][3:5])
                stop_dt_local = datetime.datetime(today_local.year, today_local.month, today_local.day, stop_hour, stop_minute, 0, tzinfo=tz)
                if stop_dt_local <= start_dt_local: # Programa seguinte é no dia seguinte
                     stop_dt_local += datetime.timedelta(days=1)
            except (ValueError, TypeError, IndexError):
                 print(f"AVISO: Não foi possível determinar hora de término para '{prog_info['title']}' baseado no próximo. Usando padrão.")
        
        if stop_dt_local is None: # Último programa do dia ou erro ao obter próximo
            stop_dt_local = datetime.datetime(today_local.year, today_local.month, today_local.day, 0, 0, 0, tzinfo=tz) + datetime.timedelta(days=1)
            if start_dt_local >= stop_dt_local: # Caso especial: se o último programa começar tarde e a lógica acima falhar
                 stop_dt_local = start_dt_local + datetime.timedelta(hours=1) # Duração padrão de 1 hora

        start_dt_utc = start_dt_local.astimezone(pytz.utc)
        stop_dt_utc = stop_dt_local.astimezone(pytz.utc)

        processed_programs.append({
            "title": prog_info["title"].strip(),
            "start": start_dt_utc.strftime("%Y%m%d%H%M%S %z").replace("+0000", "+0000"),
            "stop": stop_dt_utc.strftime("%Y%m%d%H%M%S %z").replace("+0000", "+0000"),
            "channel": channel_id,
            "description": f"Apresentado por: {prog_info.get('presenter', 'N/A')}".strip(),
            "presenter_raw": prog_info.get('presenter', '').strip()
        })
    return processed_programs

def create_xmltv_file(programs_sp, programs_rj, output_filename="epgcbns.xml"):
    tv_element = ET.Element("tv")
    tv_element.set("generator-info-name", "Manus EPG Generator for CBN")
    tv_element.set("source-info-url", "https://cbn.globo.com/grade-de-programacao/")
    tv_element.set("source-info-name", "CBN Grade de Programação")

    channels_data = [
        {"id": "CBN.SaoPaulo", "name": "CBN São Paulo"},
        {"id": "CBN.RioDeJaneiro", "name": "CBN Rio de Janeiro"}
    ]

    for ch_data in channels_data:
        channel_el = ET.SubElement(tv_element, "channel")
        channel_el.set("id", ch_data["id"])
        display_name_el = ET.SubElement(channel_el, "display-name")
        display_name_el.set("lang", "pt")
        display_name_el.text = ch_data["name"]

    all_programs = programs_sp + programs_rj
    all_programs.sort(key=lambda p: (p["channel"], p["start"])) 

    for prog_data in all_programs:
        programme_el = ET.SubElement(tv_element, "programme")
        programme_el.set("start", prog_data["start"])
        programme_el.set("stop", prog_data["stop"])
        programme_el.set("channel", prog_data["channel"])

        title_el = ET.SubElement(programme_el, "title")
        title_el.set("lang", "pt")
        title_el.text = prog_data["title"]

        if prog_data.get("description"):
            desc_el = ET.SubElement(programme_el, "desc")
            desc_el.set("lang", "pt")
            desc_el.text = prog_data["description"]
        
        presenter = prog_data.get("presenter_raw")
        if presenter and presenter != "N/A":
            credits_el = ET.SubElement(programme_el, "credits")
            presenter_el = ET.SubElement(credits_el, "presenter")
            presenter_el.text = presenter
    
    tree = ET.ElementTree(tv_element)
    try: 
        ET.indent(tree, space="  ", level=0)
    except AttributeError:
        print("AVISO: ET.indent não disponível (Python < 3.9). XML não será identado.")
        
    tree.write(output_filename, encoding="UTF-8", xml_declaration=True)
    print(f"INFO: Arquivo EPG XML '{output_filename}' gerado com sucesso.")

def fetch_city_schedule_with_playwright(page, city_button_selector, city_channel_id, city_channel_name):
    print(f"INFO: Iniciando busca da grade para {city_channel_name}...")
    try:
        page.evaluate("window.scrollTo(0, 0)") # Rolar para o topo para garantir que o botão esteja visível
        time.sleep(0.5)
        
        city_button = page.locator(city_button_selector).first
        if not city_button.is_visible(timeout=5000):
            print(f"ERRO: Botão para {city_channel_name} (seletor: '{city_button_selector}') não está visível.")
            return []
        
        city_button.click()
        print(f"INFO: Botão para {city_channel_name} clicado.")
        page.wait_for_load_state("networkidle", timeout=30000) # Esperar carregamento da rede
        time.sleep(2) # Espera adicional para renderização de JS

        print(f"INFO: Rolando a página para carregar toda a grade de {city_channel_name}...")
        last_height = page.evaluate("document.body.scrollHeight")
        scroll_attempts = 0
        while scroll_attempts < 10: # Limitar tentativas de rolagem
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2500) # Esperar conteúdo carregar após rolagem
            new_height = page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                print(f"INFO: Rolagem completa para {city_channel_name}.")
                break
            last_height = new_height
            scroll_attempts += 1
        else:
            print(f"AVISO: Limite de tentativas de rolagem atingido para {city_channel_name}.")

        # A função de parsing agora usa dados fictícios, mas receberia 'page' para extração real.
        programs = get_program_data_from_page_playwright(page, city_channel_id, city_channel_name)
        return programs

    except PlaywrightTimeoutError as pte:
        print(f"ERRO: Timeout durante a busca da grade para {city_channel_name}: {pte}")
        return []
    except Exception as e:
        print(f"ERRO: Exceção inesperada durante a busca da grade para {city_channel_name}: {e}")
        return []

def main():
    base_url = "https://cbn.globo.com/grade-de-programacao/"
    
    # Seletores para os botões das cidades. Estes podem mudar e precisar de ajuste.
    sp_button_selector = 'button:has-text("São Paulo 90.5 FM")'
    rj_button_selector = 'button:has-text("Rio de Janeiro 92.5 FM")'

    all_programs_sp = []
    all_programs_rj = []

    with sync_playwright() as p_context:
        # browser = p_context.chromium.launch(headless=True) # headless=False para debug local
        browser = p_context.chromium.launch() # Sandbox geralmente usa headless por padrão
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
        )
        page = context.new_page()
        
        try:
            print(f"INFO: Navegando para {base_url}...")
            page.goto(base_url, timeout=60000, wait_until="domcontentloaded")
            print("INFO: Navegação inicial completa.")
            page.wait_for_timeout(3000) # Tempo para scripts iniciais da página

            # São Paulo
            all_programs_sp = fetch_city_schedule_with_playwright(page, sp_button_selector, "CBN.SaoPaulo", "CBN São Paulo")
            
            # Rio de Janeiro
            # Pode ser necessário re-navegar ou garantir que a página está no estado correto
            # print(f"INFO: Re-navegando para {base_url} para garantir estado limpo antes de buscar RJ...")
            # page.goto(base_url, timeout=60000, wait_until="domcontentloaded")
            # page.wait_for_timeout(3000)
            all_programs_rj = fetch_city_schedule_with_playwright(page, rj_button_selector, "CBN.RioDeJaneiro", "CBN Rio de Janeiro")

        except PlaywrightTimeoutError as pte:
            print(f"ERRO FATAL: Timeout durante a automação do navegador: {pte}")
        except Exception as e:
            print(f"ERRO FATAL: Exceção durante a automação do navegador: {e}")
        finally:
            print("INFO: Fechando o navegador.")
            browser.close()

    if not all_programs_sp and not all_programs_rj:
        print("ERRO: Nenhum dado de programa foi obtido para nenhuma das cidades. Geração de XML abortada.")
    else:
        create_xmltv_file(all_programs_sp, all_programs_rj, output_filename="epgcbns.xml")

if __name__ == "__main__":
    print("--- Iniciando script de geração de EPG da CBN ---")
    # Para executar este script, certifique-se de ter Python com playwright e pytz instalados.
    # pip install playwright pytz
    # E instale os navegadores do Playwright: playwright install
    main()
    print("--- Script de geração de EPG da CBN finalizado ---")


