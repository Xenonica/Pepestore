import shelve
from datetime import datetime

class Listing :
    def __init__(self, name, price, description, category,OP, seller_name, quantity):
        db = shelve.open('storage.db', 'c')
        try :
            listingsDict = db['Listings']
            key = list(listingsDict.keys())
            count = sorted(key)[-1]
        except :
            count = 0
        count += 1
        self.__listingID = count
        self.__name = name
        self.__price = price
        self.__description = description
        self.__category = category
        self.__OP = OP
        self.__seller_name = seller_name
        self.__visits = 0
        self.__quantity = quantity

    def get_quantity(self):
        return self.__quantity

    def set_quantity(self, quantity):
        self.__quantity = quantity

    def get_visits(self):
        return self.__visits

    def set_visits(self, visits):
        self.__visits = visits

    def get_piclist(self):
        try :
            return self.__piclist
        except:
            self.__piclist = []
            return self.__piclist

    def get_displaypic(self):
        return self.__piclist[0]

    def get_listingID(self):
        return self.__listingID

    def get_name(self):
        return self.__name

    def get_price(self):
        return self.__price

    def get_description(self):
        return self.__description

    def get_category(self):
        return self.__category

    def get_OP(self):
        return self.__OP

    def get_seller_name(self):
        return self.__seller_name

    def set_seller_name(self, seller_name):
        self.__seller_name = seller_name

    def set_piclist(self, piclist):
        self.__piclist = piclist

    def set_listingID(self, listingID):
        self.__listingID = listingID

    def set_name(self, name):
        self.__name = name

    def set_price(self, price):
        self.__price = price

    def set_description(self, description):
        self.__description = description

    def set_category(self, category):
        self.__category = category


class Phone(Listing):
    def __init__(self,name, price, description, category, seller_name, quantity, brand, ram, storage):
        super().__init__(name, price, description, category, seller_name, quantity)
        self.brand = brand
        self.ram = ram
        self.storage = storage



class User :
    def __init__(self, username, email, password):
        db = shelve.open('storage.db', 'c')
        try :
            usersDict = db['Users']
            key = list(usersDict.keys())
            count = sorted(key)[-1]
        except :
            count = 0
        count += 1
        self.__userID = count
        self.__username = username
        self.__email = email
        self.__password = password
        self.__chats = []
        self.__sales = []
        self.__purchases = []
        self.__profpic = 'http://s3.amazonaws.com/37assets/svn/765-default-avatar.png'
        self.__bannerpic = 'https://images.unsplash.com/photo-1523895665936-7bfe172b757d?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&w=1000&q=80'
        self.__address1 = ''
        self.__address2 = ''
        self.__zipcode = ''
        self.__status = 'Normal'
        self.__sellerReviews = []
        self.__buyerReviews = []
        self.__allReviews = []
        self.__description = ''


    def get_userID(self):
        return self.__userID

    def get_username(self):
        return self.__username

    def get_email(self):
        return self.__email

    def get_password(self):
        return self.__password

    def get_chats(self):
        return self.__chats

    def get_sales(self):
        return self.__sales

    def get_purchases(self):
        return self.__purchases

    def get_profpic(self):
        return self.__profpic

    def get_bannerpic(self):
        return self.__bannerpic

    def get_address1(self):
        return self.__address1

    def get_address2(self):
        return self.__address2

    def get_zipcode(self):
        return self.__zipcode

    def get_status(self):
        return self.__status

    def get_sellerReviews(self):
        return self.__sellerReviews

    def get_buyerReviews(self):
        return self.__buyerReviews

    def get_allReviews(self):
        return self.__allReviews

    def get_description(self):
        return self.__description

    def set_userID(self, userID):
        self.__userID = userID

    def set_username(self, username):
        self.__username = username

    def set_email(self, email):
        self.__email = email

    def set_password(self, password):
        self.__password = password

    def set_chats(self,chatID):
        self.__chats.append(chatID)

    def set_sales(self,sale):
        self.__sales.append(sale)

    def set_purchases(self,purchases):
        self.__purchases.append(purchases)

    def set_profpic(self,profpic):
        self.__profpic = profpic

    def set_bannerpic(self,bannerpic):
        self.__bannerpic = bannerpic

    def set_address1(self,address1):
        self.__address1 = address1

    def set_address2(self,address2):
        self.__address2 = address2

    def set_zipcode(self,zipcode):
        self.__zipcode = zipcode

    def set_status(self,status):
        self.__status = status

    def set_sellerReviews(self,review):
        self.__sellerReviews.append(review)

    def set_buyerReviews(self,review):
        self.__buyerReviews.append(review)

    def set_allReviews(self,review):
        self.__allReviews.append(review)

    def set_description(self,description):
        self.__description = description

class Owner(User):
    def __init__(self, username, email, password):
        super().__init__(username, email, password)
        self.__status = 'Owner'

    def get_status(self):
        return self.__status

class Chat :
    def __init__(self,sellerID,buyerID,listingID):
        db = shelve.open('storage.db', 'c')
        try :
            chatsDict = db['Chats']
            key = list(chatsDict.keys())
            count = sorted(key)[-1]
        except :
            count = 0
        count += 1
        self.__chatID = count
        self.__sellerID = sellerID
        self.__buyerID = buyerID
        self.__listingID = listingID
        self.__chatLog = []
        self.__offersprice = []
        self.__offersquantity = []
        self.__BuyerLastOnline = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.__SellerLastOnline = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.__buyerreviews = 0
        self.__sellerreviews = 0

    def get_chatID(self):
        return self.__chatID

    def get_listingID(self):
        return  self.__listingID

    def get_sellerID(self):
        return self.__sellerID

    def get_buyerID(self):
        return self.__buyerID

    def get_chatLog(self):
        return self.__chatLog

    def get_offersprice(self):
        return self.__offersprice

    def get_offersquantity(self):
        return self.__offersquantity

    def get_BuyerLastOnline(self):
        return self.__BuyerLastOnline

    def get_SellerLastOnline(self):
        return self.__SellerLastOnline

    def get_buyerreview(self):
        return self.__buyerreviews

    def get_sellerreview(self):
        return self.__sellerreviews

    def set_chatLog(self,chatLog):
        self.__chatLog = chatLog

    def set_offersprice(self,offersprice):
        self.__offersprice = offersprice

    def set_offersquantity(self,offersquantity):
        self.__offersquantity = offersquantity

    def set_BuyerLastOnline(self,lastonline):
        self.__BuyerLastOnline = lastonline

    def set_SellerLastOnline(self,lastonline):
        self.__SellerLastOnline = lastonline

    def set_buyerreview(self,review):
        self.__buyerreviews = review

    def set_sellerreview(self,review):
        self.__sellerreviews     = review

class Delivery:
    def __init__(self, username, product, location,firstName,lastName,shipping,method,remarks):
        db = shelve.open('storage.db','c')
        try:
            deliveryDict = db['Delivery']
            key = list(deliveryDict.keys())
            count = sorted(key)[-1]
        except:
            count = 0
        count += 1
        self.__firstName= firstName
        self.__lastName = lastName
        self.__shipping = shipping
        self.__method = method
        self.__remarks = remarks

        self.__deliveryID = count
        self.__username = username
        self.__product  = product
        self.__location = location
        self.__status = ''
        self.__time = ''
        self.__estimatedTime = ''


    def get_firstName(self):
        return self.__firstName

    def get_lastName(self):
        return self.__lastName

    def get_shipping(self):
        return self.__shipping

    def get_method(self):
        return self.__method

    def get_remarks(self):
        return self.__remarks


    def get_estimatedTime(self):
        return self.__estimatedTime

    def set_estimatedTime(self, estimatedTime):
        self.__estimatedTime = estimatedTime

    def get_deliveryID(self):
        return self.__deliveryID

    def get_username(self):
        return self.__username

    def get_product(self):
        return self.__product

    def get_location(self):
        return self.__location

    def set_deliveryID(self, deliveryID):
        self.__deliveryID = deliveryID

    def set_username(self, username):
        self.__username = username

    def set_product(self, product):
        self.__product = product

    def set_location(self, location):
        self.__location = location

    def get_status(self):
        return self.__status

    def set_status(self, status):
        self.__status = status

    def get_time(self):
        return self.__time

    def set_time(self, time):
        self.__time = time


    def set_userID(self, userID):
        self.__userID = userID

    def set_firstName(self, firstName):
        self.__firstName = firstName

    def set_lastName(self, lastName):
        self.__lastName = lastName

    def set_shipping(self, shipping):
        self.__shipping = shipping

    def set_method(self,method):
        self.__method = method

    def set_remarks(self, remarks):
        self.__remarks = remarks

class Purchase:
    def __init__(self,productID,price,quantity,chatID):
        self.__productID = productID
        self.__price = price
        self.__quantity = quantity
        self.__chatID = chatID

    def get_productID(self):
        return self.__productID

    def get_price(self):
        return self.__price

    def get_quantity(self):
        return self.__quantity

    def get_chatID(self):
        return self.__chatID

class Review:
    def __init__(self,sender,receiver,listing,rating,feedback,seller):
        self.__sender = sender
        self.__receiver = receiver
        self.__listing = listing
        self.__rating = rating
        self.__feedback = feedback
        self.__seller = seller

    def get_sender(self):
        return self.__sender

    def get_receiver(self):
        return self.__receiver

    def get_listing(self):
        return self.__listing

    def get_rating(self):
        return self.__rating

    def get_feedback(self):
        return self.__feedback

    def get_seller(self):
        return self.__seller



class FAQ:
    countID=0
    def __init__(self,fullName,gender,contact,email):
        FAQ.countID+=1
        self.__userID=FAQ.countID
        self.__fullName=fullName
        self.__gender=gender
        self.__contact=contact
        self.__email=email
    def get_userID(self):
        return self.__userID

    def get_fullName(self):
        return self.__fullName

    def get_gender(self):
        return self.__gender

    def get_contact(self):
        return self.__contact

    def get_email(self):
        return self.__email


    def set_userID(self, userID):
        self.__userID = userID

    def set_fullName(self, fullName):
        self.__fullName = fullName

    def set_contact(self, contact):
        self.__contact = contact

    def set_gender(self, gender):
        self.__gender = gender

    def set_email(self, email):
        self.__email = email