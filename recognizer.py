from pyzbar.pyzbar import decode
from PIL import Image

def qr_data(img_path):
    try:
        result = decode(Image.open(img_path))
        result = result[0].data.decode("utf-8")
        print(result)
        return result
    except:
        return 0


def main():
    path = 'QR/qr1.png'
    data = qr_data(path)
    print(data)
    if data:
        print(f'QR-code data:\n{data}')
    else:
        print('Cannot recognize')
    


if __name__ == '__main__':
    main()
