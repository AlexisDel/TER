class Espece:
    def __init__(self, name):
        self.name = name


class Reaction:
    def __init__(self, enzyme, substrats, produits):
        self.enzyme = enzyme
        self.substrat = substrats
        self.produits = produits
