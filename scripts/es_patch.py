import re


def get_build_id():
    with open("uncompressed_es.nso0", "rb") as f:
        f.seek(0x40)
        return(f.read(0x14).hex().upper())


with open('uncompressed_es.nso0', 'rb') as fi:
    read_data = fi.read()
    result = re.search(
        b'.\x63\x00.{3}\x00\x94\xa0.{2}\xd1.{2}\xff\x97', read_data)
    patch = "%06X%s%s" % (result.end(), "0004", "E0031FAA")
    text_file = open(get_build_id() + ".ips", "wb")
    print("es build-id: " + get_build_id())
    print("es offset and patch at: " + patch)
    text_file.write(bytes.fromhex(str("5041544348" + patch + "454F46")))
    text_file.close()
