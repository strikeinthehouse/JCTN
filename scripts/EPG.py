import requests
import re
import gzip
import os
import shutil
import lzma # Adicionado para suporte a .xz
from xml.etree import ElementTree as ET
from urllib.parse import urlparse

# URL do arquivo M3U
M3U_URL = "https://raw.githubusercontent.com/strikeinthehouse/1/refs/heads/main/lista1.M3U"
OUTPUT_XMLTV_FILE = "GUIA.xml"
TEMP_DIR = "epg_temp_files"
PROCESSED_DIR = os.path.join(TEMP_DIR, "processed_xmls") # Diretório para XMLs processados

def download_file(url, destination):
    """Baixa um arquivo de uma URL para um destino local."""
    print(f"Tentando baixar: {url}")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, stream=True, timeout=60, headers=headers, allow_redirects=True)
        response.raise_for_status()  # Levanta um erro para códigos de status ruins (4xx ou 5xx)
        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Arquivo baixado com sucesso: {url} -> {destination}")
        return True
    except requests.exceptions.Timeout:
        print(f"Timeout ao baixar {url}")
        return False
    except requests.exceptions.TooManyRedirects:
        print(f"Muitos redirecionamentos ao baixar {url}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"Erro ao baixar {url}: {e}")
        return False

def extract_epg_urls_from_m3u(m3u_content):
    """Extrai URLs de EPG de um conteúdo M3U."""
    pattern = r'(?:url-tvg|x-tvg-url)="([^"]+)"'
    matches = re.findall(pattern, m3u_content)
    epg_urls = set()
    for match in matches:
        urls_in_match = match.split(',')
        for url in urls_in_match:
            cleaned_url = url.strip()
            if cleaned_url: 
                epg_urls.add(cleaned_url)
    print(f"URLs de EPG encontrados no M3U: {list(epg_urls)}")
    return list(epg_urls)

def get_file_name_from_url(url, index):
    """Gera um nome de arquivo a partir da URL ou usa um índice."""
    try:
        path = urlparse(url).path
        file_name = os.path.basename(path)
        base, ext = os.path.splitext(file_name)
        if not ext or ext.lower() not in ['.xml', '.gz', '.xz']:
            if '.xml.gz' in url.lower():
                file_name = f"epg_{index}.xml.gz"
            elif '.xml.xz' in url.lower():
                file_name = f"epg_{index}.xml.xz"
            elif '.xml' in url.lower():
                file_name = f"epg_{index}.xml"
            elif '.gz' in url.lower():
                file_name = f"epg_{index}.gz"
            elif '.xz' in url.lower():
                file_name = f"epg_{index}.xz"
            else:
                file_name = f"epg_file_{index}.dat"
        else:
            file_name = f"{base}_{index}{ext}"
        return file_name
    except Exception as e:
        print(f"Erro ao extrair nome do arquivo da URL {url}: {e}. Usando nome genérico epg_file_{index}.dat")
        return f"epg_file_{index}.dat"

def decompress_and_normalize_epgs(downloaded_files, output_dir):
    """Descompacta arquivos EPG e os normaliza para XML, salvando no output_dir."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Diretório para XMLs processados criado: {output_dir}")

    processed_xml_files = []
    for i, file_path in enumerate(downloaded_files):
        base_name = os.path.basename(file_path)
        if base_name.endswith(".gz"):
            xml_file_name = base_name[:-3]
        elif base_name.endswith(".xz"):
            xml_file_name = base_name[:-3]
        elif base_name.endswith(".xml"):
            xml_file_name = base_name
        else:
            print(f"Arquivo com extensão desconhecida ou não é um EPG esperado, pulando: {file_path}")
            continue
        
        if not xml_file_name.endswith(".xml"):
            xml_file_name += ".xml"
        
        final_xml_path = os.path.join(output_dir, f"{os.path.splitext(xml_file_name)[0]}_{i}.xml")

        try:
            print(f"Processando arquivo: {file_path} -> {final_xml_path}")
            content_to_parse = None
            if file_path.endswith(".gz"):
                with gzip.open(file_path, 'rb') as f_gz:
                    content_to_parse = f_gz.read()
            elif file_path.endswith(".xz"):
                with lzma.open(file_path, 'rb') as f_xz:
                    content_to_parse = f_xz.read()
            elif file_path.endswith(".xml"):
                with open(file_path, 'rb') as f_xml:
                    content_to_parse = f_xml.read()
            else:
                continue

            if content_to_parse:
                try:
                    decoded_content = content_to_parse.decode('utf-8')
                except UnicodeDecodeError:
                    print(f"Falha ao decodificar {file_path} como UTF-8, tentando latin-1...")
                    try:
                        decoded_content = content_to_parse.decode('latin-1')
                    except UnicodeDecodeError as ude_latin:
                        print(f"Falha ao decodificar {file_path} como latin-1: {ude_latin}. Pulando arquivo.")
                        continue
                
                ET.fromstring(decoded_content) 
                
                with open(final_xml_path, 'w', encoding='utf-8') as f_out:
                    f_out.write(decoded_content)
                processed_xml_files.append(final_xml_path)
                print(f"Arquivo XML normalizado salvo: {final_xml_path}")
            
        except ET.ParseError as e_parse:
            print(f"Erro de parsing XML em {file_path}: {e_parse}. Pulando arquivo.")
        except gzip.BadGzipFile:
            print(f"Arquivo GZip inválido: {file_path}. Pulando.")
        except lzma.LZMAError as e_lzma:
            print(f"Erro LZMA ao processar {file_path}: {e_lzma}. Pulando.")
        except Exception as e:
            print(f"Erro inesperado ao processar {file_path}: {e}. Pulando.")
            
    return processed_xml_files

def merge_xmltv_files(xml_files, output_file_path):
    """Mescla múltiplos arquivos XMLTV em um único arquivo."""
    print(f"\nIniciando mesclagem de {len(xml_files)} arquivos XMLTV para {output_file_path}")
    # Cria o elemento raiz <tv>
    merged_root = ET.Element("tv")
    # Para evitar canais duplicados, rastreia os IDs dos canais já adicionados
    channel_ids = set()

    for xml_file in xml_files:
        try:
            print(f"Mesclando arquivo: {xml_file}")
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Adiciona atributos do elemento raiz do arquivo de origem ao merged_root, se não existirem
            # Isso pode ser útil para atributos como 'source-info-url', 'source-info-name', etc.
            # Evita sobrescrever se já definido por um arquivo anterior, mas pode ser ajustado.
            for key, value in root.attrib.items():
                if key not in merged_root.attrib:
                    merged_root.set(key, value)

            for channel_element in root.findall("channel"):
                channel_id = channel_element.get("id")
                if channel_id not in channel_ids:
                    merged_root.append(channel_element)
                    channel_ids.add(channel_id)
                else:
                    print(f"Canal duplicado encontrado e ignorado: ID {channel_id} do arquivo {xml_file}")
            
            for programme_element in root.findall("programme"):
                merged_root.append(programme_element)
            print(f"Conteúdo de {xml_file} adicionado à mesclagem.")

        except ET.ParseError as e:
            print(f"Erro de parsing XML ao mesclar {xml_file}: {e}. Pulando este arquivo.")
        except Exception as e:
            print(f"Erro inesperado ao mesclar {xml_file}: {e}. Pulando este arquivo.")

    # Cria a árvore XML final e escreve no arquivo
    merged_tree = ET.ElementTree(merged_root)
    try:
        # ET.indent(merged_tree, space="  ", level=0) # Para Python 3.9+
        merged_tree.write(output_file_path, encoding="utf-8", xml_declaration=True)
        print(f"Arquivo XMLTV mesclado salvo com sucesso em: {output_file_path}")
        return True
    except Exception as e:
        print(f"Erro ao salvar o arquivo XMLTV mesclado: {e}")
        return False

def main():
    """Função principal para orquestrar o processo."""
    if os.path.exists(OUTPUT_XMLTV_FILE):
        os.remove(OUTPUT_XMLTV_FILE)
        print(f"Arquivo {OUTPUT_XMLTV_FILE} existente removido.")
        
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
        print(f"Diretório temporário {TEMP_DIR} existente removido.")
    os.makedirs(TEMP_DIR)
    print(f"Diretório temporário criado: {TEMP_DIR}")

    print(f"Baixando o arquivo M3U de: {M3U_URL}")
    m3u_file_name = "lista_original.m3u"
    m3u_file_path = os.path.join(TEMP_DIR, m3u_file_name)

    if not download_file(M3U_URL, m3u_file_path):
        print("Falha ao baixar o arquivo M3U. Saindo.")
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)
        return

    with open(m3u_file_path, 'r', encoding='utf-8', errors='ignore') as f:
        m3u_content = f.read()
    
    epg_urls = extract_epg_urls_from_m3u(m3u_content)

    if not epg_urls:
        print("Nenhum URL de EPG encontrado no arquivo M3U. Saindo.")
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)
        return

    downloaded_epg_files = []
    print("\nIniciando download dos arquivos EPG...")
    for i, epg_url in enumerate(epg_urls):
        file_name = get_file_name_from_url(epg_url, i)
        destination_path = os.path.join(TEMP_DIR, file_name)
        print(f"Baixando EPG {i+1}/{len(epg_urls)}: {epg_url}")
        if download_file(epg_url, destination_path):
            downloaded_epg_files.append(destination_path)
        else:
            print(f"Falha ao baixar EPG: {epg_url}")

    if not downloaded_epg_files:
        print("Nenhum arquivo EPG foi baixado com sucesso. Saindo.")
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)
        return
    
    print(f"\nArquivos EPG baixados com sucesso: {downloaded_epg_files}")

    print("\nIniciando descompressão e normalização dos arquivos EPG...")
    normalized_xml_files = decompress_and_normalize_epgs(downloaded_epg_files, PROCESSED_DIR)

    if not normalized_xml_files:
        print("Nenhum arquivo EPG pôde ser normalizado para XML. Saindo.")
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)
        return

    print(f"\nArquivos EPG normalizados para XML: {normalized_xml_files}")

    print("\nIniciando mesclagem dos arquivos XMLTV normalizados...")
    if merge_xmltv_files(normalized_xml_files, OUTPUT_XMLTV_FILE):
        print(f"\nProcesso concluído! Arquivo final: {OUTPUT_XMLTV_FILE}")
    else:
        print("\nProcesso concluído com erros na mesclagem ou ao salvar o arquivo final.")

    # Limpeza final do diretório temporário
    if os.path.exists(TEMP_DIR):
        try:
            shutil.rmtree(TEMP_DIR)
            print(f"Diretório temporário {TEMP_DIR} removido com sucesso.")
        except Exception as e:
            print(f"Erro ao remover o diretório temporário {TEMP_DIR}: {e}")

if __name__ == "__main__":
    main()

