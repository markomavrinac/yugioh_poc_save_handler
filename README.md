# yugioh_poc_save_handler
Yu-Gi-Oh! Power of Chaos save handler - A script to manage your save games across multiple computers

![YPOCSH](https://imgur.com/BX8htVs)

At startup, the script scans your registry for key related to game save files.
The script also attempts to locate your common folder according to the registry entry, if it fails, user will be prompted to browse for common folder.
If actual common folder path doesn't match the one in registry, the script can fix this for you by updating registry with the correct path.

In main menu, pick any slot by pressing slot number (1-5)
A slot can be empty or occupied (occupied slot should contain a text file containing your flcrc registry entry data, as well as system.dat file that matches that registry entry).
When opening a slot, you have an option to backup current game data to it and if it's occupied, you have an additional option to restore backup to the computer running the script.

It's possible the script has a minor bug here and there, feel free to contact me if you encounter any issues!
