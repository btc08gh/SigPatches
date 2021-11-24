Part 1A: Setting up Ghidra

This guide is done on Windows 10, and assumes you have some sort of git shell installed, and also that you're competent enough to be able to open cmd terminals at the location you want.

1. get openjdk 11 lts https://adoptium.net/
2. install openjdk that you just downloaded (make sure to set JAVA_HOME path while installing)
3. get ghidra https://github.com/NationalSecurityAgency/ghidra/releases/latest
4. extract it (example ghidra_10.0.3_PUBLIC_20210908.zip), and move the folder (example "ghidra_10.0.3_PUBLIC") to C:/ghidra/ghidra_10.0.3_PUBLIC
5. get the code repository, using git clone "git clone https://github.com/Adubbz/Ghidra-Switch-Loader"
6. open a terminal cmd prompt in the folder you just git cloned and put "set GHIDRA_INSTALL_DIR=C:/ghidra/ghidra_10.0.3_PUBLIC" without quotations into your cmd terminal, powershell or manually as an enviroment variable. (this value is only retained while the cmd window is open, don't rely on the "set" command for different sessions)
7. run gradlew in the Ghidra-Switch-Loader directory by doing putting "gradlew.bat" in your cmd/powershell terminal.
8. go to your ghidra folder (should be C:\ghidra\ghidra_10.0.3_PUBLIC in this specific example)
9. Click "File" top left then "Install extensions"
10. press the + button in upper right corner.
11. Navigate to your Ghidra-Switch-Loader folder and then into the "dist" folder it made, then select the .zip that should be in there.
12. restart ghidra

![alt text](https://github.com/borntohonk/SigPatches/blob/master/img/ghidra-w.png?raw=true)
