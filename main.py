import cv2
from cvzone.PoseModule import PoseDetector
import pyglet.media
import threading
import os
import requests
import firebase_admin
from firebase_admin import credentials,db,storage


cred = credentials.Certificate(
    {
  "type": "service_account",
  "project_id": "cctv-46183",
  "private_key_id": "7fea59fce19abadd37372cf87f66c72b24270d0b",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDBR52yrqoicZa3\n/zBpJxJxfonCFbkUnFfoi4Y77SP2mpOo37IqeCV7I9cZ1Bq4UCYzwrzDZBHSbkVh\n9tt+MafnkwN1rN/055jStxtEG7xfH6FPohYlG+4dqFH1Eyp/JPXpws9ub0aJz3vA\nrD8p0Ov7/rnole4++CowDkvKp+sV2EfGFI1MR8yCi+A6nnDvrftrTl7SMGxWbiOq\nCFGgyxNNx+Vp8fgQU68Gt/9yaY7C6ywYX+/WhGjpvrBhQvl2YbAe3pkZRSH9xF7U\nYv6/0qazATqfYD8YMlmjAuUoklLs+woh4nWCTNmsiTFbQfOvI+4Svet50152g8/y\nnB9WEfOtAgMBAAECggEAHQXU/0zNDWkDGdP+//s3AMXgh71dUmP7q1awLHV6jgA+\nJgCZL1llP21tUlqQPJcEdYdLcwemyXN3hbNc2EE6lkJ0JYp1AsB4KUQHmx2TFrGY\nNm3/Z0kfY2KwE93x5q+1IYn4PfwFmpIGYjM7NNtDZE6mue8xnFEFfLvY07CNU3Uo\nhI1T/y3T+lVwtiOVmL2C3R5qhWitC02BWwVcQNOu/viYvVCLWbL4tfNyPX3wszar\nWaAsBClEgzeP2bcen/EdSGeaoqQTN1ap1GZTH/K58opZA5fk0h8GfVZnvKdRx1ra\nvRFOl2+BvA6/MSzW79wUuW9wSrXHKl4EgQ5LSFZZXQKBgQD2HZZY2di8EqMsEl1N\nqQOob9CaAA11H552Kc0X0gZh7MLBPiBViZSKI17ly7z7Brf2PdJ4cxDRJNUu8Yy1\n1wXjJFTnwEHE2CCuo6VxXuunP6YpozW+94Ni68XhL4dmTAo/oL9qWeg0vvl91Nxe\nKRRVxN+Yh2Uvtp4czQ9885VqAwKBgQDJCs1tlfJty7nncOccjlsmJQBx0OH/dgKR\nuw43EkZ6u717NwykeJY9cms6CiU/z6y0jvGGJ9IpLDXT6xhnmQSfi55mCCucUsay\nvPMnFfyrf2saMgQ/7PjuOdRVtMFmCu36qF0+soyEyVZ9px8Bl5FPRUDy3/V7kGRC\nZtlJosaUjwKBgQCE69feZtFySdKMo+J2ZfjOyIzuD2c1QX1wrgTRf6Ho01kfyvDl\noadyr8W58D5BiRBj0mHQobyMaAsnDlgDgXzxfxbID4K10FBeYY2h3DUDoBGa3UXS\nvJTeIR4/D09eRWUnliarRqFtk1LlzceypxcPd4OXOlDA4y0juvBJeLjShwKBgEoV\nNvoI5VrcVdcZXbDCLIhz3iQSyxTuEahN+8EDdQFJKVu8P2ZkIUjnXuf2UR+gkY2/\nlvTOu7z8U6GR4l5anr+EHYyPujJStnGq+xcOHRu9SmROxg4gbuKqYLpsb1AA+w0A\n+cte1DUiVELdUKmvhpZleLeHG9i6rpdhevSNjQu1AoGBAIHee9JEFzYG2f5RKeRD\nMDGUqWPoXMkzXtHhOwLtHw+EeqYGrlXQruzi1xQ2WQKgfQrr+ODh5hfFCRpGEoOF\nv4SKDyYf6voZJJUUD3puSMddjzy0nlIjatBYRghsub8gTeQ7OgAOFvOa5M4erfzc\nkCVQgEANgBqHg9XgUJsHD3gC\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-kqo6l@cctv-46183.iam.gserviceaccount.com",
  "client_id": "116518382647140434338",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-kqo6l%40cctv-46183.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}


)
firebase_admin.initialize_app(cred, {
    'databaseURL':'https://cctv-46183-default-rtdb.asia-southeast1.firebasedatabase.app/',
    'storageBucket': 'cctv-46183.appspot.com'
})


storage_client = storage.bucket()
cap = cv2.VideoCapture(0) #webcam
ws, hs = 1280, 720
cap.set(3, ws)
cap.set(4, hs)

if not cap.isOpened():
    print("Camera can't open!!!")
    exit()

detector = PoseDetector()
# sound = pyglet.media.load("alarm.wav", streaming=False)
people = False
img_count, breakcount = 0, 0
os.makedirs('img', exist_ok=True)


def sendTelegram():
    path = './img/'  # Replace your path directory
    url = 'https://api.telegram.org/bot'
    token = "5985629482:AAFeieqg-M8wN0ewoGUOXtHmNP_7YI99CZk"  # Replace Your Token Bot
    chat_id = "507600509"  # Replace Your Chat ID
    caption = "People Detected!!! "
    cv2.imwrite(os.path.join(path, img_name), img)
    files = {'photo': open(path + img_name, 'rb')}
    resp = requests.post(url + token + '/sendPhoto?chat_id=' + chat_id + '&caption=' + caption, files=files)
    print(f'Response Code: {resp.status_code}')


def change_status():
    path = './img/'  # Replace your path directory
    cv2.imwrite(os.path.join(path, img_name), img)
    blob = storage_client.blob('h67dabhi/' + img_name)
    blob.upload_from_filename('./img/' + img_name)
    db.reference('h67dabhi').update({"Alert": "True"})


while True:
    success, img = cap.read()
    img = detector.findPose(img, draw=False)
    lmList, bboxInfo = detector.findPosition(img, bboxWithHands=False)
    img_name = f'image_{img_count}.png'

    # teleThread = threading.Thread(target=sendTelegram, args=())
    Alert= threading.Thread(target=change_status, args=())

    # soundThread = threading.Thread(target=sound.play, args=())

    if bboxInfo:
        cv2.rectangle(img, (120, 20), (470, 80), (0, 0, 255), cv2.FILLED)
        cv2.putText(img, "PEOPLE DETECTED!!!", (130, 60),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
        breakcount += 1

        if breakcount >= 30:
            if people == False:
                # img_count += 1
                img_count=0
                Alert.start()
                # soundThread.start()
                # teleThread.start()
                
                people = not people
    else:
        breakcount = 0
        if people:
            people = not people

    cv2.imshow("Image", img)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

cv2.destroyAllWindows()