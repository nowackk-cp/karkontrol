from playwright.sync_api import expect

from .base import Screen


class UploadPage(Screen):
    def submit(self, path, *, message=None, error=None):
        assert (message is None) != (error is None), "Specify the expected submit result"
        self.open(f"/stores/{self.store_pk}/orders/upload/")
        self.page.get_by_test_id("order-file").set_input_files(str(path))
        self.page.get_by_test_id("upload-submit").click()
        if error:
            expect(self.page.get_by_test_id("upload-errors")).to_contain_text(error)
        else:
            expect(self.page.get_by_test_id("messages")).to_contain_text(message)
