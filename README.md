# GooseTracter 
A very simple tool for modifying a squashfs based Linux root filesystem.

# What it does 
`rootfs_modifier.py` sets the root password to null. It clears the root password hash, making the root account have no password. 

This script is very likely to be used in Off-Board Firmware Extraction. Sometimes WINBOND or other EEPROM chips require a password for the root shell. 

# Usage
`python rootfs_modifier.py`

You will be prompted to put in a input file like this for example:
`~/extracted_firmware/read1.bin`

After this you will be asked on how many strings in the .bin file you want to see.
From these strings you need to derive the rootfs offset and the rootfs size.
For example:
In the output of the strings you see this:
````
mtdparts=spi0.0:0x00050000(boot),0x00190000(kernel),0x00200000(rootfs),0x00330000(user),0x000e0000(mtd),0x00010000(factory)
````
You can now derive the offset: 
We start at boot which is at `0X50000`, we add the kernel which starts at `0x190000` and we get the rootfs offset (which is the sum of the boot and the kernel) of: `0x1E0000`. The size is already in the given line which is `0x200000`.
You fill these in when prompted.

The script finishes and puts everything in a folder in the same input path you gave the program.


# Requirements
- python 3
- a .bin file using squashfs

# Important!
Make a backup of your .bin file!
