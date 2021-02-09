Windows Extras
==============

associate_shoebot_win.reg
-------------------------

This file adds registry entries that associate .bot files to Shoebot.

To associate .bot files to shoebot, double-click on the registry file and allow the keys to be added (requires administrator).
You might have to right click on a .bot file, select "open with," then select "choose another app" then select "shoebot.exe" - "always use this app to open .bot files" the first time you open a bot file directly to add the association to your user account.

If MinGW64 is not installed in the default directory `(C:\mingW64)`, you may have to edit the registry file with a text editor.

For example, change `"C:\\msys64\\mingw64\\bin\\shoebot.exe\"` to the location where MinGW is installed, such as:`"C:\\users\\I am a User\\Desktop\\Cool Vector Stuff\\msys64\\mingw64\\bin\\shoebot.exe\"` in two places

shoebot-shortcut.lnk
--------------------

This is a shortcut to Shoebot if MinGW64 is installed in the default directory.

It can be placed on the desktop, in the start menu, or pinned to the start menu. You can use 

shoebot.ico
-----------
for it's icon if you want. It's a modern Windows-style icon. Just put the icon somewhere and point to it with the shortcut -- right click on the shortcut, select "Properties," click "Change Icon," then click "Browse" and point the target to wherever you put the icon.






