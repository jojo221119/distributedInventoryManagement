import logging
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
                return [Item(item['item_id'], item['name'], item['description'], item['amount']) for item in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_inventory(self):
        data = [{'item_id': item.item_id, 'name': item.name, 'description': item.description, 'amount': item.amount}
                for item in self.items]
        with open(self.filename, 'w') as file:
            json.dump(data, file, indent=2)

    def addItem(self,name,description,amount):
        item_id = int(max(self.items, key=lambda x: x.item_id).item_id) + 1
        item = Item(item_id=item_id,name=name,description=description,amount=amount)
        self.items.append(item)
        self.save_inventory()
        return item_id

    
    def getItems(self):
        return [{"item_id": item.item_id, "name": item.name, "description": item.description, "amount": item.amount} for item in self.items]
    
    def putItem(self,itemId,amount):
        i = None
        for item in self.items:
            if item.item_id == itemId:
                i = item
                break

        if i is not None:
            i.add_amount(amount)
            return i.amount
        else:
            return -1
        
    def takeItem(self,itemId,amount):
        i = None
        for item in self.items:
            if item.item_id == itemId:
                i = item
                break

        if i is not None:
            i.reduce_amount(amount)
            return True
        else:
            return False

    def processMessage(self,message):
        response = {"type": "Error"}

        if message["type"] == "newItem":
            id = self.addItem(message["name"],message["description"],message["amount"])
            response = {"type":"NewItem", "itemId":id}
        elif message["type"] == "listItems":
            items = self.getItems()
            response = {"type":"ItemList", "items":items}
        elif message["type"] == "buyItem":
            amount = self.putItem(message["itemId"],message["amount"])
            response = {"type": "Error"}
            if amount >= 0:
                response = {"type": "amount", "itemId": message["itemId"], "amount": amount}
        elif message["type"] == "sellItem":
            amount = self.takeItem(message["itemId"],message["amount"])
            response = {"type": "Error"}
            if amount >= 0:
                response = {"type": "amount", "itemId": message["itemId"], "amount": amount}
        else:
            logging.info(f"No message type matched")
        return response      


    def __str__(self) -> str:
        return f"{[item.__str__() for item in self.items]}"