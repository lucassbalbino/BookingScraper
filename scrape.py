import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from datetime import datetime
import time
import re

InsideScraper_list = []
Accommodations_list = []


# ---------------------------------------------------------------------------
# Validação de dados — detecta campos ausentes ou padrão
# ---------------------------------------------------------------------------
BASIC_FIELDS = ['name', 'price', 'location', 'reviews', 'rating', 'stars', 'private']
ANALYTIC_FIELDS = BASIC_FIELDS + [
    'Funcionários', 'Comodidades', 'Limpeza', 'Conforto',
    'Custo-benefício', 'Localização', 'WiFi gratuito',
    'travel_proud', 'sustentability', 'TipoHotel', 'latitude', 'longitude'
]
_DEFAULT_VALUES = {'N/A', '0', '0,0', '0.0', 'Sem Classificação', '', None}


def validate_accommodation(accommodation, analytic=False):
    """Valida um dicionário de acomodação e retorna lista de problemas encontrados."""
    issues = []
    fields = ANALYTIC_FIELDS if analytic else BASIC_FIELDS
    for field in fields:
        value = accommodation.get(field)
        if value is None:
            issues.append(f"Campo '{field}' ausente")
        elif str(value).strip() in _DEFAULT_VALUES:
            issues.append(f"Campo '{field}' com valor padrão/vazio: {repr(value)}")
    return issues


def validate_all(Accommodations_list, analytic=False):
    """Valida toda a lista e retorna um resumo de problemas."""
    total = len(Accommodations_list)
    total_issues = 0
    accommodations_with_issues = 0

    for idx, acc in enumerate(Accommodations_list):
        issues = validate_accommodation(acc, analytic=analytic)
        if issues:
            accommodations_with_issues += 1
            total_issues += len(issues)

    return accommodations_with_issues, total_issues


# ---------------------------------------------------------------------------
# Relatório-resumo — gera estatísticas de qualidade da extração
# ---------------------------------------------------------------------------
def generate_summary_report(Accommodations_list, analytic=False, file_name=None):
    """Gera um relatório de qualidade dos dados extraídos."""
    total = len(Accommodations_list)
    if total == 0:
        return

    fields = ANALYTIC_FIELDS if analytic else BASIC_FIELDS
    field_stats = {f: {'ok': 0, 'default': 0, 'missing': 0} for f in fields}

    for acc in Accommodations_list:
        for field in fields:
            value = acc.get(field)
            if value is None:
                field_stats[field]['missing'] += 1
            elif str(value).strip() in _DEFAULT_VALUES:
                field_stats[field]['default'] += 1
            else:
                field_stats[field]['ok'] += 1

    report_lines = []
    report_lines.append(f"{'='*70}")
    report_lines.append(f" RELATÓRIO DE QUALIDADE — {total} acomodações")
    report_lines.append(f"{'='*70}")
    report_lines.append(f"{'Campo':<22} {'OK':>6} {'Padrão':>8} {'Ausente':>8} {'% OK':>7}")
    report_lines.append(f"{'-'*70}")

    for field in fields:
        s = field_stats[field]
        pct = (s['ok'] / total * 100) if total else 0
        report_lines.append(f"{field:<22} {s['ok']:>6} {s['default']:>8} {s['missing']:>8} {pct:>6.1f}%")

    report_lines.append(f"{'-'*70}")
    overall_ok = sum(s['ok'] for s in field_stats.values())
    overall_total = total * len(fields)
    overall_pct = (overall_ok / overall_total * 100) if overall_total else 0
    report_lines.append(f"{'TOTAL':<22} {overall_ok:>6} {'':>8} {'':>8} {overall_pct:>6.1f}%")
    report_lines.append(f"{'='*70}")

    full_report = '\n'.join(report_lines)
    print(full_report)

    # Salva relatório em arquivo separado se file_name fornecido
    if file_name:
        report_path = f"{file_name}_relatorio.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(full_report)

    return field_stats

def get_analitica():
    analitica = input('Deseja dados analiticos? (S/N)')
    return analitica
    
def get_file_name():
    file_name = input('Introduza o nome do arquivo para salvar os resultados: ')
    return file_name


def get_current_time():
    # Obtendo a data e hora atual
    global current_time
    current_time = datetime.now().strftime("%d/%m/%Y")
    return current_time


def get_dates():
    global date_checkin, date_checkout, br_checkin, br_checkout
    br_checkin = input('Introduza a data inicial (dd/mm/aaaa)')
    br_checkout = input('Introduza a data final (dd/mm/aaaa)')
    date_checkin = f'{br_checkin[6:]}-{br_checkin[3:5]}-{br_checkin[:2]}'
    date_checkout = f'{br_checkout[6:]}-{br_checkout[3:5]}-{br_checkout[:2]}'   
    return date_checkin, date_checkout, br_checkin, br_checkout

def get_location():
    place_raw = input('Introduza o local onde pretende pesquisar: ')
    place = place_raw.replace(' ', '+')
    return place



    # Configurações do Chrome (site Booking)
def get_driver():
    chrome_driver_path = './chromedriver.exe'
    options = webdriver.ChromeOptions()

    # --- Anti-detecção ---
    # 1. Remove flag que identifica automação
    options.add_argument('--disable-blink-features=AutomationControlled')

    # 2. User-Agent realista (Chrome atual em Windows)
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/145.0.0.0 Safari/537.36'
    )

    # 3. Janela em tamanho normal (bot costuma abrir em tamanho padrão pequeno)
    options.add_argument('--start-maximized')

    # 4. Ignora detecção de sandboxing
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')

    # 5. Desabilita infobars ("Chrome está sendo controlado por software de teste")
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)

    # 6. Suprime logs
    options.add_argument('--log-level=3')

    # 7. Idioma pt-BR para consistência com Booking
    options.add_argument('--lang=pt-BR')

    driver = webdriver.Chrome(service=Service(chrome_driver_path), options=options)

    # 8. Remove navigator.webdriver = true (principal flag de detecção)
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            // Simula plugins reais
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            // Simula linguagens
            Object.defineProperty(navigator, 'languages', {
                get: () => ['pt-BR', 'pt', 'en-US', 'en']
            });
            // Remove chrome.runtime para não parecer extensão
            window.chrome = { runtime: {} };
        '''
    })

    return driver

def get_id():
    # Obtendo o ID do usuário
    Identifica = input('Introduza a Identificação: ')
    return Identifica


def get_https(place, date_checkin, date_checkout, adults, rooms, children, currency):
    
    # Configurações do Chrome (site Booking)
    https = f'https://www.booking.com/searchresults.pt-br.html?ss={place}&dest_type=region&checkin={date_checkin}&checkout={date_checkout}&group_adults={adults}&no_rooms={rooms}&group_children={children}&selected_currency={currency}'
    return https

def delete_all_cookies(driver):
    # Deletando todos os cookies do navegador
    driver.delete_all_cookies()
    driver.execute_script("window.localStorage.clear();")
    driver.execute_script("window.sessionStorage.clear();")
    print("Todos os cookies foram deletados.")

def click_add_button(driver):
    try:
        add_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@class='de576f5064 b46cd7aad7 e26a59bb37 c295306d66 c7a901b0e7 daf5d4cb1c']")))
        add_button.click()
        time.sleep(2)
    except Exception as e:
        print(f"Error: {e}")

# Função que irá fazer o scrape do site
def cookie_pass(driver, https):
    driver.get(https)
    try:
        # Aceitar cookies do site
        cookies_button = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.ID, 'onetrust-accept-btn-handler')))
        cookies_button.click()
        time.sleep(2)
    except Exception as e:
        print(f"Error: {e}")
        # Se o botão não for encontrado, pode ser que o cookie já tenha sido aceito
        pass

def load_cookies():
    with open('cookies.json', 'r') as f:
        cookies = json.load(f)
        for cookie in cookies:
            value = cookie.get('sameSite')
            if not value or value == 'null':
                cookie['sameSite'] = 'None'
            elif value == 'lax':
                cookie['sameSite'] = 'Lax'
            elif value == 'strict':
                cookie['sameSite'] = 'Strict'
            else:
                cookie['sameSite'] = 'Lax'
        return cookies
    try:
        date_box = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='searchbox-dates-container']")))
        date_box.click()
        time.sleep(2)


        flexible_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@id='flexible-searchboxdatepicker-tab-trigger']")))
        flexible_button.click()
        time.sleep(2)


        custom_dates_button = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@data-testid="flexible-dates-day"]')))
        custom_dates_button[3].click()
        time.sleep(2)

        try:
            boxes = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@class="ee4cb4021c c3bfe61347"]')))
            box1 = boxes[0]  # Seleciona a segunda caixa (Check-in)
            box1.click()

            box2 = boxes[1]  # Seleciona a terceira caixa (Check-out)
            box2.click()

            box3 = boxes[2]  # Seleciona a quarta caixa (Check-in)
            box3.click()
        except Exception as e:
            print(f"Error: {e}")
    
       
        window_close = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@class='de576f5064 b46cd7aad7 ced67027e5 c7a901b0e7 ca8e0b9533 d445ed6f17']")))
        window_close.click()


        submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@class='de576f5064 b46cd7aad7 ced67027e5 dda427e6b5 e4f9ca4b0c ca8e0b9533 cfd71fb584 a9d40b8d51']")))
        submit_button.click()




        time.sleep(5)
   
    except Exception as e:
        print(f"{e}")

def load_more_results(driver):
    
    while True:
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            button = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, "//button[.//span[text()='Ver mais resultados']]")))
            

            # Fazendo o scroll para o botão "Ver mais resultados"
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            button.click()
            time.sleep(2)
        except Exception as e:
            print(f"Não há mais resultados para carregar: {e}")    
            break

    
def get_name(accomodation):
    # Obtendo o nome do hotel
    try:
        name_raw = accomodation.find_element(By.XPATH, './/*[@data-testid="title"]').text
        name = name_raw.replace(';','')
    except Exception as e:
        name = 'N/A'
        print(f"Erro ao obter o nome do hotel: {e}")
    return name

def get_price(accomodation):
    try:
    # Obtendo o preço do hotel
        price = accomodation.find_element(By.XPATH, './/*[@data-testid="price-and-discounted-price"]').text
        print(price)
    except Exception as e:
        price = 'N/A'
        print(f"Erro ao obter o preço do hotel: {e}")
    return price

def get_city(accomodation):
    try:
    # Obtendo a localização do hotel
        location = accomodation.find_element(By.XPATH, './/*[@data-testid="address-link"]').text
        print(location)
    except Exception as e:
        location = 'N/A'
        print(f"Erro ao obter a localização do hotel: {e}")
    return location

def get_reviews(accomodation):
    # Obtendo o número de reviews do hotel a partir do texto completo do container
    reviews = '0'
    try:
        containers = accomodation.find_elements(By.CSS_SELECTOR, '[data-testid="review-score"]')
        if not containers:
            return '0'
        full_text = containers[0].text
        print(f"DEBUG review-score texto: {repr(full_text)}")
        # Procura padrão "N avaliações" ou "N avaliação"
        match = re.search(r'([\d.]+)\s*(?:avaliações|avaliação|coment[áa]rios?)', full_text, re.IGNORECASE)
        if match:
            reviews = int(match.group(1).replace('.', ''))
    except Exception as e:
        reviews = '0'
        print(f"Erro ao obter o número de reviews do hotel: {e}")
    return reviews

def get_rating(accomodation):
    # Obtendo a avaliação do hotel — 2ª div descendente do container review-score
    try:
        rating_div = accomodation.find_element(By.CSS_SELECTOR, '[data-testid="review-score"] > div:nth-child(2)')

        
        rating = rating_div.text.strip()
    except Exception as e:
        print(f"Erro ao obter a avaliação do hotel: {e}")
        rating = '0'
    return rating

def get_stars(accomodation):
    # Obtendo o número de estrelas
    try:
        div_stars = accomodation.find_element(By.XPATH, ".//div[contains(@class, 'ebc566407a')]")
        stars = div_stars.get_attribute('aria-label').split(' ')[0]  
# Se o hotel não tiver estrelas o valor será 'N/A'
    except Exception as e:
        stars = 'Sem Classificação'
    return stars

def get_private_div(accomodation):
    # Obtendo se o hotel é privado ou não
            
    private_div = accomodation.find_element(By.XPATH, ".//div[contains(@class, 'fff1944c52')]").text
    if private_div == 'Gerenciada por um anfitrião (pessoa física)':
        private = 'Privado'
    else:
        private = 'Hotel'
    return private

def web_scraper(driver):
    # Reunindo as acomodações
    Accomodations = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@data-testid="property-card-container"]')))
    Accomodations_list = []
    # Criando uma lista para armazenar os dados das acomodações 
    try:
        for  accomodation in Accomodations:
            name = get_name(accomodation)
        
            price = get_price(accomodation)

            location = get_city(accomodation)

            reviews = get_reviews(accomodation)

            rating = get_rating(accomodation)

            stars = get_stars(accomodation)

            private = get_private_div(accomodation)

        # Dicionário para armazenar os dados da acomodação

            Accomodations_list.append({
                'name': name,
                'price': price,
                'location': location,
                'reviews' : reviews,
                'rating' : rating,
                'stars' : stars,
                'private' : private

                })

    except Exception as e:
        print(f"Error: {e}")
    return Accomodations_list



def get_inside_url(driver):
    inside_urls = [] 
    Accomodations = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@data-testid="property-card-container"]')))
 

    for accomodation in Accomodations:
        try:
            inside_url = accomodation.find_element(By.XPATH, './/*[@data-testid="title-link"]').get_attribute('href')
            inside_urls.append(inside_url)
        except:
            pass
    return inside_urls


def tratamento_dados(nome):
    """Extrai a parte numérica e retorna string com vírgula (ex: '7,7')."""
    if not nome:
        return '0,0'
    txt = nome.replace('\xa0', ' ').strip()
    if '\n' in txt:
        txt = txt.split('\n')[-1].strip()
    m = re.search(r'([0-9]+(?:[.,][0-9]+)?)', txt)
    if not m:
        return '0,0'
    num = m.group(1).replace(',', '.')  # normaliza para ponto antes de converter
    try:
        val = float(num)
    except Exception:
        return '0,0'
    return f"{val:.1f}".replace('.', ',')



def get_subscores(driver): 
    subscores_main = ['Funcionários', 'Comodidades', 'Limpeza', 'Conforto',
                      'Custo-benefício', 'Localização', 'WiFi gratuito']
    inside_dict = {subscore: 0.0 for subscore in subscores_main}

    try:
        WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, '//*[@data-testid="review-subscore"]')))
        subscores = driver.execute_script(
            "return Array.from(document.querySelectorAll('[data-testid=\"review-subscore\"]')).map(el => el.innerText.trim());"
        )
        for score in subscores:
            if not score:
                continue
            txt = score.replace('\xa0', ' ').strip()
            # formato esperado: "Nome\\n7,7"
            if '\n' in txt:
                nome, nota_txt = txt.split('\n', 1)
            else:
                parts = txt.rsplit(' ', 1)
                if len(parts) == 2 and re.search(r'[0-9]', parts[1]):
                    nome, nota_txt = parts
                else:
                    # se não conseguir, pula
                    continue
            nome = nome.strip()
            nota = tratamento_dados(nota_txt)
            if nome in inside_dict:
                inside_dict[nome] = nota
            else:
                # opcional: verifique nomes inesperados durante testes
                print(f"Erro ao obter subscores \nDEBUG: nome não reconhecido: {nome} -> {nota}")
    except Exception as e:
        pass
    return inside_dict


def get_travel_proud(driver):
    try:
        driver.find_element(By.XPATH, ".//span[contains(text(), 'Travel Proud')]")              
        travel_proud = 'S'   
    except:
        travel_proud = 'N'
    return travel_proud



def get_sustentability(driver):
    try:
        driver.find_element(By.XPATH,".//span[contains(text(), 'Certificado de sustentabilidade')]")
        sustentability = 'S'
    except:
        sustentability = 'N'
    return sustentability



def get_TipoHotel(driver):
    try:  
        TipoHotel_raw = driver.find_element(By.XPATH, ".//*[@data-testid='breadcrumb-current']").text
        TipoHotel = TipoHotel_raw.split(' ')
        TipoHotel = TipoHotel[-2]
        TipoHotel = TipoHotel.strip('()')
    
    except Exception as e:
        TipoHotel_raw = driver.find_element(By.XPATH, "//*[contains(@class, 'bui_breadcrumb__nolink')]").text
        TipoHotel = re.findall(r'\(([^)]*)\)', TipoHotel_raw)[0]    
    
    return TipoHotel

def get_lat_long(driver):
    try:
       lat_long_element = driver.find_element(By.XPATH, ".//*[@data-atlas-latlng]")
       lat_long_raw = lat_long_element.get_attribute('data-atlas-latlng')
       lat_long = lat_long_raw.split(',')
       latitude = lat_long[0]
       longitude = lat_long[1]
    
    except Exception as e:
        print(f'Erro ao carregar lat_long: {e}')
        latitude = 'N/A'
        longitude = 'N/A'
    return latitude, longitude


def inside_scraper(driver,inside_url, Accommodations_list):
    
    for idx, url in enumerate(inside_url):
        try:
            driver.get(url)
            subscores = get_subscores(driver)
            travel_proud = get_travel_proud(driver)
            sustentability = get_sustentability(driver)
            TipoHotel = get_TipoHotel(driver)
            latitude, longitude = get_lat_long(driver)
        

        
        except Exception as e:
            print(f"Error: {e}")
        
        try:
            #  Atualizando o dicionário da acomodação com os dados da página interna
            accommodation = Accommodations_list[idx]
            accommodation.update({
            'Funcionários' : subscores['Funcionários'],
            'Comodidades' : subscores['Comodidades'],
            'Limpeza' : subscores['Limpeza'],
            'Conforto' : subscores['Conforto'],
            'Custo-benefício' : subscores['Custo-benefício'],
            'Localização' : subscores['Localização'],
            'WiFi gratuito' : subscores['WiFi gratuito'],
            'travel_proud' : travel_proud,
            'sustentability' : sustentability,
            'TipoHotel' : TipoHotel,
            'latitude' : latitude,
            'longitude' : longitude})
            
        except Exception as e:
            print(f"Error nos dicionários: {e}")
        
    return Accommodations_list
    

def save_results(current_time, br_checkin, br_checkout, Accommodations_list, file_name, Identifica):
    #criando o arquivo de texto com os resultados
    file_name = f"{file_name}.txt"
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write('Dt-Proce;Dt-Inicio;Dt-Fim;Nome;Tarifa;Cidade;Identifica;Avaliações;Nota;Estrelas;Propriedade\n')
        for accommodation in Accommodations_list:
            file.write(f"{current_time};{br_checkin};{br_checkout};{accommodation['name']};{accommodation['price']};{accommodation['location']};{Identifica};{accommodation['reviews']};{accommodation['rating']};{accommodation['stars']};{accommodation['private']}\n")

def save_analitica(current_time, br_checkin, br_checkout, Accommodations_list, file_name, Identifica):
    #criando o arquivo de texto com os resultados
    try:
        file_name = f"{file_name}.txt"   
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write('Dt-Proce;Dt-Inicio;Dt-Fim;Nome;Tarifa;Cidade;Identifica;Avaliações;Nota;Estrelas;Propriedade;Funcionários;Comodidades;Limpeza;Conforto;Relação Qualidade/Preço;Localização;Wifi;Travel-Proud;Sustentabilidade;Tipo;Latitude;Longitude\n')
            for accommodation in Accommodations_list:
                file.write(f"{current_time};{br_checkin};{br_checkout};{accommodation['name']};{accommodation['price']};{accommodation['location']};{Identifica};{accommodation['reviews']};{accommodation['rating']};{accommodation['stars']};{accommodation['private']};{accommodation['Funcionários']};{accommodation['Comodidades']};{accommodation['Limpeza']};{accommodation['Conforto']};{accommodation['Localização']};{accommodation['Custo-benefício']};{accommodation['WiFi gratuito']};{accommodation['travel_proud']};{accommodation['sustentability']};{accommodation['TipoHotel']};{accommodation['latitude']};{accommodation['longitude']}\n")

    except Exception as e:
            print(f"Error: {e}")