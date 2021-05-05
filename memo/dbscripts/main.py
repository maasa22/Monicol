import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime
import uuid
import random

cred = credentials.Certificate("./monicol-service-firebase-adminsdk-a5qbg-dae2be810b.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

callTimeList = [datetime(2021, 5, 1, 8, 00, 00, 000), datetime(2021, 5, 1, 8, 20, 00, 000), datetime(2021, 5, 2, 8, 00, 00, 000), datetime(2021, 5, 2, 8, 20, 00, 000)]
callerIdList = ["hogehoge", "fugafuga", "hoge", "fuga"]
isReservedList = [True, False]
# create data
def createData():
    doc_ref = db.collection('reservations').document(str(uuid.uuid4().hex))
    doc_ref.set({
        'callTime' : random.choice(callTimeList), \
        'callerId' : random.choice(callerIdList[:2]), \
        'customerId' : random.choice(callerIdList[:2]), \
        'isReserved': random.choice(isReservedList), \
    })

# Delete data
def deleteData():
    users_ref = db.collection(u'reservations')
    docs = users_ref.limit(20).get()
    for doc in docs:
        print(u'Deleting doc {} => {}'.format(doc.id, doc.to_dict()))
        doc.reference.delete()

deleteData()
for i in range(10):
    createData()
