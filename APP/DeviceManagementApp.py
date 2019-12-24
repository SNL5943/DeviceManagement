import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from picamera import PiCamera
from imutils.video import VideoStream
from time import sleep
from pyzbar import pyzbar
import argparse
import cv2
import datetime
import time
import imutils

IDreader = SimpleMFRC522()

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", type=str, default="qrcodes.csv", help="./")
args = vars(ap.parse_args())


# loop over the frames from the video stream
while True:
    try:
        print("[INFO] Please Tap your ID card!")
        id, user = IDreader.read()
        print(id)
        print(user)
    finally:
        # initialize the video stream and allow the camera sensor to warm up
        print("[INFO] Please scan device code for checking out!")
        vs = VideoStream(usePiCamera=True).start()
        sleep(1.0)
        # open the output CSV file for writing and initialize the set of
        # barcodes found thus far
        csv = open('Checking_History.csv', mode = 'w')
        found = set()
       
        while True:
            # grab the frame from the threaded video stream and resize it to
            # have a maximum width of 400 pixels and rotate 180 degrees
            frame = vs.read()
            frame = imutils.resize(frame, width=400)
            frame = imutils.rotate(frame, 180)
            # find the barcodes in the frame and decode each of the barcodes
            barcodes = pyzbar.decode(frame)
            # loop over the detected barcodes
            for barcode in barcodes:
                # extract the bounding box location of the barcode and draw
                # the bounding box surrounding the barcode on the image
                (x, y, w, h) = barcode.rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
         
                # the barcode data is a bytes object so if we want to draw it
                # on our output image we need to convert it to a string first
                barcodeData = barcode.data.decode("utf-8")
                barcodeType = barcode.type
         
                # draw the barcode data and barcode type on the image
                text = "{} ({})".format(barcodeData, barcodeType)
                cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
         
                # if the barcode text is currently not in our CSV file, write
                # the timestamp + barcode to disk and update the set
                if barcodeData not in found:
                    csv.write("{},{},{},{}\n".format(datetime.datetime.now(),id, user, barcodeData))
                    csv.flush()
                    found.add(barcodeData)              
            # show the output frame
            cv2.imshow("QR Scanner", frame)
            key = cv2.waitKey(1) & 0xFF
            #hit ENTER to end checkout process
            if key == ord("e"):
                #insert data into sqlite here?
                break
               
        # close the output CSV file do a bit of cleanup
        print("[INFO] QR scanning finished...")
        #found.clean()
        csv.close()
        cv2.destroyAllWindows()
        vs.stop()
    print("[INFO] Starting new check out process...")
    


