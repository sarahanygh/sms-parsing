
import time

from datetime import datetime

import serial

import re

import firebase_admin

from firebase_admin import credentials

from firebase_admin import firestore

from google.cloud.firestore import GeoPoint



if not firebase_admin._apps:
            
    webcred = credentials.Certificate("chat-app-aa7a3-firebase-adminsdk-s3pos-8b56e4c519.json")
    web_app = firebase_admin.initialize_app(webcred)
    scoredb = firestore.client(web_app)

    andcred = credentials.Certificate("ambandriodapp-firebase-adminsdk-es0m4-d6466f7f03.json")
    android_app = firebase_admin.initialize_app(andcred, name='other')
    storedb = firestore.client(android_app)

while True :
    
    phone = serial.Serial("/dev/serial0",115200,timeout=1) 
    
    try:
        phone.write(b'ATZ\r')  # set to base user profile

        phone.write(b"AT+CMGF=1\r")  # set messages to text format 

        phone.write(b'AT+CMGL="REC UNREAD"\r')
        
        dataa = phone.readall()

        stringg = dataa.decode()

        indices_object1 = re.finditer(pattern= 'CMGL:' , string=str(stringg))
        indicesfirst = [index.start() for index in indices_object1]
        indices_object2 = re.finditer(pattern= 'Location is' , string=str(stringg))
        indiceslast = [index.start() for index in indices_object2]
       
        for i in range(len(indicesfirst)):
                j=i
                x = 23+indicesfirst[i]
                y = 37+indiceslast[j]
                substring1 = stringg[x:x+12]
                substring2 = stringg[x+18:x+37]
                substring3 = stringg[x+39:y]
                print(substring3)
                name_start = substring3.index("Name")
                name_end = substring3.index(":")
                Name2 = substring3[name_start+8:name_end-1]
                ind_start= substring3.index("Location is ")
                ind_med= substring3.index(", ")
                ind_last = substring3.index(" .")
                latitude = float(substring3[ind_start+13:ind_med-1])
                longitude = float(substring3[ind_med+2:ind_last-1])
                location = GeoPoint(latitude, longitude)
                my_timestamp = datetime.now()
                
                print(substring1)
                print(substring2)
                print(substring3)
                print(location)
                
                if "Breakdown-call" in substring3 :

                    new_db_web = scoredb.collection(u'users').document()
                    data = {
                u'location': location, 
                u'name': Name2 + substring1,
                u'isOline': 'false',
                u'createdAt': my_timestamp,
                u'text': substring3,
                u'phone':substring1,
                u'uid':new_db_web.id
            }   
                    new_db_web.set(data)
                

                elif "Emergency-call" in substring3 :

                    new_db_android = storedb.collection(u'emergency-calls').document()
                    data = {
                u'Name': Name2,
                u'title': "E-call"+"-" +substring1,       
                u'location': location, 
                u'viewedby': "null",             
                u'phone': substring1,
                u'time': my_timestamp,
                u'uid':new_db_android.id
                            }   
                    new_db_android.set(data)
                i+=1
        time.sleep(5) 
    finally: 

        phone.close()   

         

