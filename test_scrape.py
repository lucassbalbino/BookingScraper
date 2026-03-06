"""
Testes unitários para funções puras do scrape.py
  - Testes unitários:  python -m pytest test_scrape.py -v
  - Teste integrado:   python test_scrape.py
"""
import pytest
from scrape import (
    tratamento_dados,
    validate_accommodation,
    validate_all,
    generate_summary_report,
    BASIC_FIELDS,
    ANALYTIC_FIELDS,
)


# =============================================================================
# Testes para tratamento_dados
# =============================================================================
class TestTratamentoDados:
    """Garante que a extração numérica funciona para todos os formatos encontrados."""

    def test_formato_virgula(self):
        assert tratamento_dados("7,7") == "7,7"

    def test_formato_ponto(self):
        assert tratamento_dados("8.5") == "8,5"

    def test_com_newline(self):
        assert tratamento_dados("Funcionários\n9,2") == "9,2"

    def test_com_nbsp(self):
        assert tratamento_dados("Limpeza\xa09,0") == "9,0"

    def test_inteiro(self):
        assert tratamento_dados("10") == "10,0"

    def test_zero(self):
        assert tratamento_dados("0") == "0,0"

    def test_vazio(self):
        assert tratamento_dados("") == "0,0"

    def test_none(self):
        assert tratamento_dados(None) == "0,0"

    def test_sem_numero(self):
        assert tratamento_dados("sem nota") == "0,0"

    def test_texto_com_numero_embutido(self):
        # deve extrair o primeiro número encontrado
        result = tratamento_dados("nota 8,4 excelente")
        assert result == "8,4"

    def test_valor_alto(self):
        assert tratamento_dados("10,0") == "10,0"

    def test_espacos_extras(self):
        assert tratamento_dados("  9,3  ") == "9,3"


# =============================================================================
# Testes para validate_accommodation
# =============================================================================
class TestValidateAccommodation:
    """Testa a validação de campos de uma acomodação."""

    @pytest.fixture
    def accommodation_ok(self):
        return {
            'name': 'Hotel Teste',
            'price': 'R$ 200',
            'location': 'Cidade X',
            'reviews': 50,
            'rating': '8,5',
            'stars': '4',
            'private': 'Hotel',
        }

    @pytest.fixture
    def accommodation_analytic_ok(self, accommodation_ok):
        accommodation_ok.update({
            'Funcionários': '9,0',
            'Comodidades': '8,5',
            'Limpeza': '9,2',
            'Conforto': '8,8',
            'Custo-benefício': '8,0',
            'Localização': '9,1',
            'WiFi gratuito': '7,5',
            'travel_proud': 'S',
            'sustentability': 'N',
            'TipoHotel': 'Hotel',
            'latitude': '-21.77',
            'longitude': '-41.28',
        })
        return accommodation_ok

    def test_accommodation_valida(self, accommodation_ok):
        issues = validate_accommodation(accommodation_ok)
        assert issues == []

    def test_accommodation_analytic_valida(self, accommodation_analytic_ok):
        issues = validate_accommodation(accommodation_analytic_ok, analytic=True)
        assert issues == []

    def test_campo_ausente(self):
        acc = {'name': 'Teste'}  # faltam todos os outros
        issues = validate_accommodation(acc)
        assert len(issues) >= 6  # price, location, reviews, rating, stars, private

    def test_campo_com_valor_padrao(self):
        acc = {
            'name': 'N/A',
            'price': 'R$ 100',
            'location': 'Cidade',
            'reviews': '0',
            'rating': '8,0',
            'stars': 'Sem Classificação',
            'private': 'Hotel',
        }
        issues = validate_accommodation(acc)
        # name = N/A, reviews = 0, stars = Sem Classificação
        assert len(issues) == 3

    def test_campo_vazio(self):
        acc = {
            'name': '',
            'price': '',
            'location': '',
            'reviews': '',
            'rating': '',
            'stars': '',
            'private': '',
        }
        issues = validate_accommodation(acc)
        assert len(issues) == 7


# =============================================================================
# Testes para validate_all
# =============================================================================
class TestValidateAll:
    def test_lista_vazia(self):
        with_issues, total_issues = validate_all([])
        assert with_issues == 0
        assert total_issues == 0

    def test_tudo_ok(self):
        accs = [{
            'name': 'Hotel A',
            'price': 'R$ 150',
            'location': 'Cidade',
            'reviews': 10,
            'rating': '7,5',
            'stars': '3',
            'private': 'Hotel',
        }]
        with_issues, total_issues = validate_all(accs)
        assert with_issues == 0
        assert total_issues == 0

    def test_com_problemas(self):
        accs = [
            {
                'name': 'Hotel A',
                'price': 'N/A',  # problema
                'location': 'Cidade',
                'reviews': '0',  # problema
                'rating': '7,5',
                'stars': '3',
                'private': 'Hotel',
            },
            {
                'name': 'Hotel B',
                'price': 'R$ 200',
                'location': 'Cidade',
                'reviews': 5,
                'rating': '8,0',
                'stars': '4',
                'private': 'Hotel',
            },
        ]
        with_issues, total_issues = validate_all(accs)
        assert with_issues == 1
        assert total_issues == 2


# =============================================================================
# Testes para generate_summary_report
# =============================================================================
class TestSummaryReport:
    def test_lista_vazia(self):
        result = generate_summary_report([])
        assert result is None

    def test_relatorio_basico(self):
        accs = [{
            'name': 'Hotel A',
            'price': 'R$ 150',
            'location': 'Cidade',
            'reviews': 10,
            'rating': '7,5',
            'stars': '3',
            'private': 'Hotel',
        }]
        stats = generate_summary_report(accs, analytic=False)
        assert stats is not None
        assert stats['name']['ok'] == 1
        assert stats['name']['default'] == 0
        assert stats['name']['missing'] == 0

    def test_relatorio_com_problemas(self):
        accs = [
            {'name': 'Hotel A', 'price': 'N/A', 'location': '', 'reviews': '0',
             'rating': '0', 'stars': 'Sem Classificação', 'private': 'Hotel'},
        ]
        stats = generate_summary_report(accs, analytic=False)
        # price=N/A(default), location=''(default), reviews=0(default), 
        # rating=0(default), stars=Sem Classificação(default)
        assert stats['price']['default'] == 1
        assert stats['private']['ok'] == 1

    def test_salva_arquivo(self, tmp_path):
        accs = [{'name': 'Hotel A', 'price': 'R$ 100', 'location': 'X',
                 'reviews': 5, 'rating': '8,0', 'stars': '3', 'private': 'Hotel'}]
        file_path = str(tmp_path / "test_output")
        generate_summary_report(accs, file_name=file_path)
        import os
        assert os.path.exists(f"{file_path}_relatorio.txt")


# =============================================================================
# Teste integrado — roda o scraper real com parâmetros simplificados
# Pergunta apenas: localização e nome do arquivo
# Datas: hoje → amanhã  |  Identificação: "teste"  |  Limite: 5 acomodações
# Execução: python test_scrape.py
# =============================================================================
def run_integration_test():
    from datetime import datetime, timedelta
    import time as _time
    import sys, os
    from scrape import (
        cookie_pass, load_more_results, web_scraper, save_results,
        get_current_time, get_driver, get_https, get_inside_url,
        inside_scraper, save_analitica, load_cookies,
        validate_all, generate_summary_report,
    )

    sys.stderr = open(os.devnull, 'w')
    start = _time.perf_counter()

    # --- Parâmetros automáticos ---
    hoje = datetime.now()
    amanha = hoje + timedelta(days=1)
    date_checkin = hoje.strftime('%Y-%m-%d')
    date_checkout = amanha.strftime('%Y-%m-%d')
    br_checkin = hoje.strftime('%d/%m/%Y')
    br_checkout = amanha.strftime('%d/%m/%Y')
    Identifica = 'teste'
    test_limit = 5

    # --- Perguntas mínimas ---
    place_raw = input('Local de pesquisa: ')
    place = place_raw.replace(' ', '+')
    file_name = input('Nome do arquivo: ')

    print(f"\n--- TESTE INTEGRADO ---")
    print(f"Datas: {br_checkin} → {br_checkout}")
    print(f"Identificação: {Identifica}")
    print(f"Limite: {test_limit} acomodações")
    print(f"Local: {place_raw}\n")

    https = get_https(place, date_checkin, date_checkout,
                      adults='1', rooms='1', children='0', currency='BRL')

    driver = get_driver()
    cookie_pass(driver, https)

    cookies = load_cookies()
    for cookie in cookies:
        driver.add_cookie(cookie)

    cookie_pass(driver, https)

    # Não carrega todos os resultados — pega só a primeira página
    Accommodations_list = web_scraper(driver)

    # Limitar
    if len(Accommodations_list) > test_limit:
        print(f"Limitando de {len(Accommodations_list)} para {test_limit} acomodações")
        Accommodations_list = Accommodations_list[:test_limit]

    current_time = get_current_time()

    # Sempre analítico no teste
    print('Iniciando análise analítica...')
    inside_url = get_inside_url(driver)
    inside_url = inside_url[:test_limit]
    Accommodations_list = inside_scraper(driver, inside_url, Accommodations_list)
    print('Análise analítica concluída')

    validate_all(Accommodations_list, analytic=True)
    generate_summary_report(Accommodations_list, analytic=True, file_name=file_name)
    save_analitica(current_time, br_checkin, br_checkout,
                   Accommodations_list, file_name, Identifica)

    driver.quit()
    end = _time.perf_counter()
    print(f"\nTeste concluído em {end - start:.2f} segundos")


if __name__ == '__main__':
    run_integration_test()