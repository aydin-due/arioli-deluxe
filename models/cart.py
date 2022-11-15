class Cart:
    def __init__(self, id, products, total):
        self.id = id
        self.products = products
        self.total = total
    
    def toDBCollection(self):
        return {
            "_id": self.id,
            "products": self.products,
            "total": self.total
        }