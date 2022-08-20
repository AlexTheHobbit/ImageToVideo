import os
import cv2

def scaleAndBlur(img_file, targetWidth = 1920, targetHeight = 1080):
    
    img = cv2.imread(img_file)
    imgData = img.shape

    initialWidth = imgData[1]
    initialHeight = imgData[0]
    

    idealRatio = targetWidth/targetHeight
    initRatio = initialWidth/initialHeight
    
    #distinguishes between wide and narrow images
    if initRatio > idealRatio:
        #print("wide image!")
        scaleFactor = targetWidth / initialWidth
        invScaleFactor = targetHeight / initialHeight
    elif initRatio == idealRatio:
        #print("perfect aspect ratio!")
        scaleFactor = targetHeight / initialHeight
        invScaleFactor = targetWidth / initialWidth
    else:
        #print("narrow image!")
        scaleFactor = targetHeight / initialHeight
        invScaleFactor = targetWidth / initialWidth

    inv_h_offset = (int(initialHeight*(targetHeight / initialHeight)//4))

    w_offset = ((targetWidth//2) - (initialWidth*scaleFactor//2))
    outputData = (int(targetWidth), int(targetHeight))
    newData = (int(scaleFactor*initialWidth), int(scaleFactor*initialHeight))
    invNewData = (int(invScaleFactor*initialWidth), int(invScaleFactor*initialHeight)) 


    scaled_img = cv2.resize(img, newData)
    inverted_scaled_img = cv2.resize(img, invNewData)
    
    #unsure if works yet, changes blurred image depending on if image is wide or narrow
    if initRatio > idealRatio:
        blurred_img = cv2.GaussianBlur(inverted_scaled_img,(61,61),0)
    else:
        blurred_img = cv2.GaussianBlur(inverted_scaled_img,(61,61),0)
        
    inv_crop_img = blurred_img[inv_h_offset:1080+inv_h_offset, 0:1920].copy()

    #print("blurred image is " + str(blurred_img.shape))
    #print("scaled image is " + str(scaled_img.shape))
    
    #show mid-stage for debugging, safe to delete
    #cv2.imshow("blurred_img", blurred_img)
    #cv2.waitKey(0)
    #cv2.imshow("scaled_img", scaled_img)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    
    h_offset = (int(targetHeight//2))
    x_offset = int(w_offset)
    
    #x_offset = 0
    if initRatio > idealRatio:
        y_offset = int((targetHeight//2) - (initialHeight*scaleFactor//2))
        #y_offset = 0
    else:
        y_offset = 0

    #print("x offset is " + str(x_offset))
    #print("y offset is " + str(y_offset))
        
    #overlay_image = cv2.addWeighted(scaled_img,1,blurred_img,1,0)
    #l_img[y_offset:y_offset+s_img.shape[0], x_offset:x_offset+s_img.shape[1]] = s_img
    if initRatio > idealRatio:
        #blurred_img[y_offset:y_offset+scaled_img.shape[0], x_offset:x_offset+scaled_img.shape[1]] = scaled_img
        blurred_img[y_offset:y_offset+scaled_img.shape[0], x_offset:x_offset+scaled_img.shape[1]] = scaled_img
    else:
        blurred_img[y_offset:y_offset+scaled_img.shape[0], x_offset:x_offset+scaled_img.shape[1]] = scaled_img

    final_img = blurred_img[0:1080, 0:1920]
    #print("final image resolution is " + str(final_img.shape[1]) + "x" + str(final_img.shape[0]))
    #cv2.imshow("overlaid", blurred_img)
    #cv2.waitKey(0)
    cv2.destroyAllWindows()
    #cv2.imshow("final", final_img)
    #cv2.waitKey(0)
    cv2.destroyAllWindows()
    #cv2.imwrite('messigray.png',img)    #needs fixing, saves image

    #finalImg_file = "exported_" + img_file + ".jpg"            works, but shouldnt save the file from within the function
    #cv2.imwrite(finalImg_file, final_img)                      works, but shouldnt save the file from within the function
    return final_img
    #print("\n" + "done!")


def frames_from_image(image):
    frameRate = 25
    imgDuration = 10
    frameTotal = frameRate * imgDuration
    framesFinal = []
    for i in range(frameTotal):
        currentScale = 1 + i*0.0004
        currentHeight = 1080 * currentScale
        currentWidth = 1920 * currentScale
        currentDimensions = (round(currentWidth), round(currentHeight))
        currentFrame = cv2.resize(image, currentDimensions, interpolation=cv2.INTER_CUBIC)
        #widthOffset = int(currentWidth/2)                       #wrong, figure out better formula
        #heightOffset = int(currentHeight/2)                     #wrong, figure out better formula
        widthOffset = round((currentWidth-1920)/2)                   
        heightOffset = round((currentHeight-1080)/2)

        #croppedFrame = currentFrame[0:1080, 0:1920]                                                                 #top-left corner zoom
        croppedFrame = currentFrame[heightOffset:1080+heightOffset, widthOffset:1920+widthOffset]                  #good but jitters
        framesFinal.append(croppedFrame)
    return framesFinal

#def video_from_frames(frames):
#    frameTotal = len(frames) * 10
#    for i in frameTotal:
#        return

#for file in os.listdir():
#    if file.endswith(".jpg") or file.endswith(".jpeg") or file.endswith(".png") or file.endswith(".JPG") or file.endswith(".PNG"):
#        blurredImg = scaleAndBlur(file)
#        imgSequence = frames_from_image(blurredImg)
#        for count, frame in enumerate(imgSequence):
#            fileName = "exported_" + str(file) + "_" + str(count) + ".jpg"
#            cv2.imwrite(fileName, frame)

for file in os.listdir():
    if file.endswith(".jpg") or file.endswith(".jpeg") or file.endswith(".png") or file.endswith(".JPG") or file.endswith(".PNG"):
        blurredImg = scaleAndBlur(file)
        imgSequence = frames_from_image(blurredImg)
        
        out = cv2.VideoWriter((str(file)+'project.avi'),cv2.VideoWriter_fourcc(*'DIVX'), 25, (1920,1080))

        for i in range(len(imgSequence)):
            out.write(imgSequence[i])
        out.release()
#        for count, frame in enumerate(imgSequence):
#            fileName = "exported_" + str(file) + "_" + str(count) + ".jpg"
#            cv2.imwrite(fileName, frame)


