import os
import cv2

def scaleAndBlur(img_file, targetWidth = 1920, targetHeight = 1080, targetBlur = 195):
    img = cv2.imread(img_file)
    imgData = img.shape

    initialWidth = imgData[1]
    initialHeight = imgData[0]

    idealRatio = targetWidth/targetHeight
    initRatio = initialWidth/initialHeight
    
    #distinguishes between wide and narrow images
    if initRatio > idealRatio:
        scaleFactor = targetWidth / initialWidth
        invScaleFactor = targetHeight / initialHeight
    else:
        scaleFactor = targetHeight / initialHeight
        invScaleFactor = targetWidth / initialWidth

    w_offset = ((targetWidth//2) - (initialWidth*scaleFactor//2))
    newData = (int(scaleFactor*initialWidth), int(scaleFactor*initialHeight))
    invNewData = (int(invScaleFactor*initialWidth), int(invScaleFactor*initialHeight)) 


    scaled_img = cv2.resize(img, newData)
    inverted_scaled_img = cv2.resize(img, invNewData)
    
    #changes blurred image depending on if image is wide or narrow
    if initRatio > idealRatio:
        blurred_img = cv2.GaussianBlur(inverted_scaled_img,(targetBlur,targetBlur),0)
    else:
        blurred_img = cv2.GaussianBlur(inverted_scaled_img,(targetBlur,targetBlur),0)

    x_offset = int(w_offset)
    
    if initRatio > idealRatio:
        y_offset = int((targetHeight//2) - (initialHeight*scaleFactor//2))
    else:
        y_offset = 0

    if initRatio > idealRatio:
        blurred_img[y_offset:y_offset+scaled_img.shape[0], x_offset:x_offset+scaled_img.shape[1]] = scaled_img
    else:
        blurred_img[y_offset:y_offset+scaled_img.shape[0], x_offset:x_offset+scaled_img.shape[1]] = scaled_img

    final_img = blurred_img[0:targetHeight, 0:targetWidth]
    cv2.destroyAllWindows()
    cv2.destroyAllWindows()
    return final_img

def frames_from_image(
    image, 
    frameRate = 25,
    imgDuration = 10,
    zoomRate = 0.0004,
    targetWidth = 1920,
    targetHeight = 1080,
):
    frameTotal = frameRate * imgDuration
    framesFinal = []

    for i in range(frameTotal):
        currentScale = 1 + i*zoomRate

        horizontalOffset = int((currentScale - 1)*targetHeight)
        verticalOffset = int((currentScale - 1)*targetWidth)

        currentHeight = targetHeight + horizontalOffset*2
        currentWidth = targetWidth + verticalOffset*2
        currentDimensions = (currentWidth, currentHeight)

        currentFrame = cv2.resize(image, currentDimensions, interpolation=cv2.INTER_CUBIC)

        croppedFrame = currentFrame[horizontalOffset:targetHeight+horizontalOffset, verticalOffset:targetWidth+verticalOffset]
        framesFinal.append(croppedFrame)

    return framesFinal

if __name__ == "__main__":
    for file in os.listdir():
        if file.endswith(".jpg") or file.endswith(".jpeg") or file.endswith(".png") or file.endswith(".JPG") or file.endswith(".PNG") or file.endswith(".jfif") or file.endswith(".webp"):
            blurredImg = scaleAndBlur(file)
            imgSequence = frames_from_image(blurredImg)
            shortenedName = str(file)
            fileName = os.path.splitext(file)
            out = cv2.VideoWriter((str(fileName[0])+'_video.mxf'),cv2.VideoWriter_fourcc(*'xdv7'), 25, (1920,1080))

            for i in range(len(imgSequence)):
                out.write(imgSequence[i])
            out.release()
