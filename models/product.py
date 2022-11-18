class Product:
    def __init__(self, id, name, description, price, image):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.image = image
    
    def toDBCollection(self):
        return {
            "_id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "image": self.image
        }
    
    def updateDBCollection(self):
        return {
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "image": self.image
        }