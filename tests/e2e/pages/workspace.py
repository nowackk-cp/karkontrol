from .base import Screen
from .login import LoginPage
from .report import ReportPage
from .return_form import ReturnFormPage
from .store_form import StoreFormPage
from .subscription import SubscriptionPage
from .upload import UploadPage


class Workspace(Screen):
    def __init__(self, page, base_url, store_pk):
        super().__init__(page, base_url, store_pk)
        self.login_screen = LoginPage(page, base_url, store_pk)
        self.store_form = StoreFormPage(page, base_url, store_pk)
        self.upload_screen = UploadPage(page, base_url, store_pk)
        self.report_screen = ReportPage(page, base_url, store_pk)
        self.return_form = ReturnFormPage(page, base_url, store_pk)
        self.subscription = SubscriptionPage(page, base_url, store_pk)

    def login(self):
        self.login_screen.login()
