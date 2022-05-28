This repository contains "signature patch" bundle releases, and tutorials on how to make them, aswell as scripts to automate/simplify the process to make them.

14.0.0 firmware revision note:
A lot of things changed in ES, FS, NIFM for 14.0.0, most notably, you now need to generate separate fs patches.

* Ghidra/Patch making tutorial:
  - Part 1A detailing how to set up ghidra and the switch loader for windows [(link)](guides/Part1A-WindowsSetup.MD)
  - Part 1B detailing how to set up ghidra and the switch loader for linux [(link)](guides/Part1B-LinuxSetup.MD)
  - Part 2 detailing how to set up hactool and use the firmware organizer to output files to work further with, and a basic introduction to ghidra with making patches for nifm as an example. [(link)](guides/Part2.MD)

* Various Guides and scripts to make patches:
  - Python script to generate nifm patches, usage: place uncompressed nifm as "main" in the same folder then use "python scripts/nifm_patch.py" (pattern applicable for 12.0.0 and up) [(link)](scripts/nifm_patch.py)
  - Guide describing how to patch out the online check in Diablo 2 Resurrected - TitleID 0100726014352000/0100726014352800. for v65536-v589824+++ [(link)](guides/D2R-0100726014352800.md)
  - Python script to generate D2R patches, usage: place uncompressed D2R as "main" in the same folder then use "python scripts/d2r_patch.py" [(link)](scripts/d2r_patch.py)
  - Guide describing how to patch FS, - TitleID 0100000000000819/010000000000081B. [(link)](guides/FS-010000000000081B-0100000000000819.md)
  - Python script to generate FS patches, usage: place uncompressed_exfat.kip1, compressed_exfat.kip1 and compressed_fat32.kip1 in the same folder then use "python scripts/fs_patch.py" [(link)](scripts/fs_patch.py)
  - Guide describing how to patch ES, - TitleID 0100000000000033. [(link)](guides/ES-0100000000000033.md)
  - Python script to generate ES patches, usage: place uncompressed ES as "main" in the same folder then use "python scripts/es_patch.py" [(link)](scripts/es_patch.py)
  - Python script to generate patches for Atmospheres loader re-implementation, requires lz4 from pip, usage: use "python scripts/loader_patch.py" and it will automatically download, make patches, then clean up after itself. And then make a combined bundle ready for release under filename SigPatches.zip [(link)](scripts/loader_patch.py)
  - Python script to process dumped FW files from system partition and organize then output binaries of interest, Usage: create a folder called "firmware", put firmware .ncas inside of the "firmware" folder then use "python scripts/firmware_organizer.py." [(link)](scripts/firmware_organizer.py)

* Powerful batch-processing script capable of processing multiple system firmwares at once, while also outputting patches for each one:
  - Python script to process dumped FW files from system partition and make patches for the system firmware version that was dumped. Usage: make a directory in the organize folder (example 13.0.0 , or just generic "firmware" instead of numbered folders, anything works.), then place the dumped nca.00/nca files/folders (both works) in a sub-folder called "nca" (example: organize/13.0.0/nca/*.nca), then use "cd organize && python organize.py". The patches will be output to the atmosphere folder, ready to be packed up and pushed as a release [(link)](organize/organize.py)

* Credits: [@borntohonk](https://github.com/borntohonk)
