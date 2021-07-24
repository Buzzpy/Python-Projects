import cv2
image = cv2.imread("profile.jpg") #Import the image
grey_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) #Add grey filter.
invert = cv2.bitwise_not(grey_img) #Add inverted filter.
blur = cv2.GaussianBlur(invert,(21,21),0) #Add Blur effect
invertedblur = cv2.bitwise_not(blur)
sketch = cv2.divide(grey_img, invertedblur, scale = 256.0)
cv2.imwrite("profile_sketch.png", sketch) #Export the sketch image

# Coded with 💙 by Mr. Unity Buddy
