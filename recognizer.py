import cv2

def qr_data(img_path):
    try:
        img = cv2.imread(f"{img_path}")
    except:
        return 0

    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(img)

    if bbox is not None:
        return data
    
    return 0


def main():
    path = '1083312661.png'
    data = qr_data(path)
    print(data)
    if data:
        print(f'QR-code data:\n{data}')
    else:
        print('Cannot recognize')
    


if __name__ == '__main__':
    main()
