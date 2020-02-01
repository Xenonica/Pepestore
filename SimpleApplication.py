from flask import Flask, render_template, request, redirect, url_for , session, blueprints
from Forms import CreateListing , CreateAccount , LoginAccount, Logout , Chat , ChatOffer , ProfileForm , CreateDeliveryForm
from flask_socketio import SocketIO , send , disconnect
from datetime import datetime , timedelta
import shelve, os , Classes , hashlib,shutil
import folium
import geocoder
from folium import plugins
from geopy import distance
import random

# Absolute path of the program
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)
app.secret_key = 'J'
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True



socketio = SocketIO(app)

permimagelist = []
tempimagelist = []
tempimagenames = []
run = 0

target = os.path.join(APP_ROOT, 'static/')
if not os.path.isdir(target) :
    os.mkdir(target)


def navbar() :
    alert = ''
    logout = Logout(request.form)
    regform = CreateAccount(request.form)
    logform = LoginAccount(request.form)

    if request.method == 'POST':
        if logout.logout.data :
            session.pop('userID',None)
            session.pop('username',None)
            session.pop('profpic',None)
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
                user = Classes.User(regform.username.data, regform.email.data, hashlib.md5(regform.password.data.encode()).hexdigest())
                usersDict[user.get_userID()] = user
                db['Users'] = usersDict
                # Test codes
                usersDict = db['Users']
                user = usersDict[user.get_userID()]
                print(user.get_username(), user.get_email(),user.get_password(), "was stored in shelve successfully with userID =", user.get_userID())
            db.close()
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
                        alert = 'Login Successful'
                    elif logform.username.data == usersDict[i].get_username():
                        alert = 'WPW'
            except :
                pass
            db.close()
    return [alert,logout,regform,logform]


@app.route('/',methods=['GET', 'POST'])
def home():
    listingList = []
    listingDict = {}
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
    print(listingList)
    for key in listingList:
        if len(listingList) > 5:
            listingList.remove(key)
        if len(listingList) == 5:
            break
    print(listingList)
    newestLists = listingList[::-1]

    return render_template('home.html',newestLists =newestLists,alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3])


@app.route('/createUserImages',methods=['GET', 'POST'])
def createUserImages() :
    if request.method == 'POST':
        todelete = request.form['todelete']
        if todelete == '' :

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
                        count+=1
                        if staticdestination in tempimagelist :
                            continue
                        else:
                            tempimagelist.append(staticdestination)
                            tempimagenames.append(filename)
        else :
            todeleteplace = int(todelete)-1
            tempimagelist.remove(tempimagelist[todeleteplace])
            tempimagenames.remove(tempimagenames[todeleteplace])
    Class = ['','','','']
    Img = ['','','','']
    for i in range(len(tempimagelist)) :
        Img[i] = tempimagelist[i]
        Class[i] = 'Img'
    for i in range(len(tempimagelist),4) :
        Img[i] = 'https://matthewsenvironmentalsolutions.com/images/com_hikashop/upload/not-available.png'
        Class[i] = 'NoImg'
    print(tempimagelist)
    print(tempimagenames)
    print('img ', Img)
    print('class', Class)
    return render_template('createUserImages.html' ,Img1 = Img[0] , Img2 = Img[1] , Img3 = Img[2] , Img4 = Img[3], Class1 = Class[0] , Class2 = Class[1] , Class3 = Class[2] , Class4 = Class[3], alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3])


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

    return render_template('manageListing.html', listingList=listingList, count=len(listingList),alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3])


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

        listing = Classes.Listing(createlisting.name.data, createlisting.price.data, createlisting.description.data, createlisting.category.data, session['username'], createlisting.quantity.data)
        listingDict[listing.get_listingID()] = listing
        listing.set_visits(0)
        #Path of where to store images
        target = os.path.join(APP_ROOT, 'static/listings/', str(listing.get_listingID()))
        #Check whether path target exists / creates path if it doesn't.
        if not os.path.isdir(target) :
            os.mkdir(target)
        imgnamecount = 0
        for i in tempimagelist :
            print(i)
            olddir = APP_ROOT+i
            newdir = os.path.join(target,tempimagenames[imgnamecount])
            newstatic = os.path.join('/static/listings/', str(listing.get_listingID()),tempimagenames[imgnamecount])
            permimagelist.append(newstatic)
            imgnamecount += 1
            print('old', olddir)
            print('new', newdir)
            if not os.path.isfile(newdir) :
                os.rename(olddir,newdir)
        listing.set_piclist(permimagelist)
        db['Listings'] = listingDict

        listingDict = db['Listings']
        listing = listingDict[listing.get_listingID()]
        print(listing.get_name(), listing.get_price(), "was stored in shelve successfully with listingID =", listing.get_listingID())

        db.close()

        permimagelist.clear()
        tempimagelist.clear()


        return redirect(url_for('home'))
    return render_template('createListing.html', form=createlisting , Img1=Image1, alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3])


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

    return render_template('listingPage.html',piclist=piclist,chatform=chatform,listingID = listingDict[listingID],alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3])


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

    return render_template('allListing.html',count=len(listingDict),form=createListing,listingDict=listingDict,selected_category=createListing.filter_type.data,alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3])


@app.route('/update/<int:id>/', methods=['GET', 'POST'])
def updateItem(id):
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
                    listingForm.price.data = listingDict[list_id].get_price()
                    listingForm.description.data = listingDict[list_id].get_description()
                    listingForm.quantity.data = listingDict[list_id].get_quantity()
                    listingForm.category.data = listingDict[list_id].get_category()
        print(listingDict)

    return render_template('updateItem.html', form=listingForm,alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3])


@app.route('/deleteListing/<int:id>', methods=['POST'])
def deleteListing(id):
     listingDict = {}
     db = shelve.open('storage.db', 'w')
     listingDict = db['Listings']
     listingDict.pop(id)
     shutil.rmtree("static/listings/"+str(id))
     db['Listings'] = listingDict
     db.close()
     return redirect(url_for('manageListing'))



@app.route('/analytics')
def analytics():
    labels = []
    values = []
    db = shelve.open('storage.db')
    listingDict = {}
    listingDict = db['Listings']
    for listingID in listingDict:
        if session.get('username') == listingDict[listingID].get_seller_name():
            labels.append(listingDict[listingID].get_name())
            values.append(listingDict[listingID].get_visits())
    legend = 'Traffic'
    print(values)
    return render_template('analytics.html', values=values, labels=labels, legend=legend,alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3])


@app.route('/UserChats/<int:chatID>/', methods=['POST','GET'])
def UserChats(chatID) :
    if 'userID' in session:
        tdeltaseconds = 0
        tdeltaseconds2 = 0
        chatofferform = ChatOffer(request.form)
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

        if not (session['userID'] == chatsDict[chatID].get_sellerID() or session['userID'] == chatsDict[chatID].get_buyerID()) :
            db.close()
            return redirect(url_for('home'))

        if session['userID'] ==  chatsDict[chatID].get_sellerID() :
            OtherProfPic = usersDict[chatsDict[chatID].get_buyerID()].get_profpic()
            Position = 'S'
        else :
            OtherProfPic = usersDict[chatsDict[chatID].get_sellerID()].get_profpic()
            Position = 'B'
        ListingImage = listingsDict[chatsDict[chatID].get_listingID()].get_displaypic()
        ListingName = listingsDict[chatsDict[chatID].get_listingID()].get_name()
        ListingPrice = listingsDict[chatsDict[chatID].get_listingID()].get_price()
        Buyer = usersDict[chatsDict[chatID].get_buyerID()]
        Seller = usersDict[chatsDict[chatID].get_sellerID()]

        chatlog = chatsDict[chatID].get_chatLog()
        db.close()
        chatIDx = chatsDict[chatID]
        Offers = chatsDict[chatID].get_offers()
        if chatsDict[chatID].get_SellerLastOnline() != '' :
            T1 = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            T2 = chatsDict[chatID].get_SellerLastOnline()
            FMT = '%Y-%m-%d %H:%M:%S'
            tdelta = datetime.strptime(T1, FMT) - datetime.strptime(T2, FMT)
            tdeltaseconds = tdelta.total_seconds()
        elif chatsDict[chatID].get_BuyerLastOnline() != '' :
            T1 = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            T2 = chatsDict[chatID].get_BuyerLastOnline()
            FMT = '%Y-%m-%d %H:%M:%S'
            tdelta2 = datetime.strptime(T1, FMT) - datetime.strptime(T2, FMT)
            tdeltaseconds2 = tdelta2.total_seconds()
    else:
        return redirect(url_for('home'))

    return render_template('UserChats.html',OtherProfPic = OtherProfPic,SOfflineTime = tdeltaseconds,BOfflineTime = tdeltaseconds2,chatID = chatID ,Buyer = Buyer,Seller = Seller,Offers = Offers,chatIDx = chatIDx,chatofferform = chatofferform,Position=Position,ListingImage = ListingImage,ListingName = ListingName,ListingPrice = ListingPrice,messages = chatlog,alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3])

@socketio.on('message')
def handleMessage(msg):
        usersDict = {}
        chatsDict = {}
        db = shelve.open('storage.db', 'c')
        try:
            chatsDict = db['Chats']
        except:
            print("Error Chats")

        try:
            usersDict = db['Users']
        except:
            print("Error Users")
        chatID = request.headers.get("Referer").split('/')[-2]
        if msg == None :
            pass

        if msg[:4] == 'Pos:' :
            if msg[4] == 'B' :
                chatsDict[int(chatID)].set_BuyerLastOnline(msg[6:])
                msg = 'BuyerDisconnected'
            elif msg[4] == 'S' :
                chatsDict[int(chatID)].set_SellerLastOnline(msg[6:])
                msg = 'SellerDisconnected'

        elif msg == 'SellerConnected' :
            chatsDict[int(chatID)].set_SellerLastOnline('')
            pass

        elif msg == 'BuyerConnected' :
            chatsDict[int(chatID)].set_BuyerLastOnline('')
            pass

        elif '/Offer ' in msg :
            if chatsDict[int(chatID)].get_offers() == [] :
                Offers = float(msg[7:])
                Offers = ("%.2f" % Offers)
                Offers = [float(Offers)]
                print(Offers)
                chatsDict[int(chatID)].set_offers(Offers)
            else :
                msg = None

        elif msg == '/CancelOffer':
            if chatsDict[int(chatID)].get_offers() != [] :
                chatsDict[int(chatID)].set_offers([])
            else:
                msg = None

        elif msg == '/DeclineOffer':
            if chatsDict[int(chatID)].get_offers() != [] :
                chatsDict[int(chatID)].set_offers([])
            else:
                msg = None

        elif msg == ('/AcceptOffer'+str(chatsDict[int(chatID)].get_sellerID())) :
            if chatsDict[int(chatID)].get_offers() != [] :
                usersDict[chatsDict[int(chatID)].get_sellerID()].set_sales(chatsDict[int(chatID)].get_listingID())
                usersDict[chatsDict[int(chatID)].get_buyerID()].set_purchases(chatsDict[int(chatID)].get_listingID())
                chatsDict[int(chatID)].set_offers([])
                msg = '/AcceptOffer'
            else:
                msg = None

        elif msg == ('/AcceptOffer'+str(chatsDict[int(chatID)].get_buyerID())) :
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
        db['Users'] = usersDict
        db['Chats'] = chatsDict
        db.close()

        send(msg,broadcast=True)

@app.route('/userProfile/<int:id>/', methods=['GET', 'POST'])
def userProfile(id):
    Profile = ProfileForm(request.form)
    ProfPic = 'http://s3.amazonaws.com/37assets/svn/765-default-avatar.png'
    if request.method == 'POST':
        userDict = {}
        db = shelve.open('storage.db', 'w')
        userDict = db['Users']
        user = userDict.get(id)
        user.set_username(Profile.username.data)
        user.set_address1(Profile.address1.data)
        user.set_address2(Profile.address2.data)
        user.set_zipcode(Profile.zipcode.data)
        #Path of where to store images
        target1 = os.path.join(APP_ROOT, 'static/users/')
        target = os.path.join(APP_ROOT, 'static/users/', str(user.get_userID()))
        #Check whether path target exists / creates path if it doesn't.
        if not os.path.isdir(target1) :
            os.mkdir(target1)
        if not os.path.isdir(target) :
            os.mkdir(target)
        try :
            newProfPic = request.files.get('file')
            filename = newProfPic.filename
            #Make directory for image
            destination = '/'.join([target]+[filename])
            newProfPic.save(destination)
            staticdestination = '/static/users/'+ str(user.get_userID())+'/'+filename+'/'
            print(staticdestination)
            user.set_profpic(staticdestination)
            session['profpic'] = user.get_profpic()
        except:
            pass
        ProfPic = user.get_profpic()
        db['Users'] = userDict
        db.close()
    else:
        userDict = {}
        db = shelve.open('storage.db', 'r')
        userDict = db['Users']
        db.close()
        user = userDict.get(id)
        Profile.username.data = user.get_username()
        Profile.address1.data = user.get_address1()
        Profile.address2.data = user.get_address2()
        Profile.zipcode.data = user.get_zipcode()
        ProfPic = user.get_profpic()

    return render_template('userProfile.html',ProfPic = ProfPic,Profile = Profile,alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3])

@app.route('/Cart')
def Cart():
    PurchaseList = []
    listingDict = {}
    userDict = {}

    db = shelve.open('storage.db', 'c')

    try:
        listingDict = db['Listings']
    except:
        print("Error in retrieving Listings")

    try:
        userDict = db['Users']
    except:
        print("Error in retrieving Users")

    Purchases = userDict[session['userID']].get_purchases()
    for i in Purchases :
        PurchaseList.append(listingDict[i])

    return render_template('Cart.html',PurchaseList = PurchaseList,alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3])


@app.route('/retrieveUsers', methods=['GET', 'POST'])
def retrieveUsers():
    if session['userID'] == 1 :
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

    return render_template('retrieveUsers.html', userList=userList, count=len(userList),alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3])




@app.route('/deleteUser/<int:id>', methods=['POST'])
def deleteUser(id):
    usersDict = {}
    db = shelve.open('storage.db', 'w')
    usersDict = db['Users']
    usersDict.pop(id)
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


    return render_template('AllChats.html',userDict = userDict,listingDict = listingDict,ChatList = ChatList,alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3])


@app.route('/retrieveDelivery')
def retrieveDelivery():
    if session['userID'] == 1 :
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

    return render_template('retrieveDelivery.html', deliveryList=deliveryList, count=len(deliveryList),alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3])


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
        deliveryDict = {}
        db = shelve.open('storage.db', 'c')

        try:
            deliveryDict = db['Delivery']
            print(deliveryDict)
        except:
            print("Error in retrieving delivery from storage")

        if validateaddress(createDeliveryForm.location.data) == True:
            delivery = Classes.Delivery(session['username'], createDeliveryForm.product.data, createDeliveryForm.location.data)
            delivery.set_time(datetime.now())
            randomtime = random.randint(20,35) # Random generate estimated time of delivery
            delivery.set_estimatedTime(datetime.now() + timedelta(seconds = randomtime))
            delivery.set_status('In Delivery')


            deliveryDict[delivery.get_deliveryID()] = delivery
            db['Delivery'] = deliveryDict
            deliveryDict = db['Delivery']
            delivery = deliveryDict[delivery.get_deliveryID()]

            print(deliveryDict)
            db.close()
            print("valid address")
            return redirect(url_for('manageDelivery'))
        else:
            print("Invalid address")
            invalidlocation = True
            return render_template('createDelivery.html', form=createDeliveryForm,invalidlocation=invalidlocation,alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3])

    return render_template('createDelivery.html', form=createDeliveryForm,alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3])


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

    return render_template('manageDelivery.html', deliveryList=deliveryList, count=len(deliveryList),alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3])





@app.route('/updateDelivery/<int:id>',methods = ["GET","POST"])
def updateDelivery(id):
    updateDeliveryForm = CreateDeliveryForm(request.form)

    if request.method == 'POST' and updateDeliveryForm.validate():
        deliveryDict ={}
        db = shelve.open('storage.db','w')
        deliveryDict = db['Delivery']

        if validateaddress(updateDeliveryForm.location.data) == True:
            delivery = deliveryDict.get(id)
            delivery.set_product(updateDeliveryForm.product.data)
            delivery.set_location(updateDeliveryForm.location.data)

            db['Delivery'] =deliveryDict
            db.close()

            return redirect(url_for('manageDelivery'))

        else:
            invalidlocation = True
            return render_template('updateDelivery.html',invalidlocation=invalidlocation, form=updateDeliveryForm, alert=navbar()[0], logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3])

    else:
        deliveryDict={}
        db = shelve.open('storage.db', 'r')
        deliveryDict = db['Delivery']
        db.close()
        delivery = deliveryDict.get(id)
        updateDeliveryForm.product.data = delivery.get_product()
        updateDeliveryForm.location.data = delivery.get_location()

        return render_template('updateDelivery.html', form=updateDeliveryForm, alert=navbar()[0], logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3])

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

    return render_template('Proof.html', deliveryList=deliveryList, count=len(deliveryList),alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3])


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

    return render_template('Track.html',delivery=delivery,alert = navbar()[0] , logout = navbar()[1] , regform = navbar()[2] , logform = navbar()[3])

@app.route('/map')
def map():
    return render_template("map.html")



if __name__ == '__main__':
    socketio.run(app)
