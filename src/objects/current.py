

class Current:
    '''
    An class stores current information

    Field:
        contents    -   dict;       current information
    '''

    def __init__(self) -> None:
        self.contents = dict()
        self.contents.setdefault("price", dict())

    def get_contents(self) -> dict:
        return self.contents

    def set_price(self, label, price = -1):
        self.contents["price"][label] = price

    def get_price(self, label) -> float | int:
        return self.contents["price"].setdefault(label, -1)
    
    def remove_stock(self, label) -> float | int:
        self.set_price(label)
        self.contents["price"].pop(label)
