class Order:
    def __init__(self, id, products, total, date):
        self.id = id
        self.products = products
        self.total = total
        self.date = date
        self.canceled = False
        self.delivered = False
    
    def toDBCollection(self):
        return {
            "_id": self.id,
            "products": self.products,
            "total": self.total,
            "date": self.date,
            "canceled": self.canceled,
            "delivered": self.delivered
        }