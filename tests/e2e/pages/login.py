from playwright.sync_api import expect

from .base import Screen


class LoginPage(Screen):
    def login(self, username="e2e-owner", password="synthetic-browser-pass"):
        self.open("/accounts/login/")
        self.page.get_by_test_id("login-username").fill(username)
        self.page.get_by_test_id("login-password").fill(password)
        self.page.get_by_test_id("login-submit").click()
        expect(self.page.get_by_test_id("welcome")).to_contain_text(username)

    def logout(self):
        self.page.get_by_test_id("logout").click()
        expect(self.page.get_by_test_id("login-link")).to_be_visible()
