import os
import cv2

def scaleAndBlur(img_file, targetWidth = 1920, targetHeight = 1080, targetBlur = 195):
    # Input validation
    if targetWidth <= 0 or targetHeight <= 0:
        raise ValueError(f"Target dimensions must be positive. Got width={targetWidth}, height={targetHeight}")

    if targetBlur <= 0:
        raise ValueError(f"Target blur must be positive. Got blur={targetBlur}")

    if targetBlur % 2 == 0:
        raise ValueError(f"Target blur must be odd for GaussianBlur. Got blur={targetBlur}")

    img = cv2.imread(img_file)

    if img is None:
        raise ValueError(f"Failed to load image: {img_file}. File may be corrupted or not a valid image format.")

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

    if scaleFactor > 1:        
        scaled_img = cv2.resize(img, newData, interpolation = cv2.INTER_CUBIC)
        inverted_scaled_img = cv2.resize(img, invNewData, interpolation = cv2.INTER_CUBIC)
    else:
        scaled_img = cv2.resize(img, newData, interpolation = cv2.INTER_AREA)
        inverted_scaled_img = cv2.resize(img, invNewData, interpolation = cv2.INTER_CUBIC)

    #apply gaussian blur to create background
    blurred_img = cv2.GaussianBlur(inverted_scaled_img,(targetBlur,targetBlur),0)

    x_offset = int(w_offset)

    if initRatio > idealRatio:
        y_offset = int((targetHeight//2) - (initialHeight*scaleFactor//2))
    else:
        y_offset = 0

    blurred_img[y_offset:y_offset+scaled_img.shape[0], x_offset:x_offset+scaled_img.shape[1]] = scaled_img

    final_img = blurred_img[0:targetHeight, 0:targetWidth]
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
    # Input validation
    if frameRate <= 0:
        raise ValueError(f"Frame rate must be positive. Got frameRate={frameRate}")

    if imgDuration <= 0:
        raise ValueError(f"Image duration must be positive. Got imgDuration={imgDuration}")

    if zoomRate < 0 or zoomRate > 0.1:
        raise ValueError(f"Zoom rate must be between 0 and 0.1 for reasonable results. Got zoomRate={zoomRate}")

    if targetWidth <= 0 or targetHeight <= 0:
        raise ValueError(f"Target dimensions must be positive. Got width={targetWidth}, height={targetHeight}")

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
    # Supported image formats
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.jfif', '.webp'}

    for file in os.listdir():
        # Check if file has a supported image extension (case-insensitive)
        file_ext = os.path.splitext(file)[1].lower()
        if file_ext in SUPPORTED_FORMATS:
            try:
                print(f"Processing: {file}")

                # Process image and generate frames
                blurredImg = scaleAndBlur(file)
                imgSequence = frames_from_image(blurredImg)

                # Setup video writer
                fileName = os.path.splitext(file)
                outputPath = str(fileName[0]) + '_video.mxf'
                out = cv2.VideoWriter(outputPath, cv2.VideoWriter_fourcc(*'xdv7'), 25, (1920,1080))

                if not out.isOpened():
                    raise RuntimeError(f"Failed to initialize video writer for {outputPath}. Check codec availability.")

                # Write frames to video
                for i in range(len(imgSequence)):
                    out.write(imgSequence[i])

                out.release()
                print(f"✓ Successfully created: {outputPath}")

            except ValueError as e:
                print(f"✗ Error processing {file}: {e}")
                continue
            except RuntimeError as e:
                print(f"✗ Error creating video for {file}: {e}")
                continue
            except Exception as e:
                print(f"✗ Unexpected error processing {file}: {e}")
                continue
