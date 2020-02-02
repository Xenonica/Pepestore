from wtforms import Form, StringField, RadioField, SelectField, TextAreaField, validators, PasswordField, SubmitField , FloatField , DecimalField
from wtforms.fields.html5 import EmailField , IntegerField


class CreateListing(Form):
    name = StringField('Listing Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    price = DecimalField('Price', [validators.NumberRange(min=0,max=9999),validators.DataRequired()],default=0)
    description = TextAreaField('Description', [validators.Length(min=0, max=200)])
    quantity = IntegerField('Quantity', [validators.DataRequired()])
    category = SelectField('Category', [validators.DataRequired()], choices=[('', 'Select'),('Electronics', 'Electronics'), ('Home Appliances', 'Home Appliances'),
                                       ('Sports', 'Sports'),
                                       ('Books/Stationary', 'Books/Stationary'), ('Vehicles', 'Vehicles'),
                                       ('Health/Beauty', 'Health/Beauty'),
                                       ('Fashion', 'Fashion'), ('Luxury', 'Luxury'),
                                       ('Entertainment', 'Entertainment'), ('Toys/Games', 'Toys/Games'),
                                       ('Food/Drinks', 'Food/Drinks'),
                                       ('Babies/Kids', 'Babies/Kids'), ('Furniture', 'Furniture')], default='')

    filter_type = SelectField('Item Type', [validators.DataRequired()],
                              choices=[('All', 'All'), ('Electronics', 'Electronics'), ('Home Appliances', 'Home Appliances'),
                                       ('Sports', 'Sports'),
                                       ('Books/Stationary', 'Books/Stationary'), ('Vehicles', 'Vehicles'),
                                       ('Health/Beauty', 'Health/Beauty'),
                                       ('Fashion', 'Fashion'), ('Luxury', 'Luxury'),
                                       ('Entertainment', 'Entertainment'), ('Toys/Games', 'Toys/Games'),
                                       ('Food/Drinks', 'Food/Drinks'),
                                       ('Babies/Kids', 'Babies/Kids'), ('Furniture', 'Furniture')], default='All')


class CreateAccount(Form):
    username = StringField('Username', [validators.Length(min=1, max=150), validators.DataRequired()])
    email = EmailField('Email',[validators.DataRequired(),validators.Email()])
    password = PasswordField('Password', [validators.Length(min=1, max=150), validators.DataRequired()])
    register = SubmitField('Register')


class LoginAccount(Form):
    username = StringField('Username', [validators.Length(min=1, max=150), validators.DataRequired()])
    password = PasswordField('Password', [validators.Length(min=1, max=150), validators.DataRequired()])
    login = SubmitField('Login')


class Logout(Form):
    logout = SubmitField('Logout')


class Chat(Form):
    chat = SubmitField('Chat')


class ChatOffer(Form):
    price = FloatField('State your offer', [validators.NumberRange(min=0,max=9999),validators.DataRequired()],default=0)
    quantity = IntegerField('Quantity',[validators.DataRequired()],default=1)


class ProfileForm(Form):
    username = StringField('Username', [validators.Length(min=1, max=30), validators.DataRequired()])
    description = TextAreaField('Description', [validators.Length(min=1, max=300), validators.Optional()])


class CreateDeliveryForm(Form):
    product = StringField('product ID', [validators.Length(min=1, max=150), validators.DataRequired()])
    location = StringField('location', [validators.Length(min=1, max=150), validators.DataRequired()])

