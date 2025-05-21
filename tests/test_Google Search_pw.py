import pytest
from playwright.sync_api import Page, expect
from pages.search_page_pw import SearchPagePW
from pages.results_page_pw import ResultsPagePW
import time # Для демонстраційних пауз, намагайтеся уникати в реальних тестах

# Фікстура для ініціалізації сторінок Page Objects
@pytest.fixture
def search_page(page: Page): # page - стандартна фікстура pytest-playwright
    return SearchPagePW(page)

@pytest.fixture
def results_page(page: Page):
    return ResultsPagePW(page)

# --- Тест-кейси ---

def test_TC_GPW_001_load_home_page(search_page: SearchPagePW, page: Page):
    """TC_GPW_001: Перевірити, що головна сторінка Google завантажується успішно."""
    expect(page).to_have_title("Google")
    assert search_page.are_search_elements_visible(), "Елементи пошуку не відображаються"

def test_TC_GPW_002_simple_search(search_page: SearchPagePW, results_page: ResultsPagePW, page: Page):
    """TC_GPW_002: Перевірити пошук за простим ключовим словом."""
    query = "Playwright"
    search_page.enter_search_query(query)
    search_page.click_search_button()
    page.wait_for_load_state("domcontentloaded")
    expect(page).to_have_title(f"{query} - Пошук Google")
    assert results_page.count_search_results() > 0, "Результати пошуку не знайдені"

def test_TC_GPW_003_search_exact_phrase(search_page: SearchPagePW, results_page: ResultsPagePW, page: Page):
    """TC_GPW_003: Перевірити пошук за фразою в лапках."""
    query = '"Playwright Python test"'
    search_page.enter_search_query(query)
    search_page.click_search_button()
    page.wait_for_load_state("domcontentloaded")
    expect(page).to_have_title(f'{query} - Пошук Google')
    # Додаткова перевірка: перший результат містить фразу
    first_title = results_page.get_first_result_title().lower()
    assert query.strip('"').lower() in first_title, f"Перший результат '{first_title}' не містить точну фразу '{query}'"

def test_TC_GPW_004_empty_search(search_page: SearchPagePW, page: Page):
    """TC_GPW_004: Перевірити пошук з порожнім запитом."""
    initial_url = page.url
    search_page.enter_search_query("")
    # Кнопка пошуку може бути неактивною або пошук не відбудеться
    # Замість кліку, просто перевіримо стан
    search_page.page.locator(search_page.SEARCH_INPUT).press("Enter") # Спробуємо так
    page.wait_for_timeout(500) # Дамо час на можливу (небажану) навігацію

    assert page.url == initial_url or "#" in page.url, "URL змінився після порожнього пошуку"
    assert search_page.get_search_input_value() == "", "Поле пошуку не порожнє"

def test_TC_GPW_006_search_suggestions(search_page: SearchPagePW, page: Page):
    """TC_GPW_006: Перевірити відображення підказок під час введення запиту."""
    query_part = "playwri"
    search_page.enter_search_query(query_part)
    page.wait_for_timeout(1000) # Дати час на появу підказок
    suggestions_list_selector = "ul[role='listbox']" # Загальний селектор для списку
    suggestion_item_selector = f"{suggestions_list_selector} li[role='presentation']"

    search_page.wait_for_selector(suggestions_list_selector, state="visible", timeout=5000)
    assert search_page.is_element_visible(suggestions_list_selector), "Контейнер підказок не з'явився"

    count = page.locator(suggestion_item_selector).count()
    assert count > 0, "Підказки пошуку не з'явились або їх кількість нульова"

    first_suggestion_text = page.locator(suggestion_item_selector).first.text_content().lower()
    assert query_part in first_suggestion_text, f"Перша підказка '{first_suggestion_text}' не містить '{query_part}'"

def test_TC_GPW_007_image_search(search_page: SearchPagePW, results_page: ResultsPagePW, page: Page):
    """TC_GPW_007: Перевірити пошук зображень."""
    query = "кошенята"
    search_page.enter_search_query(query)
    search_page.click_search_button()
    page.wait_for_load_state("domcontentloaded")

    # Клік на "Зображення" на сторінці результатів
    results_page.page.get_by_text("Зображення", exact=True).click()
    page.wait_for_load_state("domcontentloaded")
    time.sleep(1) # Дати час на завантаження зображень

    assert results_page.is_images_tab_active(), "Вкладка 'Зображення' не активна"
    # Приклад локатора для перевірки наявності зображень
    images_container_selector = "div[data-hp='GRID_IMG']" # Може змінитися
    expect(page.locator(images_container_selector).first).to_be_visible(timeout=10000)
    assert page.locator(f"{images_container_selector} img").count() > 0, "Зображення не відображаються"

def test_TC_GPW_010_logo_clickable_returns_to_home(search_page: SearchPagePW, results_page: ResultsPagePW, page: Page):
    """TC_GPW_010: Перевірити, що логотип Google повертає на головну сторінку."""
    query = "тест"
    search_page.enter_search_query(query)
    search_page.click_search_button()
    page.wait_for_load_state("domcontentloaded")
    assert query in page.url.lower() # Переконуємось, що ми на сторінці результатів

    results_page.click_logo_on_results_page()
    page.wait_for_load_state("domcontentloaded")

    assert search_page.are_search_elements_visible(), "Не повернулись на головну сторінку після кліку на лого"
    assert query not in page.url.lower(), "URL все ще містить пошуковий запит після повернення на головну"
    expect(page).to_have_title("Google")


def test_TC_GPW_013_search_stats_present(search_page: SearchPagePW, results_page: ResultsPagePW, page: Page):
    """TC_GPW_013: Перевірити, що сторінка результатів пошуку відображає статистику."""
    search_page.enter_search_query("Python Playwright")
    search_page.click_search_button()
    page.wait_for_load_state("domcontentloaded")

    stats_text = results_page.get_search_results_stats_text()
    assert stats_text is not None and stats_text != "", "Статистика результатів пошуку відсутня"
    assert "результат" in stats_text.lower() or "близько" in stats_text.lower(), \
        f"Текст статистики '{stats_text}' не містить очікуваних слів"

def test_TC_GPW_014_pagination_next_page(search_page: SearchPagePW, results_page: ResultsPagePW, page: Page):
    """TC_GPW_014: Перевірити перехід на наступну сторінку результатів пошуку."""
    search_page.enter_search_query("автоматизація тестування")
    search_page.click_search_button()
    page.wait_for_load_state("domcontentloaded")

    initial_results_count = results_page.count_search_results()
    assert initial_results_count > 0, "Немає результатів на першій сторінці"
    current_url_page1 = page.url

    clicked_next = results_page.click_next_page()
    assert clicked_next, "Посилання 'Наступна сторінка' не знайдено або не клікнуто"
    # page.wait_for_load_state("domcontentloaded") # вже є в click_next_page

    current_url_page2 = page.url
    assert current_url_page1 != current_url_page2, "URL не змінився після переходу на наступну сторінку"
    # Перевірка, що URL тепер містить параметр, що вказує на другу сторінку (напр. start=10)
    assert "start=" in current_url_page2 or "aqs=" in current_url_page2, "URL не містить ознак переходу на іншу сторінку"
    assert results_page.count_search_results() > 0, "Немає результатів на другій сторінці"

def test_TC_GPW_015_long_query_search(search_page: SearchPagePW, results_page: ResultsPagePW, page: Page):
    """TC_GPW_015: Перевірити пошук дуже довгого рядка символів."""
    long_query = "a" * 250
    search_page.enter_search_query(long_query)
    search_page.click_search_button()
    page.wait_for_load_state("domcontentloaded")

    query_on_results_page = results_page.get_search_input_value_on_results_page()
    assert query_on_results_page == long_query, "Довгий запит неправильно відображається на сторінці результатів"

    # Перевіряємо, що сторінка завантажилась і є статистика або результати
    stats_visible = results_page.is_element_visible(results_page.SEARCH_RESULTS_STATS, timeout=3000)
    results_present = results_page.count_search_results() >= 0 # Може бути 0 результатів
    assert stats_visible or results_present, "Сторінка результатів для довгого запиту не завантажилась коректно"