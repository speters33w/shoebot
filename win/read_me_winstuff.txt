These files assume MinGW64 is installed in default directory (C:\mingW64).

If not edit .reg file with a text editor, 
and shortcut properties target.

For example in shoebot.reg, change
"C:\\msys64\\mingw64\\bin\\shoebot.exe\"
to
"C:\\users\\I am a User\\Desktop\\Cool Vector Stuff\\msys64\\mingw64\\bin\\shoebot.exe"
in two places

and in shoebot.lnk right-click, select properties and change target and start in fields. Use the "Change Icon" button to target the icon if you want to use it.

To associate .bot files to shoebot, double-click on the registry file and allow the keys to be added (requires administrator).
You might have to right click on a .bot file, select "open with," and select shoebot.exe - always open with the first time you open a bot file directly.
