import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import asyncio
import subprocess

cred = credentials.Certificate('blitzgowest-firebase-adminsdk-a0vzp-be4c05ae95.json')
firebase_admin.initialize_app(cred)

db = firestore.client()
sessions_ref = db.collection('Users')
queue_ref = db.collection('queue')

async def create_game():
    def queue_snapshot(doc_snapshot, changes, read_time):
        codes_array = db.collection("queue").document('Games').get().get("codes")
        if codes_array[-1] != 'filler':
            db.collection("queue").document('Games').set({"codes": codes_array[:-1]})
            val = codes_array[-1]
            print(val)
            subprocess.Popen(["python3", "main.py", val])

    queue_listener = queue_ref.document('Games').on_snapshot(queue_snapshot)

    while True:
        await asyncio.sleep(1) 

create_loop = asyncio.get_event_loop()
create_loop.run_until_complete(create_game())