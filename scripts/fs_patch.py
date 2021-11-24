import re, hashlib

with open('uncompressed_exfat.kip1', 'rb') as fi1:
    read_data = fi1.read()
    result1 = re.search(b'.{3}\x12.{3}\x71.{3}\x54.{3}\x12.{3}\x71.{3}\x54.{3}\x36.{3}\xf9', read_data)
    result2 = re.search(b'.{3}\xaa.{3}\x97.{3}\x36.{3}\x91.{3}\xaa.{7}\xaa.{11}\xaa.{7}\x52.{3}\x72.{3}\x97', read_data)
    patch1 = "%06X%s%s" % (result1.end(), "0004", "E0031F2A")
    patch2 = "%06X%s%s" % (result2.end(), "0004", "1F2003D5")
    exfathash = hashlib.sha256(open('compressed_exfat.kip1', 'rb').read()).hexdigest().upper()
    print("found FS first offset and patch at: " + patch1)
    print("found FS second offset and patch at: " + patch2)
    print("exfat sha256: " + exfathash)
    text_file = open('%s.ips' % exfathash, 'wb')
    text_file.write(bytes.fromhex(str("5041544348" + patch1 + patch2 + "454F46")))
    text_file.close()
    fat32hash = hashlib.sha256(open('compressed_fat32.kip1', 'rb').read()).hexdigest().upper()
    print("fat32 sha256: " + fat32hash)
    text_file = open('%s.ips' % fat32hash, 'wb')
    text_file.write(bytes.fromhex(str("5041544348" + patch1 + patch2 + "454F46")))
    text_file.close()
    text_file = open('patches.ini', 'w')
    text_file.write('\n')
    text_file.write("[FS:" + '%s' % fat32hash[:16] + "]\n")
    hekate_bytes = fi1.seek(result1.end())
    text_file.write('.nosigchk=0:0x' + '%05X' % (result1.end()-0x100) + ':0x4:' + fi1.read(0x4).hex().upper() + ',E0031F2A\n')
    hekate_bytes = fi1.seek(result2.end())
    text_file.write('.nosigchk=0:0x' + '%05X' % (result2.end()-0x100) + ':0x4:' + fi1.read(0x4).hex().upper() + ',1F2003D5\n')
    text_file.write('\n')
    text_file.write("[FS:" + '%s' % exfathash[:16] + "]\n")
    hekate_bytes = fi1.seek(result1.end())
    text_file.write('.nosigchk=0:0x' + '%05X' % (result1.end()-0x100) + ':0x4:' + fi1.read(0x4).hex().upper() + ',E0031F2A\n')
    hekate_bytes = fi1.seek(result2.end())
    text_file.write('.nosigchk=0:0x' + '%05X' % (result2.end()-0x100) + ':0x4:' + fi1.read(0x4).hex().upper() + ',1F2003D5\n')
    text_file.close()
    