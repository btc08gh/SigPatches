import re


def get_build_id():
    with open('uncompressed_usb.nso0', 'rb') as f:
        f.seek(0x40)
        return(f.read(0x14).hex().upper())

with open('uncompressed_usb.nso0', 'rb') as usbf:
    read_data = usbf.read()
    result1 = re.search(b'\xd1.{3}\xa9.{3}\x91.{3}\x52.{3}\x72.{3}\xb9.{7}\x91.{7}\x91.{3}\xa9', read_data).start() - 0x103  
    result2 = result1 + 0x90
    patch1 = '    { 0x%04X, "\\x20\\x00\\x80\\x52\\xC0\\x03\\x5F\\xD6", 8 },' % (result1)
    patch2 = '    { 0x%04X, "\\x20\\x00\\x80\\x52\\xC0\\x03\\x5F\\xD6", 8 },' % (result2)
    print('note: usb patch not generated, only printed to see if the offsets has changed to compare against Loader')
    print(patch1)
    print(patch2)
    print('    { ParseModuleID("' + get_build_id() + '"), util::size(Usb30ForceEnablePatches_XX_X_X), Usb30ForceEnablePatches_XX_X_X },\n')
    print('see this link for more information:')
    print('https://github.com/Atmosphere-NX/Atmosphere/blob/master/stratosphere/loader/source/ldr_embedded_usb_patches.inc\n')
usbf.close()