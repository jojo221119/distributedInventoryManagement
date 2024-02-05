import logging
from flask import Flask, render_template, request, redirect
from flask_bootstrap import Bootstrap5

from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length

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
# this does not actually belong in a git but since this is uni project..
app.secret_key = 'ksdh&f|HeuWIW0?$'

# Bootstrap-Flask requires this line
bootstrap = Bootstrap5(app)
# Flask-WTF requires this line
csrf = CSRFProtect(app)

serverAPI = ServerAPI()

class ItemForm(FlaskForm):
    item_id = IntegerField('Item ID', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired(), Length(3, 15)])
    description = StringField('Description', validators=[DataRequired(), Length(10, 40)])
    amount = IntegerField('Amount', validators=[DataRequired()])
    submit = SubmitField('Add new item to warehouse')

# simple model so I can test stuff on the webpage
# TODO: Change this
class ItemModel():
    def __init__(self, item_id, name, description, amount):
        self.item_id = item_id # should be the primary key if it is desinged like a database
        self.name = name
        self.description = description
        self.amount = amount # amount should ofc come frome the server / database, just a placeholder


@app.route('/', methods=['POST', 'GET'])
def index():
    form = ItemForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            message = {"type":"newItem", "name": form.name.data, "description": form.description.data}
            response = serverAPI.sendMessageToServer(message)

            message = {"type":"listItems"}
            response = serverAPI.sendMessageToServer(message)
            items = []
            if response["type"] == "ItemList":
                items = [ItemModel(item_id=int(item['item_id']), name=item['name'], description=item['description'], amount=item['amount']) for item in response["items"]]
                app.logger.info(f"{items}")
            return render_template('client_index.html', form=form, items=items)
        else:
            return redirect('/')

        # TODO: Work with try and except


    else:
        message = {"type":"listItems"}
        response = serverAPI.sendMessageToServer(message)
        items = []
        if response["type"] == "ItemList":
            items = [ItemModel(item_id=int(item['item_id']), name=item['name'], description=item['description'], amount=item['amount']) for item in response["items"]]
            app.logger.info(f"{items}")
        return render_template('client_index.html', form=form, items=items)


@app.route('/buy/<int:id>')
def buy(id):
    # TODO: Update ofc
    #message = {"type":"buyItem", "itemId": id, "amount": amount}
    #response = serverAPI.sendMessageToServer(message)
    # from Server response = {"type": "amount", "itemId": message["itemId"], "amount": amount}
    return("implement this")

@app.route('/sell/<int:id>', methods=['GET', 'POST'])
def sell(id):
    # TODO: Update ofc
    #message = {"type":"sellItem", "itemId": id, "amount": amount}
    #response = serverAPI.sendMessageToServer(message)
    # from Server response = {"type": "amount", "itemId": message["itemId"], "amount": amount}
    return("implement this")

# if we ever need an errorhandler
#@app.errorhandler(404)

if __name__ == '__main__':
    app.run(debug=False, port=8082,host="0.0.0.0")