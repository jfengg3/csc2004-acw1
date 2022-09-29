from PIL import Image
import sys
from filestream import format_identifier, get_stream
from bitarray import bitarray


class Encoder:
    def __init__(self, imageUrl):
        self.originalArr = []
        self.resultArr = []
        image = Image.open(imageUrl)
        self.width = image.width
        self.height = image.height
        self.size = self.width * self.height
        self.bitNumber = 1

        self.tail = "0011101010001001010010011100101101101001100000010001010011101011011100111000011000000010100111001011110100001000000001010111000001011100010111010110101111011001101101001111100110111110100101001100111110101110010111101111100100010111011101111100010110001101"
        pixel = image.load()

        print("***** Encoder *****")
        # convert image to bits
        intValue = list(image.getdata())
        for i in range(len(intValue)):
            red = format(intValue[i][0], "08b")
            green = format(intValue[i][1], "08b")
            blue = format(intValue[i][2], "08b")
            self.originalArr.append([red, green, blue])

        # save to file for debug
        # print("Saving to data text")
        # file = open('./results/img/data.txt', 'w')
        #
        # for elements in self.originalArr:
        #     for data in elements:
        #         file.write(data + "  ")
        #     file.write("\n")
        #
        # file.close()

    def wrapPayload(self, payload):
        print("* Wrapping Payload")
        # add tail
        tail = self.tail
        fullPayload = payload + tail
        return fullPayload

    def setPayload(self, payload):
        # add header and tail
        fullPayload = self.wrapPayload(payload)
        # calls self.checkPayload()
        check = self.checkPayload(len(fullPayload))
        # returns binary string array

        if(check == True):
            print("* Payload Size Check: PASSED")
            return fullPayload
        else:
            raise Exception("! Payload is larger than file !")
            sys.exit("! Payload is larger than file !")

    def checkPayload(self, payloadLength):
        # returns True or False
        bitNumber = self.bitNumber
        size = self.size

        if(bitNumber == 1 and (size*3) > payloadLength):
            return True
        elif(bitNumber == 2 and payloadLength < (size*6)):
            return True
        elif(bitNumber == 3 and payloadLength < (size*9)):
            return True
        elif(bitNumber == 4 and payloadLength < (size*12)):
            return True
        elif(bitNumber == 5 and payloadLength < (size*15)):
            return True
        elif(bitNumber == 6 and payloadLength < (size*18)):
            return True
        elif(bitNumber == 7 and payloadLength < (size*21)):
            return True
        elif(bitNumber == 8 and payloadLength < (size*24)):
            return True
        else:
            return False

    def setBitNumber(self, bitNumber):
        self.bitNumber = bitNumber

    def encode(self, userInput):
        counter = 0
        color = 0
        i = 0
        payload = self.setPayload(userInput)
        bitNumber = self.bitNumber
        pixArr = self.originalArr
        print("* Encoding...")

        while(i < len(payload)):
            # modify red bit
            if(color == 0):
                temp = pixArr[counter][0][:-bitNumber]
                for j in range(bitNumber):
                    if((i+j) < len(payload)):
                        temp += payload[i+j]
                    else:
                        temp += "0"
                pixArr[counter][0] = temp
                i += bitNumber
                color += 1

            # modify green bit
            elif(color == 1):
                temp = pixArr[counter][1][:-bitNumber]
                for j in range(bitNumber):
                    if((i+j) < len(payload)):
                        temp += payload[i+j]
                    else:
                        temp += "0"
                pixArr[counter][1] = temp
                i += bitNumber
                color += 1

            # modify blue bit
            elif(color == 2):
                temp = pixArr[counter][2][:-bitNumber]
                for j in range(bitNumber):
                    if((i+j) < len(payload)):
                        temp += payload[i+j]
                    else:
                        temp += "0"
                pixArr[counter][2] = temp
                i += bitNumber
                color = 0
                counter += 1

        # return pixArr
        self.resultArr = pixArr
        print("* Encoding Successful")

    def generateNewPic(self, saveUrl):
        print("* Saving to new image")
        pixArr = self.resultArr
        temp = []
        for i in range(len(pixArr)):
            red = int(pixArr[i][0], 2)
            green = int(pixArr[i][1], 2)
            blue = int(pixArr[i][2], 2)
            temp.append((red, green, blue))

        result = Image.new('RGB', (self.width, self.height))
        result.putdata(temp)
        result.save(saveUrl)
        print("***** Done Encoding! *****\n")

    def writeText(self):
        file = open('./results/img/data2.txt', 'w')

        for elements in self.resultArr:
            for data in elements:
                file.write(data + "  ")
            file.write("\n")

        file.close()


class Decoder:
    def __init__(self, url):
        image = Image.open(url)
        self.rawData = list(image.getdata())
        self.tail = "0011101010001001010010011100101101101001100000010001010011101011011100111000011000000010100111001011110100001000000001010111000001011100010111010110101111011001101101001111100110111110100101001100111110101110010111101111100100010111011101111100010110001101"
        print("***** Decoder *****")

    def getFileType(self):
        if self.payloadData:
            self.fileType = format_identifier(self.payloadData[:4])
            print(f'* Detected File Type: {self.fileType}')
            return self.fileType
        return None

    def setBitNumber(self, bitNumber):
        self.bitNumber = bitNumber

    def readPayload(self):
        print("* Reading Payload")
        bitNum = self.bitNumber
        newArray = ''
        for i in self.rawData:
            newArray += (bin(i[0])[2:].zfill(8)[-bitNum:] + bin(i[1])
                         [2:].zfill(8)[-bitNum:] + bin(i[2])[2:].zfill(8)[-bitNum:])
        self.payloadData = newArray.split(self.tail)[0]
        self.getFileType()

    def extractEmbeddedToFile(self):
        print(f"* Writing to file as output")
        binNum = bitarray(self.payloadData[4:]).tobytes()
        file = open(f'res/output/output.txt', 'wb')
        print('output found at')
        file.write(binNum)
        file.close()
        print("***** Done Decoding! *****\n")
        return self.fileType

if __name__ == '__main__':
    """ test = Encoder("res/input/photo.jpg")
    test.setBitNumber(3)
    test.encode(get_stream("res/input/payload2.txt"))
    test.generateNewPic("res/output/hihi.png") """
    test = Decoder("res/output/hihi.png")
    test.setBitNumber(3)
    test.readPayload()
    test.extractEmbeddedToFile()