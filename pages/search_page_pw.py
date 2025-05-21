from playwright.sync_api import Page
from .base_page import BasePage

class SearchPagePW(BasePage):
    """
    Клас для взаємодії з головною сторінкою пошуку Google (Playwright).
    """
    # Локатори можуть бути ті ж самі, що і для Selenium, але синтаксис їх використання інший
    SEARCH_INPUT = "textarea[name='q']"  # CSS селектор
    # Кнопки пошуку можуть бути декілька, вибираємо видиму
    SEARCH_BUTTON_PRIMARY = "input[name='btnK']" # Головна кнопка
    SEARCH_BUTTON_FALLBACK = "//input[@name='btnK' and @type='submit']" # XPath для кнопки, якщо перша не спрацює
    LUCKY_BUTTON = "input[name='btnI']"
    IMAGES_LINK_TEXT = "Зображення" # Або "Images"
    NEWS_LINK_TEXT = "Новини" # Або "News"
    GOOGLE_LOGO = "img[alt='Google']"

    def __init__(self, page: Page):
        super().__init__(page, "https://www.google.com/?hl=uk") # Додаємо hl=uk для українського інтерфейсу

    def enter_search_query(self, query: str):
        self.type_text(self.SEARCH_INPUT, query)

    def click_search_button(self):
        # Playwright краще обробляє ситуації з кількома елементами
        # Спробуємо клікнути на видиму кнопку "Пошук Google"
        try:
            # Спочатку спробуємо клікнути на кнопку, яка є видимою і не перекрита підказками
            button_locator = self.page.locator(f"{self.SEARCH_BUTTON_PRIMARY} >> visible=true").first
            if button_locator.is_visible() and button_locator.is_enabled():
                button_locator.click(timeout=5000)
                return
        except Exception:
            pass # Якщо не вдалося, спробуємо інший підхід

        # Якщо перша кнопка не спрацювала (можливо, через підказки),
        # натискаємо Enter на полі вводу
        try:
            self.page.locator(self.SEARCH_INPUT).press("Enter")
        except Exception as e:
            print(f"Не вдалося виконати пошук через Enter: {e}")
            # Як останній варіант, спробуємо клікнути на кнопку за більш загальним XPath
            try:
                self.page.locator(self.SEARCH_BUTTON_FALLBACK).first.click(timeout=3000)
            except Exception as ex_final:
                 print(f"Фінальна спроба кліку на кнопку пошуку не вдалася: {ex_final}")
                 raise ex_final


    def click_lucky_button(self):
        # Потрібно вибрати видиму кнопку
        self.page.locator(f"{self.LUCKY_BUTTON} >> visible=true").first.click()

    def get_search_input_value(self) -> str:
        return self.get_attribute(self.SEARCH_INPUT, "value") or ""

    def are_search_elements_visible(self) -> bool:
        input_visible = self.is_element_visible(self.SEARCH_INPUT)
        # Перевіряємо видимість хоча б однієї з кнопок пошуку
        button_primary_visible = self.is_element_visible(self.SEARCH_BUTTON_PRIMARY)
        button_fallback_visible = self.is_element_visible(self.SEARCH_BUTTON_FALLBACK)
        return input_visible and (button_primary_visible or button_fallback_visible)

    def click_images_link(self):
        self.page.get_by_text(self.IMAGES_LINK_TEXT, exact=True).click()

    def click_news_link(self):
        self.page.get_by_text(self.NEWS_LINK_TEXT, exact=True).click()

    def click_google_logo(self):
        self.click(self.GOOGLE_LOGO)