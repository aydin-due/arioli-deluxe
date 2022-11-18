class Restaurant:
    def __init__(self, id, username, email, password, description, address, category, logo):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.description = description
        self.address = address
        self.category = category
        self.logo = logo
    
    def toBDCollection(self):
        return {
            "_id": self.id,
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "description": self.description,
            "address": self.address,
            "category": self.category,
            "logo": self.logo
        }