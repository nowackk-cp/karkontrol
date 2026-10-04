from playwright.sync_api import expect

from .base import Screen


class ReturnFormPage(Screen):
    def submit(self, line_pk, quantity):
        self.open(f"/stores/{self.store_pk}/orders/{line_pk}/return/")
        self.page.get_by_test_id("return-quantity").fill(str(quantity))
        self.page.get_by_test_id("return-save").click()
        expect(self.page.get_by_test_id("messages")).to_contain_text("İade adedi güncellendi")
