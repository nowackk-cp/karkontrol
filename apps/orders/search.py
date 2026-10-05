import unicodedata


def normalize_search(value):
    """Normalize Turkish casing without relying on a database collation."""
    return unicodedata.normalize("NFC", value).translate(str.maketrans("İI", "iı")).lower()


def product_search_text(product_name, sku):
    return normalize_search(f"{product_name}\n{sku}")
