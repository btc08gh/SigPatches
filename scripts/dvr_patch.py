import re


def get_build_id():
    with open("main", "rb") as f:
        f.seek(0x40)
        return(f.read(0x20).hex().upper())


with open('main', 'rb') as fi:
    read_data = fi.read()
    result1 = re.search(
        b'\x1F\x08\x00\x71\xE0\x17\x9F\x1A\xFD\x7B\xC1\xA8\xC0\x03\x5F\xD6', read_data)
    result3 = read_data.find(
        b'\x00\x71\xE0\x17\x9F\x1A\xFD\x7B\xC1\xA8\xC0\x03\x5F\xD6\xE0\x03\x1F\x2A\xC0\x03')
    result5 = read_data.find(
        b'\xFD\x7B\xC2\xA8\xC0\x03\x5F\xD6\x3F\x08\x00\x71\xA8\x04\x00\x54')
    result6 = read_data.find(b'\x1F\xAA\x28\x00\x00\x39\xC0\x03\x5F\xD6')
    result7 = re.search(b'\x0B\x00\x94\xF5\x03\x00\xAA\x15', read_data)
    result8 = re.search(
        b'\x97\xC0\x07\x00.\x00..\x91\xA4\x63\x00\x91\xE1\x03\x00\xAA', read_data)
    result9 = re.search(
        b'\x98.\x86\x52\x68\x6A\x78\x38\x1F\x01\x00\x71', read_data)
    result10 = re.search(
        b'\x08\x01\x40\x39\x09\x4C\x41\xF9\x1F\x01\x00\x71', read_data)
    result12 = re.search(
        b'\x97\xE0\x03\x13\xAA\xF3\x0B\x40\xF9\xFD\x7B\xC2\xA8\xC0\x03\x5F\xD6\x68\x00', read_data)
    patch1 = "%08X%s%s" % (result1.end(), "0005", "20008052C0")
    patch2 = "%08X%s%s" % ((result1.end() + 0x6), "0002", "5FD6")
    patch3 = "%08X%s%s" % ((result3 - 0x1), "0001", "05")
    patch4 = "%08X%s%s" % ((result3 + 0x3), "0001", "07")
    patch5 = "%08X%s%s" % ((result5 + 0x8), "0008", "210080521F2003D5")
    patch6 = "%08X%s%s" % ((result6 + 0xA), "0008", "210080521F2003D5")
    patch7 = "%08X%s%s" % ((result7.end()), "0001", "0C")
    patch8 = "%08X%s%s" % ((result8.start() + 0x1), "0010",
                           "1F2003D5F44F42A9E003172AF3FFFF17")
    patch9 = "%08X%s%s" % ((result9.end() - 0x8), "0004", "08008052")
    patch10 = "%08X%s%s" % (result10.end(), "0004", "28008052")
    patch11 = "%08X%s%s" % ((result12.end() - 0x2), "0001", "00")
    patch12 = "%08X%s%s" % (result12.end(), "0006", "80D2C0035FD6")
    # if a patch doesn't print or errors with nonetype, the pattern for that offset was changed - pattern applicable for 12.1.0 and up
    print(patch1)
    print(patch2)
    print(patch3)
    print(patch4)
    print(patch5)
    print(patch6)
    print(patch7)
    print(patch8)
    print(patch9)
    print(patch10)
    print(patch11)
    print(patch12)
    text_file = open("atmosphere/exefs_patches/am/" +
                     get_build_id() + ".ips", "wb")
    print("AM build-id: " + get_build_id())
    text_file.write(bytes.fromhex(str("4950533332" + patch1 + patch2 + patch3 + patch4 +
                    patch5 + patch6 + patch7 + patch8 + patch9 + patch10 + patch11 + patch12 + "45454F46")))
