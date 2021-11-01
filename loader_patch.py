import re, time, os, sys, shutil
from io import BytesIO
from pathlib import Path
from urllib.parse import unquote
from urllib.request import urlretrieve, urlopen
from zipfile import ZipFile
from hashlib import sha256
from glob import glob
from struct import unpack as up, pack as pk, calcsize as calc

iter_range = range
int_types = (int,)
ascii_string = lambda b: b.decode('ascii')
bytes_to_list = lambda b: list(b)
list_to_bytes = lambda l: bytes(l)

class BinFile(object):
    def __init__(self, li):
        self._f = li

    def read(self, arg):
        if isinstance(arg, str):
            fmt = '<' + arg
            size = calc(fmt)
            raw = self._f.read(size)
            out = up(fmt, raw)
            if len(out) == 1:
                return out[0]
            return out
        elif arg is None:
            return self._f.read()
        else:
            out = self._f.read(arg)
            return out

    def read_from(self, arg, offset):
        old = self.tell()
        try:
            self.seek(offset)
            out = self.read(arg)
        finally:
            self.seek(old)
        return out

    def seek(self, off):
        self._f.seek(off)

    def close(self):
        self._f.close()

    def tell(self):
        return self._f.tell()

def kip1_blz_decompress(compressed):
    compressed_size, init_index, uncompressed_addl_size = up('<III', compressed[-0xC:])
    decompressed = compressed[:] + b'\x00' * uncompressed_addl_size
    decompressed_size = len(decompressed)
    if len(compressed) != compressed_size:
        assert len(compressed) > compressed_size
        compressed = compressed[len(compressed) - compressed_size:]
    if not (compressed_size + uncompressed_addl_size):
        return b''
    compressed = bytes_to_list(compressed)
    decompressed = bytes_to_list(decompressed)
    index = compressed_size - init_index
    outindex = decompressed_size
    while outindex > 0:
        index -= 1
        control = compressed[index]
        for i in iter_range(8):
            if control & 0x80:
                if index < 2:
                    raise ValueError('Compression out of bounds!')
                index -= 2
                segmentoffset = compressed[index] | (compressed[index+1] << 8)
                segmentsize = ((segmentoffset >> 12) & 0xF) + 3
                segmentoffset &= 0x0FFF
                segmentoffset += 2
                if outindex < segmentsize:
                    raise ValueError('Compression out of bounds!')
                for j in iter_range(segmentsize):
                    if outindex + segmentoffset >= decompressed_size:
                        raise ValueError('Compression out of bounds!')
                    data = decompressed[outindex+segmentoffset]
                    outindex -= 1
                    decompressed[outindex] = data
            else:
                if outindex < 1:
                    raise ValueError('Compression out of bounds!')
                outindex -= 1
                index -= 1
                decompressed[outindex] = compressed[index]
            control <<= 1
            control &= 0xFF
            if not outindex:
                break
    return list_to_bytes(decompressed)
    
Path("./hekate_patches").mkdir(parents=True, exist_ok=True)
Path("./patches/atmosphere/kip_patches/loader_patches").mkdir(parents=True, exist_ok=True)
Path("./patches/bootloader").mkdir(parents=True, exist_ok=True)
amszipname = unquote(urlopen('https://api.github.com/repos/Atmosphere-NX/Atmosphere/releases').read().split(b'browser_download_url')[1].split(b'\"')[2].decode('utf-8').split('/')[-1])
urlretrieve(urlopen('https://api.github.com/repos/Atmosphere-NX/Atmosphere/releases').read().split(b'browser_download_url')[1].split(b'\"')[2].decode('utf-8'), amszipname)
print(glob('./atmosphere-*.zip')[0])
AMSVER = (glob('./atmosphere-*.zip')[0][13:18])
with ZipFile(glob('./atmosphere-*.zip')[0], 'r') as amszip:
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
        with open('loader.kip1', 'rb') as f:
            kip1_magic = f.read(0x4)
            f = BinFile(f)
            if kip1_magic != "b'KIP1'":
                flags = f.read_from('b', 0x1F)
                tloc, tsize, tfilesize = f.read_from('III', 0x20)
                rloc, rsize, rfilesize = f.read_from('III', 0x30)
                dloc, dsize, dfilesize = f.read_from('III', 0x40)
                toff = 0x100
                roff = toff + tfilesize
                doff = roff + rfilesize
                bsssize = f.read_from('I', 0x54)
                text = (kip1_blz_decompress(f.read_from(tfilesize, toff)), None, tloc, tsize) if flags & 1 else (f.read_from(tfilesize, toff), toff, tloc, tsize)
                ro   = (kip1_blz_decompress(f.read_from(rfilesize, roff)), None, rloc, rsize) if flags & 2 else (f.read_from(rfilesize, roff), roff, rloc, rsize)
                data = (kip1_blz_decompress(f.read_from(dfilesize, doff)), None, dloc, dsize) if flags & 4 else (f.read_from(dfilesize, doff), doff, dloc, dsize)
                loader_data = text[0] + ro[0] + data[0]
                result = re.search(b'\x00\x94\x01\xC0\xBE\x12\x1F\x00', loader_data)
                patch = "%06X%s%s" % (result.end() + 0x100, "0001", "00")
                hash = sha256(open('loader.kip1', 'rb').read()).hexdigest().upper()
                print("IPS LOADER HASH     : " + "%s" % hash)
                print("IPS LOADER PATCH    : " + patch)
                text_file = open('patches/atmosphere/kip_patches/loader_patches/%s.ips' % hash, 'wb')
                text_file.write(bytes.fromhex(str("5041544348" + patch + "454F46")))
                text_file.close()
                text_file = open('hekate_patches/loader_patch_%s.ini' % hash[:16], 'w')
                text_file.write('\n')
                text_file.write("#Loader Atmosphere-" + AMSVER + "-" + AMSHASH + "\n")
                text_file.write("[Loader:" + '%s' % hash[:16] + "]\n")
                text_file.write('.nosigchk=0:0x' + '%04X' % (result.end()) + ':0x1:01,00\n')
                print("HEKATE LOADER HASH  : " + "%s" % hash[:16])
                print("HEKATE LOADER PATCH : " + "%04X" % (result.end()) + ":0x1:01,00")
                text_file.close()
                f.close()
                package3.close()
                amszip.close()
                os.remove(glob('./atmosphere-*.zip')[0])
                os.remove("./loader.kip1")
                with open("./patches/bootloader/patches.ini", 'wb') as outfile:
                    for filename in glob('./hekate_patches/*.ini'):
                        with open(filename, 'rb') as readfile:
                            shutil.copyfileobj(readfile, outfile)
                shutil.make_archive("patches", "zip", "patches")
