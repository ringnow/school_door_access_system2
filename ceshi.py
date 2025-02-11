import cv2

def open_camera():
    cap = cv2.VideoCapture(1)  # 使用默认的相机索引
    if not cap.isOpened():
        raise Exception("无法打开摄像头")
    return cap

def close_camera(cap):
    cap.release()
    cv2.destroyAllWindows()

cap = open_camera()
while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        break

    cv2.imshow('Camera Feed', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

close_camera(cap)