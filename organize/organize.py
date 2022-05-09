#!/usr/bin/env python

from pathlib import Path
from glob import glob
import subprocess
import shutil
import re
import os
import hashlib
import errno
VERBOSE = False


def get_es_build_id():
    with open(version + "/uncompressed_es.nso0", "rb") as f:
        f.seek(0x40)
        return(f.read(0x14).hex().upper())


def get_nifm_build_id():
    with open(version + "/uncompressed_nifm.nso0", "rb") as f:
        f.seek(0x40)
        return(f.read(0x14).hex().upper())


def get_usb_build_id():
    with open(version + "/uncompressed_usb.nso0", "rb") as f:
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
        newName = version + "/nca/" + ncaid + "." + \
            ".".join(os.path.basename(ncaFull).split(".")[1:])
        print_verbose(f"{ncaFull} -> {newName}")
        os.rename(ncaFull, newName)
        ncaFull = newName

        # Ensure meta files have .cnmt.nca extension
        process = subprocess.Popen(
            ["hactool", "--intype=nca", ncaFull], stdout=subprocess.PIPE, universal_newlines=True)
        contentType = process.communicate()[0].split(
            "Content Type:                       ")[1].split("\n")[0]
        if contentType == "Meta" and not nca.endswith(".cnmt.nca"):
            print_verbose(ncaFull + " -> " +
                          ".".join(ncaFull.split(".")[:-1]) + ".cnmt.nca")
            shutil.move(ncaFull, ".".join(
                ncaFull.split(".")[:-1]) + ".cnmt.nca")

    print("# Sort by titleid")
    for nca in os.listdir(version + "/nca"):
        ncaFull = version + "/nca/" + nca
        process = subprocess.Popen(
            ["hactool", "--intype=nca", ncaFull], stdout=subprocess.PIPE, universal_newlines=True)
        titleId = process.communicate()[0].split(
            "Title ID:                           ")[1].split("\n")[0]
        process = subprocess.Popen(
            ["hactool", "--intype=nca", ncaFull], stdout=subprocess.PIPE, universal_newlines=True)
        contentType = process.communicate()[0].split(
            "Content Type:                       ")[1].split("\n")[0]

        mkdirp(version + "/titleid/" + titleId)

        print_verbose(version + "/titleid/" + titleId + "/" +
                      contentType + ".nca -> " + "../../nca/" + nca)
        shutil.copyfile(version + "/nca/" + nca, version +
                        "/titleid/" + titleId + "/" + contentType + ".nca")

    print("# Extracting ES")
    esFull = version + "/"
    ncaParent = version + "/titleid/0100000000000033"
    ncaPartial = ncaParent + "/Program.nca"
    ncaFull = version + "/titleid/0100000000000033/exefs/main"
    process = subprocess.Popen(["hactool", "--intype=nca", "--exefsdir=" + version + "/titleid/0100000000000033/exefs/",
                               version + "/titleid/0100000000000033/Program.nca"], stdout=subprocess.DEVNULL)
    process.wait()
    process = subprocess.Popen(["hactool", "--intype=nso0", "--uncompressed=" +
                               version + "/uncompressed_es.nso0", ncaFull], stdout=subprocess.DEVNULL)
    process.wait()

    print("# Extracting USB")
    esFull = version + "/"
    ncaParent = version + "/titleid/0100000000000006"
    ncaPartial = ncaParent + "/Program.nca"
    ncaFull = version + "/titleid/0100000000000006/exefs/main"
    process = subprocess.Popen(["hactool", "--intype=nca", "--exefsdir=" + version + "/titleid/0100000000000006/exefs/",
                               version + "/titleid/0100000000000006/Program.nca"], stdout=subprocess.DEVNULL)
    process.wait()
    process = subprocess.Popen(["hactool", "--intype=nso0", "--uncompressed=" +
                               version + "/uncompressed_usb.nso0", ncaFull], stdout=subprocess.DEVNULL)
    process.wait()

    print("# Extracting NIFM")
    nifmFull = version + "/"
    ncaParent = version + "/titleid/010000000000000f"
    ncaPartial = ncaParent + "/Program.nca"
    ncaFull = version + "/titleid/010000000000000f/exefs/main"
    process = subprocess.Popen(["hactool", "--intype=nca", "--exefsdir=" + version + "/titleid/010000000000000f/exefs/",
                               version + "/titleid/010000000000000f/Program.nca"], stdout=subprocess.DEVNULL)
    process.wait()
    process = subprocess.Popen(["hactool", "--intype=nso0", "--uncompressed=" +
                               version + "/uncompressed_nifm.nso0", ncaFull], stdout=subprocess.DEVNULL)
    process.wait()

    print("# Extracting fat32")
    ncaParent = version + "/titleid/0100000000000819"
    pk21dir = ncaParent + "/romfs/nx/package2"
    ini1dir = ncaParent + "/romfs/nx/ini1"
    ncaFull = ncaParent + "/Data.nca"
    fat32Full = version + "/uncompressed_fat32.kip1"
    process = subprocess.Popen(["hactool", "--intype=nca", "--romfsdir=" +
                               ncaParent + "/romfs", ncaFull], stdout=subprocess.DEVNULL)
    process.wait()
    process = subprocess.Popen(
        ["hactool", "--intype=pk21", "--ini1dir=" + ini1dir, pk21dir], stdout=subprocess.DEVNULL)
    process.wait()
    process = subprocess.Popen(["hactool", "--intype=kip1", "--uncompressed=" +
                               fat32Full, ini1dir + "/FS.kip1"], stdout=subprocess.DEVNULL)
    process.wait()
    fat32Compressed = version + "/titleid/0100000000000819/romfs/nx/ini1/FS.kip1"
    fsCopy = version + "/compressed_fat32.kip1"
    process = shutil.copyfile(fat32Compressed, fsCopy)

    print("# Extracting exfat")
    ncaParent = version + "/titleid/010000000000081b"
    pk21dir = ncaParent + "/romfs/nx/package2"
    ini1dir = ncaParent + "/romfs/nx/ini1"
    ncaFull = ncaParent + "/Data.nca"
    exfatFull = version + "/uncompressed_exfat.kip1"
    process = subprocess.Popen(["hactool", "--intype=nca", "--romfsdir=" +
                               ncaParent + "/romfs", ncaFull], stdout=subprocess.DEVNULL)
    process.wait()
    process = subprocess.Popen(
        ["hactool", "--intype=pk21", "--ini1dir=" + ini1dir, pk21dir], stdout=subprocess.DEVNULL)
    process.wait()
    process = subprocess.Popen(["hactool", "--intype=kip1", "--uncompressed=" +
                               exfatFull, ini1dir + "/FS.kip1"], stdout=subprocess.DEVNULL)
    process.wait()
    exfatCompressed = version + "/titleid/010000000000081b/romfs/nx/ini1/FS.kip1"
    fsCopy = version + "/compressed_exfat.kip1"
    process = shutil.copyfile(exfatCompressed, fsCopy)

for version in os.listdir("."):
    # Ignore files (only treat directories)
    if os.path.isfile(version):
        continue

    print(f"===== Making patches for {version} =====")
    changelog = open('../fw_patch_changelog/' + version + '.txt', 'w')
    changelog.write("Patch changelog for " + version + ": \n")
    changelog.write("\n")
    HACTOOL_PROGRAM = "hactool"
    if os.path.isfile(version + "/dev"):
        HACTOOL_PROGRAM += " --dev"

    esuncompressed = version + "/uncompressed_es.nso0"
    nifmuncompressed = version + "/uncompressed_nifm.nso0"
    usbuncompressed = version + "/uncompressed_usb.nso0"
    exfatuncompressed = version + "/uncompressed_exfat.kip1"
    fat32uncompressed = version + "/uncompressed_fat32.kip1"
    exfatcompressed = version + "/compressed_exfat.kip1"
    fat32compressed = version + "/compressed_fat32.kip1"

    with open(usbuncompressed, 'rb') as usbf:
        read_data = usbf.read()
        result1 = re.search(
            b'\xd1.{3}\xa9.{3}\x91.{3}\x52.{3}\x72.{3}\xb9.{7}\x91.{7}\x91.{3}\xa9', read_data).start() - 0x103
        result2 = result1 + 0x90
        patch1 = '    { 0x%04X, "\\x20\\x00\\x80\\x52\\xC0\\x03\\x5F\\xD6", 8 },' % (
            result1)
        patch2 = '    { 0x%04X, "\\x20\\x00\\x80\\x52\\xC0\\x03\\x5F\\xD6", 8 },' % (
            result2)
        changelog.write("USB related patch changelog for " + version + ": \n")
        changelog.write(patch1 + "\n")
        changelog.write(patch2 + "\n")
        changelog.write('    { ParseModuleID("' + get_usb_build_id() + '"), util::size(Usb30ForceEnablePatches_XX_X_X), Usb30ForceEnablePatches_XX_X_X },\n')
        changelog.write("\n")
    usbf.close()

    es_patch = '../SigPatches/atmosphere/exefs_patches/es_patches/' + get_es_build_id() + \
        '.ips'
    if es_patch in glob('../SigPatches/atmosphere/exefs_patches/es_patches/*.ips'):
        changelog.write("ES related patch changelog for " + version + ": \n")
        changelog.write("ES patch for version " + version + " already exists as an .ips patch, and the build id is: " + get_es_build_id() + "\n")
        changelog.write("\n")
    else:
        with open(esuncompressed, 'rb') as esf:
            read_data = esf.read()
            result = re.search(
                b'.\x63\x00.{3}\x00\x94\xa0.{2}\xd1.{2}\xff\x97', read_data)
            patch = "%06X%s%s" % (result.end(), "0004", "E0031FAA")
            text_file = open("../SigPatches/atmosphere/exefs_patches/es_patches/" + get_es_build_id() + ".ips", "wb")
            changelog.write("ES related patch changelog for " + version + ": \n")
            changelog.write(version + " ES build-id: " + get_es_build_id() + "\n")
            changelog.write(version + " ES offset and patch at: " + patch + "\n")
            changelog.write("\n")
            text_file.write(bytes.fromhex(
                str("5041544348" + patch + "454F46")))
            text_file.close()
        esf.close()

    nifm_patch = '../SigPatches/atmosphere/exefs_patches/nifm_ctest/' + \
        get_nifm_build_id() + '.ips'
    if nifm_patch in glob('../SigPatches/atmosphere/exefs_patches/nifm_ctest/*.ips'):
        changelog.write("NIFM CTEST related patch changelog for " + version + ": \n")
        changelog.write("NIFM CTEST patch for version " + version + " already exists as an .ips patch, and the build id is: " + get_nifm_build_id() + "\n")
        changelog.write("\n")
    else:
        with open(nifmuncompressed, 'rb') as nifmf:
            read_data = nifmf.read()
            result = re.search(
                b'.{16}\xf5\x03\x01\xaa\xf4\x03\x00\xaa.{4}\xf3\x03\x14\xaa\xe0\x03\x14\xaa\x9f\x02\x01\x39\x7f\x8e\x04\xf8', read_data)
            text_file = open("../SigPatches/atmosphere/exefs_patches/nifm_ctest/" + get_nifm_build_id() + ".ips", "wb")
            patch = "%06X%s%s" % (result.start(), "0008", "E0031FAAC0035FD6")
            changelog.write("NIFM related patch changelog for " + version + ": \n")
            changelog.write(version + " NIFM CTEST build-id: " + get_nifm_build_id() + "\n")
            changelog.write(version + " NIFM CTEST offset and patch at: " + patch + "\n")
            changelog.write("\n")
            text_file.write(bytes.fromhex(
                str("5041544348" + patch + "454F46")))
            text_file.close()
        nifmf.close()

    fat32hash = hashlib.sha256(
        open(fat32compressed, 'rb').read()).hexdigest().upper()
    with open('../hekate_patches/fs_patches.ini') as fs_patches:
        if fat32hash[:16] in fs_patches.read():
            changelog.write("FS-FAT32 patch related changelog for " + version + ": \n")
            changelog.write("FS-FAT32 patch for version " + version + " already exists in fs_patches.ini and as an .ips patch, with the short hash of: " + fat32hash[:16] + "\n")
            changelog.write("\n")
        else:
            with open(fat32uncompressed, 'rb') as fat32f:
                read_data = fat32f.read()
                result1 = re.search(b'.{3}\x12.{3}\x71.{3}\x54.{3}\x12.{3}\x71.{3}\x54.{3}\x36.{3}\xf9', read_data)
                result2 = re.search(b'\x1e\x42\xb9\x1f\xc1\x42\x71', read_data)
                patch1 = "%06X%s%s" % (result1.end(), "0004", "E0031F2A")
                patch2 = "%06X%s%s" % (result2.start() - 0x5, "0004", "1F2003D5")
                changelog.write("FS-FAT32 patch related changelog for " + version + ": \n")
                changelog.write(version + " First FS-FAT32 offset and patch at: " + patch1 + "\n")
                changelog.write(version + " Second FS-FAT32 offset and patch at: " + patch2 + "\n")
                changelog.write(version + " FS-FAT32 SHA256 hash: " + fat32hash + "\n")
                changelog.write("\n")
                fat32_ips = open('../SigPatches/atmosphere/kip_patches/fs_patches/%s.ips' % fat32hash, 'wb')
                fat32_ips.write(bytes.fromhex(str("5041544348" + patch1 + patch2 + "454F46")))
                fat32_ips.close()
                fat32_hekate = open('../hekate_patches/fs_patches.ini', 'a')
                fat32_hekate.write('\n')
                fat32_hekate.write("#FS " + version + "-fat32\n")
                fat32_hekate.write("[FS:" + '%s' % fat32hash[:16] + "]\n")
                hekate_bytes = fat32f.seek(result1.end())
                fat32_hekate.write('.nosigchk=0:0x' + '%06X' % (result1.end()-0x100) + ':0x4:' + fat32f.read(0x4).hex().upper() + ',E0031F2A\n')
                hekate_bytes = fat32f.seek(result2.start() - 0x5)
                fat32_hekate.write('.nosigchk=0:0x' + '%06X' % (result2.start()-0x105) + ':0x4:' + fat32f.read(0x4).hex().upper() + ',1F2003D5\n')
                fat32_hekate.close()
            fat32f.close()
    fs_patches.close()

    exfathash = hashlib.sha256(
        open(exfatcompressed, 'rb').read()).hexdigest().upper()
    with open('../hekate_patches/fs_patches.ini') as fs_patches:
        if exfathash[:16] in fs_patches.read():
            changelog.write("FS-ExFAT patch related changelog for " + version + ": \n")
            changelog.write("FS-ExFAT patch for version " + version + " already exists in fs_patches.ini and as an .ips patch, with the short hash of: " + exfathash[:16] + "\n")
        else:
            with open(exfatuncompressed, 'rb') as exfatf:
                read_data = exfatf.read()
                result1 = re.search(b'.{3}\x12.{3}\x71.{3}\x54.{3}\x12.{3}\x71.{3}\x54.{3}\x36.{3}\xf9', read_data)
                result2 = re.search(b'\x1e\x42\xb9\x1f\xc1\x42\x71', read_data)
                patch1 = "%06X%s%s" % (result1.end(), "0004", "E0031F2A")
                patch2 = "%06X%s%s" % ( result2.start() - 0x5, "0004", "1F2003D5")
                changelog.write("FS-ExFAT patch related changelog for " + version + ": \n")
                changelog.write(version + " First FS-ExFAT offset and patch at: " + patch1 + "\n")
                changelog.write(version + " Second FS-exFAT offset and patch at: " + patch2 + "\n")
                changelog.write(version + " FS-exFAT SHA256 hash: " + exfathash + "\n")
                exfat_ips = open('../SigPatches/atmosphere/kip_patches/fs_patches/%s.ips' % exfathash, 'wb')
                exfat_ips.write(bytes.fromhex(str("5041544348" + patch1 + patch2 + "454F46")))
                exfat_ips.close()
                exfat_hekate = open('../hekate_patches/fs_patches.ini', 'a')
                exfat_hekate.write('\n')
                exfat_hekate.write("#FS " + version + "-exfat\n")
                exfat_hekate.write("[FS:" + '%s' % exfathash[:16] + "]\n")
                hekate_bytes = exfatf.seek(result1.end())
                exfat_hekate.write('.nosigchk=0:0x' + '%06X' % (result1.end()-0x100) + ':0x4:' + exfatf.read(0x4).hex().upper() + ',E0031F2A\n')
                hekate_bytes = exfatf.seek(result2.start() - 0x5)
                exfat_hekate.write('.nosigchk=0:0x' + '%06X' % (result2.start()-0x105) + ':0x4:' + exfatf.read(0x4).hex().upper() + ',1F2003D5\n')
                exfat_hekate.close()
            exfatf.close()
    fs_patches.close()
    changelog.close()

    with open('../fw_patch_changelog/' + version + '.txt') as print_changelog:
        print(print_changelog.read())
    print_changelog.close()
