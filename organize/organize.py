#!/usr/bin/env python

VERBOSE = False

import os
import subprocess
import shutil
import errno
import hashlib
import re
from pathlib import Path

def get_es_build_id():
  with open(version + "/uncompressed_es.nso0", "rb") as f:
    f.seek(0x40)
    return(f.read(0x14).hex().upper())

def get_nifm_build_id():
  with open(version + "/uncompressed_nifm.nso0", "rb") as f:
    f.seek(0x40)
    return(f.read(0x14).hex().upper())

def mkdirp(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def get_ncaid(filename):
    BLOCKSIZE = 65536
    hasher = hashlib.sha256()
    with open(filename, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return hasher.hexdigest()[:32]

def print_verbose(*args, **kwargs):
    if VERBOSE:
        print(*args, **kwargs)

for version in os.listdir("."):
    # Ignore files (only treat directories)
    if os.path.isfile(version):
        continue

    if version == "updaters":
        continue

    # Rename CNMTs to make them easier to find. Also, if nca is a folder,
    # get its content. Also, get the hash, and give it the proper ncaid name
    print(f"===== Handling {version} =====")

    HACTOOL_PROGRAM = "hactool"
    if os.path.isfile(version + "/dev"):
        HACTOOL_PROGRAM += " --dev"

    print(f"# Normalizing the nca folder")
    for nca in os.listdir(version + "/nca"):
        ncaFull = version + "/nca/" + nca
        # Fix "folder-as-file" files when dumped from Switch NAND
        if os.path.isdir(ncaFull):
            print_verbose(f"{ncaFull}/00 -> {ncaFull}")
            os.rename(ncaFull, ncaFull + "_folder")
            os.rename(ncaFull + "_folder/00", ncaFull)
            os.rmdir(ncaFull + "_folder")
        # Ensure the NCAID is correct (It's wrong when dumped from the
        # Placeholder folder on a Switch NAND
        ncaid = get_ncaid(ncaFull)
        newName = version + "/nca/" + ncaid + "." + ".".join(os.path.basename(ncaFull).split(".")[1:])
        print_verbose(f"{ncaFull} -> {newName}")
        os.rename(ncaFull, newName)
        ncaFull = newName

        # Ensure meta files have .cnmt.nca extension
        process = subprocess.Popen(["hactool", "--intype=nca", ncaFull], stdout=subprocess.PIPE, universal_newlines=True)
        contentType = process.communicate()[0].split("Content Type:                       ")[1].split("\n")[0]
        if contentType == "Meta" and not nca.endswith(".cnmt.nca"):
            print_verbose(ncaFull + " -> " + ".".join(ncaFull.split(".")[:-1]) + ".cnmt.nca")
            shutil.move(ncaFull, ".".join(ncaFull.split(".")[:-1]) + ".cnmt.nca")

    print("# Sort by titleid")    
    for nca in os.listdir(version + "/nca"):
        ncaFull = version + "/nca/" + nca
        process = subprocess.Popen(["hactool", "--intype=nca", ncaFull], stdout=subprocess.PIPE, universal_newlines=True)
        titleId = process.communicate()[0].split("Title ID:                           ")[1].split("\n")[0]
        process = subprocess.Popen(["hactool", "--intype=nca", ncaFull], stdout=subprocess.PIPE, universal_newlines=True)
        contentType = process.communicate()[0].split("Content Type:                       ")[1].split("\n")[0]

        mkdirp(version + "/titleid/" + titleId)

        print_verbose(version + "/titleid/" + titleId + "/" + contentType + ".nca -> " + "../../nca/" + nca)
        shutil.copyfile(version + "/nca/" + nca, version + "/titleid/" + titleId + "/" + contentType + ".nca")

    print("# Extracting ES")
    esFull = version + "/"
    ncaParent = version + "/titleid/0100000000000033"
    ncaPartial = ncaParent + "/Program.nca"
    ncaFull = version + "/titleid/0100000000000033/exefs/main"
    process = subprocess.Popen(["hactool", "--intype=nca", "--exefsdir=" + version + "/titleid/0100000000000033/exefs/", version + "/titleid/0100000000000033/Program.nca"], stdout=subprocess.DEVNULL)
    process.wait()
    process = subprocess.Popen(["hactool", "--intype=nso0", "--uncompressed=" + version + "/uncompressed_es.nso0", ncaFull], stdout=subprocess.DEVNULL)
    process.wait()

    print("# Extracting NIFM")
    nifmFull = version + "/"
    ncaParent = version + "/titleid/010000000000000f"
    ncaPartial = ncaParent + "/Program.nca"
    ncaFull = version + "/titleid/010000000000000f/exefs/main"
    process = subprocess.Popen(["hactool", "--intype=nca", "--exefsdir=" + version + "/titleid/010000000000000f/exefs/", version + "/titleid/010000000000000f/Program.nca"], stdout=subprocess.DEVNULL)
    process.wait()
    process = subprocess.Popen(["hactool", "--intype=nso0", "--uncompressed=" + version + "/uncompressed_nifm.nso0", ncaFull], stdout=subprocess.DEVNULL)
    process.wait()

    print("# Extracting fat32")
    ncaParent = version + "/titleid/0100000000000819"
    pk21dir = ncaParent + "/romfs/nx/package2"
    ini1dir = ncaParent + "/romfs/nx/ini1"
    ncaFull = ncaParent + "/Data.nca"
    fat32Full = version + "/uncompressed_fat32.kip1"    
    process = subprocess.Popen(["hactool", "--intype=nca", "--romfsdir=" + ncaParent + "/romfs", ncaFull], stdout=subprocess.DEVNULL)
    process.wait()
    process = subprocess.Popen(["hactool", "--intype=pk21", "--ini1dir=" + ini1dir, pk21dir], stdout=subprocess.DEVNULL)
    process.wait()
    process = subprocess.Popen(["hactool", "--intype=kip1", "--uncompressed=" + fat32Full, ini1dir + "/FS.kip1"], stdout=subprocess.DEVNULL)
    process.wait()
    fat32Compressed = version + "/titleid/0100000000000819/romfs/nx/ini1/FS.kip1"
    fsCopy = version  + "/compressed_fat32.kip1"
    process = shutil.copyfile(fat32Compressed, fsCopy)
    
    print("# Extracting exfat")
    ncaParent = version + "/titleid/010000000000081b"
    pk21dir = ncaParent + "/romfs/nx/package2"
    ini1dir = ncaParent + "/romfs/nx/ini1"
    ncaFull = ncaParent + "/Data.nca"
    exfatFull = version + "/uncompressed_exfat.kip1"
    process = subprocess.Popen(["hactool", "--intype=nca", "--romfsdir=" + ncaParent + "/romfs", ncaFull], stdout=subprocess.DEVNULL)
    process.wait()
    process = subprocess.Popen(["hactool", "--intype=pk21", "--ini1dir=" + ini1dir, pk21dir], stdout=subprocess.DEVNULL)
    process.wait()
    process = subprocess.Popen(["hactool", "--intype=kip1", "--uncompressed=" + exfatFull, ini1dir + "/FS.kip1"], stdout=subprocess.DEVNULL)
    process.wait()
    exfatCompressed = version + "/titleid/010000000000081b/romfs/nx/ini1/FS.kip1"
    fsCopy = version  + "/compressed_exfat.kip1"
    process = shutil.copyfile(exfatCompressed, fsCopy)

for version in os.listdir("."):
    # Ignore files (only treat directories)
    if os.path.isfile(version):
        continue

    print(f"===== Making patches for {version} =====")

    HACTOOL_PROGRAM = "hactool"
    if os.path.isfile(version + "/dev"):
        HACTOOL_PROGRAM += " --dev"

    esuncompressed = version + "/uncompressed_es.nso0"
    nifmuncompressed = version + "/uncompressed_nifm.nso0"
    exfatuncompressed = version + "/uncompressed_exfat.kip1"
    fat32uncompressed = version + "/uncompressed_fat32.kip1"
    fat32compressed = version + "/compressed_exfat.kip1"
    exfatcompressed = version + "/compressed_fat32.kip1"

    with open(esuncompressed, 'rb') as fi:
        read_data = fi.read()
    result = re.search(b'.\x63\x00.{3}\x00\x94\xa0.{2}\xd1.{2}\xff\x97', read_data)
    patch = "%06X%s%s" % (result.end(), "0004", "E0031FAA")
    text_file = open("../atmosphere/exefs_patches/es_patches/" + get_es_build_id() + ".ips", "wb")
    print("es build-id: " + get_es_build_id())
    print("es offset and patch at: " + patch)
    text_file.write(bytes.fromhex(str("5041544348" + patch + "454F46")))
    text_file.close()
    fi.close()

    with open(nifmuncompressed, 'rb') as fi:
        read_data = fi.read()
    result = re.search(b'.{16}\xf5\x03\x01\xaa\xf4\x03\x00\xaa.{4}\xf3\x03\x14\xaa\xe0\x03\x14\xaa\x9f\x02\x01\x39\x7f\x8e\x04\xf8', read_data)
    text_file = open("../atmosphere/exefs_patches/nifm_ctest/" + get_nifm_build_id() + ".ips", "wb")
    patch = "%06X%s%s" % (result.start(), "0008", "E0031FAAC0035FD6")
    print("nifm build-id: " + get_nifm_build_id())
    print("nifm offset and patch at: " + patch)
    text_file.write(bytes.fromhex(str("5041544348" + patch + "454F46")))
    text_file.close()
    fi.close()

    with open(exfatuncompressed, 'rb') as fi1:
        read_data = fi1.read()
        result1 = re.search(b'.{3}\x12.{3}\x71.{3}\x54.{3}\x12.{3}\x71.{3}\x54.{3}\x36.{3}\xf9', read_data)
        result2 = re.search(b'.{3}\xaa.{3}\x97.{3}\x36.{3}\x91.{3}\xaa.{7}\xaa.{11}\xaa.{7}\x52.{3}\x72.{3}\x97', read_data)
        patch1 = "%06X%s%s" % (result1.end(), "0004", "E0031F2A")
        patch2 = "%06X%s%s" % (result2.end(), "0004", "1F2003D5")
        exfathash = hashlib.sha256(open(exfatcompressed, 'rb').read()).hexdigest().upper()
        print("found FS first offset and patch at: " + patch1)
        print("found FS second offset and patch at: " + patch2)
        print("exfat sha256: " + exfathash)
        text_file = open('../atmosphere/kip_patches/fs_patches/%s.ips' % exfathash, 'wb')
        text_file.write(bytes.fromhex(str("5041544348" + patch1 + patch2 + "454F46")))
        text_file.close()
        fat32hash = hashlib.sha256(open(fat32compressed, 'rb').read()).hexdigest().upper()
        print("fat32 sha256: " + fat32hash)
        text_file = open('../atmosphere/kip_patches/fs_patches/%s.ips' % fat32hash, 'wb')
        text_file.write(bytes.fromhex(str("5041544348" + patch1 + patch2 + "454F46")))
        text_file.close()
        text_file = open('../hekate_patches/' + version + '.ini', 'w')
        text_file.write('\n')
        text_file.write("#FS " + version + "-fat32\n")
        text_file.write("[FS:" + '%s' % fat32hash[:16] + "]\n")
        hekate_bytes = fi1.seek(result1.end())
        text_file.write('.nosigchk=0:0x' + '%05X' % (result1.end()-0x100) + ':0x4:' + fi1.read(0x4).hex().upper() + ',E0031F2A\n')
        hekate_bytes = fi1.seek(result2.end())
        text_file.write('.nosigchk=0:0x' + '%05X' % (result2.end()-0x100) + ':0x4:' + fi1.read(0x4).hex().upper() + ',1F2003D5\n')
        text_file.write('\n')
        text_file.write("#FS " + version + "-exfat\n")
        text_file.write("[FS:" + '%s' % exfathash[:16] + "]\n")
        hekate_bytes = fi1.seek(result1.end())
        text_file.write('.nosigchk=0:0x' + '%05X' % (result1.end()-0x100) + ':0x4:' + fi1.read(0x4).hex().upper() + ',E0031F2A\n')
        hekate_bytes = fi1.seek(result2.end())
        text_file.write('.nosigchk=0:0x' + '%05X' % (result2.end()-0x100) + ':0x4:' + fi1.read(0x4).hex().upper() + ',1F2003D5\n')
        text_file.close()
    fi1.close()