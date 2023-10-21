import cv2
import numpy as np
import pytesseract
from color_validation import find_largest_color_area


async def crop_killer(file_binary_code):
    pixel_matrix = np.frombuffer(file_binary_code, dtype=np.uint8)

    image = cv2.imdecode(pixel_matrix, cv2.IMREAD_UNCHANGED)
    # image = cv2.imread(image)

    # Convert the image from BGR to grayscale
    grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    average_intensity = find_largest_color_area(image)

    if average_intensity > 127:  # if average_intensity bigger than 127 it's mean image area is contained white
        # Threshold the grayscale image to obtain a binary image
        _, threshold_image = cv2.threshold(grayscale_image, 200, 255, cv2.THRESH_BINARY)
    else:
        _, threshold_image = cv2.threshold(grayscale_image, 50, 255, cv2.THRESH_BINARY_INV)

    # Find contours in the binary image
    contours, _ = cv2.findContours(threshold_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Find the contour with the largest area (white or black layout)
    max_area = 0
    max_contour = None
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > max_area:
            max_area = area
            max_contour = contour

    # Create a bounding rectangle around the white layout contour
    x, y, w, h = cv2.boundingRect(max_contour)

    # Crop the image using the bounding rectangle
    cropped_image = image[y:y + h, x:x + w]

    text = pytesseract.image_to_string(cropped_image).upper()
    print({'detail': text})

    keywords = ['USD', 'MAO RITH', 'RITH MAO', 'ABA', 'GO TO ACCOUNTS', 'DONE', '000 354 079']

    if any(keyword in text for keyword in keywords):
        amount_paid = None
        if 'USD' in text:
            amount_paid = text.split('USD')[0].split('-')[1]
        if 'USP' in text:
            amount_paid = text.split('USP')[0].split('-')[1]

        print({'user_transaction': amount_paid})

        _, encoded_image = cv2.imencode('.jpg', cropped_image)

        return encoded_image, amount_paid
    else:
        encoded_image = []
        amount_paid = None

        return encoded_image, amount_paid
