from flask import Flask, request, render_template, send_file, session, redirect, url_for
from stegano import exifHeader as stg
from databaseHelper import *
from werkzeug.utils import secure_filename
import os

# creating flask app
app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['UPLOAD_FOLDER'] = "uploaded_images"

app.secret_key = "1234"
encryptDictionary = {

    0: 'N', 1: 'C', 2: 'X', 3: 'Y', 4: 'V', 5: 'W', 6: 'D', 7: '(', 8: ')', 9: 'O', 10: 'P',
    11: ',', 12: '-', 13: 'B', 14: 'I', 15: 'J', 16: 'K', 17: 'L', 18: 'G', 19: 'M', 20: 'Q',
    21: 'R', 22: 'S', 23: 'E', 24: 'T', 25: 'U', 26: 'F', 27: 'H', 28: 'a', 29: 'b', 30: 'c',
    31: 'd', 32: 'e', 33: 'f', 34: 'g', 35: 'h', 36: 'i', 37: 'j', 38: 'k', 39: 'l', 40: 'm',
    41: 'n', 42: 'o', 43: 'p', 44: 'q', 45: 'r', 46: 's', 47: 't', 48: 'u', 49: 'v', 50: 'w',
    51: 'x', 52: 'y', 53: 'z', 54: 'A'

}


decryptDictionary = {

    'N': 0, 'C': 1, 'X': 2, 'Y': 3, 'V': 4, 'W': 5, 'D': 6, '(': 7, ')': 8, 'O': 9, 'P': 10,
    ',': 11, '-': 12, 'B': 13, 'I': 14, 'J': 15, 'K': 16, 'L': 17, 'G': 18, 'M': 19, 'Q': 20,
    'R': 21, 'S': 22, 'E': 23, 'T': 24, 'U': 25, 'F': 26, 'H': 27, 'a': 28, 'b': 29, 'c': 30,
    'd': 31, 'e': 32, 'f': 33, 'g': 34, 'h': 35, 'i': 36, 'j': 37, 'k': 38, 'l': 39, 'm': 40,
    'n': 41, 'o': 42, 'p': 43, 'q': 44, 'r': 45, 's': 46, 't': 47, 'u': 48, 'v': 49, 'w': 50,
    'x': 51, 'y': 52, 'z': 53, 'A': 54

}

def manipul(msg):
    res=""
    for i in msg:
        if(ord(i)<79):
            res+=chr(ord(i)+47)
        else:
            res+=chr(ord(i)-47)
    return res

def demanipul(msg):
    res = ""
    for i in msg:
        if (ord(i) < 79):
            res += chr(ord(i) + 47)
        else:
            res += chr(ord(i) - 47)
    return res
        # Image type Validation
def validateImage(imageName):

    valid_extensions = ['jpg', 'jpeg']


    if '.' in imageName:
        imageName.lower()
        l = imageName.split('.')
        if l[-1] in valid_extensions:
            return 1

        else:
            return 0

    return 0


def validatePassword(password, confirmPassword):

    for i in range(0, 6):

        if password[i] != confirmPassword[i]:
            return False

    return True


def encryptPassword(password):

    list_password = []

    for i in range(0, 6):

        list_password.append(int(password[i]))

    list_password.reverse()
    sum = 0

    for i in range(6):
        list_password[i] += sum
        sum = list_password[i]

    encryptedPassword = ''

    for i in range(6):

        encryptedPassword += encryptDictionary[list_password[i]]

    return encryptedPassword


def decryptPassword(imagePath):
    encryptedPassword = imagePath.split('_')[-2]

    list_password = []

    for ch in encryptedPassword:
        list_password.append(decryptDictionary[ch])

    for i in range(5, -1, -1):

        if i!=0:
            list_password[i] = list_password[i] - list_password[i-1]

    list_password.reverse()

    decryptedPassword = ''

    for i in list_password:

        decryptedPassword += str(i)

    return decryptedPassword

# Encoder and Decoder Logic Functions
def encoder(imagePath, message):

    filename = imagePath.split('/')

    encryptedPassword = encryptPassword(session['password'])
    l = filename[-1].split('.')
    filename[-1] = l[0]+'_'+encryptedPassword+'_.'+l[1]

    n = len(session)
    session['imagePath'+str(n+1)] = './static/encoded_images/'+filename[-1]
    stg.hide(imagePath, './static/encoded_images/'+filename[-1], message)

    return [1, encryptedPassword]


def decoder(imagePath):

    try:
        message = stg.reveal(imagePath)
        return message
    except:
        return 0


# Handling web pages
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/getEncoderPage', methods=['GET'])
def renderEncoderPage():
    if session.get('uid'):
        return render_template('encoder.html', status=None)
    return redirect('/login')

@app.route('/getDecoderPage', methods=['GET'])
def renderDecoderPage():
    if session.get('uid'):
        return render_template('decoder.html', status=None)
    return redirect('/login')
# ============================================================================================================================
@app.route("/login",methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        passwd = request.form.get("password")
        if username and passwd:
            d = DBlogin(username,passwd)
            if d:
                session['uid'] = d['uid']
                session['username'] = d['username']
                return redirect('/')
        return render_template("login.html",data={"err":"invalid username or password"})
    if session.get('uid'):
        return redirect('/')
    return render_template("login.html",data={})

@app.route("/signup",methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        firstname = request.form.get("firstname")
        username = request.form.get("username")
        passwd = request.form.get("password")
        if firstname and username and passwd:
            d = DBsignUp(firstname,username,passwd)
            if d:
                session["uid"] = d['uid']
                session['username'] = d['username']

                return redirect('/')
            return render_template("signup.html",data={"err":"username exists"})
        return render_template("signup.html",data={"err":"fields cannot be left empty"})
    else:
        if session.get('uid'):
            return redirect('/')
        return render_template('signup.html',data={})

@app.route("/signout",methods=['GET'])
def signout():
    if session.get('uid'):
        session.pop('uid')
        session.pop('username')
    return redirect('/')

@app.route('/deleteImage',methods=["POST"])
def deleteImage():
    imgid = request.form.get("imgid")
    filename = request.form.get("filename")
    if imgid and filename:
        DBimgdelete(imgid)
        os.remove('./uploaded_images/'+filename)
        return redirect('/Images')
    return redirect('/')

@app.route('/Images',methods=['GET'])
def getImages():
    if session.get('uid'):
        imglist = DBimgget(session['uid'])
        return render_template('images.html',data={'imglist':imglist})
    return redirect('/login')

@app.route("/downloadImage",methods=["GET"])
def downloadImage():
    filename = request.args.get("filename")
    if filename:
        return send_file(os.path.join('./static/encoded_images/',filename), as_attachment=True)
    return redirect('/')

@app.route('/uploadImage', methods=['GET', 'POST'])
def uploadImage():

    message = request.form['encode_message']
    message=manipul(message)
    file = request.files['encode_image']
    imageName = file.filename

    password = []
    confirmPassword = []

    for i in range(1, 7):

        password.append(request.form['pin-'+str(i)])
        confirmPassword.append(request.form['cPin-'+str(i)])

    if validatePassword(password, confirmPassword):

        s = ''
        for i in password:
            s += i
        session['password'] = s

        if validateImage(imageName):
            filename = secure_filename(imageName)

            file.save('./uploaded_images/'+filename)
            imagePath = './uploaded_images/'+filename
            

            n = len(session)
            session['imagePath' + str(n)] = './uploaded_images/' + filename

            [status, encryptedPassword] = encoder(imagePath, message)[0:]

            l = filename.split('.')
            filename = l[0] + '_' + encryptedPassword + '_.' + l[1]
            
            DBimginsert(filename,message,session['uid'])

            global return_status

            if status:
                return_status = 'Message Encoded Successfully'

            else:
                return_status = 'Unable to Encode Message'

            return render_template('resultPage.html', status=return_status, filename=filename)

        else:
            return render_template('encoder.html', status='Invalid Image Format (accepted only *.jpg, *.jpeg formats only)')

    # wrong password
    else:
        return render_template('encoder.html', status="Pin Didn't match")


@app.route('/getMessage', methods=['GET', 'POST'])
def getMessage():

    file = request.files['decode_image']
    filename = file.filename

    list_password = []
    for i in range(1, 7):

        list_password.append(request.form['pin-'+str(i)])

    password = ''

    for i in list_password:
        password += i

    decryptedPassword = decryptPassword(filename)

    print(decryptedPassword, password)

    if validatePassword(password, decryptedPassword):

        if validateImage(filename):
            filename = secure_filename(filename)
            n = len(session)
            session['imagePath' + str(n)] = './static/encoded_images/'+filename
            file.save('./static/encoded_images/'+filename)
            message = decoder('./static/encoded_images/'+filename)

            if isinstance( message, bytes):

                message = str(message)
                l = message.split('\'')
                message = l[1]
                message=demanipul(message)

                return render_template('resultPage.html', decoded_message=message, filename=None)

            else:
                message = 'Invalid image detected, Unable to decode the image please verify whether the image is encoded.'
                return render_template('resultPage.html', status=message, filename=None, decoded_message=None)

        else:
            return render_template('decoder.html', status='Invalid Image Format (accepted only *.jpg, *.jpeg formats only)')

    else:
        return render_template('decoder.html', status='Invalid Pin')


@app.route('/clear_session', methods=['GET'])
def clearSession():

    if(len(session) > 0):
        for i in session.keys():
            imagePath = session[i]

            try:
                os.remove(imagePath)
            except:
                continue

        session.clear()

    return redirect(url_for('index'))

@app.route('/downloadEncodedImage/<filename>', methods=['GET'])
def downloadEncodedImage(filename):

    return send_file('./static/encoded_images/'+filename, as_attachment=True)


if __name__ == '__main__':

    app.run(debug=True)