Part 2 of this guide assumes you have succesfully set up ghidra as described in Part1A (for windows users) or Part1B (for linux users).

Part 2 will go through the basics of getting the type of switch binaries you need. To proceed you will need hactool (https://github.com/SciresM/hactool) for opening switch binaries, the binaries for hactool can be gotten from the artifacts (requires logging into github) or compiling it yourself. Lockpick_RCM (https://github.com/shchmue/Lockpick_RCM) for getting the keys required for hactool to open said switch binaries. Set up an enviroment variable for hactool / place it /usr/local/bin/hactool if you're a linux user.

Part 2 also assumes you have python 3 installed.

1. Run the lockpick_RCM binary on a nintendo switch capable of doing so.

2. Copy the outputting prod.keys (located on your switch sd card at /switch/prod.keys) to ~/.switch/prod.keys (this translates to /home/youruser/.switch/prod.keys and C:/users/youruser/.switch/prod.keys).

3. Run "hactool -t keygen" in your terminal/cmd prompt to verify it populates a list of keys.
   - Assuming you completed step 3 and it does produce a list of keys, you should now be capable of extracting .ncas, this specific guide (part 2) will cover system firmware files.

4. Dump your own system version files or get them from https://darthsternie.net/switch-firmwares/ this specific example will will use the latest version at the time of writing this, 13.0.0

5. Organize the .nca containers in a fashion that lets you identify them more easily, a script to do that and also output a copy of compressed/uncompressed versions of binaries can be found here: [firmware_organizer.py](firmware_organizer.py) Usage: create a folder called "firmware", put firmware .ncas inside of the "firmware" folder then use "python firmware_organizer.py" (this should also be covered in Part 2 of the tutorial)
   - Take note of the buildid that is output. (which is 8CB532EA199207191F04CE3DDECEC854C7CF07D6000000000000000000000000 in this example for nifm)
   - You should now have the system firmware files organized by titleid in the folder you had them in.
   - For this example we will use "010000000000000F", "nifm". You should already have an "uncompressed_nifm.nso0" output if you used firmware_organizer.py.

6. Open ghidra, make a new project where you want.
   - Click File -> import file -> Select uncompressed_nifm.nso0 that you just extracted (make certain it says the format is Nintendo Switch Binary)
   - Click the dragon to open the ghidra CodeBrowser.
   - Click File -> open uncompressed_nifm.nso0 (that you added to the project)
   - Click yes to analyze, and tick the switch-ipc option, then click analyze. Then let the process run until completed. If there are any errors, just hit "Ok"
   
![alt text](https://github.com/borntohonk/SigPatches/blob/master/img/ghidra-nso.png?raw=true)

7. For this specific example the intent is to make a function that otherwise usually looks for X-Organization: Nintendo to be true, if it does not find it to be true your wifi/lan adapter is disabled. We're going to make it do the opposite.
   - To find this offset of the function, press S to open memory search mode, and search for this HEX string ".. .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. f5 03 01 aa f4 03 00 aa .. .. .. .. f3 03 14 aa e0 03 14 aa 9f 02 01 39 7f 8e 04 f8", the the start offset of the result is the offset to grab for the patch.

![alt text](https://github.com/borntohonk/SigPatches/blob/master/img/ghidra-nifm-offset.png?raw=true)

8. The patch we want to make is to change out the instruction at that offset, with "MOV X0, XZR" + "RET" (E0 03 1F AA C0 03 5F D6) - This will make the function at offset 01 07 14 to end instead of doing the function it previously did, essentially cutting it short. (These are ARM instructions)

**note:** the offsets ghidra-loader gives you are -0x100, so the resulting offset we use in the next part is +0x100 (01 08 14, up from 01 07 14)

9. To use this patch on the switch, you're going to want to save "50 41 54 43 48 01 08 14 00 08 E0 03 1F AA C0 03 5F D6 45 4F 46" as 8CB532EA199207191F04CE3DDECEC854C7CF07D6.ips (the build id that you got earlier) "50 41 54 43 48" is "PATCH", "01 08 14" is the offset we're patching, "00 08" is the length of patch we're applying, "E0 03 1F AA C0 03 5F D6" Is the patch we are applying at that offset (MOV X0, XZR" and "RET"), and 45 4F 46 is EOF. This effectively patches out the "connectivity test" and lets you use network functionality on closed networks where otherwise X-Organization: Nintendo would never be returned to the console. (You can look at the table below to get a more visual concept of how this patch is structured)

| PATCH magic | Offset | Size of patch | Patch to be applied | EOF magic |
| :---: | :---: | :---: | :---: | :---: |
| 50 41 54 43 48 | 01 08 14 | 00 08 | E0 03 1F AA C0 03 5F D6 | 45 4F 46 |

10. You should now have a functional patch for nifm for system firmware version 13.0.0, and it can be used with Atmosphere by putting it into /atmosphere/exefs_patches/nifm_ctest/8CB532EA199207191F04CE3DDECEC854C7CF07D6.ips

* [Python script to generate nifm patches, usage: place uncompressed nifm as "main" in the same folder then use "python3 nifm_patch.py" (pattern applicable for 12.0.0 and up)](nifm_patch.py)
