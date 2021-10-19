from zipfile import ZipFile
import subprocess
import re
import glob
import time
import hashlib

print(glob.glob('./atmosphere-*.zip')[0])
AMSVER = (glob.glob('./atmosphere-*.zip')[0][13:18])
with ZipFile(glob.glob('./atmosphere-*.zip')[0], 'r') as amszip:
    with amszip.open('atmosphere/package3') as package3:
        read_data = package3.read()
        size = int.from_bytes(read_data[0x43C:0x43F], "little")
        AMSHASH = hex(int.from_bytes(read_data[0x3C:0x40], "little"))[2:]
        loader_start = int.from_bytes(read_data[0x438:0x43B], "little") + 0x100000
        loader_end = loader_start + size
        loader_kip = read_data[loader_start:loader_end]
        text_file = open('loader.kip1', 'wb')
        text_file.write(loader_kip)
        text_file.close()
        process = subprocess.Popen(["hactool", "--intype=kip1", "--uncompressed=uloader.kip1", "loader.kip1"], stdout=subprocess.DEVNULL)
        time.sleep(3)
        with open('uloader.kip1', 'rb') as fi:
            read_loader = fi.read()
            result = re.search(b'\x00\x94\x01\xC0\xBE\x12\x1F\x00', read_loader)
            patch = "%06X%s%s" % (result.end(), "0001", "00")
            hash = hashlib.sha256(open('loader.kip1', 'rb').read()).hexdigest().upper()
            text_file = open('atmosphere/kip_patches/loader_patches/%s.ips' % hash, 'wb')
            text_file.write(bytes.fromhex(str("5041544348" + patch + "454F46")))
            text_file.close()
            text_file = open('hekate_patches/loader_patch_%s.ini' % hash[:16], 'w')
            text_file.write('\n')
            text_file.write("#Loader Atmosphere-" + AMSVER + "-" + AMSHASH + "\n")
            text_file.write("[Loader:" + '%s' % hash[:16] + "]\n")
            hekate_bytes = fi.seek(result.end())
            text_file.write('.nosigchk=0:0x' + '%04X' % (result.end()-0x100) + ':0x1:' + fi.read(0x1).hex().upper() + ',00\n')
            text_file.close()