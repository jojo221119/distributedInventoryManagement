import logging
from flask import Flask, render_template, request, redirect, flash
from flask_bootstrap import Bootstrap5

from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

from serverAPI.serverAPI import ServerAPI

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set the desired logging level
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()  # Log to the console
        # Add additional handlers or specify a file to log to
    ]
)

app = Flask(__name__)
# This does never belong in a git... Buuuuut since this is uni project..
app.secret_key = 'ksdh&f|HeuWIW0?$'

# Bootstrap-Flask requires this line
bootstrap = Bootstrap5(app)
# Flask-WTF requires this line
csrf = CSRFProtect(app)

serverAPI = ServerAPI()

class ItemForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(3, 15)])
    description = StringField('Description', validators=[DataRequired(), Length(10, 150)])
    amount = IntegerField('Amount', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Add new item to warehouse')

class BuyForm(FlaskForm):
    buy_amount = IntegerField('Amount', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Buy')

class SellForm(FlaskForm):
    sell_amount = IntegerField('Amount', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Sell')

# simple item model 
class ItemModel():
    def __init__(self, item_id, name, description, amount):
        self.item_id = item_id # this is the primary key
        self.name = name
        self.description = description
        self.amount = amount


@app.route('/', methods=['POST', 'GET'])
def index():
    item_form = ItemForm()
    if request.method == 'POST':
        if item_form.validate_on_submit():
            message = {"type":"newItem", "name": item_form.name.data, "description": item_form.description.data, "amount": item_form.amount.data}
            response = serverAPI.sendMessageToServer(message)
            if response["type"] == "Error":
                abort(400)
            message = {"type":"listItems"}
            response = serverAPI.sendMessageToServer(message)
            if response["type"] == "Error":
                abort(404)
            items = []
            if response["type"] == "ItemList":
                items = [ItemModel(item_id=int(item['item_id']), name=item['name'], description=item['description'], amount=item['amount']) for item in response["items"]]
                app.logger.info(f"{items}")
            return render_template('client_index.html', item_form=item_form, items=items)
        else:
            return redirect('/')
    else:
        message = {"type":"listItems"}
        response = serverAPI.sendMessageToServer(message)
        items = []
        if response["type"] == "ItemList":
            items = [ItemModel(item_id=int(item['item_id']), name=item['name'], description=item['description'], amount=item['amount']) for item in response["items"]]
            app.logger.info(f"{items}")
        return render_template('client_index.html', item_form=item_form, items=items)

@app.route('/buy/<int:item_id>', methods=['POST', 'GET'])
def buy(item_id):
    trade_form = BuyForm()
    if request.method == 'POST':
        if trade_form.validate_on_submit():
            amount = trade_form.buy_amount.data
            message = {"type":"buyItem", "itemId": item_id, "amount": amount}
            response = serverAPI.sendMessageToServer(message)
            flash(f"You bought {amount}")
            return redirect('/')
    else:
        return render_template('client_trade.html', trade_form=trade_form)


@app.route('/sell/<int:item_id>', methods=['GET', 'POST'])
def sell(item_id):
    trade_form = SellForm()
    if request.method == 'POST':
        if trade_form.validate_on_submit():
            amount = trade_form.sell_amount.data
            message = {"type":"sellItem", "itemId": item_id, "amount": amount}
            response = serverAPI.sendMessageToServer(message)
            flash(f"You sold {amount}")
            return redirect('/')
        else:
            flash("Error filling out form")
            return redirect('/')
    else:
        return render_template('client_trade.html', trade_form=trade_form)

if __name__ == '__main__':
    app.run(debug=False, port=8082,host="0.0.0.0")