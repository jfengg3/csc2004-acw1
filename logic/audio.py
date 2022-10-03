import os
import sys
import wave
import numpy as np
from pydub import AudioSegment
import filestream

def to_bin(data):
        # Convert 'data' to binary format as String
        if isinstance(data, str):
            return ''.join([format(ord(i), "08b") for i in data])
        elif isinstance(data, bytes) or isinstance(data, np.ndarray):
            return [format(i, "08b") for i in data]
        elif isinstance(data, int) or isinstance(data, np.uint8):
            return format(data, "08b")
        else:
            raise TypeError("Type is not supported.")

def limit_check(payload, cover_frames, bitrange):
        payload_length = len(payload)
        cover_length = len(cover_frames)
        print('Payload length:', payload_length)
        print('Cover length:', cover_length)
        if(payload_length > (cover_length * bitrange)):
            return 1
        return 0

def convert_audio(source, dest):
        
        print('[*] Converting', source[-3:], 'to', dest[-3:], '...')
        if source[-4:] == '.mp3':       # check if its a mp3 file, if it is, then convert to wav
            AudioSegment.from_mp3(source).export(dest, format=dest[-3:])
            return
        if source[-4:] == '.wav':
            AudioSegment.from_mp3(source).export(dest, format=dest[-3:])
        return

def encode_audio(source, dest, payload, bitrange):
        # error checking, and checking if file exists
        print('[*] Cover image URI is:', source, 'using', bitrange, 'bits.')
        if source[-4:] != '.wav':
            # convert mp3 to wav
            if source[-4:] == '.mp3':
                # convert current mp3 source into wav, as this method expects source to be of .wav type
                source_mp3 = source
                source = source[:-4]
                source += '.wav'
                # convert mp3 to wav
                convert_audio(source_mp3, source)
            else:
                print('[!] Only .wav and .mp3 files are supported.')
                return
        if dest[-4:] != '.wav':
            dest += '.wav'
        if not os.path.exists(source):
            print(
                '[!] Source file does not exist, only .wav files are accepted for encoding')
            return 1
        # check if payload is a file or plaintext
        if os.path.exists(payload):
            # convert file's bytestream to binary stream, at the same time appending file type identifier
            bin_payload = filestream.get_stream(payload)
            # Append delimiter A5= to payload
            bin_payload += to_bin('A5=')
        else:
            print('[*] Payload is not a file, encoding as plaintext')
            # Append delimiter A5= to payload
            payload += "A5="
            # Convert payload to binary
            bin_payload = to_bin(payload)

        song = wave.open(source, 'rb')      # open audio file
        # Get all frames in wav
        # read all frames and store them
        frames = song.readframes(song.getnframes())
        # Do limit checking
        if limit_check(bin_payload, frames, bitrange):
            print(
                '[!] Payload size too large for cover .wav file, please use something smaller')
            raise Exception("! Payload is larger than file !")
        print('[*] Encoding...')
        frames = list(frames)
        # convert frames into bytearrays to work with
        frames = bytearray(frames)

        # apply payload padding
        # Split the payload into specified bitrange slices
        bin_payload = [bin_payload[index: index + bitrange]
                       for index in range(0, len(bin_payload), bitrange)]

        # set bitmask clear to specified bitranges
        bitmask = 0
        for i in range(0, bitrange):
            bitmask += 1 << i
        # convert bitmask integer into bytearray
        bitmask = bitmask.to_bytes(1, byteorder=sys.byteorder)
        # get first index of bytearray, as there is no use for lists
        bitmask = bitmask[0]

        # embed payload into frames, payload slices determined by bitrange specified
        for i, bits in enumerate(bin_payload):
            # if binary slice is not the specified bitrange length (usually happens to the last bit), add trailing 0s
            if len(bits) < bitrange:
                bits = bits.ljust(bitrange, '0')
            # clear specified number of bits, and set bits according to payload
            frames[i] = (frames[i] & ~bitmask) | int(bits, 2)
        # convert bytearray into bytes, the format to write to a wav file
        modded_frames = bytes(frames)
        # write to a wav file on specified destination
        with wave.open(dest, 'wb') as newfile:
            # ensure that song properties are maintained
            newfile.setparams(song.getparams())
            # write the embedded audio file
            newfile.writeframes(modded_frames)
            newfile.close()
        song.close()
        return 0

def decode_audio(source, dest, bitrange,decodeformat='file'):
        print('[*] Attempting to decode:', source, 'using', bitrange, 'bits.')
        # Store decoded characters to see the delimiter
        prevprev_char = ''
        prev_char = ''
        current_char = ''

        if source[-4:] != '.wav':
            # convert mp3 to wav
            if source[-4:] == '.mp3':
                # convert current mp3 source into wav, as this method expects source to be of .wav type
                source_mp3 = source
                source = source[:-4]
                source += '.wav'
                # convert mp3 to wav
                convert_audio(source_mp3, source)

        if not os.path.exists(source):
            print('[!] Source file', source,
                  'does not exist, only .wav and .mp3 files are accepted for decoding')
            return
        # Read frames from specified file
        print('[*] Decoding...')
        song = wave.open(source, 'rb')              # open audio file
        # read frames from audio file
        frames = song.readframes(song.getnframes())
        # convert frames into byte arrays for manipulation
        frames = bytearray(frames)
        decoded_bin = ''
        decoded_string = ''
        for byte in frames:
            # extract out bytearray into binary strings
            decoded_bin += to_bin(byte)[-bitrange:]

        if decodeformat == 'file':
            # slice out the front 4 bits first to identify format
            decoded_string = decoded_bin[:4]
            # extract data starting from 4th bit, as 1-4 is for identifier
            decoded_bin = decoded_bin[4:]
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

            with open(dest, 'w') as newfile:
                newfile.write(decoded_string)
                newfile.close()
            print('[*] Successfully decoded and exported to')
            return decoded_string


#def main():
    #encode_audio("payload.mp3", "encoded.mp3","pokemon.png", 2)
    #decode_audio("encoded.mp3.wav", 2)