from playwright.sync_api import expect


class Workspace:
    def __init__(self, page, base_url, store_pk):
        self.page = page
        self.base_url = base_url
        self.store_pk = store_pk

    def open(self, path):
        return self.page.goto(self.base_url + path)

    def login(self):
        self.open("/accounts/login/")
        self.page.locator("#id_username").fill("e2e-owner")
        self.page.locator("#id_password").fill("synthetic-browser-pass")
        self.page.get_by_test_id("login-submit").click()
        expect(self.page.get_by_test_id("welcome")).to_contain_text("e2e-owner")

    def upload(self, path):
        self.open(f"/stores/{self.store_pk}/orders/upload/")
        self.page.locator("input[type=file]").set_input_files(str(path))
        self.page.get_by_test_id("upload-submit").click()

    def report(self):
        self.open(f"/stores/{self.store_pk}/reports/")
        return self.page.get_by_test_id("total-profit")
