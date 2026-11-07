[app]
title = Pixel Adventure
package.name = pixeladventure
package.domain = org.test
source.dir = .
source.include_exts = py,json,txt,png,jpg,mp3,wav,ogg
version = 0.1
requirements = python3==3.10.12, hostpython3==3.10.12, cython==0.29.33, pygame-ce
orientation = landscape
fullscreen = 1
android.permissions = android.permission.INTERNET, android.permission.WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 24
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.ndk = 23b
p4a.bootstrap = sdl2
android.app_main = game_android.py

[buildozer]
log_level = 2
warn_on_root = 1
