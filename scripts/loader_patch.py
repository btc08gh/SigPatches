import os
import re
import shutil
import subprocess
import sys
import time
from glob import glob
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from urllib.parse import unquote
from urllib.request import urlopen, urlretrieve
from zipfile import ZipFile

import nxo64

Path('./hekate_patches').mkdir(parents=True, exist_ok=True)
Path('./SigPatches/atmosphere/kip_patches/loader_patches').mkdir(parents=True, exist_ok=True)
Path('./SigPatches/bootloader').mkdir(parents=True, exist_ok=True)
atmosphere_archive_name = unquote(urlopen('https://api.github.com/repos/Atmosphere-NX/Atmosphere/releases').read().split(b'browser_download_url')[1].split(b'\"')[2].decode('utf-8').split('/')[-1])
urlretrieve(urlopen('https://api.github.com/repos/Atmosphere-NX/Atmosphere/releases').read().split(b'browser_download_url')[1].split(b'\"')[2].decode('utf-8'), atmosphere_archive_name)
atmosphere_zip = glob('./atmosphere-*.zip')[0]
atmosphere_version = re.search('[0-9.]{5}', atmosphere_zip).group()
atmosphere_hash = re.search('[0-9A-Fa-f]{9}', atmosphere_zip).group()
with open('./hekate_patches/loader_patches.ini') as loader_patches:
    if atmosphere_hash in loader_patches.read():
        print('A patch for this version of Atmosphere already exists in loader_patches.ini')
        os.remove(atmosphere_zip)
    else:
        with ZipFile(glob('./atmosphere-*.zip')[0], 'r') as amszip:
            with amszip.open('atmosphere/package3') as package3:
                read_data = package3.read()
                locate_loader = read_data.find(b'Loader')
                loader_size_start = locate_loader - 0xC
                loader_size_end = locate_loader - 0x9
                size = int.from_bytes(read_data[loader_size_start:loader_size_end], 'little')
                loader_offset_start = locate_loader - 0x10
                loader_offset_end = locate_loader - 0xD
                loader_start = int.from_bytes(read_data[loader_offset_start:loader_offset_end], 'little')
                loader_end = loader_start + size
                loader_kip = read_data[loader_start:loader_end]
                if re.compile(b'\x4B\x49\x50\x31\x4C\x6F\x61\x64\x65\x72').search(loader_kip):
                    compressed_loader_file = open('loader.kip1', 'wb')
                    compressed_loader_file.write(loader_kip)
                    compressed_loader_file.close()
                    with open('loader.kip1', 'rb') as compressed_loader_kip:
                        nxo64.write_file(f'uloader.kip1', nxo64.decompress_kip(compressed_loader_kip))
                        with open('uloader.kip1', 'rb') as decompressed_loader_kip:
                            loader_data = decompressed_loader_kip.read()
                            result = re.search(b'\x00\x94\x01\xC0\xBE\x12\x1F\x00', loader_data)
                            patch = '%06X%s%s' % (result.end(), '0001', '00')
                            hash = sha256(open('loader.kip1', 'rb').read()).hexdigest().upper()
                            print('IPS LOADER HASH     : ' + '%s' % hash)
                            print('IPS LOADER PATCH    : ' + patch)
                            ips_file = open('SigPatches/atmosphere/kip_patches/loader_patches/%s.ips' % hash, 'wb')
                            ips_file.write(bytes.fromhex(str('5041544348' + patch + '454F46')))
                            ips_file.close()
                            hekate_file = open('./hekate_patches/loader_patches.ini', 'a')
                            hekate_file.write('\n')
                            hekate_file.write('#Loader Atmosphere-' + atmosphere_version + '-' + atmosphere_hash + '\n')
                            hekate_file.write('[Loader:' + '%s' % hash[:16] + ']\n')
                            hekate_file.write('.nosigchk=0:0x' + '%04X' % (result.end() - 0x100) + ':0x1:01,00\n')
                            print('HEKATE LOADER HASH  : ' + '%s' % hash[:16])
                            print('HEKATE LOADER PATCH : ' + '%04X' % (result.end() - 0x100) + ':0x1:01,00')
                            hekate_file.close()
                            decompressed_loader_kip.close()
                            package3.close()
                            amszip.close()
                            compressed_loader_kip.close()
                            os.remove('./uloader.kip1')
                            os.remove('./loader.kip1')
                            os.remove(atmosphere_zip)
                            with open('./hekate_patches/patches.ini', 'wb') as outfile:
                                for filename in ['./hekate_patches/header.ini', './hekate_patches/fs_patches.ini', './hekate_patches/loader_patches.ini']:
                                    with open(filename, 'rb') as readfile:
                                        shutil.copyfileobj(readfile, outfile)
                            outfile.close()
                            shutil.copyfile('./hekate_patches/patches.ini', './SigPatches/bootloader/patches.ini')
                            shutil.make_archive('SigPatches', 'zip', 'SigPatches')
                else:
                    print(
                        'KIP1Loader magic not found! - Script needs to be fixed, loader_kip is not correct!')
