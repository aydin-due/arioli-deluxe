class Restaurant:
    def __init__(self, id, name, email, password, description, address, category, logo):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.description = description
        self.address = address
        self.category = category
        self.logo = logo
    
    def toBDCollection(self):
        return {
            "_id": self.id,
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "description": self.description,
            "address": self.address,
            "category": self.category,
            "logo": self.logo
        }

    def updateDBCollection(self):
        return {
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "description": self.description,
            "address": self.address,
            "category": self.category,
            "logo": self.logo
        }