class Cart:
    def __init__(self, id, restaurant, products, total):
        self.id = id
        self.restaurant = restaurant
        self.products = products
        self.total = total
    
    def toDBCollection(self):
        return {
            "_id": self.id,
            "restaurant": self.restaurant,
            "products": self.products,
            "total": self.total
        }