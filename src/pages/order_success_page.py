from src.pages.base_page import BasePage


class OrderSuccessPage(BasePage):
    def url(self) -> str:
        return self.page.url

    def messages(self) -> list[str]:
        return [text.strip() for text in self.page.locator("#content p").all_inner_texts() if text.strip()]
