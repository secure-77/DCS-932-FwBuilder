#!/usr/bin/env python3

import sys
import os

f = open(sys.argv[1], 'rb')
fileSize = os.fstat(f.fileno()).st_size
print("filesize: ", fileSize)

fileSize = int(fileSize / 4)
checksum = 0x00000000


for i in range(0, fileSize-1):
	mybytes = f.read(4)
	mybytes = int.from_bytes(mybytes, byteorder='little')
	checksum = 0xFFFFFFFF & (checksum + mybytes)
	
finalsum = 0xFFFFFFFF & (0x55aa55aa - checksum)
print("checksum: ", hex(finalsum))
