import cv2
import numpy as np

# Load video
cap = cv2.VideoCapture('Video.mp4')

# Initialize background subtractor (standard OpenCV MOG2)
algo = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=40)

# Settings for counting
count_line_position = 550  # Y-coordinate of the counting line
min_width = 80             # Minimum width of vehicle bounding box
min_height = 80            # Minimum height of vehicle bounding box
offset = 6                 # Pixel tolerance for line crossing

counter = 0
matches = []

def get_centroid(x, y, w, h):
    """Calculates the center point of a bounding box."""
    cx = x + int(w / 2)
    cy = y + int(h / 2)
    return cx, cy

while True:
    ret, frame1 = cap.read()
    
    if not ret or frame1 is None:
        break

    # Pre-processing
    grey = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(grey, (3, 3), 5)
    img_sub = algo.apply(blur)
    
    # Morphological operations to remove noise and fill gaps
    dilat = cv2.dilate(img_sub, np.ones((5, 5)))
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    dilatada = cv2.morphologyEx(dilat, cv2.MORPH_CLOSE, kernel)
    dilatada = cv2.morphologyEx(dilatada, cv2.MORPH_CLOSE, kernel)
    
    # Find contours
    contours, _ = cv2.findContours(dilatada, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Draw counting line (Red line across the frame)
    cv2.line(frame1, (25, count_line_position), (1200, count_line_position), (0, 0, 255), 3)

    for c in contours:
        (x, y, w, h) = cv2.boundingRect(c)
        
        # Filter out small noise
        if w >= min_width and h >= min_height:
            # Draw bounding box around vehicle
            cv2.rectangle(frame1, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Calculate centroid
            centroid = get_centroid(x, y, w, h)
            matches.append(centroid)
            cv2.circle(frame1, centroid, 4, (0, 0, 255), -1)

    # Check if centroid crossed the counting line
    for (cx, cy) in matches:
        if (count_line_position - offset) < cy < (count_line_position + offset):
            counter += 1
            # Change line color to green briefly to visually confirm detect
            cv2.line(frame1, (25, count_line_position), (1200, count_line_position), (0, 255, 0), 3)
            matches.remove((cx, cy))

    # Display Vehicle Counter Text
    cv2.putText(frame1, f"VEHICLE COUNT: {counter}", (450, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

    cv2.imshow('Detector', dilatada)
    cv2.imshow('Vehicle Counter', frame1)

    # Press Enter (13) or 'q' to exit
    if cv2.waitKey(1) == 13:
        break

cv2.destroyAllWindows()
cap.release()