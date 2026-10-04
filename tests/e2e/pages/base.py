class Screen:
    def __init__(self, page, base_url, store_pk):
        self.page = page
        self.base_url = base_url
        self.store_pk = store_pk

    def open(self, path):
        return self.page.goto(self.base_url + path)
