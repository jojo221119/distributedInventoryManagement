from flask import Flask, render_template, request, redirect
from flask_bootstrap import Bootstrap5

from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length

app = Flask(__name__)
# this does not actually belong in a git but since this is uni project..
app.secret_key = 'ksdh&f|HeuWIW0?$'

# Bootstrap-Flask requires this line
bootstrap = Bootstrap5(app)
# Flask-WTF requires this line
csrf = CSRFProtect(app)

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
        # Not sure what post request we want to give the custumer but lets make him create a new item
        if form.validate_on_submit():
            item1 = ItemModel(1, "Schraube", "Kann was festhalten", 25)
            item2 = ItemModel(2, "Kugellager", "Kann Kugeln lagern", 10)
            item3 = ItemModel(3, "Lufthaken", "Für Azubis", 1)
            item4 = ItemModel(4, "Platte", "Eine normale Platte", 1)
            items = [item1, item2, item3, item4]

            new_item = ItemModel(item_id=form.item_id.data, name=form.name.data, description=form.description.data, amount=form.amount.data)
            items.append(new_item)
            return render_template('client_index.html', form=form, items=items)
        else:
            return redirect('/')

        # TODO: Work with try and except


    else:
        # items are created statically
        item1 = ItemModel(1, "Schraube", "Kann was festhalten", 25)
        item2 = ItemModel(2, "Kugellager", "Kann Kugeln lagern", 10)
        item3 = ItemModel(3, "Lufthaken", "Für Azubis", 1)
        item4 = ItemModel(4, "Platte", "Eine normale Platte", 1)
        items = [item1, item2, item3, item4]
        # TODO: here the amount of items need to be requested from server

        return render_template('client_index.html', form=form, items=items)


@app.route('/buy/<int:id>')
def buy(id):
    # TODO: Update ofc
    return("implement this")

@app.route('/sell/<int:id>', methods=['GET', 'POST'])
def sell(id):
    # TODO: Update ofc
    return("implement this")

# if we ever need an errorhandler
#@app.errorhandler(404)

if __name__ == '__main__':
    app.run(debug=True, port=8082)