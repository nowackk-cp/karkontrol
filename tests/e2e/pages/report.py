from playwright.sync_api import expect

from .base import Screen


class ReportPage(Screen):
    def show(self):
        response = self.open(f"/stores/{self.store_pk}/reports/")
        expect(self.page.get_by_test_id("total-profit")).to_be_visible()
        return response

    def filter(self, *, start="", end="", product="", count):
        self.page.get_by_test_id("filter-start").fill(start)
        self.page.get_by_test_id("filter-end").fill(end)
        self.page.get_by_test_id("filter-product").fill(product)
        self.page.get_by_test_id("report-filter").click()
        expect(self.page.get_by_test_id("report-count")).to_have_text(f"{count} satır · TRY")

    def card(self, name):
        return self.page.get_by_test_id(f"total-{name}")

    def rows(self):
        return self.page.get_by_test_id("profit-row")
