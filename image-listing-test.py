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


@app.route('/createListing', methods=['GET', 'POST'])
def createListing():
    createlisting = CreateListing(request.form)
    listingDict = {}
    if len(tempimagelist) == 0 :
            Image1 = 'https://matthewsenvironmentalsolutions.com/images/com_hikashop/upload/not-available.png'
    else :
        Image1 = tempimagelist[0]
    if request.method == 'POST' and createlisting.validate():

        db = shelve.open('storage.db', 'c')

        try:
            listingDict = db['Listings']
        except:
            print("Error in retrieving Users from storage.db.")

        print(tempimagelist)
        listing = Classes.Listing(createlisting.name.data, createlisting.price.data, createlisting.description.data, createlisting.category.data,session['userID'], session['username'], createlisting.quantity.data, 0)
        listingDict[listing.get_listingID()] = listing
        #Path of where to store images
        target1 = os.path.join(APP_ROOT, 'static/listings/')
        target = os.path.join(APP_ROOT, 'static/listings/', str(listing.get_listingID()))
        #Check whether path target exists / creates path if it doesn't.
        if not os.path.isdir(target1) :
            os.mkdir(target1)
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
            print('new',newdir)
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

