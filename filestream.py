from pydub import AudioSegment


# FILE FORMATS (first 4 bits only)
# 0000 = .jpg
# 0001 = .jpeg
# 0010 = .png
# 0011 = .bmp
# 0100 = .wav
# 0101 = .mp3
# 0110 = .mp4
# 0111 = .pdf
# 1000 = .docx
# 1001 = .csv
# 1010 = .txt

def format_identifier(data):
    # conversions for 4-bit strings
    if data == '0000':
        return '.jpg'
    if data == '0001':
        return '.jpeg'
    if data == '0010':
        return '.png'
    if data == '0011':
        return '.bmp'
    if data == '0100':
        return '.wav'
    if data == '0101':
        return '.mp3'
    if data == '0110':
        return '.mp4'
    if data == '0111':
        return '.pdf'
    if data == '1000':
        return '.docx'
    if data == '1001':
        return '.csv'
    if data == '1010':
        return '.txt'

    # conversions for extension strings
    if data[0] != '.':  # check if it is a 4char or 3char extension
        data = data[1:]
    if data == '.jpg':
        return '0000'
    if data == '.jpeg':
        return '0001'
    if data == '.png':
        return '0010'
    if data == '.bmp':
        return '0011'
    if data == '.wav':
        return '0100'
    if data == '.mp3':
        return '0101'
    if data == '.mp4':
        return '0110'
    if data == '.pdf':
        return '0111'
    if data == '.docx':
        return '1000'
    if data == '.csv':
        return '1001'
    if data == '.txt':
        return '1010'

    return


def get_stream(source):
    # get stream as 8-bit string
    identifier = format_identifier(source[-5:])
    bitstring = identifier
    file = open(source, 'rb')
    byte = file.read(1)
    print('[*] Extracting bits from bytestream...')
    while byte:
        bitstring += format(byte[0], "08b")
        byte = file.read(1)
    # get stream as 8-bit array
    # bitarray = []
    # while byte:
    #     bitarray.append(bin(byte[0]))
    #     byte = file.read(1)
    # print(bitarray)

    # get stream as bytearray
    # bitarray = bytearray()
    # while byte:
    #     bitarray.append(byte[0])
    #     byte = file.read(1)
    #
    # file.close()
    # print(bitarray)
    return bitstring

    # function to generate a file from file stream


def generate_from_stream(data, dest):
    # error checking and file URI matching / correction
    identifier = data[:4]     # get encoded format identifier
    extension = format_identifier(identifier)
    if extension != dest[-(len(extension)):]:
        print(
            '[*] destination file format and decoded format mismatch, correcting extension...')
        dest += extension   # apply error correction

    # slice out format identifier to get actual file stream
    datastream = data[4:]
    # split data into byte-sized bites
    datastream = [datastream[index: index + 8]
                  for index in range(0, len(datastream), 8)]
    # convert bitstring into int array
    datastream = [int(index, 2) for index in datastream]
    # convert int array into bytearary, to be used as writable file stream
    datastream = bytearray(datastream)

    # write to file destination
    file = open(dest, "wb")
    file.write(datastream)
    file.close
    return extension


if __name__ == '__main__':
    # imgstream = get_stream('./cover_assets/iloverocks.jpg')
    # wavstream = get_stream('./cover_assets/audio.wav')
    # generate_from_stream(imgstream, './cover_assets/ihaterocks.jpg')
    # generate_from_stream(wavstream, './cover_assets/ilovethisaudio.jpg') # testing for wrong extension
    txtstream = get_stream('./payload_assets/test.txt')
    generate_from_stream(txtstream, './results/testgen.txt')