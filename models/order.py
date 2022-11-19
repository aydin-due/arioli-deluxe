class Order:
    def __init__(self, id, table, products, total, date):
        self.id = id
        self.table = table
        self.products = products
        self.total = total
        self.date = date
        self.status = 'pending'
    
    def toDBCollection(self):
        return {
            "_id": self.id,
            "table": self.table,
            "products": self.products,
            "total": self.total,
            "date": self.date,
            "status": self.status
        }