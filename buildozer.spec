[app]

# (str) Title of your application
title = Pixel Adventure Metal Slopes

# (str) Package name
package.name = pixeladventure

# (str) Package domain
package.domain = org.test

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include
source.include_exts = py,json,txt,png,jpg,atlas,mp3,wav,ogg

# (str) Application versioning
version = 0.1

# (list) Application requirements
# Фиксируем версии Python и Cython (с маленькой буквы), чтобы Pygame собрался
requirements = python3==3.10.12, hostpython3==3.10.12, cython==0.29.33, pygame

# (list) Supported orientations
orientation = landscape

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (list) Permissions
android.permissions = android.permission.INTERNET, android.permission.WRITE_EXTERNAL_STORAGE

# (int) Target Android API
android.api = 33

# (int) Minimum API
android.minapi = 24

# (bool) Automatically accept SDK license
android.accept_sdk_license = True

# (list) The Android archs to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup feature
android.allow_backup = True

#
# Python for android (p4a) specific
#

# КРИТИЧЕСКИ ВАЖНО: для Pygame нужен SDL2 bootstrap (НЕ kivy!)
p4a.bootstrap = sdl2

# Указываем ваш главный файл (если он называется не main.py)
android.app_main = game_android.py

[buildozer]

log_level = 2
warn_on_root = 1
