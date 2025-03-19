# fuzz_m10s.py by XXX (Anonymized for submission)
import os
import serial
import sys
import hashlib
import struct

# Where fandango has left the inputs
CORPUS = 'corpus'

# Where we write inputs that cause crashes
CRASHES = 'crashes'

# The baud rate with which we communicate with the MAX-M10S.
# The default is 9600 baud.
BAUD_RATE = 9600

# Conclude that something has gone wrong if we don't see
# a valid preamble after this much time
READ_TIMEOUT = 2.0

# Maximum length of a UBX message is
#    2        preamble
#    1        class
#    1        ID
#    2        length field
#    2^16 - 1 payload
#    2        checksum
MAXLEN = 2 + 1 + 1 + 2 + ((1 << 16) - 1) + 2

# CFG messages are either acknowledged (ACK-ACK) or not
# acknowledged (ACK-NAK), depending on whether the
# requested configuration was actually performed.
ACK_ACK = b'\xb5\x62\x05\x01\x02\x00\x06\x8a\x98\xc1'
ACK_NAK = b'\xb5\x62\x05\x00\x02\x00\x06\x8a\x97\xbc'

# UBX message preamble.
PREAMBLE = b'\xb5\x62'

def ubx_checksum(message: bytes, length: int) -> bytes:
    """Compute checksum over message of payload length length."""
    ck_a = 0
    ck_b = 0
    for i in range(2, 2 + length + 4):
        ck_a = (ck_a + message[i]) & 0xff
        ck_b = (ck_b + ck_a) & 0xff

    return bytes([ck_a, ck_b])

def ubx_check_checksum(message: bytes, length: int, checksum: bytes) -> bool:
    """Check correctness of a given checksum against freshly computed
       checksum of message with payload length length."""
    computed_checksum = ubx_checksum(message, length)
    return computed_checksum == checksum

def write_infile_as_crash(infile: bytes):
    """Write the input file into the crashes directory. The file name
       will be a hash of the input so that each unique input gets
       its own file."""
    h = hashlib.sha256()
    h.update(infile)
    filename = os.path.join(CRASHES, h.hexdigest() + ".crash")

    with open(filename, 'wb') as f:
        f.write(infile)

if __name__ == '__main__':
    if not os.path.exists(CORPUS):
        sys.exit('Corpus directory {0:s} does not exist'.format(CORPUS))
    if not os.path.exists(CRASHES):
        sys.exit('Crashes directory {0:s} does not exist'.format(CRASHES))
        
    serial = serial.Serial('/dev/ttyUSB0',
                           baudrate=BAUD_RATE,
                           bytesize=serial.EIGHTBITS,
                           parity=serial.PARITY_NONE,
                           stopbits=serial.STOPBITS_ONE,
                           timeout=READ_TIMEOUT)

    directory = CORPUS
    response = bytearray(MAXLEN)
    n_successful_tests = 0
    n_files = len([name for name in os.listdir(CORPUS)
                   if os.path.isfile(os.path.join(CORPUS, name))])

    for filename in os.listdir(directory):
        infile_name = os.path.join(directory, filename)
        print('File {0:s}'.format(infile_name), end=' ')

        # Read file with input
        with open(infile_name, 'rb') as f:
            infile = bytearray(f.read());

        # Write input to GNSS module
        serial.write(infile);

        # Read output from module
        # Step 1: read preamble
        preamble = serial.read_until(PREAMBLE)
        if not preamble.endswith(PREAMBLE): # Timeout
            print('Timeout while reading preamble')
            write_infile_as_crash(infile)
            break
            
        response[0:2] = PREAMBLE

        # Step 2: read rest of header
        header = serial.read(size=4)
        if len(header) != 4:
            print('Timeout while reading header')
            write_infile_as_crash(infile)
            break
        response[2:6] = header

        # Step 3: read rest of response
        (payload_length,) = struct.unpack('<H', response[4:6])
        rest = serial.read(payload_length + 2) # + 2 for checksum
        if len(rest) != payload_length + 2:
            print('Timeout while reading message body, have {0:d} bytes,'
                  + ' want {1:d}'.format(len(rest), payload_length))
            write_infile_as_crash(infile)
            break
            
        response[6:] = rest

        # Step 4: compare checksums
        if not ubx_check_checksum(response, payload_length,
                                  response[payload_length + 6:]):
            print('Checksum mismatch')
            write_infile_as_crash(infile)
            break

        # Step 5: Check if it's ACK or NAK
        if response[:payload_length + 8] == ACK_ACK:
            print('ACK')
        elif response[:payload_length + 8] == ACK_NAK:
            print('NAK')
        else:
            print('Response mismatch, neither ACK nor NAK')
            write_infile_as_crash(infile)
            write_infile_as_crash(response[:payload_length + 8])
            break

        n_successful_tests += 1

    print('{0:d}/{1:d} successfully concluded tests'
          .format(n_successful_tests, n_files))
    serial.close()
