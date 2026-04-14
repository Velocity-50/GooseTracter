import re
import os
import subprocess
import time


s_sc = r"""
==============================================================
   ____                     _____               _            
  / ___| ___   ___  ___  __|_   _| __ __ _  ___| |_ ___ _ __ 
 | |  _ / _ \ / _ \/ __|/ _ \| || '__/ _` |/ __| __/ _ \ '__|
 | |_| | (_) | (_) \__ \  __/| || | | (_| | (__| ||  __/ |   
  \____|\___/ \___/|___/\___||_||_|  \__,_|\___|\__\___|_|   
                                                             
version 1.1 - by Velocity50  
==============================================================
"""
print(s_sc)


data = None
dumbness_counter = 1
for dumbness_counter in range(0, 3):
    bin_file = input("Enter the path to the binary file: ")
    bin_file = os.path.expanduser(bin_file)
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        print(f'Successfully read {bin_file} ({len(data)} bytes)')
        break

    except Exception as e:
            print(f'ERROR: could not read file: {bin_file}')
            dumbness_counter +=1
if dumbness_counter >= 3:
    print(f'💀')
    time.sleep(1)
    print(f'Bro, are you really this dumb?')
    time.sleep(1)
    print(f'Goodbye!')
    exit()

def carve_part(data, offest, size, output_path):
    with open(output_path, 'wb') as f:
        chunk = data[offest:offest+size]
        padded = chunk + b'\xff' *(size - len(chunk))
        f.write(padded)
    print(f'Carved {output_path} ({size} bytes)')

def detect_comp(bin_path):
    result = subprocess.run(['file', bin_path], capture_output=True, text=True)
    output= result.stdout.lower()
    for comp in ['xz', 'gzip', 'lzma', 'lzo']:
        if comp in output:
            return comp
        
    print(f' ERROR: no compression found: {result.stdout}')
    return None

def extract_squashfs(bin_path, output_dir):

    extract_dir = output_dir.rstrip('/') + '_extracted'
    if os.path.exists(output_dir):
        subprocess.run(['rm', '-rf', output_dir])
    result = subprocess.run(
        ['unsquashfs', '-d', output_dir, bin_path],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f' ERROR: failed to extract squashfs from {bin_path}')
        print(result.stderr)
        return None
    return extract_dir

def repack_squashfs(input_dir, output_bin, compression='xz'):
    result = subprocess.run(
        ['mksquashfs', input_dir, output_bin,
         '-comp', compression, '-no-xattrs', '-noappend'],
        capture_output=True, text=True
    )
    print(result.stdout)
    size = os.path.getsize(output_bin)
    print(f'  Repacked: {size} bytes ({size/1024/1024:.2f} MB)')
    return size


def patch_image(original_path, new_partition_path, offset, size, output_path):
    with open(original_path, 'rb') as f:
        data = bytearray(f.read())
    with open(new_partition_path, 'rb') as f:
        new_data = f.read()
    if len(new_data) > size:
        print(f'ERROR: new partition ({len(new_data)} bytes) exceeds partition size ({size} bytes)!')
        return False
    padded = new_data + b'\xff' * (size - len(new_data))
    data[offset:offset+size] = padded
    with open(output_path, 'wb') as f:
        f.write(data)
    print(f'  Patched {output_path} ({len(data)} bytes)')
    return True

strings = re.findall(b'[ -~]{8,}', data)
pattern = re.compile(b'mtdparts|boot|kernel|rootfs|offset|size|password|passphrase|pass|wpa|ipaddr|version|crypt', re.IGNORECASE)

bool_print_all = False
bool_print_none = False
print(f'Found {len(strings)} strings in .bin file:\n')
time.sleep(0.5)
amount_strings = input(f'View selected strings or all strings? ("[s]elected, [a]ll" or "[n]one"): ')


if amount_strings.lower() == 'all' or amount_strings.lower() == 'a':
    bool_print_all = True
    bool_print_none = False
elif amount_strings.lower() == 'none' or amount_strings.lower() == 'n':
    bool_print_all = False
    bool_print_none = True
if bool_print_all:
    for s in strings:
           print(s.decode('ascii', errors='replace'))
elif not bool_print_none:
    for s in strings:
        if pattern.search(s):
           print(s.decode('ascii', errors='replace'))
else:
    print(f'No strings will be printed.')
    

rootfs_offset = int(input("Enter the ROOTFS offset (hex): "), 16)
rootfs_size = int(input("Enter the ROOTFS size (hex): "), 16)

input_dir = os.path.dirname(bin_file)
out_dir = os.path.join(input_dir, 'goostracter_out')
os.makedirs(out_dir, exist_ok=True)
rootfs_carved = os.path.join(out_dir, 'rootfs.bin')
rootfs_extracted = os.path.join(out_dir, 'rootfs_extracted')
rootfs_new = os.path.join(out_dir, 'new_rootfs.squashfs')
modified = os.path.join(out_dir, 'modified.bin')
print(f'New output directory created: {out_dir}')
time.sleep(0.5)


carve_part(data, rootfs_offset, rootfs_size, rootfs_carved)
comp = detect_comp(rootfs_carved)
print(f'Detected compression: {comp}')
time.sleep(0.5)
extract_squashfs(rootfs_carved, rootfs_extracted)
repack_squashfs(rootfs_extracted, rootfs_new, compression=comp or 'xz')
patch_image(bin_file, rootfs_new, rootfs_offset, rootfs_size, modified)


print(f'Program completed! Modified image saved as "modified.bin" in {out_dir}. Its ready to be flashed! Good luck!')