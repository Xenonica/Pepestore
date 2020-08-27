from wtforms import Form, StringField, RadioField, SelectField, TextAreaField, validators, PasswordField, SubmitField , FloatField , DecimalField
from wtforms.fields.html5 import EmailField , IntegerField


class CreateListing(Form):
    name = StringField('Listing Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    price = DecimalField('Price', [validators.NumberRange(min=0, max=9999),validators.DataRequired()], default=0)
    description = TextAreaField('Description', [validators.Length(min=0, max=200)])
    quantity = IntegerField('Quantity', [validators.DataRequired(), validators.NumberRange(min=1, max=9999)], default=1)
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
    search_bar = StringField('')


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

class ForgetPassword(Form):
    forgetemail = EmailField('Email',[validators.DataRequired(),validators.Email()])
    submit = SubmitField('Submit')

class ChangePassword(Form):
    changepassword = PasswordField('Password', [validators.Length(min=1, max=150), validators.DataRequired()])
    confirmpassword = PasswordField('Confirm Password', [validators.Length(min=1, max=150), validators.DataRequired()])

class Chat(Form):
    chat = SubmitField('Chat')

class ChatOffer(Form):
    price = FloatField('State your offer', [validators.NumberRange(min=0,max=9999),validators.DataRequired()],default=0)
    quantity = IntegerField('Quantity',[validators.DataRequired()],default=1)


class ProfileForm(Form):
    username = StringField('Username', [validators.Length(min=1, max=30), validators.DataRequired()])
    description = TextAreaField('Description', [validators.Length(min=1, max=300), validators.Optional()])


class CreateDeliveryForm(Form):
    firstName = StringField('First Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    lastName = StringField('Last Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    shipping = SelectField('Type', [validators.DataRequired()],
                           choices=[('', 'Select'), ('Normal Mail', 'Normal Mail'), ('Registered Mail', 'Registered Mail')], default='')
    method = SelectField('Payment Method', [validators.DataRequired()],
                         choices=[('', 'Select'), ('Credit Card', 'Credit Card'), ('Paypal', 'Paypal')], default='')
    remarks = TextAreaField('Remarks', [validators.Optional()])
    location = StringField('Address', [validators.Length(min=1, max=150), validators.DataRequired()])


class CreatePaymentForm(Form):
    firstName = StringField('First Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    lastName = StringField('Last Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    address = StringField('Address', [validators.Length(min=1, max=150), validators.DataRequired()])
    shipping = SelectField('Shipping', [validators.DataRequired()], choices=[('', 'Select'), ('N', 'Normal Mail'), ('R', 'Registered Mail')], default='')
    method = SelectField('Payment Method', [validators.DataRequired()], choices=[('', 'Select'), ('Credit', 'Credit Card'), ('Paypal', 'Paypal')], default='')
    remarks = TextAreaField('Remarks', [validators.Optional()])


class CreateFeedbackForm(Form):
 question = StringField('Question', [validators.Length(min=1,max=150), validators.DataRequired()])
 answer = TextAreaField('Answer', [validators.Length(min=1,max=1000), validators.DataRequired()])

