import re
from pathlib import Path

Path("./SigPatches/atmosphere/exefs_patches/d2r_offline_fix").mkdir(parents=True, exist_ok=True)
Path("./cheats/atmosphere/contents/0100726014352000/cheats").mkdir(parents=True, exist_ok=True)

def get_build_id():
  with open("main", "rb") as f:
    f.seek(0x40)
    return(f.read(0x14).hex().upper())

with open('main', 'rb') as fi:
    read_data = fi.read()
    result = re.search(b'\xd2...\xf2...\xf2...\xcb...\xeb.......\x14', read_data)
    patch = "%06X%s%s" % (result.end(), "0004", "1F2003D5")
    text_file = open("SigPatches/atmosphere/exefs_patches/d2r_offline_fix/" + get_build_id() + ".ips", "wb")
    print("d2r build-id: " + get_build_id())
    print("d2r offset and patch at: " + patch)
    text_file.write(bytes.fromhex(str("5041544348" + patch + "454F46")))
    text_file.close()
    cheat = "%s%08X%s" % ("04000000 ", result.end() - 0x100,  " D503201F")
    print("d2r cheat string: " + cheat)
    text_file = open("cheats/atmosphere/contents/0100726014352000/cheats/" + get_build_id()[:16] + ".txt", "w")
    text_file.write("{@borntohonk}\n")
    text_file.write("[D2R Bypass Online Check]\n")
    text_file.write(cheat)
    text_file.close()
    