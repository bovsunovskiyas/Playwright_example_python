from playwright.sync_api import Page, expect
from .base_page import BasePage

class ResultsPagePW(BasePage):
    """
    Клас для взаємодії зі сторінкою результатів пошуку Google (Playwright).
    """
    SEARCH_RESULTS_STATS = "#result-stats"
    SEARCH_RESULT_ITEMS = "div.g" # Загальний CSS селектор для блоку результату
    # Локатори для активних вкладок. Можуть потребувати адаптації.
    IMAGES_TAB_ACTIVE = "a[href*='tbm=isch'][aria-selected='true']"
    NEWS_TAB_ACTIVE = "a[href*='tbm=nws'][aria-selected='true']"
    NEXT_PAGE_LINK = "#pnnext" # Зазвичай це ID для "Наступна"
    SEARCH_INPUT_ON_RESULTS_PAGE = "textarea[name='q']" # Поле пошуку на сторінці результатів
    LOGO_ON_RESULTS_PAGE = "#logo"


    def __init__(self, page: Page):
        super().__init__(page)

    def get_search_results_stats_text(self) -> str:
        if self.is_element_visible(self.SEARCH_RESULTS_STATS):
            return self.get_text(self.SEARCH_RESULTS_STATS)
        return ""

    def count_search_results(self) -> int:
        if self.is_element_visible(self.SEARCH_RESULT_ITEMS, timeout=3000):
            return self.page.locator(self.SEARCH_RESULT_ITEMS).count()
        return 0

    def get_first_result_title(self) -> str:
        first_result_title_selector = f"{self.SEARCH_RESULT_ITEMS} h3 >> nth=0"
        if self.is_element_visible(first_result_title_selector):
            return self.get_text(first_result_title_selector)
        return ""

    def is_images_tab_active(self) -> bool:
        return self.is_element_visible(self.IMAGES_TAB_ACTIVE)

    def is_news_tab_active(self) -> bool:
        return self.is_element_visible(self.NEWS_TAB_ACTIVE)

    def click_next_page(self):
        if self.is_element_visible(self.NEXT_PAGE_LINK):
            self.click(self.NEXT_PAGE_LINK)
            self.page.wait_for_load_state("domcontentloaded") # Чекаємо завантаження нової сторінки
            return True
        return False

    def get_search_input_value_on_results_page(self) -> str:
        return self.get_attribute(self.SEARCH_INPUT_ON_RESULTS_PAGE, "value") or ""

    def click_logo_on_results_page(self):
        """Клікає на логотип на сторінці результатів."""
        self.click(self.LOGO_ON_RESULTS_PAGE)