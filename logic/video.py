import cv2, numpy as np
import os
import shutil
from subprocess import call, STDOUT
import filestream


class VideoCoder:
    def __init__(self):
        self.source = ''
        self.payload = ''
        self.dest = ''

    def convert_to_bin(self, data):
        #Convert 'data' to binary format as string
        if isinstance(data, str):
            return ''.join([ format(ord(i), "08b") for i in data ])
        elif isinstance(data, bytes) or isinstance(data, np.ndarray):
            return [ format(i, "08b") for i in data ]
        elif isinstance(data, int) or isinstance(data, np.uint8):
            return format(data, "08b")
        else:
            raise TypeError("Type not supported.")

    
    def limit_check(self, payload, cover_length, bitRange):
        payload_length = len(payload)
        print('Payload length:', payload_length)
        print('Cover length:', cover_length)
        if(payload_length > (cover_length * bitRange)):
            return 1
        return 0


    def extract_frames(self, videoName):
        if not os.path.exists("./temp"):
            os.makedirs("temp")
        print("[INFO] temp directory created")

        #Loads video and capture it's frames
        vidframecap = cv2.VideoCapture(videoName)
        #Create a loop to capture all frames then save each to unique filename for sorting later on
        framesgenerated = 0
        while True:
            success, image = vidframecap.read()
            if not success:
                break
            cv2.imwrite(os.path.join("./temp", "frame{:d}.png".format(framesgenerated)), image)
            framesgenerated += 1

        return framesgenerated

    def clean(self, path):
        if os.path.exists("./" + path):
            shutil.rmtree("./" + path)
            print("[INFO] " + path + " files cleaned up")

    def encode_video( self, videoName, secretData, dest, bitRange):

        framecount = self.extract_frames(videoName)
        #Check total number of frames generated
        print("Total Number of Frames Generated from Video:", framecount)
        totalbytes = 0

        # check if payload is a file or plaintext
        if os.path.exists(secretData):
            # convert file's bytestream to binary stream, at the same time appending file type identifier
            binarysecretdata = filestream.get_stream(secretData)
            binarysecretdata += self.convert_to_bin('A5=')
        else:
            print('[*] Payload is not a file, encoding as plaintext')
            # Convert payload to binary
            secretData += "A5="
            binarysecretdata = self.convert_to_bin(secretData) 

        totalbytes = 0
        #Checking if there is sufficient bytes in video to encode data
        for frame in range(0, framecount, 1):
            framepath = (os.path.join("./temp", "frame{:d}.png".format(frame)))
            image = cv2.imread(framepath)  #Read the image
            totalbytes += image.shape[0] * image.shape[1] * 3 // 8  #Maximum bytes to encode
        print("[*] Bytes available for encoding:", totalbytes)
        
        Allbytes = [binarysecretdata[index: index + 8] for index in range(0, len(binarysecretdata), 8)]
        if self.limit_check(Allbytes, totalbytes, bitRange):
            print('[!] Payload size too large for cover, please use something smaller')
            raise Exception("! Payload is larger than file !")
        else:
            print("[*] Sufficient bytes to encode data of bytes")
        
        #Extract audio from video
        call(["ffmpeg", "-i", videoName, "-q:a", "0", "-map", "a", "temp/audio.mp3", "-y"], stdout=open(os.devnull, "w"), stderr=STDOUT)

        #Start encoding process
        dataencoded = False
        iterations = 1
        dataindex = 0
        datalen = len(binarysecretdata) #Size of data to hide
        pixelarray = np.zeros((1,3))

        while dataencoded == False:
            for frame in range(0, framecount, 1):
                framepath = (os.path.join("./temp", "frame{:d}.png".format(frame)))
                image = cv2.imread(framepath)  #Read the image

                print("[*] Encoding data...")
                if dataindex < datalen:
                    for row in image:
                        if np.isin(np.array(row), np.array(pixelarray)).all():
                            continue #All pixels in row is already encoded with data, go next row

                        i = 1
                        for pixel in row:
                            if i < iterations:
                                i += 1
                                continue

                            r, g, b = self.convert_to_bin(pixel) #Convert RGB values to binary format
                            if dataindex < datalen: #Modify the red pixel bits depending on bitRange only if there is still data to store
                                if (datalen - dataindex) < bitRange: #If data left to store is less than the bitRange, left shift the data accordingly then store so that it can be decoded correctly later
                                    pixel[0] = int(r[:-bitRange] + self.convert_to_bin(int(binarysecretdata[dataindex:(dataindex + (datalen - dataindex))]) << (bitRange-(datalen-dataindex))), 2)
                                    dataindex += (datalen - dataindex)
                                else:
                                    pixel[0] = int(r[:-bitRange] + binarysecretdata[dataindex:(dataindex + bitRange)], 2)
                                    dataindex += bitRange
                            if dataindex < datalen: #Modify the green pixel bits depending on bitRange only if there is still data to store
                                if (datalen - dataindex) < bitRange: #If data left to store is less than the bitRange, left shift the data accordingly then store so that it can be decoded correctly later
                                    pixel[1] = int(g[:-bitRange] + self.convert_to_bin(int(binarysecretdata[dataindex:(dataindex + (datalen - dataindex))]) << (bitRange-(datalen-dataindex))), 2)
                                    dataindex += (datalen - dataindex)
                                else:
                                    pixel[1] = int(g[:-bitRange] + binarysecretdata[dataindex:(dataindex + bitRange)], 2)
                                    dataindex += bitRange
                            if dataindex < datalen: #Modify the blue pixel bits depending on bitRange only if there is still data to store
                                if (datalen - dataindex) < bitRange: #If data left to store is less than the bitRange, left shift the data accordingly then store so that it can be decoded correctly later
                                    pixel[2] = int(b[:-bitRange] + self.convert_to_bin(int(binarysecretdata[dataindex:(dataindex + (datalen - dataindex))]) << (bitRange-(datalen-dataindex))), 2)
                                    dataindex += (datalen - dataindex)
                                else:
                                    pixel[2] = int(b[:-bitRange] + binarysecretdata[dataindex:(dataindex + bitRange)], 2)
                                    dataindex += bitRange
                            print("Data encoded in Frame " + str(frame))

                            pixelarray = np.append(pixelarray, [pixel], axis=0)

                            if dataindex >= datalen: #If data is encoded, just break out of the Loop
                                dataencoded = True #All data encoded, change variable to True to end While Loop
                                break

                            if len(row) + 1 == iterations:  # If all pixels in a row of a frame is encoded, go next row
                                iterations = 0

                            if frame + 1 == framecount: #All frames have that certain pixel encoded e.g. 1st pixel)
                                if len(row) + 1 == iterations: #If last pixels of the row encoded
                                    iterations = 1 #Restart the iteration variable
                                elif len(row) + 1 > iterations: #If not all pixels of the row encoded
                                    iterations += 1 #The loop restarts from first frame and now encode the next pixel available

                            break
                        break
                cv2.imwrite(os.path.join("./temp", "frame{:d}.png".format(frame)), image) #Replace old frame with new frame
                if dataindex >= datalen: #If data is encoded, just break out of the Loop
                    break
                #If not all data encoded, program will continue looping
     
        call(["ffmpeg", "-i", "temp/frame%d.png", "-vcodec", "png", "./temp/noAudioStegoVid.avi", "-y"], stdout=open(os.devnull, "w"), stderr=STDOUT)
        call(["ffmpeg", "-i", "temp/noAudioStegoVid.avi", "-i", "./temp/audio.mp3", "-codec", "copy", "temp/audioStegoVid.avi", "-y"], stdout=open(os.devnull, "w"), stderr=STDOUT)
        call(["ffmpeg", "-i", "temp/audioStegoVid.avi", "-f", "avi", "-c:v", "rawvideo", "-pix_fmt", "rgb32", dest], stdout=open(os.devnull, "w"), stderr=STDOUT)
        self.clean("temp")

    def decode_video(self, videoName, dest, bitRange, decodeformat='file'):
        framecount = self.extract_frames(videoName)

        #Check total number of frames generated
        print("Total Number of Frames Generated from Video:", framecount)

        datadecoded = False
        iterations = 1
        binarydata = ""
        pixelarray = np.zeros((1, 3))
        while datadecoded == False:
            for frame in range(0, framecount, 1):
                framepath = (os.path.join("./temp", "frame{:d}.png".format(frame)))
                image = cv2.imread(framepath)  #Read the image

                print("[+] Decoding...")
                for row in image:
                    if np.isin(np.array(row), np.array(pixelarray)).all():
                        continue  #All pixels in row is already encoded with data, go next row

                    i = 1
                    for pixel in row:
                        if i < iterations:
                            i += 1
                            continue

                        r, g, b = self.convert_to_bin(pixel)
                        binarydata += r[-bitRange:]
                        binarydata += g[-bitRange:]
                        binarydata += b[-bitRange:]

                        pixelarray = np.append(pixelarray, [pixel], axis=0)

                        if frame + 1 == framecount:  # All frames have that certain pixel encoded e.g. 1st pixel)
                            if len(row) + 1 == iterations:  # If last pixels of the row encoded
                                iterations = 1  # Restart the iteration variable
                            elif len(row) + 1 > iterations:  # If not all pixels of the row encoded
                                iterations += 1  # The loop restarts from first frame and now encode the next pixel available

                        break
                    break
            
            #Convert from bits to characters
            decoded_string = ''
            prevprev_char = ''
            prev_char = ''
            current_char = ''

            if decodeformat == 'file':
                # slice out the front 4 bits first to identify format
                decoded_string = binarydata[:4]
                # extract data starting from 4th bit, as 1-4 is for identifier
                decoded_bin = binarydata[4:]
                # format as byte representation
                decoded_bin = [decoded_bin[index: index + 8]
                            for index in range(0, len(decoded_bin), 8)]
                for byte in decoded_bin:
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
                    datadecoded = True
                extension = filestream.generate_from_stream(decoded_string, dest)   # generate file from
                return extension
            else:
                # Decoding plaintext string in audio file, no need for first 4 bit file identifier
                decoded_bin = [decoded_bin[index: index + 8]
                            for index in range(0, len(decoded_bin), 8)]
                for byte in decoded_bin:
                    val = int(byte, 2)
                    if 31 < val < 128:
                        current_char = format(val, 'c')
                        if prevprev_char == 'A' and prev_char == '5' and current_char == '=':
                            decoded_string = decoded_string[:-2]
                            break
                        prevprev_char = prev_char
                        prev_char = current_char
                        decoded_string += current_char
            

        self.clean("temp")
        with open(dest, 'w') as newfile:
            newfile.write(decoded_string)
            newfile.close()

""" def main():
    VideoCoder.encode_video(VideoCoder(),"payload_mp4.mp4", "payload2.txt", 6)
    VideoCoder.decode_video(VideoCoder(), "results/aviResult.avi", 6) """

""" if __name__ == '__main__':
    main() """