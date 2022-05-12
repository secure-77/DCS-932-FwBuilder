#!/usr/bin/env python3

import sys
import os
import pwd
import binascii
import sys


class FirmwarePart:
    def __init__(self, name, offset, size):
        self.name = name
        self.offset = offset
        self.size = size


def CRC32_from_file(filename):
    buf = open(filename,'rb').read()
    buf = (binascii.crc32(buf) & 0xFFFFFFFF)
    return "%08X" % buf

def Fixing_size(t_filename, targetsize, fillbytes):
    f = open(t_filename, "ab")
    fileSize = os.fstat(f.fileno()).st_size
    if (fileSize > targetsize):
        print("\n[+] Current File Size to big! Use higher compression rate!\n")
        sys.exit()

    print("[+] Current File Size", fileSize)
    print("[+] Target File Size", targetsize)
    fillSize = targetsize - fileSize
    f.write(fillbytes * fillSize)
    fileSize_new = os.fstat(f.fileno()).st_size
    print("[+] Fixing Size, New Size:", fileSize_new)
    if (fileSize_new == targetsize):
        print("[+] File Size Match!") 



firmware_parts_stage1 = [
    FirmwarePart("tmp/image_start", 0x0, 0x50000),
    FirmwarePart("tmp/image_header", 0x50000, 0x40),
    FirmwarePart("tmp/image_data.kernel.lzma", 0x50040, 0x3A0F1E)
]


firmware_parts_stage2 = [
    FirmwarePart("tmp/kernel_start", 0x0, 0x3DA000),
    FirmwarePart("tmp/kernel_fs.cpio.lzma", 0x3DA000, 0x26742B)
]

if sys.argv[1] == "unpack":
    f = open(sys.argv[2], "rb")
    print("\n    ##### Extracting Firmware Image #####")
    print("----------------------------------------------------")
    os.system("rm -rf tmp; mkdir tmp")
    for part in firmware_parts_stage1:
        outfile = open(part.name, "wb")
        f.seek(part.offset, 0)
        data = f.read(part.size)
        outfile.write(data)
        outfile.close()
        print(f"[+] Wrote {part.name} - {hex(len(data))} bytes")

    print("[+] Decomporess LZMA Kernel --> image_data.kernel ")
    os.system("bin/lzma -d -k -c tmp/image_data.kernel.lzma > tmp/image_data.kernel")

    print("\n    ##### Extracting Kernel #####")
    print("----------------------------------------------------")
    f = open("tmp/image_data.kernel", "rb")
    for part in firmware_parts_stage2:
        outfile = open(part.name, "wb")
        f.seek(part.offset, 0)
        data = f.read(part.size)
        outfile.write(data)
        outfile.close()
        print(f"[+] Wrote {part.name} - {hex(len(data))} bytes")
    
    print("[+] Decomporess CPIO Filesystem --> kernel_fs.cpio")
    os.system("bin/lzma -d -k -c tmp/kernel_fs.cpio.lzma > tmp/kernel_fs.cpio")
    os.system("sudo rm -rf root_fs")
    print("[+] Unpack CPIO Filesystem --> root_fs")
    os.system("mkdir root_fs;sudo su root -c 'cd root_fs;cpio -idm --no-absolute-filenames < ../tmp/kernel_fs.cpio'")
    
    print("\n[+] Extraction Complete: root_fs\n")


# PACKING


elif sys.argv[1] == "pack":

    
    print("\n    ##### Building Kernel #####")
    print("----------------------------------------------------")    
    print("[+] Building CPIO System: root_fs --> root_fs.cpio")
    os.system("sudo su root -c 'bin/gen_initramfs_list.sh root_fs > tmp/root_fs.list'")
    os.system("sudo su root -c 'bin/gen_init_cpio tmp/root_fs.list > tmp/root_fs.cpio'")
    username = pwd.getpwuid(os.getuid())[0]
    os.system(f"sudo su root -c 'chown {username}:{username} tmp/root_fs.cpio'")

    print("[+] Compressing File System: root_fs.cpio --> root_fs.cpio.lzma")    
    
    # change the -5 parameter here to something higher if you cpio archive gets to big!!!
    os.system("bin/lzma -z -k -f -5 -c tmp/root_fs.cpio > tmp/kernel_fs.cpio.lzma")
    
    # fix target kernel size
    Fixing_size("tmp/kernel_fs.cpio.lzma", 2520107, b'\x00')


    print("[+] Building Kernel --> image_data.kernel")
    f = open("tmp/image_data.kernel", "wb")
    for part in firmware_parts_stage2[0:]:
        i = open(part.name, "rb")
        data = i.read()
        f.write(data)
        print(f"[+] Wrote {part.name} - {hex(len(data))} bytes")
    

    print("[+] Compressing Kernel: image_data.kernel --> image_data.kernel.lzma")
    os.system("bin/lzma -z -k -f -9 -c tmp/image_data.kernel > tmp/image_data.kernel.lzma")
    
    # rebuilding header
    print("\n[+] ##### Building Kernel Header #####")
    print("----------------------------------------------------")

    # reset header crc
    f_header = open("tmp/image_header", "r+b")
    f_header.seek(4)
    f_header.write(b'\x00\x00\x00\x00')
    
    # set kernel size
    f = open("tmp/image_data.kernel.lzma", "rb")
    stage1_data_size = os.fstat(f.fileno()).st_size
    size_bytes = stage1_data_size.to_bytes(4, byteorder='big')
    print(f"[+] Fixing Size of Kernel {stage1_data_size} (0x{size_bytes.hex()})", )
    f_header.seek(4,1)
    f_header.write(size_bytes)

    # set kernel crc
    crc_data = bytearray.fromhex(CRC32_from_file("tmp/image_data.kernel.lzma"))
    print(f"[+] Fixing CRC for Kernel Data: 0x{crc_data.hex()}")
    f_header.seek(24)
    f_header.write(crc_data)
    f_header.close()

    # calc header crc sum
    crc_header = bytearray.fromhex(CRC32_from_file("tmp/image_header"))
    print(f"[+] Fixing CRC for Kernel Header: 0x0x{crc_header.hex()}")
    f_header = open("tmp/image_header", "r+b")
    f_header.seek(4)
    f_header.write(crc_header)
    f_header.close()

    
    print("\n[+] ##### Building Image #####")
    print("----------------------------------------------------")
    f = open(sys.argv[2], "wb")
    padding = 0
    for part in firmware_parts_stage1[0:]:
        i = open(part.name, "rb")
        data = i.read()
        f.write(data)
        print(f"[+] Wrote {part.name} - {hex(len(data))} bytes")
        

    # fix the file size
    Fixing_size(sys.argv[2], 4194304, b'\xff' )

    print("[+] Adding CheckSum")
    os.system("bin/addchecksum {}".format(sys.argv[2]))


    print("\n[+] Building Complete")
