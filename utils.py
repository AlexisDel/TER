class Espece:
    def __init__(self, name):
        self.name = name
        self.inhibited = False

    def __repr__(self):
        return self.name


class Reaction:
    def __init__(self, enzyme, substrats, produits):
        self.enzyme = enzyme
        self.substrats = substrats
        self.produits = produits
        self.next = []
        self.previous = []
        self.used = False

    def __str__(self):
        return (
            str(self.enzyme) + " : " + str(self.substrats) + " -> " + str(self.produits)
        )

    def __repr__(self):
        return (
            str(self.enzyme) + " : " + str(self.substrats) + " -> " + str(self.produits)
        )


class Inhibition:
    def __init__(self, enzyme, substrats):
        self.enzyme = enzyme
        self.substrats = substrats

    def __repr__(self):
        return str(self.enzyme) + " : " + str(self.substrats)
