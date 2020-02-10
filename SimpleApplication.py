from flask import Flask, render_template, request, redirect, url_for , session, blueprints
from Forms import CreateListing , CreateAccount , LoginAccount, Logout , Chat , ChatOffer , ProfileForm , CreateDeliveryForm,CreateFeedbackForm,ForgetPassword,ChangePassword
from flask_socketio import SocketIO , send , disconnect
from datetime import datetime , timedelta
import shelve, os , Classes , hashlib,shutil
import folium
import geocoder
from folium import plugins
from geopy import distance
from flask_mail import Mail , Message
import random

# Absolute path of the program
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)
app.secret_key = 'J'
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config.update(
	DEBUG=True,
	#EMAIL SETTINGS
	MAIL_SERVER='smtp.gmail.com',
	MAIL_PORT=465,
	MAIL_USE_SSL=True,
	MAIL_USERNAME = 'PepeStoreXD@gmail.com',
	MAIL_PASSWORD = 'JustMeat123'
	)

mail = Mail(app)


socketio = SocketIO(app)

permimagelist = []
tempimagelist = []
tempimagenames = []
changePasswordList = []
run = 0
counter = 0

#Create static folder if doesn't exist
target = os.path.join(APP_ROOT, 'static/')
if not os.path.isdir(target) :
    os.mkdir(target)

def navbar() :
    global counter
    global changePasswordList
    alert = ''
    logout = Logout(request.form)
    regform = CreateAccount(request.form)
    logform = LoginAccount(request.form)
    fpwform = ForgetPassword(request.form)
    if request.method == 'POST' and counter != 1:
        counter = 1
        #If logout form was used
        if logout.logout.data :
            session.pop('userID',None)
            session.pop('username',None)
            session.pop('profpic',None)
            session.pop('status',None)
        #If register form was used
        if regform.validate() and regform.register.data :
            usedUsernames = []
            usedEmails = []
            usersDict = {}
            db = shelve.open('storage.db', 'c')
            try :
                usersDict = db['Users']
                key = list(usersDict.keys())
                for i in key :
                    usedUsernames.append(usersDict[i].get_username())
                    usedEmails.append(usersDict[i].get_email())
            except :
                pass
            if regform.username.data in usedUsernames :
                alert = 'Username already in use.'
            elif regform.email.data in usedEmails :
                alert = 'Email already in use.'
            else:
                #If no used usernames means that its first user ( owner )
                #Uses MD5 to encrypt the password (hash)
                if usedUsernames == []:
                    user = Classes.Owner(regform.username.data, regform.email.data, hashlib.md5(regform.password.data.encode()).hexdigest())
                else:
                    user = Classes.User(regform.username.data, regform.email.data, hashlib.md5(regform.password.data.encode()).hexdigest())
                usersDict[user.get_userID()] = user
                db['Users'] = usersDict
                alert = 'User successfully registered'
                # Test codes
                usersDict = db['Users']
                user = usersDict[user.get_userID()]
                print('A New User Has Been Registered')
                print("Username:",user.get_username(),'\nEmail:',user.get_email(),'\nPassword:',user.get_password(),'\n', "was stored in shelve successfully with userID =", user.get_userID())
                print(user.get_userID(),user.get_status())
            db.close()
        #If login form is used
        if logform.validate() and logform.login.data :
            db = shelve.open('storage.db', 'c')
            try :
                usersDict = db['Users']
                key = list(usersDict.keys())
                alert = 'Invalid User'
                for i in key :
                    if logform.username.data == usersDict[i].get_username() and hashlib.md5(logform.password.data.encode()).hexdigest() == usersDict[i].get_password() :
                        session['userID'] = usersDict[i].get_userID()
                        session['username'] = usersDict[i].get_username()
                        session['profpic'] = usersDict[i].get_profpic()
                        session['status'] = usersDict[i].get_status()
                        alert = 'Login Successful'
                    elif logform.username.data == usersDict[i].get_username() :
                        alert = 'WPW'
            except :
                alert = 'Invalid User'
                pass
            db.close()

        if fpwform.validate() and fpwform.forgetemail.data :
            db = shelve.open('storage.db', 'c')
            try :
                usersDict = db['Users']
                key = list(usersDict.keys())
                print(key)
                for i in key :
                    if fpwform.forgetemail.data == usersDict[i].get_email():
                        mess = 'Reset your password <a href="http://127.0.0.1:5000/changePassword/'+str(i)+'/">here</a>'
                        changePasswordList.append(i)
                        msg = Message('Reset Your Password',sender='PepeStoreXD@gmail.com',recipients=[usersDict[i].get_email()])
                        msg.html = mess
                        mail.send(msg)
                        alert = 'Password Reset Email Sent'
                        print('Mail Sent')
                        db.close()
                        break
                    print('XD')
                    alert = 'WEmail'
            except :
                alert = 'WEmail'
                pass
            db.close()
    return [alert,logout,regform,logform,fpwform]

@app.before_request
def before_request():
    global counter
    counter = 0
    #Make sure that session info is up to date before every request
    db = shelve.open('storage.db', 'c')
    usersDict = {}
    try :
        usersDict = db['Users']
    except:
        pass
    try :
        #If the user account is deleted, logout
        if int(session['userID']) not in list(usersDict.keys()) :
            session.pop('userID',None)
            session.pop('username',None)
            session.pop('profpic',None)
            session.pop('status',None)
            db.close()
            return
        session['status'] = usersDict[session['userID']].get_status()
        session['username'] = usersDict[session['userID']].get_username()
        session['profpic'] = usersDict[session['userID']].get_profpic()
    except:
        pass
    db.close()

@app.route('/',methods=['GET', 'POST'])
def home():
    listingList = []
    listingDict = {}
    mostViewedList = []
    a=[]
    print(session)
    if 'userID' not in session :
        try:
            folder = os.path.join(APP_ROOT, 'static/tempimages/')
            for image in os.listdir(folder):
                image_path = os.path.join(folder, image)
                if os.path.isfile(image_path):
                    os.unlink(image_path)
        except:
            pass
    else :
        pass

    try :
        db = shelve.open('storage.db', 'r')
        listingDict = db['Listings']
        print(listingDict)
        db.close()
    except :
        db = shelve.open('storage.db', 'c')
        db.close()

    for i in listingDict:
        listing = listingDict.get(i)
        listingList.append(listing)
        if listing.get_visits() >= 1:
            a.append(listing)

    a = sorted(a, key=lambda a:a.get_visits(), reverse=True)

    for key in listingList:
        if len(listingList) > 5:
            listingList.remove(key)
        if len(listingList) == 5:
            break
    newestLists = listingList[::-1]

    for i in range(0,5):
        try:
            mostViewedList.append(a[i])
        except IndexError:
            print('IndexError (Most viewed)')
            break

    return render_template('home.html', popularLists=mostViewedList, newestLists =newestLists,alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3] , fpwform= navbar()[4])

@app.route('/changePassword/<int:id>/', methods=['GET', 'POST'])
def changePassword(id):
    global changePasswordList
    if id in changePasswordList:
        usersDict = {}
        same = 'Y'
        cpwform = ChangePassword(request.form)
        db = shelve.open('storage.db', 'a')

        try:
            usersDict = db['Users']
        except:
            print("Error Users")

        if request.method == 'POST' :
            if cpwform.changepassword.data == cpwform.confirmpassword.data and cpwform != '':
                print(cpwform.changepassword.data)
                usersDict[id].set_password(hashlib.md5(cpwform.changepassword.data.encode()).hexdigest())
                changePasswordList.remove(id)
                return redirect(url_for('home'))
            else:
                same = 'N'
        db['Users'] = usersDict
        db.close()
    else:
        return redirect(url_for('home'))
    return render_template('changePassword.html',same=same,cpwform = cpwform,alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3] , fpwform= navbar()[4])

@app.route('/createUserImages',methods=['GET', 'POST'])
def createUserImages():
    if request.method == 'POST':
        todelete = request.form['todelete']
        if todelete == '':

            #Path of where to store images
            target = os.path.join(APP_ROOT, 'static/tempimages/')

            #Check whether path target exists / creates path if it doesn't.
            if not os.path.isdir(target) :
                os.mkdir(target)

            #Go through multiple images
            count = 0
            for file in request.files.getlist("file") :
                if count < 4 :
                    filename = file.filename
                    if filename == '' :
                        break
                    else :
                        filename = file.filename
                        #Make directory for image
                        destination = '/'.join([target]+[filename])
                        file.save(destination)
                        staticdestination = url_for('static', filename='tempimages/'+filename)
                        # print('staticdest', staticdestination)
                        count+=1
                        if staticdestination in tempimagelist :
                            continue
                        else:
                            tempimagelist.append(staticdestination)
                            # tempimagelist.append(filename)
                            # tempimagenames.append(filename)
        else :
            todeleteplace = int(todelete)-1
            try:
                os.remove(tempimagelist[todeleteplace][1:])
                tempimagelist.remove(tempimagelist[todeleteplace])
            except IndexError:
                print('idk why')
            # tempimagenames.remove(tempimagenames[todeleteplace])

    Img = ['','','','']
    print('temp',tempimagelist)

    for i in range(len(tempimagelist)):
        try:
            Img[i] = tempimagelist[i]
        except IndexError:
            print('Max 4 images are allowed')
            break

    print('img ', Img)

    return render_template('createUserImages.html', Img1=Img[0], Img2=Img[1], Img3=Img[2], Img4=Img[3], alert=navbar()[0], logout=navbar()[1], regform=navbar()[2], logform=navbar()[3] , fpwform= navbar()[4])


@app.route('/manageListing', methods=['GET', 'POST'])
def manageListing():
    listingDict = {}
    try :
        db = shelve.open('storage.db', 'r')
        listingDict = db['Listings']
        db.close()
    except :
        db = shelve.open('storage.db', 'c')
        listingDict = []
        db.close()

    listingList = []
    for key in listingDict:
        listing = listingDict.get(key)
        listingList.append(listing)

    return render_template('manageListing.html', listingList=listingList, count=len(listingList),alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3] , fpwform= navbar()[4])


@app.route('/createListing', methods=['GET', 'POST'])
def createListing():
    createlisting = CreateListing(request.form)
    listingDict = {}

    if len(tempimagelist) == 0:
        Image1 = 'https://matthewsenvironmentalsolutions.com/images/com_hikashop/upload/not-available.png'
    else:
        Image1 = tempimagelist[0]

    if request.method == 'POST' and createlisting.validate():
        db = shelve.open('storage.db', 'c')
        try:
            listingDict = db['Listings']
        except:
            print("Error in retrieving 'Listings' from storage.db.")

        listing = Classes.Listing(createlisting.name.data, createlisting.price.data, createlisting.description.data,
                                  createlisting.category.data, session['userID'], session['username'], createlisting.quantity.data)
        listingDict[listing.get_listingID()] = listing
        listing.set_visits(0)

        # Path of where to store images
        target = os.path.join(APP_ROOT, 'static/listings/')
        target1 = os.path.join(APP_ROOT, 'static/listings/', str(listing.get_listingID()))

        # Check whether path target exists / creates path if it doesn't.
        if not os.path.isdir(target):
            os.mkdir(target)
        if not os.path.isdir(target1):
            os.mkdir(target1)

        imgnamecount = 0
        for i in tempimagelist:
            print(i)
            olddir = APP_ROOT + i
            newdir = os.path.join(target1, i[19:])
            newstatic = os.path.join('/static/listings/', str(listing.get_listingID()), i[19:])
            permimagelist.append(newstatic)
            imgnamecount += 1
            print('old', olddir)
            print('new', newdir)
            if not os.path.isfile(newdir):
                os.rename(olddir, newdir)
        listing.set_piclist(permimagelist)
        db['Listings'] = listingDict

        listingDict = db['Listings']
        db.close()

        permimagelist.clear()
        tempimagelist.clear()

        return redirect(url_for('home'))
    return render_template('createListing.html', form=createlisting, Img1=Image1, alert=navbar()[0], logout=navbar()[1],
                           regform=navbar()[2], logform=navbar()[3] , fpwform= navbar()[4])


@app.route('/listingPage/<int:listingID>/',methods=['GET', 'POST'])
def listingPage(listingID) :
    chatform = Chat(request.form)
    usersDict = {}
    listingDict = {}
    chatsDict = {}
    db = shelve.open('storage.db', 'c')

    try:
        usersDict = db['Users']
    except:
        print("Error Users")

    try:
        listingDict = db['Listings']
    except:
        print("Error Listings")

    try:
        chatsDict = db['Chats']
    except:
        print("Error Chats")

    listingslist = []
    if request.method == 'POST' and chatform.chat.data :
        if 'userID' not in session:
            return redirect(url_for('home'))
        if usersDict[session['userID']].get_chats() != '[]':
            for i in usersDict[session['userID']].get_chats() :
                listingslist.append(chatsDict[i].get_listingID())
            chat = Classes.Chat(listingDict[listingID].get_OP(),session['userID'],listingDict[listingID].get_listingID())
            if chat.get_buyerID() != chat.get_sellerID() :
                if listingDict[listingID].get_listingID() not in listingslist :
                    chatsDict[chat.get_chatID()] = chat
                    db['Chats'] = chatsDict
                    usersDict[listingDict[listingID].get_OP()].set_chats(chat.get_chatID())
                    usersDict[session['userID']].set_chats(chat.get_chatID())
                    db['Users'] = usersDict
                    db['Listings'] = listingDict
                    db['Chats'] = chatsDict
                    db.close()

                    return redirect('/UserChats/'+str(chat.get_chatID())+'/')
                else :
                    for i in usersDict[session['userID']].get_chats():
                        if chatsDict[i].get_listingID() == listingDict[listingID].get_listingID():
                            return redirect('/UserChats/'+str(chatsDict[i].get_chatID())+'/')
            else:
                pass

    listingDict[listingID].set_visits(listingDict[listingID].get_visits() + 1)
    print('Number of visits:', listingDict[listingID].get_visits())
    piclist = listingDict[listingID].get_piclist()
    db['Listings'] = listingDict
    db.close()

    return render_template('listingPage.html',piclist=piclist,chatform=chatform,listingID = listingDict[listingID],alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3] , fpwform= navbar()[4])


@app.route('/allListing', methods=['GET','POST'])
def allListing():
    createListing = CreateListing(request.form)
    listingDict = {}

    try:
        db = shelve.open('storage.db', 'r')
        listingDict = db['Listings']
        db.close()
    except:
        print('???????')

    return render_template('allListing.html',count=len(listingDict),form=createListing,listingDict=listingDict,selected_category=createListing.filter_type.data,alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3] , fpwform= navbar()[4])


@app.route('/update/<int:id>/', methods=['GET', 'POST'])
def updateItem(id):
    name = ''
    listingForm = CreateListing(request.form)
    if request.method == 'POST' and listingForm.validate():
        listingDict = {}
        db = shelve.open('storage.db', 'w')
        listingDict = db['Listings']

        for list_id in listingDict:
            if list_id == id:
                listingDict[list_id].set_name(listingForm.name.data)
                listingDict[list_id].set_price(listingForm.price.data)
                listingDict[list_id].set_description(listingForm.description.data)
                listingDict[list_id].set_quantity(listingForm.quantity.data)
                listingDict[list_id].set_category(listingForm.category.data)

        db['Listings'] = listingDict
        db.close()

        return redirect(url_for('manageListing'))
    else:
        listingDict = {}
        try:
            db = shelve.open('storage.db', 'r')
            listingDict = db['Listings']
            db.close()
        except:
            print()

        for list_id in listingDict:
            if list_id == id:
                    listingForm.name.data = listingDict[list_id].get_name()
                    name = listingDict[list_id].get_name()
                    listingForm.price.data = listingDict[list_id].get_price()
                    listingForm.description.data = listingDict[list_id].get_description()
                    listingForm.quantity.data = listingDict[list_id].get_quantity()
                    listingForm.category.data = listingDict[list_id].get_category()
        print(listingDict)

    return render_template('updateItem.html',name=name,form=listingForm,alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3] , fpwform= navbar()[4])


@app.route('/deleteListing/<int:id>', methods=['POST'])
def deleteListing(id):
    listingDict = {}
    db = shelve.open('storage.db', 'w')
    listingDict = db['Listings']
    if listingDict[id].get_approved() == 1:
         listingDict.pop(id)
         shutil.rmtree("static/listings/"+str(id))
         db['Listings'] = listingDict
         db.close()
         return redirect(url_for('manageListing'))
    else:
        listingDict.pop(id)
        shutil.rmtree("static/listings/" + str(id))
        db['Listings'] = listingDict
        db.close()
        return redirect(url_for('pendingListing'))


@app.route('/analytics')
def analytics():
    labels = []
    values = []
    listingDict = {}
    try:
        db = shelve.open('storage.db')
        listingDict = db['Listings']
    except:
        print('db Listing error')
    for listingID in listingDict:
        if session.get('username') == listingDict[listingID].get_seller_name():
            labels.append(listingDict[listingID].get_name())
            values.append(listingDict[listingID].get_visits())
    legend = 'Traffic'
    print(values)
    return render_template('analytics.html', values=values, labels=labels, legend=legend,alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3] , fpwform= navbar()[4])


@app.route('/UserChats/<int:chatID>/',methods=['GET', 'POST'])
def UserChats(chatID) :
    usersDict = {}
    chatsDict = {}
    listingsDict = {}
    db = shelve.open('storage.db', 'c')
    try:
        chatsDict = db['Chats']
    except:
        print("Error Chats")

    try:
        listingsDict = db['Listings']
    except:
        print("Error Listings")

    try:
        usersDict = db['Users']
    except:
        print("Error Users")

    #Make sure that user is authorized to enter the page
    if (session['userID'] == chatsDict[chatID].get_sellerID() or session['userID'] == chatsDict[chatID].get_buyerID()):
        tdeltaseconds = 0
        tdeltaseconds2 = 0
        chatofferform = ChatOffer(request.form)

        if session['userID'] ==  chatsDict[chatID].get_sellerID() :
            OtherProfPic = usersDict[chatsDict[chatID].get_buyerID()].get_profpic()
            Position = 'S'
        else :
            OtherProfPic = usersDict[chatsDict[chatID].get_sellerID()].get_profpic()
            Position = 'B'

        ListingImage = listingsDict[chatsDict[chatID].get_listingID()].get_displaypic()
        ListingName = listingsDict[chatsDict[chatID].get_listingID()].get_name()
        ListingPrice = listingsDict[chatsDict[chatID].get_listingID()].get_price()
        ListingQuantity = listingsDict[chatsDict[chatID].get_listingID()].get_quantity()
        Buyer = usersDict[chatsDict[chatID].get_buyerID()]
        Seller = usersDict[chatsDict[chatID].get_sellerID()]
        if request.method == 'POST' :
            print(request.form['cross'])
            if request.form['cross'] == '1' :
                chatsDict[chatID].set_sellerreview(0)
            elif request.form['cross'] == '2':
                chatsDict[chatID].set_buyerreview(0)
            else:
                if Position == 'S':
                    review = Classes.Review(Seller,Buyer,listingsDict[chatsDict[chatID].get_listingID()],float(request.form.get("rating", False)),request.form['Feedback'],chatsDict[chatID].get_sellerID())
                    Buyer.set_sellerReviews(review)
                    Buyer.set_allReviews(review)
                    chatsDict[chatID].set_sellerreview(0)
                else:
                    review = Classes.Review(Buyer,Seller,listingsDict[chatsDict[chatID].get_listingID()],float(request.form.get("rating", False)),request.form['Feedback'],chatsDict[chatID].get_sellerID())
                    Seller.set_buyerReviews(review)
                    Seller.set_allReviews(review)
                    chatsDict[chatID].set_buyerreview(0)

        BuyerReview = chatsDict[chatID].get_buyerreview()
        SellerReview = chatsDict[chatID].get_sellerreview()
        # print('Buyer Review',BuyerReview)
        # print('Seller Review',SellerReview)

        chatlog = chatsDict[chatID].get_chatLog()
        chatIDx = chatsDict[chatID]
        OffersPrice = chatsDict[chatID].get_offersprice()
        OffersQuantity = chatsDict[chatID].get_offersquantity()
        if chatsDict[chatID].get_SellerLastOnline() != '' :
            T1 = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            T2 = chatsDict[chatID].get_SellerLastOnline()
            FMT = '%Y-%m-%d %H:%M:%S'
            tdelta = datetime.strptime(T1, FMT) - datetime.strptime(T2, FMT)
            tdeltaseconds = tdelta.total_seconds()
        if chatsDict[chatID].get_BuyerLastOnline() != '' :
            T1 = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            T2 = chatsDict[chatID].get_BuyerLastOnline()
            FMT = '%Y-%m-%d %H:%M:%S'
            tdelta2 = datetime.strptime(T1, FMT) - datetime.strptime(T2, FMT)
            tdeltaseconds2 = tdelta2.total_seconds()

    else:
        return redirect(url_for('home'))
    db['Chats'] = chatsDict
    db['Users'] = usersDict
    db.close()

    return render_template('UserChats.html',SellerReview=SellerReview,BuyerReview = BuyerReview,OtherProfPic = OtherProfPic,SOfflineTime = tdeltaseconds,BOfflineTime = tdeltaseconds2,chatID = chatID ,Buyer = Buyer,Seller = Seller,OffersPrice = OffersPrice,OffersQuantity=OffersQuantity,chatIDx = chatIDx,chatofferform = chatofferform,Position=Position,ListingImage = ListingImage,ListingName = ListingName,ListingPrice = ListingPrice,ListingQuantity = ListingQuantity,messages = chatlog,alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3] , fpwform= navbar()[4])

@socketio.on('message')
def handleMessage(msg):
        usersDict = {}
        chatsDict = {}
        listingsDict = {}

        db = shelve.open('storage.db', 'c')
        try:
            chatsDict = db['Chats']
        except:
            print("Error Chats")

        try:
            usersDict = db['Users']
        except:
            print("Error Users")

        try:
            listingsDict = db['Listings']
        except:
            print("Error Listings")

        chatID = request.headers.get("Referer").split('/')[-2]

        ListingQuantity = listingsDict[chatsDict[int(chatID)].get_listingID()].get_quantity()
        if msg == None :
            pass

        if msg[:5] == '/Pos:' :
            if msg[5] == 'B' :
                chatsDict[int(chatID)].set_BuyerLastOnline(msg[7:])
                msg = 'BuyerDisconnected'
            elif msg[5] == 'S' :
                chatsDict[int(chatID)].set_SellerLastOnline(msg[7:])
                msg = 'SellerDisconnected'

        elif msg == '/SellerConnected' :
            chatsDict[int(chatID)].set_SellerLastOnline('')

        elif msg == '/BuyerConnected' :
            chatsDict[int(chatID)].set_BuyerLastOnline('')

        elif '/Offer ' in msg :
            if chatsDict[int(chatID)].get_offersprice() == [] and session['userID'] == chatsDict[int(chatID)].get_buyerID() and int(msg.split(' ')[2]) <= ListingQuantity:
                Offers = msg[7:]
                Offers = str(Offers).split(' ')
                OffersPrice =  float(Offers[0])
                OffersPrice = ("%.2f" % OffersPrice)
                OffersPrice = [float(OffersPrice)]
                chatsDict[int(chatID)].set_offersprice(OffersPrice)
                chatsDict[int(chatID)].set_offersquantity(int(Offers[1]))
            else :
                msg = None

        elif msg == '/CancelOffer':
            if chatsDict[int(chatID)].get_offersprice() != [] and session['userID'] == chatsDict[int(chatID)].get_buyerID():
                chatsDict[int(chatID)].set_offersprice([])
                chatsDict[int(chatID)].set_offersquantity([])
            else:
                msg = None

        elif msg == '/DeclineOffer':
            if chatsDict[int(chatID)].get_offersprice() != [] and session['userID'] == chatsDict[int(chatID)].get_sellerID():
                chatsDict[int(chatID)].set_offersprice([])
                chatsDict[int(chatID)].set_offersquantity([])
            else:
                msg = None

        elif msg == '/AcceptOffer' :
            if chatsDict[int(chatID)].get_offersprice() != [] and session['userID'] == chatsDict[int(chatID)].get_sellerID():
                Purchase = Classes.Purchase(chatsDict[int(chatID)].get_listingID(),float(chatsDict[int(chatID)].get_offersprice()[0]),chatsDict[int(chatID)].get_offersquantity(),int(chatID))
                usersDict[chatsDict[int(chatID)].get_sellerID()].set_sales(Purchase)
                usersDict[chatsDict[int(chatID)].get_buyerID()].set_purchases(Purchase)
                listingsDict[chatsDict[int(chatID)].get_listingID()].set_quantity(ListingQuantity-chatsDict[int(chatID)].get_offersquantity())
                chatsDict[int(chatID)].set_offersprice([])
                chatsDict[int(chatID)].set_offersquantity([])
                msg = '/AcceptOffer'
            else:
                msg = None

        else:
            chatlog = chatsDict[int(chatID)].get_chatLog()
            msgdict = {'Username':session['username']}
            msgdict.update({'Message':msg})
            msgdict.update({'Time':datetime.now().strftime('%H:%M:%S')})
            msgdict.update({'Date':datetime.now().strftime('%Y-%m-%d')})
            msg = msgdict
            chatlog.append(msg)
            chatsDict[int(chatID)].set_chatLog(chatlog)
        db['Listings'] = listingsDict
        db['Users'] = usersDict
        db['Chats'] = chatsDict
        db.close()

        send(msg,broadcast=True)

@app.route('/editUser/<int:id>/', methods=['GET', 'POST'])
def editUser(id):
    userDict = {}
    listingDict = {}
    deliveryDict = {}
    if id == 1 and session['status'] != 'Owner' :
        return redirect(url_for('home'))
    else:
        if session['status'] == 'Admin' or session['status'] == 'Owner' or session['userID'] == id:
            Used = 0
            Profile = ProfileForm(request.form)
            db = shelve.open('storage.db', 'r')
            try:
                userDict = db['Users']
                listingDict = db['Listings']
                deliveryDict = db['Delivery']
            except:
                print('error loading (profile)')
            db.close()
            user = userDict.get(id)
            ProfPic = user.get_profpic()
            Banner = user.get_bannerpic()
            usedUsernames = []
            key = list(userDict.keys())
            for i in key:
                if userDict[i].get_username() != user.get_username():
                    usedUsernames.append(userDict[i].get_username())
            if request.method == 'POST':
                db = shelve.open('storage.db', 'w')
                userDict = db['Users']
                user = userDict.get(id)
                if Profile.username.data not in usedUsernames :
                    for i in deliveryDict:
                        if deliveryDict[i].get_username() == user.get_username():
                            deliveryDict[i].set_username(Profile.username.data)
                    for i in listingDict:
                        if listingDict[i].get_seller_name() == user.get_username():
                            listingDict[i].set_seller_name(Profile.username.data)

                    user.set_username(Profile.username.data)

                else:
                    Used=1
                user.set_description(Profile.description.data)
                #Path of where to store images
                target = os.path.join(APP_ROOT, 'static/users/')
                target1 = os.path.join(APP_ROOT, 'static/users/', str(user.get_userID()))
                target2 = os.path.join(APP_ROOT, 'static/users/', str(user.get_userID()),'ProfPic')
                target3 = os.path.join(APP_ROOT, 'static/users/', str(user.get_userID()),'Banner')
                #Check whether path target exists / creates path if it doesn't.
                if not os.path.isdir(target) :
                    os.mkdir(target)
                if not os.path.isdir(target1) :
                    os.mkdir(target1)
                if not os.path.isdir(target2) :
                    os.mkdir(target2)
                if not os.path.isdir(target3) :
                    os.mkdir(target3)
                try :
                    newProfPic = request.files.get('file')
                    filename = newProfPic.filename
                    if filename != '':
                        for root, dirs, files in os.walk(target2):
                            for f in files:
                                os.unlink(os.path.join(root, f))
                    #Make directory for image
                    destination = '/'.join([target2]+[filename])
                    newProfPic.save(destination)
                    staticdestination = '/static/users/'+ str(user.get_userID())+'/ProfPic/'+filename+'/'
                    print(staticdestination)
                    user.set_profpic(staticdestination)
                    session['profpic'] = user.get_profpic()
                    ProfPic = user.get_profpic()
                except:
                    pass

                try :
                    newBanner = request.files.get('banner')
                    filename = newBanner.filename
                    if filename != '':
                        for root, dirs, files in os.walk(target3):
                            for f in files:
                                os.unlink(os.path.join(root, f))
                    #Make directory for image
                    destination = '/'.join([target3]+[filename])
                    newBanner.save(destination)
                    staticdestination = '/static/users/'+ str(user.get_userID())+'/Banner/'+filename+'/'
                    user.set_bannerpic(staticdestination)
                    Banner = user.get_bannerpic()
                except:
                    pass

                ProfPic = user.get_profpic()
                db['Users'] = userDict
                db['Listings'] = listingDict
                db['Delivery'] = deliveryDict
                db.close()
            else:
                user = userDict.get(id)
                Profile.username.data = user.get_username()
                Profile.description.data = user.get_description()
        else:
            return redirect(url_for('home'))

    return render_template('editUser.html',id=id,Used=Used,Banner=Banner,ProfPic = ProfPic,Profile = Profile,alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3] , fpwform= navbar()[4])

@app.route('/userProfile/<int:id>/', methods=['GET', 'POST'])
def userProfile(id):
    db = shelve.open('storage.db', 'w')
    userDict = db['Users']
    ProfPic = userDict[id].get_profpic()
    Banner = userDict[id].get_bannerpic()
    Username = userDict[id].get_username()
    Description = userDict[id].get_description()
    listingDict = {}
    userListings = []
    userReviews = userDict[id].get_allReviews()
    userRating = 0
    try:
        db = shelve.open('storage.db', 'r')
        listingDict = db['Listings']
        db.close()
    except:
        pass
    for i in listingDict :
        if listingDict[i].get_OP() == id :
            userListings.append(listingDict[i])

    if len(userReviews) != 0 :
        for i in userReviews:
            userRating+=i.get_rating()
        userRating = round((userRating/len(userReviews))*2)/2

    reviewsamt = len(userReviews)

    return render_template('userProfile.html',Description=Description,id=id,reviewsamt=reviewsamt,userRating=userRating,Username=Username,Banner=Banner,ProfPic = ProfPic,userListings = userListings,alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3] , fpwform= navbar()[4])

@app.route('/userProfile/<int:id>/reviews/', methods=['GET', 'POST'])
def userProfileReviews(id):
    db = shelve.open('storage.db', 'w')
    userDict = db['Users']
    Description = userDict[id].get_description()
    ProfPic = userDict[id].get_profpic()
    Banner = userDict[id].get_bannerpic()
    Username = userDict[id].get_username()
    listingDict = {}
    userListings = []
    userReviews = userDict[id].get_allReviews()
    userRating = 0
    try:
        db = shelve.open('storage.db', 'r')
        listingDict = db['Listings']
        db.close()
    except:
        pass

    for i in listingDict :
        if listingDict[i].get_OP() == id :
            userListings.append(listingDict[i])

    if len(userReviews) != 0 :
        for i in userReviews:
            userRating+=i.get_rating()
        userRating = round((userRating/len(userReviews))*2)/2

    reviewsamt = len(userReviews)

    return render_template('userProfileReviews.html',Description=Description,select='all',userReviews=userReviews,id=id,reviewsamt=reviewsamt,userRating=userRating,Username=Username,Banner=Banner,ProfPic = ProfPic,userListings = userListings,alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3] , fpwform= navbar()[4])

@app.route('/userProfile/<int:id>/reviews/sellers/', methods=['GET', 'POST'])
def userProfileReviewsSellers(id):
    db = shelve.open('storage.db', 'w')
    userDict = db['Users']
    Description = userDict[id].get_description()
    ProfPic = userDict[id].get_profpic()
    Banner = userDict[id].get_bannerpic()
    Username = userDict[id].get_username()
    listingDict = {}
    userListings = []
    userReviews = userDict[id].get_allReviews()
    userSellerReviews = userDict[id].get_sellerReviews()
    userRating = 0
    try:
        db = shelve.open('storage.db', 'r')
        listingDict = db['Listings']
        db.close()
    except:
        pass

    for i in listingDict :
        if listingDict[i].get_OP() == id :
            userListings.append(listingDict[i])

    if len(userReviews) != 0 :
        for i in userReviews:
            userRating+=i.get_rating()
        userRating = round((userRating/len(userReviews))*2)/2

    reviewsamt = len(userReviews)

    return render_template('userProfileReviews.html',Description=Description,select = 'sellers',userReviews=userSellerReviews,id=id,reviewsamt=reviewsamt,userRating=userRating,Username=Username,Banner=Banner,ProfPic = ProfPic,userListings = userListings,alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3] , fpwform= navbar()[4])

@app.route('/userProfile/<int:id>/reviews/buyers/', methods=['GET', 'POST'])
def userProfileReviewsBuyers(id):
    db = shelve.open('storage.db', 'w')
    userDict = db['Users']
    Description = userDict[id].get_description()
    ProfPic = userDict[id].get_profpic()
    Banner = userDict[id].get_bannerpic()
    Username = userDict[id].get_username()
    listingDict = {}
    userListings = []
    userReviews = userDict[id].get_allReviews()
    userBuyerReviews = userDict[id].get_buyerReviews()
    userRating = 0
    try:
        db = shelve.open('storage.db', 'r')
        listingDict = db['Listings']
        db.close()
    except:
        pass

    for i in listingDict :
        if listingDict[i].get_OP() == id :
            userListings.append(listingDict[i])

    if len(userReviews) != 0 :
        for i in userReviews:
            userRating+=i.get_rating()
        userRating = round((userRating/len(userReviews))*2)/2

    reviewsamt = len(userReviews)

    return render_template('userProfileReviews.html',Description=Description,select = 'buyers',userReviews=userBuyerReviews,id=id,reviewsamt=reviewsamt,userRating=userRating,Username=Username,Banner=Banner,ProfPic = ProfPic,userListings = userListings,alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3] , fpwform= navbar()[4])

@app.route('/Cart',methods=['GET', 'POST'])
def Cart():
    PurchaseList = []
    listingDict = {}
    userDict = {}
    chatDict = {}

    db = shelve.open('storage.db', 'c')

    try:
        listingDict = db['Listings']
    except:
        print("Error in retrieving Listings")

    try:
        userDict = db['Users']
    except:
        print("Error in retrieving Users")

    try:
        chatDict = db['Chats']

    except:
        print("Error in retrieving Chats")

    Purchases = userDict[session['userID']].get_purchases()
    TotalPrice = 0
    for i in Purchases :
        TotalPrice += i.get_price()*i.get_quantity()

    if request.method=='POST' :
        return redirect(url_for('createDelivery'))

    db['Chats'] = chatDict
    db.close()

    return render_template('Cart.html',TotalPrice=('%.2f'%TotalPrice),Purchases = Purchases,listingDict = listingDict,alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3] , fpwform= navbar()[4])

@app.route('/pendingListing', methods=['GET', 'POST'])
def pendingListing():
    if session['status'] == 'Admin' or session['status'] == 'Owner':
        listingDict = {}
        try :
            db = shelve.open('storage.db', 'r')
            listingDict = db['Listings']
            db.close()
        except :
            print('Error retrieving Listings')

        listingList = []
        for key in listingDict:
            if listingDict[key].get_approved() == 0 :
                listing = listingDict.get(key)
                listingList.append(listing)
    else:
        return redirect(url_for('home'))

    return render_template('pendingListing.html', listingList = listingList,alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3] , fpwform= navbar()[4])

@app.route('/approveListing/<int:id>', methods=['GET', 'POST'])
def approveListing(id):
    listingsDict = {}
    db = shelve.open('storage.db', 'w')
    listingsDict = db['Listings']
    listingsDict[id].approve()
    db['Listings'] = listingsDict
    db.close()
    return redirect(url_for('pendingListing'))

@app.route('/retrieveUsers', methods=['GET', 'POST'])
def retrieveUsers():
    if session['status'] == 'Admin' or session['status'] == 'Owner':
        userDict = {}
        try :
            db = shelve.open('storage.db', 'r')
            userDict = db['Users']
            db.close()
        except :
            print('Error retrieving Users')

        userList = []
        for key in userDict:
            user = userDict.get(key)
            userList.append(user)
    else:
        return redirect(url_for('home'))

    return render_template('retrieveUsers.html', userList=userList, count=len(userList),alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3] , fpwform= navbar()[4])

@app.route('/deleteUser/<int:id>', methods=['GET', 'POST'])
def deleteUser(id):
    usersDict = {}
    db = shelve.open('storage.db', 'w')
    usersDict = db['Users']
    usersDict.pop(id)
    db['Users'] = usersDict
    db.close()
    if session['userID'] != id:
        return redirect(url_for('retrieveUsers'))
    else:
        return redirect(url_for('home'))

@app.route('/makeAdmin/<int:id>', methods=['GET', 'POST'])
def makeAdmin(id):
    if id != 1 :
        usersDict = {}
        db = shelve.open('storage.db', 'w')
        usersDict = db['Users']
        usersDict[id].set_status('Admin')
        db['Users'] = usersDict
        db.close()
    return redirect(url_for('retrieveUsers'))

@app.route('/makeNormal/<int:id>', methods=['GET', 'POST'])
def makeNormal(id):
    if id != 1 :
        usersDict = {}
        db = shelve.open('storage.db', 'w')
        usersDict = db['Users']
        usersDict[id].set_status('Normal')
        db['Users'] = usersDict
        db.close()
    return redirect(url_for('retrieveUsers'))

@app.route('/AllChats')
def AllChats():
    ChatList = []
    listingDict = {}
    chatDict = {}
    userDict = {}

    db = shelve.open('storage.db', 'c')

    try:
        listingDict = db['Listings']
    except:
        print("Error in retrieving Listings")

    try:
        chatDict = db['Chats']
    except:
        print("Error in retrieving Chats")

    try:
        userDict = db['Users']
    except:
        print("Error in retrieving Users")

    Chats = userDict[session['userID']].get_chats()

    for i in Chats :
        ChatList.append(chatDict[i])


    return render_template('AllChats.html',userDict = userDict,listingDict = listingDict,ChatList = ChatList,alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3] , fpwform= navbar()[4])

@app.route('/retrieveDelivery')
def retrieveDelivery():
    if session['status'] == "Owner" or session['status'] == "Admin" :
        deliveryDict = {}
        db = shelve.open('storage.db', 'w')
        try:

            deliveryDict = db['Delivery']

        except:
            print(deliveryDict)

        deliveryList = []
        for key in deliveryDict:
            delivery = deliveryDict.get(key)
            deliveryList.append(delivery)

        for key in deliveryList:
            print(deliveryList)
            if key.get_status() == "In Delivery":
                if datetime.now() > key.get_estimatedTime():
                    key.set_status('Delivered')

        db.close()


    else:
        return redirect(url_for('home'))

    return render_template('retrieveDelivery.html', deliveryList=deliveryList, count=len(deliveryList),alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3] , fpwform= navbar()[4])


def validateaddress(location):
    center_point = [{'lat': 1.290270, 'lng': 103.851959}] #center point of singapore coordinates
    address = geocoder.osm(location)
    x = address.lat
    y = address.lng
    test_point = [{'lat': x, 'lng': y}]
    radius = 24 # in kilometer

    center_point_tuple = tuple(center_point[0].values())
    test_point_tuple = tuple(test_point[0].values())

    dis = distance.distance(center_point_tuple, test_point_tuple).km
    print("Distance: {}".format(dis))

    if dis <= radius: # if the location is in Singapore
        return True
    else:            # if the  location is not in Singapore
        return False


@app.route('/createDelivery', methods=['GET', 'POST'])
def createDelivery():
    createDeliveryForm = CreateDeliveryForm(request.form)
    if request.method == 'POST' and createDeliveryForm.validate():
        IDs = []
        SellerNames = []
        userDict = {}
        deliveryDict = {}
        listingDict = {}
        db = shelve.open('storage.db', 'c')

        try:
            deliveryDict = db['Delivery']
            print(deliveryDict)
        except:
            print("Error in retrieving delivery from storage")

        try:
            listingDict = db['Listings']
        except:
            print("Error in retrieving listings from storage")

        try:
            userDict = db['Users']
        except:
            print("Error in retrieving Users")

        try:
            chatDict = db['Chats']
        except:
            print("Error in retrieving Chats")

        Purchases = userDict[session['userID']].get_purchases()

        for i in Purchases:
            IDs.append(i.get_productID())

        AllID = (''.join(str(IDs))).replace('[','').replace(']','')

        for i in IDs :
            SellerNames.append(listingDict[i].get_seller_name())

        AllSellerNames = ((''.join(str(SellerNames))).replace('[','').replace(']','').replace("'",''))
        print(AllSellerNames)

        if validateaddress(createDeliveryForm.location.data) == True:
            delivery = Classes.Delivery(session['username'],AllSellerNames,AllID, createDeliveryForm.location.data, createDeliveryForm.firstName.data,createDeliveryForm.lastName.data,createDeliveryForm.shipping.data,createDeliveryForm.method.data,createDeliveryForm.remarks.data)
            print('allid',AllID)
            delivery.set_time(datetime.now())
            randomtime = random.randint(70,80) # Random generate estimated time of delivery
            delivery.set_estimatedTime(datetime.now() + timedelta(seconds = randomtime))
            delivery.set_status('In Delivery')

            deliveryDict[delivery.get_deliveryID()] = delivery
            db['Delivery'] = deliveryDict
            deliveryDict = db['Delivery']
            delivery = deliveryDict[delivery.get_deliveryID()]

            for i in Purchases:
                chatDict[i.get_chatID()].set_buyerreview(1)
                chatDict[i.get_chatID()].set_sellerreview(1)

            userDict[session['userID']].reset_purchases()

            db['Chats'] = chatDict
            db['Users'] = userDict

            print(deliveryDict)
            db.close()
            print("valid address")
            return redirect(url_for('manageDelivery'))
        else:
            print("Invalid address")
            invalidlocation = True
            return render_template('createDelivery.html', form=createDeliveryForm,invalidlocation=invalidlocation,alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3] , fpwform= navbar()[4])

    return render_template('createDelivery.html', form=createDeliveryForm,alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3] , fpwform= navbar()[4])


@app.route('/manageDelivery', methods=['GET', 'POST'])
def manageDelivery():
    deliveryDict = {}
    try :
        db = shelve.open('storage.db', 'r')
        deliveryDict = db['Delivery']
        db.close()
    except :
        db = shelve.open('storage.db', 'c')
        deliveryDict = []
        db.close()

    deliveryList = []
    for key in deliveryDict:
        delivery = deliveryDict.get(key)
        if delivery.get_username() == session['username']:
            deliveryList.append(delivery)

    for key in deliveryList:
        print(deliveryList)
        if key.get_status() == 'In Delivery':
            if datetime.now() > key.get_estimatedTime():
                key.set_status('Delivered')

    return render_template('manageDelivery.html', deliveryList=deliveryList, count=len(deliveryList),alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3] , fpwform= navbar()[4])


@app.route('/updateDelivery/<int:id>',methods = ["GET","POST"])
def updateDelivery(id):
    updateDeliveryForm = CreateDeliveryForm(request.form)

    if request.method == 'POST' and updateDeliveryForm.validate():
        deliveryDict ={}
        db = shelve.open('storage.db','w')
        deliveryDict = db['Delivery']

        if validateaddress(updateDeliveryForm.location.data) == True:
            delivery = deliveryDict.get(id)
            delivery.set_firstName(updateDeliveryForm.firstName.data)
            delivery.set_lastName(updateDeliveryForm.lastName.data)
            delivery.set_location(updateDeliveryForm.location.data)
            delivery.set_shipping(updateDeliveryForm.shipping.data)
            delivery.set_method(updateDeliveryForm.method.data)
            delivery.set_remarks(updateDeliveryForm.remarks.data)
            db['Delivery'] =deliveryDict
            db.close()

            return redirect(url_for('manageDelivery'))

        else:
            invalidlocation = True
            return render_template('updateDelivery.html',invalidlocation=invalidlocation, form=updateDeliveryForm, alert=navbar()[0], logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3] , fpwform= navbar()[4])

    else:
        deliveryDict={}
        db = shelve.open('storage.db', 'r')
        deliveryDict = db['Delivery']
        db.close()
        delivery = deliveryDict.get(id)
        updateDeliveryForm.location.data = delivery.get_location()
        updateDeliveryForm.firstName.data = delivery.get_firstName()
        updateDeliveryForm.lastName.data = delivery.get_lastName()
        updateDeliveryForm.shipping.data = delivery.get_shipping()
        updateDeliveryForm.method.data = delivery.get_method()
        updateDeliveryForm.remarks.data = delivery.get_remarks()

        return render_template('updateDelivery.html', form=updateDeliveryForm, alert=navbar()[0], logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3] , fpwform= navbar()[4])

@app.route('/deleteDelivery/<int:id>', methods = ['POST'])
def deleteDelivery(id):
    deliveryDict = {}
    db = shelve.open('storage.db','w')
    deliveryDict = db['Delivery']

    deliveryDict.pop(id)

    db["Delivery"] = deliveryDict
    db.close()

    if session['username'] == 1:
        return redirect(url_for('retrieveDelivery'))
    else:
        return redirect(url_for('manageDelivery'))


@app.route('/deleteDeliveryatretrieve/<int:id>', methods = ['POST'])
def deleteDeliveryatretrieve(id):
    deliveryDict = {}
    db = shelve.open('storage.db','w')
    deliveryDict = db['Delivery']

    deliveryDict.pop(id)

    db["Delivery"] = deliveryDict
    db.close()

    return redirect(url_for('retrieveDelivery'))


@app.route('/CancelDelivery/<int:id>')
def CancelDelivery(id):
    deliveryDict = {}
    db =shelve.open('storage.db', 'w')
    deliveryDict = db['Delivery']

    delivery = deliveryDict.get(id)
    delivery.set_status("Cancelled")

    db['Delivery'] = deliveryDict
    db.close()
    return redirect(url_for('manageDelivery'))


@app.route('/Proof')
def Proof():
    deliveryDict = {}
    db = shelve.open('storage.db', 'r')
    try:
        deliveryDict = db['Delivery']

    except:
        print(deliveryDict)

    deliveryList = []
    for key in deliveryDict:
        delivery = deliveryDict.get(key)
        if delivery.get_username() == session['username']:
            deliveryList.append(delivery)

    for key in deliveryList:
        print(deliveryList)
        if key.get_status() == "In Delivery":
            if datetime.now() > key.get_estimatedTime():
                key.set_status('Delivered')


    db.close()

    return render_template('Proof.html', deliveryList=deliveryList, count=len(deliveryList),alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3] , fpwform= navbar()[4])


@app.route('/Track/<int:id>')
def Track(id):
    deliveryDict={}
    db = shelve.open('storage.db', 'w')

    deliveryDict = db['Delivery']

    delivery = deliveryDict.get(id)
    locationx = delivery.get_location()
    statusx = delivery.get_status()
    buyer = delivery .get_username()

    m = folium.Map(location=[1.3800,103.8489], zoom_start=12)
    tooltip = 'Pepestore'
    folium.Marker([1.3800,103.8489], popup='<strong>PepeStore</strong>',tooltip=tooltip).add_to(m)

    pepe= geocoder.osm('Nanyang Polytechnic,Singapore')
    address = geocoder.osm(locationx)
    address_latlng = [address.lat, address.lng]
    pepe_latlng = [pepe.lat, pepe.lng]
    folium.Marker(address_latlng, popup=locationx, tooltip=buyer).add_to(m)
    distance_path = [pepe_latlng,address_latlng]
    plugins.AntPath(distance_path,tooltip = "In Delivery",).add_to(m)


    m.save('templates/map.html')


    db['Delivery'] =deliveryDict
    db.close()

    return render_template('Track.html',delivery=delivery,alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3] , fpwform= navbar()[4])

@app.route('/map')
def map():
    return render_template("map.html")


@app.route('/createFeedback', methods=['GET', 'POST'])
def createFeedback():
    faqDict = {}
    createFeedbackForm = CreateFeedbackForm(request.form)
    if request.method == 'POST' and createFeedbackForm.validate():
        db = shelve.open('storage.db', 'c')

        try:
            faqDict = db['FAQ']
        except:
            print("Error in retrieving Feedback from storage.db.")

        faq = Classes.FAQ(createFeedbackForm.question.data, createFeedbackForm.answer.data)
        faqDict[faq.get_id()] = faq
        db['FAQ'] = faqDict
        db.close()

        return redirect(url_for('retrieveFeedback'))
    return render_template('createFeedback.html', form=createFeedbackForm,alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3] , fpwform= navbar()[4])


@app.route('/retrieveFeedback')
def retrieveFeedback():
    faqDict = {}
    db = shelve.open('storage.db', 'r')
    faqList = []
    try:
        faqDict = db['FAQ']
        db.close()
    except:
        print('error in retrieve Feeedback')

    for key in faqDict:
        user = faqDict.get(key)
        faqList.append(user)

    return render_template('retrieveFeedback.html',faqList=faqList, count=len(faqList),alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3] , fpwform= navbar()[4])


@app.route('/updateFAQ/<int:id>/', methods=['GET', 'POST'])
def updateFAQ(id):
    updateUserForm = CreateFeedbackForm(request.form)
    if request.method == 'POST' and updateUserForm.validate():
        faqDict = {}
        db = shelve.open('storage.db','w')
        faqDict = db['FAQ']
        faq = faqDict.get(id)
        faq.set_question(updateUserForm.question.data)
        faq.set_answer(updateUserForm.answer.data)
        db['FAQ'] = faqDict
        db.close()

        return redirect(url_for('retrieveFeedback'))
    else:
        faqDict = {}
        db = shelve.open('storage.db', 'r')
        faqDict = db['FAQ']
        db.close()
        faq = faqDict.get(id)
        updateUserForm.question.data = faq.get_question()
        updateUserForm.answer.data = faq.get_answer()
        return render_template('updateFeedback.html',form=updateUserForm,alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3] , fpwform= navbar()[4])


@app.route('/deleteFAQ/<int:id>', methods=['POST'])
def deleteFAQ(id):
    usersDict = {}
    db = shelve.open('storage.db', 'w')
    usersDict = db['FAQ']
    usersDict.pop(id)
    db['FAQ'] = usersDict
    db.close()
    return redirect(url_for('retrieveFeedback'))


@app.route('/FAQ', methods=['POST','GET'])
def FAQ():
    faqDict = {}
    db = shelve.open('storage.db', 'r')
    faqList = []
    try:
        faqDict = db['FAQ']
        db.close()
    except:
        print('error in retrieve Feeedback')

    for key in faqDict:
        faq = faqDict.get(key)
        faqList.append(faq)

    return render_template('FAQ.html', faqList=faqList, alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3] , fpwform= navbar()[4])


if __name__ == '__main__':
    socketio.run(app)
