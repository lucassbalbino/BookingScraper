
from scrape import cookie_pass, load_more_results, web_scraper, save_results, get_current_time, get_dates, get_location, get_driver, get_https, delete_all_cookies, get_file_name, get_id, inside_scraper, get_analitica, get_inside_url, save_analitica, load_cookies, validate_all, generate_summary_report
import time
import sys
import os

def main():
    start = time.perf_counter()
    #stderr_original = sys.stderr
    sys.stderr = open(os.devnull, 'w')  # Redireciona stderr para /dev/null para suprimir mensagens de erro
    start = time.perf_counter()

    # Obter qual análise será
    analitica = get_analitica()
    
    # Obter o nome do arquivo de saída
    file_name = get_file_name()
    
    # Obter Identificação
    Identifica = get_id()

    # Obtendo a localização
    place = get_location()

    # Obtendo as datas de check-in e check-out
    date_checkin, date_checkout, br_checkin, br_checkout = get_dates()

    # Obtendo o link do Booking direto para a pesquisa
    https = get_https(place, date_checkin, date_checkout, adults='1', rooms='1', children='0', currency='BRL')

    # Configurando o drivSer do Seleniumx
    driver = get_driver()
   
    #Aceitando os cookies na página inicial do Booking
    cookie_pass(driver, https)
    
    cookies = load_cookies()
    for cookie in cookies:
        driver.add_cookie(cookie)
    # Deletando todos os cookies do navegador, para evitar bloqueios
    #delete_all_cookies(driver) 
    
    #load_flexible_dates(driver)

    cookie_pass(driver, https)
    
    # Scroll para baixo para carregar mais resultados
    load_more_results(driver)

    Accommodations_list = web_scraper(driver)
    
    # Obtendo o tempo atual para salvar os resultados
    current_time = get_current_time()

    if analitica == 'S':
        print('Iniciando a análise analítica')
        inside_url = get_inside_url(driver)
        Accommodations_list = inside_scraper(driver, inside_url, Accommodations_list)
        print('Análise analítica concluída')

        # Validação dos dados coletados
        validate_all(Accommodations_list, analytic=True)

        # Relatório de qualidade
        generate_summary_report(Accommodations_list, analytic=True, file_name=file_name)

        save_analitica(current_time, br_checkin, br_checkout, Accommodations_list, file_name, Identifica)
    else:
        print('Iniciando a análise não analítica')

        # Validação dos dados coletados
        validate_all(Accommodations_list, analytic=False)

        # Relatório de qualidade
        generate_summary_report(Accommodations_list, analytic=False, file_name=file_name)

        save_results(current_time, br_checkin, br_checkout, Accommodations_list, file_name, Identifica)

    end = time.perf_counter()
    print(f"Tempo total de execução: {end - start:.2f} segundos")
    time.sleep(5)
if __name__ == "__main__":
  main()
  