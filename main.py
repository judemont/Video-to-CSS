from datetime import timedelta
import cv2
import numpy as np
import os


videoPath = input("Enter the path of the video: ")
resultFps = int(input("Frames per second: "))
resultHeight = int(input("Resolution (height): "))

cssFileName = "video.css"



cap = cv2.VideoCapture(videoPath)
success, frame = cap.read() 

height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
resultWidth = int(width * resultHeight / height)


nbFrames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
videoFps = cap.get(cv2.CAP_PROP_FPS) 
videoDuration = round(nbFrames / videoFps) 
nbFramesResult = videoDuration * resultFps


cssResult = """
#cssVideo {
    position: sticky;
    top: -1px;
    left: -1px;
    overflow: visible;
    width: 1px;
    height: 1px;
    animation: cssVideo linear %ss both infinite;
}

@keyframes cssVideo {

""" % (str(videoDuration))



i = 0
while True:
    success, frame = cap.read() 
    print(i / nbFrames * 100)
    if not success:
        print(success)
        break

    if i % round(nbFrames / nbFramesResult) == 0:
        cssResult += "%s%% {box-shadow: " % (str(i * 100 / nbFrames ))
        resizedFrame = cv2.resize(frame, (resultWidth, resultHeight))
        cssColors = []
        for x in range(0, resultWidth):
            for y in range(0, resultHeight):
                cssColors.append(f"{x}px {y}px 0 {'#%02x%02x%02x' % (resizedFrame[y,x,2], resizedFrame[y,x,1], resizedFrame[y,x,0])},")
                # print (frame[x,y,0]) #B 
                # print (frame[x,y,1]) #G 
                # print (frame[x,y,2]) #R 
        cssResult += "".join(cssColors)[:-1] + ";}\n"
    i += 1

cap.release()

cssResult += "}"


with open(cssFileName, "w") as cssFile:
    cssFile.write(cssResult)
    cssFile.close()

with open("index.html", "w") as htmlFile:
    htmlFile.write(f"""
<!DOCTYPE html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CSS Video</title>
    <link rel="stylesheet" href="video.css">
</head>
<body>
    <div style="scale:5" id="cssVideo"></div>
</body>
</html>
    """)