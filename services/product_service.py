import json
from backend.config import DATA_PATH

class ProductService:
    def __init__(self):
        self.data_path = DATA_PATH
        self.products = self._load_products()

    def _load_products(self):
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading products from {self.data_path}: {e}")
            return []

    def get_all_products(self):
        return self.products

    def get_product_by_id(self, product_id: str):
        for product in self.products:
            if product.get("id") == product_id:
                return product
        return None
