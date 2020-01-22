import shelve

class Listing :
    def __init__(self, name, price, description, category ,OP, seller_name, quantity, visits):
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
        self.__visits = visits
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
        self.__sales = {}
        self.__purchases = []
        self.__profpic = 'http://s3.amazonaws.com/37assets/svn/765-default-avatar.png'
        self.__address1 = ''
        self.__address2 = ''
        self.__zipcode = ''


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

    def get_address1(self):
        return self.__address1

    def get_address2(self):
        return self.__address2

    def get_zipcode(self):
        return self.__zipcode

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
        self.__sales.update({sale:1})

    def set_purchases(self,purchases):
        self.__purchases.append(purchases)

    def set_profpic(self,profpic):
        self.__profpic = profpic

    def set_address1(self,address1):
        self.__address1 = address1

    def set_address2(self,address2):
        self.__address2 = address2

    def set_zipcode(self,zipcode):
        self.__zipcode = zipcode

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
        self.__offers = []
        self.__BuyerLastOnline = ''
        self.__SellerLastOnline = ''

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

    def get_offers(self):
        return self.__offers

    def get_BuyerLastOnline(self):
        return self.__BuyerLastOnline

    def get_SellerLastOnline(self):
        return self.__SellerLastOnline

    def set_chatLog(self,chatLog):
        self.__chatLog = chatLog

    def set_offers(self,offers):
        self.__offers = offers

    def set_BuyerLastOnline(self,lastonline):
        self.__BuyerLastOnline = lastonline

    def set_SellerLastOnline(self,lastonline):
        self.__SellerLastOnline = lastonline

class Delivery:
    def __init__(self, username, product, location):
        db = shelve.open('storage.db','c')
        try:
            deliveryDict = db['Delivery']
            key = list(deliveryDict.keys())
            count = sorted(key)[-1]
        except:
            count = 0
        count += 1
        self.__deliveryID = count
        self.__username = username
        self.__product  = product
        self.__location = location
        self.__status = ''
        self.__time = ''
        self.__estimatedTime = ''

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