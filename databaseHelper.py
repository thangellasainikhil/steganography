import mysql.connector
from cryptography.fernet import Fernet

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Nikhil@3666",
    database="STEG"
)

cursor = db.cursor(buffered=True)


def DBsignUp(firstname,username,password):
    cursor.execute("SELECT * FROM users WHERE username = %s",(username,))
    if len(cursor.fetchall()) == 0:
        cursor.execute("SELECT fernetkey FROM util")
        key = cursor.fetchall()[0][0]
        fernet = Fernet(key)
        passwd = fernet.encrypt(password.encode())
        cursor.execute("INSERT INTO users (firstname,username,upassword) VALUES(%s,%s,%s);",(firstname,username,passwd))
        db.commit()
        cursor.execute("SELECT userid,username FROM users WHERE username = %s",(username,))
        res = cursor.fetchall()
        if len(res) > 0:
            return {"uid":res[0][0],'username':res[0][1]}
    return None

def DBlogin(username,password):
    cursor.execute("SELECT userid,username,upassword FROM users WHERE username = %s",(username,))
    res = cursor.fetchall()
    if len(res) > 0:
        uid,username,passwd = res[0]
        cursor.execute("SELECT fernetkey FROM util")
        key = cursor.fetchall()[0][0]
        fernet = Fernet(key)
        decpass = fernet.decrypt(passwd).decode()
        if password == decpass:
            return {"username":username,"uid":uid}
    return None

def DBimgget(uid):
    cursor.execute("SELECT * FROM images WHERE userid=%s",(uid,))
    return cursor.fetchall()

def DBimginsert(imgname,imgdesc,uid):
    cursor.execute("INSERT INTO images (imgname,imgdesc,userid) VALUES(%s,%s,%s)",(imgname,imgdesc,uid))
    db.commit()

def DBimgdelete(imgid):
    cursor.execute("DELETE FROM images WHERE imgid = %s",(imgid,))
    db.commit()