class Recipe:
    def __init__(self, id, ingredients, procedure, portions):
        self.id = id
        self.ingredients = ingredients
        self.procedure = procedure
        self.portions = portions
    
    def toDBCollection(self):
        return {
            "_id": self.id,
            "ingredients": self.ingredients,
            "steps": self.procedure,
            "portions": self.portions
        }
    
    def updateDBCollection(self):
        return {
            "ingredients": self.ingredients,
            "steps": self.procedure,
            "portions": self.portions
        }