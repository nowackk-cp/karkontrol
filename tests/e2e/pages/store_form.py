from playwright.sync_api import expect

from .base import Screen


class StoreFormPage(Screen):
    def create(self, name, *, marketplace="demo_tr", commission="20", error=None):
        self.open("/stores/new/")
        self.page.get_by_test_id("store-name").fill(name)
        self.page.get_by_test_id("store-marketplace").select_option(marketplace)
        self.page.get_by_test_id("store-commission_percent").fill(commission)
        self.page.get_by_test_id("store-save").click()
        if error:
            expect(self.page.get_by_test_id("store-errors")).to_contain_text(error)
        else:
            expect(self.page.get_by_test_id("store-heading")).to_have_text(name)
