import logging

from flask_restful import Resource



class Item(Resource):
    def __init__(self, item_id, name, description, amount):
        self.id = item_id
        self.name = name
        self.description = description
        self.amount = amount

    def add_amount(self, additional_amount):
        """Add a specified amount to the current amount."""
        self.amount += additional_amount

    def reduce_amount(self, reduction_amount):
        """Reduce a specified amount from the current amount."""
        if reduction_amount <= self.amount:
            self.amount -= reduction_amount
        else:
            logging.info("Error: Cannot reduce amount below 0")
    
    def to_dict(self):
        """Convert the Item object to a dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'amount': self.amount
        }