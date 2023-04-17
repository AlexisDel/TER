class Espece:
    def __init__(self, name):
        self.name = name
        self.inhibited = False

    def __str__(self):
        return '"' + self.name + '"'


class Reaction:
    def __init__(self, enzyme, substrats, produits, concentrations, quantity):
        self.enzyme = enzyme
        self.substrats = substrats
        self.produits = produits
        self.concentrations = concentrations
        self.quantity = quantity
        self.next = []
        self.previous = []
        self.used = False

    def __str__(self):
        return (
            str(self.enzyme)
            + " : "
            + " + ".join(map(str, reversed(self.substrats)))
            + " -> "
            + " + ".join(map(str, reversed(self.produits)))
            + " | "
            + ", ".join(map(str, reversed(self.concentrations)))
            + " - "
            + str(self.quantity)
            + ";"
        )


class Inhibition:
    def __init__(self, enzyme, substrats):
        self.enzyme = enzyme
        self.substrats = substrats

    def __repr__(self):
        return str(self.enzyme) + " : " + str(self.substrats)
