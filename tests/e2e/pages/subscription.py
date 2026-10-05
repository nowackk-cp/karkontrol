from playwright.sync_api import expect

from .base import Screen


class SubscriptionPage(Screen):
    def pay(self, outcome, *, plan, message):
        self.open("/subscription/")
        self.page.get_by_test_id("payment-outcome").select_option(outcome)
        self.page.get_by_test_id("demo-pay").click()
        expect(self.page.get_by_test_id("messages")).to_contain_text(message)
        expect(self.page.get_by_test_id("active-plan")).to_have_text(plan)
