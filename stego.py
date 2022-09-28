import cv2, numpy as np

def to_bin(data):
    """Convert `data` to binary format as string"""
    if isinstance(data, str):
        return ''.join([ format(ord(i), "08b") for i in data ])
    elif isinstance(data, bytes) or isinstance(data, np.ndarray):
        return [ format(i, "08b") for i in data ]
    elif isinstance(data, int) or isinstance(data, np.uint8):
        return format(data, "08b")
    else:
        raise TypeError("Type not supported.")

def encode(image_name, secret_data):
    image = cv2.imread(image_name) # read the image
    print ("Shape is ", image.shape)
    n_bytes = image.shape[0] * image.shape[1] * 3 // 8 # maximum bytes to encode
    print("[*] Maximum bytes to encode:", n_bytes)
    secret_data += "=====" # add stopping criteria
    if len(secret_data) > n_bytes:
        raise ValueError("[!] Insufficient bytes, need bigger image or less data.")
    print("[*] Encoding data...")
    
    data_index = 0
    binary_secret_data = to_bin(secret_data) # convert data to binary
    data_len = len(binary_secret_data) # size of data to hide
    for row in image:
        for pixel in row:
            r, g, b = to_bin(pixel) # convert RGB values to binary format
            if data_index < data_len: # modify the least significant bit only if there is still data to store
                pixel[0] = int(r[:-1] + binary_secret_data[data_index], 2) # least significant red pixel bit
                data_index += 1
            if data_index < data_len:
                pixel[1] = int(g[:-1] + binary_secret_data[data_index], 2) # least significant green pixel bit
                data_index += 1
            if data_index < data_len:
                pixel[2] = int(b[:-1] + binary_secret_data[data_index], 2) # least significant blue pixel bit
                data_index += 1
            if data_index >= data_len: # if data is encoded, just break out of the loop
                break
    return image

def decode(image_name):
    print("[+] Decoding...")
    # read the image
    image = cv2.imread(image_name)
    binary_data = ""
    for row in image:
        for pixel in row:
            r, g, b = to_bin(pixel)
            binary_data += r[-1]
            binary_data += g[-1]
            binary_data += b[-1]
    # split by 8-bits
    all_bytes = [ binary_data[i: i+8] for i in range(0, len(binary_data), 8) ]
    # convert from bits to characters
    decoded_data = ""
    for byte in all_bytes:
        decoded_data += chr(int(byte, 2))
        if decoded_data[-5:] == "=====": # we keep decoding until we see the stopping criteria.
            break
    return decoded_data[:-5]

""" if __name__ == "__main__":
    input_image = "pokemon.PNG"
    output_image = "stego_pokemon.PNG"
    secret_data = open("payload2.txt","r")
    data = secret_data.read()
    # encode the data into the image
    encoded_image = encode(image_name=input_image, secret_data=data)
    secret_data.close()
    # save the output image (encoded image)
    cv2.imwrite(output_image, encoded_image)
    # decode the secret data from the image
    decoded_data = decode(output_image)
    print("[+] Decoded data:", decoded_data) """