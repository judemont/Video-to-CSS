import cv2
import numpy as np
import os
import threading


videoPath = input("Enter the path of the video: ")
resultFps = int(input("Frames per second: "))
resultHeight = int(input("Resolution (height): "))
num_threads = int(input("Number of threads: "))


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

cssHeader = """
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

# Write the header to the CSS file initially
with open(cssFileName, "w") as cssFile:
    cssFile.write(cssHeader)


def writeCssColors(frame):
    resizedFrame = cv2.resize(frame, (resultWidth, resultHeight))
    cssColors = []
    for x in range(0, resultWidth):
        for y in range(0, resultHeight):
            cssColors.append(f"{x}px {y}px 0 {'#%02x%02x%02x' % (resizedFrame[y,x,2], resizedFrame[y,x,1], resizedFrame[y,x,0])},")
    return cssColors


def process_frames(start, end, thread_id):
    cap = cv2.VideoCapture(videoPath) 
    cap.set(cv2.CAP_PROP_POS_FRAMES, start)

    with open(cssFileName, "a") as cssFile:  # Open the file in append mode
        for i in range(start, end):
            success, frame = cap.read()
            if not success:
                break

            if i % round(nbFrames / nbFramesResult) == 0:
                frameCss = "%s%% {box-shadow: " % (str(i * 100 / nbFrames))
                cssColors = writeCssColors(frame)
                frameCss += "".join(cssColors)[:-1] + ";}\n"

                cssFile.write(frameCss)  # Write CSS for the frame directly to the file

            if thread_id == num_threads - 1:
                percentage_done = ((i - start) / (end - start)) * 100
                print(f"Thread {thread_id}: {percentage_done:.2f}% done")

    cap.release()


threads = []
frames_per_thread = nbFrames // num_threads

for i in range(num_threads):
    start_frame = i * frames_per_thread
    end_frame = (i + 1) * frames_per_thread if i != num_threads - 1 else nbFrames
    thread = threading.Thread(target=process_frames, args=(start_frame, end_frame, i))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

# Finish the CSS file
with open(cssFileName, "a") as cssFile:
    cssFile.write("}")

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
    <div style="scale: {resultHeight/10};" id="cssVideo"></div>
</body>
</html>
    """)