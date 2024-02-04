import pickle
import socket
from serverLogic.item import Item
import json

class Inventory():
    def __init__(self, filename='items.json'):
        self.filename = filename
        self.items = self.load_inventory()

    def load_inventory(self):
        try:
            with open(self.filename, 'r') as file:
                data = json.load(file)
                return [Item(item['id'], item['name'], item['description'], item['amount']) for item in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_inventory(self):
        data = [{'id': item.id, 'name': item.name, 'description': item.description, 'amount': item.amount}
                for item in self.items]
        with open(self.filename, 'w') as file:
            json.dump(data, file, indent=2)

    def addItem(self,name,description):
        item_id = int(max(self.items, key=lambda x: x.id).id) + 1
        item = Item(item_id=item_id,name=name,description=description,amount=0)
        self.items.append(item)
        self.save_inventory()
        return item_id

    
    def getItems(self):
        return [{"id": item.id, "name": item.name, "amount": item.amount} for item in self.items]
    
    def putItem(self,itemId,ammount):
        i = None
        for item in self.items:
            if item.id == itemId:
                i = item
                break

        if i is not None:
            i.add_amount(ammount)
            return True
        else:
            return False
        
    def takeItem(self,itemId,ammount):
        i = None
        for item in self.items:
            if item.id == itemId:
                i = item
                break

        if i is not None:
            i.reduce_amount(ammount)
            return True
        else:
            return False


            

