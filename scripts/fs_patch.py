import hashlib
import re

with open('uncompressed_exfat.kip1', 'rb') as exfatf:
    read_data = exfatf.read()
    result1 = re.search(
        b'.{3}\x12.{3}\x71.{3}\x54.{3}\x12.{3}\x71.{3}\x54.{3}\x36.{3}\xf9', read_data)
    result2 = re.search(b'\x1e\x42\xb9\x1f\xc1\x42\x71', read_data)
    patch1 = "%06X%s%s" % (result1.end(), "0004", "E0031F2A")
    patch2 = "%06X%s%s" % (result2.start() - 0x5, "0004", "1F2003D5")
    print("found FS first offset and patch at: " + patch1)
    print("found FS second offset and patch at: " + patch2)
    exfathash = hashlib.sha256(
        open('compressed_exfat.kip1', 'rb').read()).hexdigest().upper()
    print("found FS first offset and patch at: " + patch1)
    print("found FS second offset and patch at: " + patch2)
    print("exfat sha256: " + exfathash)
    exfat_ips = open('%s.ips' % exfathash, 'wb')
    exfat_ips.write(bytes.fromhex(
        str("5041544348" + patch1 + patch2 + "454F46")))
    exfat_ips.close()
    exfat_hekate = open('exfat_patch.ini', 'w')
    exfat_hekate.write('\n')
    exfat_hekate.write("#exfat\n")
    exfat_hekate.write("[FS:" + '%s' % exfathash[:16] + "]\n")
    hekate_bytes = exfatf.seek(result1.end())
    exfat_hekate.write('.nosigchk=0:0x' + '%05X' % (result1.end()-0x100) +
                       ':0x4:' + exfatf.read(0x4).hex().upper() + ',E0031F2A\n')
    hekate_bytes = exfatf.seek(result2.start() - 0x5)
    exfat_hekate.write('.nosigchk=0:0x' + '%05X' % (result2.start()-0x105) +
                       ':0x4:' + exfatf.read(0x4).hex().upper() + ',1F2003D5\n')
    exfat_hekate.close()
    exfatf.close()

with open('uncompressed_fat32.kip1', 'rb') as fat32f:
    read_data = fat32f.read()
    result1 = re.search(
        b'.{3}\x12.{3}\x71.{3}\x54.{3}\x12.{3}\x71.{3}\x54.{3}\x36.{3}\xf9', read_data)
    result2 = re.search(b'\x1e\x42\xb9\x1f\xc1\x42\x71', read_data)
    patch1 = "%06X%s%s" % (result1.end(), "0004", "E0031F2A")
    patch2 = "%06X%s%s" % (result2.start() - 0x5, "0004", "1F2003D5")
    print("found FS first offset and patch at: " + patch1)
    print("found FS second offset and patch at: " + patch2)
    fat32hash = hashlib.sha256(
        open('compressed_fat32.kip1', 'rb').read()).hexdigest().upper()
    print("fat32 sha256: " + fat32hash)
    fat32_ips = open('%s.ips' % fat32hash, 'wb')
    fat32_ips.write(bytes.fromhex(
        str("5041544348" + patch1 + patch2 + "454F46")))
    fat32_ips.close()
    fat32_hekate = open('fat32_patch.ini', 'w')
    fat32_hekate.write('\n')
    fat32_hekate.write("#fat32\n")
    fat32_hekate.write("[FS:" + '%s' % fat32hash[:16] + "]\n")
    hekate_bytes = fat32f.seek(result1.end())
    fat32_hekate.write('.nosigchk=0:0x' + '%05X' % (result1.end()-0x100) +
                       ':0x4:' + fat32f.read(0x4).hex().upper() + ',E0031F2A\n')
    hekate_bytes = fat32f.seek(result2.start() - 0x5)
    fat32_hekate.write('.nosigchk=0:0x' + '%05X' % (result2.start()-0x105) +
                       ':0x4:' + fat32f.read(0x4).hex().upper() + ',1F2003D5\n')
    fat32_hekate.close()
    fat32f.close()
