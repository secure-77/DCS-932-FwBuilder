# DCS-932-FwBuilder

Extract and repack the root file system of the firmware 1.14.04 for the Webcam D-Link DCS-932L (Revision A)

Original FW download at: https://ftp.dlink.de/dcs/dcs-932l/driver_software/DCS-932L_fw_reva_114b04_all_en_20170227.zip

More information on my blog: https://secure77.de/d-link-dcs-932l-webcam-hacking/


## Unpack the Firmware

```bash
./dlink_fw.py unpack dcs932l_v1.14.04.bin
```

This will create a new folder tmp with all extracted data, don't touch this folder, you need the files for the packing.

You are looking for the folder `root_fs`

Make sure you edit the files as root and don´t put to large files into it, as this archive has a file size limit.


## Pack the Firmware

```bash
./dlink_fw.py pack dcs932l_v1.14.04.bin.custom
```

