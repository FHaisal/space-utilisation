import cv2

cap = cv2.VideoCapture(0)

while True:
    ret, image = cap.read()

    cv2.imshow('People Detection', image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()