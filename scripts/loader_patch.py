import re, time, os, sys, shutil, subprocess
from io import BytesIO
from pathlib import Path
from urllib.parse import unquote
from urllib.request import urlretrieve, urlopen
from zipfile import ZipFile
from hashlib import sha256
from glob import glob
    
Path("./hekate_patches").mkdir(parents=True, exist_ok=True)
Path("./SigPatches/atmosphere/kip_patches/loader_patches").mkdir(parents=True, exist_ok=True)
Path("./SigPatches/bootloader").mkdir(parents=True, exist_ok=True)
amszipname = unquote(urlopen('https://api.github.com/repos/Atmosphere-NX/Atmosphere/releases').read().split(b'browser_download_url')[1].split(b'\"')[2].decode('utf-8').split('/')[-1])
urlretrieve(urlopen('https://api.github.com/repos/Atmosphere-NX/Atmosphere/releases').read().split(b'browser_download_url')[1].split(b'\"')[2].decode('utf-8'), amszipname)
print(glob('./atmosphere-*.zip')[0])
AMSVER = (glob('./atmosphere-*.zip')[0][13:18])
with ZipFile(glob('./atmosphere-*.zip')[0], 'r') as amszip:
    with amszip.open('atmosphere/package3') as package3:
        read_data = package3.read()
        locate_loader = read_data.find(b'Loader')
        loader_size_start = locate_loader - 0xC
        loader_size_end = locate_loader - 0x9
        size = int.from_bytes(read_data[loader_size_start:loader_size_end], "little")
        AMSHASH = hex(int.from_bytes(read_data[0x3C:0x40], "little"))[2:]
        loader_offset_start = locate_loader - 0x10
        loader_offset_end = locate_loader - 0xD
        loader_start = int.from_bytes(read_data[loader_offset_start:loader_offset_end], "little")
        loader_end = loader_start + size
        loader_kip = read_data[loader_start:loader_end]
        text_file = open('loader.kip1', 'wb')
        text_file.write(loader_kip)
        text_file.close()
        process = subprocess.Popen(["hactool", "--intype=kip1", "--uncompressed=uloader.kip1", "loader.kip1"], stdout=subprocess.DEVNULL)
        time.sleep(5)
        with open('uloader.kip1', 'rb') as f:
            loader_data = f.read()
            result = re.search(b'\x00\x94\x01\xC0\xBE\x12\x1F\x00', loader_data)
            patch = "%06X%s%s" % (result.end(), "0001", "00")
            hash = sha256(open('loader.kip1', 'rb').read()).hexdigest().upper()
            print("IPS LOADER HASH     : " + "%s" % hash)
            print("IPS LOADER PATCH    : " + patch)
            text_file = open('SigPatches/atmosphere/kip_patches/loader_patches/%s.ips' % hash, 'wb')
            text_file.write(bytes.fromhex(str("5041544348" + patch + "454F46")))
            text_file.close()
            text_file = open('hekate_patches/loader_patch_%s.ini' % hash[:16], 'w')
            text_file.write('\n')
            text_file.write("#Loader Atmosphere-" + AMSVER + "-" + AMSHASH + "\n")
            text_file.write("[Loader:" + '%s' % hash[:16] + "]\n")
            text_file.write('.nosigchk=0:0x' + '%04X' % (result.end() - 0x100) + ':0x1:01,00\n')
            print("HEKATE LOADER HASH  : " + "%s" % hash[:16])
            print("HEKATE LOADER PATCH : " + "%04X" % (result.end() - 0x100) + ":0x1:01,00")
            text_file.close()
            f.close()
            package3.close()
            amszip.close()
            os.remove(glob('./atmosphere-*.zip')[0])
            os.remove("./uloader.kip1")
            os.remove("./loader.kip1")
            with open("./SigPatches/bootloader/patches.ini", 'wb') as outfile:
                for filename in glob('./hekate_patches/*.ini'):
                    with open(filename, 'rb') as readfile:
                        shutil.copyfileobj(readfile, outfile)
            shutil.make_archive("SigPatches", "zip", "SigPatches")
