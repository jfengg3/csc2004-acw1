from tkinter import E
import os
import cv2
import numpy as np

import filestream


# Works with PNG only.


def to_bin(data):
    "Convert `data` to binary format as string"
    if isinstance(data, str):
        return ''.join([format(ord(i), "08b") for i in data])
    elif isinstance(data, bytes):
        return [format(i, "08b") for i in data]
    elif isinstance(data, np.ndarray):
        # Convert elements in np.ndarray to binary format
        return np.vectorize(np.binary_repr)(data, 8)
    elif isinstance(data, int) or isinstance(data, np.uint8):
        return format(data, "08b")
    # For formatting image width and height
    elif isinstance(data, np.uint16):
        return format(data, "016b")
    else:
        raise TypeError("Type not supported.")


def bin_to_decimal(n) -> int:
    return int(n, 2)


def png_max_bytes(image: cv2.Mat, num_lsbs) -> int:
    return image.shape[0] * image.shape[1] * 3 * num_lsbs // 8


def encode_png(source, payload, dest,num_lsbs):
    # error checking, and checking if file exists
    print('[*] Cover image URI is:', source, 'using', num_lsbs, 'bits.')
    if not os.path.exists(source):
        print(
            '[!] Source file does not exist, only .png files are accepted for encoding')
        return 1
    # Temp variable. Used here to cache number of bytes in the payload.
    payload_bytes = 0
    # check if payload is a file or plaintext
    if os.path.exists(payload):
        format_id = filestream.format_identifier(payload[-5:])
        # For encoding pngs
        if format_id == '0010':
            # convert file's bytestream to binary stream, at the same time appending file type identifier
            # bin_payload = png_to_bits(payload, num_lsbs)
            bin_payload = np.append(
                np.array([0, 0, 1, 0]), png_to_bits(payload, num_lsbs))
            # For payload byte size check
            payload_bytes = png_max_bytes(cv2.imread(payload), num_lsbs)
        else:
            # convert file's bytestream to binary stream, at the same time appending file type identifier
            bin_payload = filestream.get_stream(payload)
            # Append delimiter A5= to payload
            bin_payload += to_bin('A5=')
            payload_bytes = len(bin_payload) // 8
    else:
        print('[*] Payload is not a file, encoding as plaintext')
        # Append delimiter A5= to payload
        payload += "A5="
        # Convert payload to binary
        bin_payload = to_bin(payload)
        payload_bytes = len(bin_payload) // 8

    # Encode into png
    # read the image
    cover_img = cv2.imread(source)
    # maximum bytes to encode
    encoding_space_bytes = png_max_bytes(cover_img, num_lsbs)

    if payload_bytes > encoding_space_bytes:
        print(
            '[!] Payload size too large for cover .png file, please use something smaller')
        raise Exception("! Payload is larger than file!")

    payload_index = 0

    # size of data to hide
    data_len = len(bin_payload)
    for bit_index in range(1, num_lsbs + 1, 1):
        # print("encoding, bit_index: ", bit_index, num_lsbs + 1)
        for row in cover_img:
            for pixel in row:
                # convert RGB values to binary format
                r, g, b = to_bin(pixel)
                # print(type(pixel), pixel)
                # Modify current LSB of red pixel bit, only if there's still data left to store
                if payload_index < data_len:
                    # Replaces the bit_index-th element from the end of the colour value byte (goes backwards).
                    # If condition because if bit_index is 1, we dont want to add anything at the end.
                    pixel[0] = int("".join(
                        (r[:-bit_index], bin_payload[payload_index], "" if (-bit_index+1 == 0) else r[-bit_index+1:])), base=2)
                    payload_index += 1

                # Modify current LSB of green pixel bit, only if there's still data left to store
                if payload_index < data_len:
                    pixel[1] = int("".join(
                        (g[:-bit_index], bin_payload[payload_index], "" if (-bit_index+1 == 0) else g[-bit_index+1:])), base=2)
                    payload_index += 1

                # Modify current LSB of blue pixel bit, only if there's still data left to store
                if payload_index < data_len:
                    pixel[2] = int("".join(
                        (b[:-bit_index], bin_payload[payload_index], "" if (-bit_index+1 == 0) else b[-bit_index+1:])), base=2)
                    payload_index += 1

                # if data is encoded, just break out of the loop
                if payload_index >= data_len:
                    break
            # if data is encoded, just break out of the loop
            if payload_index >= data_len:
                break
        # if data is encoded, just break out of the loop
        if payload_index >= data_len:
            break

    cv2.imwrite(dest, cover_img)
    # print("payload encoded: ", payload_index, data_len)
    return 0


def decode_png(source, dest, num_lsbs, decodeformat='file'):
    print('[*] Attempting to decode:', source, 'using', num_lsbs, 'bits.')
    # Store decoded characters to see the delimiter
    prevprev_char = ''
    prev_char = ''
    current_char = ''

    if not os.path.exists(source):
        print('[!] Source file', source,
              'does not exist, only .png files are accepted for decoding')
        return
    print('[*] Decoding...')
    # Read image from specified file
    steg_img: cv2.Mat = cv2.imread(source)
    img_width = 0
    img_height = 0
    img_size = 0
    decoded_bin_stream = ""
    decoded_string = ''
    bin_index = 0
    for bit_index in range(1, num_lsbs + 1, 1):
        for row in steg_img:
            for pixel in row:
                # Loop through the pixels and decode to r, g, b
                r, g, b = to_bin(pixel)
                decoded_bin_stream += r[-bit_index]
                decoded_bin_stream += g[-bit_index]
                decoded_bin_stream += b[-bit_index]

    if decodeformat == 'file':
        # slice out the front 4 bits first to identify format
        decoded_string = decoded_bin_stream[:4]
        # png only
        if decoded_string == '0010':
            decoded_bin_stream = decoded_bin_stream[4:]
            # Extract img_height
            img_height = decoded_bin_stream[:16]
            decoded_bin_stream = decoded_bin_stream[16:]
            # Extract img_width
            img_width = decoded_bin_stream[:16]
            decoded_bin_stream = decoded_bin_stream[16:]
            # Convert to int
            img_width = bin_to_decimal(img_width)
            img_height = bin_to_decimal(img_height)
            # Compute img_size
            img_size = img_width * img_height * 3 * num_lsbs
            # Trim excess
            decoded_bin_stream = decoded_bin_stream[:img_size]

            # # Synch with teammate: don't rebuild using cv2, do this:
            # # format as byte representation
            # decoded_bin_stream = [decoded_bin_stream[index: index + 8]
            #                       for index in range(0, len(decoded_bin_stream), 8)]
            # # Generate file from stream
            # extension = filestream.generate_from_stream(
            #     decoded_string, "decoded_file.png")   # generate file from
            # return extension

            # rebuild png.
            # Counter to track index in bin_stream
            bin_index = 0
            decoded_data: np.ndarray = np.zeros(
                (img_width, img_height, 3), np.uint8)
            # Loop through bin stream.
            for bit_index in range(7, 7 - num_lsbs, -1):
                # Plane of RGB pixels. For each row in the plane,
                for row in range(decoded_data.shape[0]):
                    # For each RGB pixel in a row,
                    for pixel in range(decoded_data.shape[1]):
                        # For red, green, blue pixels,
                        for rgb in range(decoded_data.shape[2]):
                            # For each bit, create a uint8. Slot the bit into the correct MSB location, then return the completed np.array
                            decoded_data[row, pixel, rgb] = decoded_data[row, pixel, rgb] | (
                                (int(decoded_bin_stream[bin_index]) << bit_index))
                            bin_index = bin_index + 1
            extension = ".\\decoded\\decoded_image.png"
            cv2.imwrite(extension, decoded_data)
            return extension
        else:
            # slice out the front 4 bits first to identify format
            decoded_string = decoded_bin_stream[:4]
            # extract data starting from 4th bit, as 1-4 is for identifier
            decoded_bin_stream = decoded_bin_stream[4:]
            # format as byte representation
            decoded_bin_stream = [decoded_bin_stream[index: index + 8]
                                  for index in range(0, len(decoded_bin_stream), 8)]
            for byte in decoded_bin_stream:
                val = int(byte, 2)                  # convert byte to int
                # convert int to ascii characters
                current_char = format(val, 'c')
                if prevprev_char == 'A' and prev_char == '5' and current_char == '=':   # identify stop code A5=
                    # trim off stop code
                    decoded_string = decoded_string[:-16]
                    break
                prevprev_char = prev_char       # update previous char for stop code identification
                prev_char = current_char        # update previous char for stop code identification
                decoded_string += byte
            extension = filestream.generate_from_stream(
                decoded_string, dest)   # generate file from
            return extension
    else:
        # Decoding plaintext string in png file, no need for first 4 bit file identifier
        decoded_bin_stream = [decoded_bin_stream[index: index + 8]
                              for index in range(0, len(decoded_bin_stream), 8)]
        for byte in decoded_bin_stream:
            val = int(byte, 2)
            if 31 < val < 128:
                current_char = format(val, 'c')
                if prevprev_char == 'A' and prev_char == '5' and current_char == '=':
                    decoded_string = decoded_string[:-2]
                    break
                prevprev_char = prev_char
                prev_char = current_char
                decoded_string += current_char

        with open(dest, 'w') as newfile:
            newfile.write(decoded_string)
            newfile.close()
        print('[*] Successfully decoded and exported to')
        return decoded_string


def png_to_bits(payload, num_lsbs: int) -> np.ndarray:
    # check if payload is a png. Ignore if it isn't.
    if os.path.exists(payload) is False:
        raise ValueError(
            "[!] Payload not found!")

    payload_img = cv2.imread(payload)

    # convert data to binary. to_bin converts numbers inside to binary. flatten makes it 1D.
    # payload_binary, an np.ndarray, contains binary strings.
    payload_binary = np.ndarray.flatten(to_bin(payload_img))

    # Initialise the payload_bits array with the image height, then image width.
    # Convert image height and width into uint16 before adding to payload_bits.
    payload_bits = np.append(np.array([x for x in to_bin(np.uint16(payload_img.shape[0]))]), [
        x for x in to_bin(np.uint16(payload_img.shape[1]))])

    # Now get MSBs of each binary nums, and append them to payload_bits.
    for bit_index in range(0, num_lsbs, 1):
        for x in payload_binary:
            payload_bits = np.append(payload_bits, x[bit_index])

    # Return the bits of the png.
    return payload_bits
