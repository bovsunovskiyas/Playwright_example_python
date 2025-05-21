from playwright.sync_api import Page, expect

class BasePage:
    """
    Базовий клас для всіх сторінок з Playwright.
    """
    def __init__(self, page: Page, url: str = ""):
        self.page = page
        if url:
            self.page.goto(url, wait_until="domcontentloaded")

    def navigate(self, url: str):
        """Переходить за вказаною URL-адресою."""
        self.page.goto(url, wait_until="domcontentloaded")

    def click(self, selector: str, timeout: int = 10000):
        """Клікає на елемент."""
        self.page.locator(selector).click(timeout=timeout)

    def type_text(self, selector: str, text: str, timeout: int = 10000):
        """Вводить текст в поле."""
        locator = self.page.locator(selector)
        locator.wait_for(state="visible", timeout=timeout)
        locator.fill(text)

    def get_text(self, selector: str, timeout: int = 10000) -> str:
        """Отримує текст елемента."""
        locator = self.page.locator(selector)
        locator.wait_for(state="visible", timeout=timeout)
        return locator.inner_text()

    def get_attribute(self, selector: str, attribute_name: str, timeout: int = 10000) -> str | None:
        """Отримує значення атрибута елемента."""
        locator = self.page.locator(selector)
        locator.wait_for(state="visible", timeout=timeout)
        return locator.get_attribute(attribute_name)

    def get_title(self) -> str:
        """Отримує заголовок поточної сторінки."""
        return self.page.title()

    def is_element_visible(self, selector: str, timeout: int = 5000) -> bool:
        """Перевіряє, чи відображається елемент на сторінці."""
        try:
            self.page.locator(selector).wait_for(state="visible", timeout=timeout)
            return self.page.locator(selector).is_visible()
        except Exception:
            return False

    def wait_for_selector(self, selector: str, state: str = "visible", timeout: int = 10000):
        """Очікує на елемент з певним станом."""
        self.page.locator(selector).wait_for(state=state, timeout=timeout)

    def expect_locator(self, selector: str):
        """Повертає об'єкт expect для локатора Playwright."""
        return expect(self.page.locator(selector))