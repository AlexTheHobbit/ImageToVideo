import os
import cv2
import argparse

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

    for i in range(frameTotal):
        currentScale = 1 + i*zoomRate

        horizontalOffset = int((currentScale - 1)*targetHeight)
        verticalOffset = int((currentScale - 1)*targetWidth)

        currentHeight = targetHeight + horizontalOffset*2
        currentWidth = targetWidth + verticalOffset*2
        currentDimensions = (currentWidth, currentHeight)

        currentFrame = cv2.resize(image, currentDimensions, interpolation=cv2.INTER_CUBIC)

        croppedFrame = currentFrame[horizontalOffset:targetHeight+horizontalOffset, verticalOffset:targetWidth+verticalOffset]
        yield croppedFrame

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Convert images to videos with Ken Burns zoom effect',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process images in current directory with defaults
  python imgToVideo.py

  # Specify input and output directories
  python imgToVideo.py -i ./images -o ./videos

  # Custom resolution and settings
  python imgToVideo.py --width 3840 --height 2160 --fps 30 --duration 15

  # Adjust zoom and blur
  python imgToVideo.py --zoom 0.0006 --blur 201
        """
    )

    parser.add_argument('-i', '--input',
                        default='.',
                        help='Input directory containing images (default: current directory)')

    parser.add_argument('-o', '--output',
                        default='.',
                        help='Output directory for videos (default: current directory)')

    parser.add_argument('-w', '--width',
                        type=int,
                        default=1920,
                        help='Target video width in pixels (default: 1920)')

    parser.add_argument('--height',
                        type=int,
                        default=1080,
                        help='Target video height in pixels (default: 1080)')

    parser.add_argument('--fps',
                        type=int,
                        default=25,
                        help='Frame rate (frames per second) (default: 25)')

    parser.add_argument('-d', '--duration',
                        type=int,
                        default=10,
                        help='Video duration in seconds (default: 10)')

    parser.add_argument('-z', '--zoom',
                        type=float,
                        default=0.0004,
                        help='Zoom rate (0.0001-0.01) (default: 0.0004)')

    parser.add_argument('-b', '--blur',
                        type=int,
                        default=195,
                        help='Blur strength (must be odd number) (default: 195)')

    parser.add_argument('--codec',
                        default='xdv7',
                        help='Video codec fourcc code (default: xdv7 for MXF)')

    parser.add_argument('--extension',
                        default='mxf',
                        help='Output video file extension (default: mxf)')

    return parser.parse_args()

if __name__ == "__main__":
    # Parse command-line arguments
    args = parse_arguments()

    # Supported image formats
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.jfif', '.webp'}

    # Validate and create output directory if needed
    if not os.path.exists(args.input):
        print(f"[ERROR] Input directory '{args.input}' does not exist")
        exit(1)

    if not os.path.exists(args.output):
        try:
            os.makedirs(args.output)
            print(f"Created output directory: {args.output}")
        except Exception as e:
            print(f"[ERROR] Error creating output directory '{args.output}': {e}")
            exit(1)

    # Get list of image files
    image_files = []
    for file in os.listdir(args.input):
        file_ext = os.path.splitext(file)[1].lower()
        if file_ext in SUPPORTED_FORMATS:
            image_files.append(file)

    if not image_files:
        print(f"[ERROR] No supported image files found in '{args.input}'")
        print(f"Supported formats: {', '.join(SUPPORTED_FORMATS)}")
        exit(0)

    print(f"Found {len(image_files)} image(s) to process")
    print(f"Settings: {args.width}x{args.height}, {args.fps}fps, {args.duration}s, zoom={args.zoom}, blur={args.blur}")
    print()

    # Process each image file
    success_count = 0
    error_count = 0

    for file in image_files:
        # Check if file has a supported image extension (case-insensitive)
        file_ext = os.path.splitext(file)[1].lower()
        if file_ext in SUPPORTED_FORMATS:
            try:
                print(f"Processing: {file}")

                # Build full input path
                input_path = os.path.join(args.input, file)

                # Process image and generate frames
                blurredImg = scaleAndBlur(
                    input_path,
                    targetWidth=args.width,
                    targetHeight=args.height,
                    targetBlur=args.blur
                )
                imgSequence = frames_from_image(
                    blurredImg,
                    frameRate=args.fps,
                    imgDuration=args.duration,
                    zoomRate=args.zoom,
                    targetWidth=args.width,
                    targetHeight=args.height
                )

                # Setup video writer
                fileName = os.path.splitext(file)
                output_filename = f"{fileName[0]}_video.{args.extension}"
                outputPath = os.path.join(args.output, output_filename)

                out = cv2.VideoWriter(
                    outputPath,
                    cv2.VideoWriter_fourcc(*args.codec),
                    args.fps,
                    (args.width, args.height)
                )

                if not out.isOpened():
                    raise RuntimeError(f"Failed to initialize video writer for {outputPath}. Check codec availability.")

                # Write frames to video
                for frame in imgSequence:
                    out.write(frame)

                out.release()
                print(f"[OK] Successfully created: {outputPath}")
                success_count += 1

            except ValueError as e:
                print(f"[ERROR] Error processing {file}: {e}")
                error_count += 1
                continue
            except RuntimeError as e:
                print(f"[ERROR] Error creating video for {file}: {e}")
                error_count += 1
                continue
            except Exception as e:
                print(f"[ERROR] Unexpected error processing {file}: {e}")
                error_count += 1
                continue

    # Print summary
    print()
    print("=" * 50)
    print(f"Processing complete: {success_count} succeeded, {error_count} failed")
    print("=" * 50)
