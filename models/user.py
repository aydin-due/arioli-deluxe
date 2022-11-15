class User:
    def __init__(self, username, email, password, phone):
        self.username = username
        self.email = email
        self.password = password
        self.phone = phone
        self.admin = False
    
    def toBDCollection(self):
        return {
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "phone": self.phone,
            "admin": self.admin
        }