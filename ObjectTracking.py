import cv2
import serial
import time

# Serial communication setup
ser = serial.Serial('/dev/cu.usbmodem11101', 9600, timeout=1) 

#pixel to step conversion factor
PIXELS_TO_STEPS_X = 0.1  
PIXELS_TO_STEPS_Y = 0.1  

# send moves to Arduino
def send_command_to_arduino(steps_x, steps_y):
    command = f"{steps_x},{steps_y}\n"
    ser.write(command.encode())
    time.sleep(0.05) 

# calculate the movement 
def get_movement_steps(x, y, frame_center_x, frame_center_y):
    delta_x = x - frame_center_x
    delta_y = y - frame_center_y
    
    steps_x = int(delta_x * PIXELS_TO_STEPS_X)
    steps_y = int(delta_y * PIXELS_TO_STEPS_Y)
    
    return steps_x, steps_y

# \ adjust brightness and contrast of image
def adjust_brightness_contrast(image, brightness=30, contrast=30):
    brightness = int((brightness / 100.0) * 255)
    contrast = int(contrast / 100.0 * 127)
    return cv2.addWeighted(image, 1 + contrast/127.0, image, 0, brightness - contrast)

# Start video capture
cap = cv2.VideoCapture(0)  # Use the default camera

if not cap.isOpened():
    print("Error: Could not open video stream")
    exit()
#camera properties
cap.set(cv2.CAP_PROP_BRIGHTNESS, 0.7)  # brightness
cap.set(cv2.CAP_PROP_CONTRAST, 0.7)    # contrast
cap.set(cv2.CAP_PROP_GAIN, 0.5)        #  gain
cap.set(cv2.CAP_PROP_EXPOSURE, -6)     # exposure


time.sleep(5)

# Read  first frame
ret, frame = cap.read()
if not ret:
    print("Failed to grab frame")
    cap.release()
    cv2.destroyAllWindows()
    exit()

frame = cv2.resize(frame, (640, 480))

# Adjust brightness and contrast of the initial frame
frame = adjust_brightness_contrast(frame, brightness=100, contrast=100)  

bbox = cv2.selectROI("Frame", frame, False)
cv2.destroyWindow("Frame")

# Initialize  tracker
tracker = cv2.legacy.TrackerCSRT_create()
init_ok = tracker.init(frame, bbox)
print(f"Tracker initialized: {init_ok}")


frame_count = 0
skip_frames = 1 #prcess every so frame

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    frame_count += 1
    if frame_count % skip_frames != 0:
        continue


    frame = cv2.resize(frame, (640, 480))

  
    frame = adjust_brightness_contrast(frame, brightness=60, contrast=50) 

    # Update the tracker
    ret, bbox = tracker.update(frame)
    print(f"Tracker update: {ret}, Bbox: {bbox}")

    if ret:
        # Tracking success
        p1 = (int(bbox[0]), int(bbox[1]))
        p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
        cv2.rectangle(frame, p1, p2, (0, 255, 0), 2, 1)

        # Calculate the center of the bounding box
        box_center_x = int(bbox[0] + bbox[2] / 2)
        box_center_y = int(bbox[1] + bbox[3] / 2)

        # Calculate the center of the frame
        frame_center_x = frame.shape[1] // 2
        frame_center_y = frame.shape[0] // 2

        # Get the movement steps
        steps_x, steps_y = get_movement_steps(box_center_x, box_center_y, frame_center_x, frame_center_y)

        # Print the steps
        print(f"Steps X: {steps_x}, Steps Y: {steps_y}")

        # Send steps to Arduino
        send_command_to_arduino(steps_x, steps_y)
    else:
        # Tracking failure
        cv2.putText(frame, "Tracking failure detected", (100, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

    # Display the frame with the tracked object
    cv2.imshow("Tracking", frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
ser.close()