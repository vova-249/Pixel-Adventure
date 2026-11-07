[app]
title = Pixel Adventure
package.name = pixeladventure
package.domain = org.test
source.dir = .
source.include_exts = py,json,txt,png,jpg,mp3,wav,ogg
version = 0.1

# Используем pygame-ce (он стабильнее собирается под Android)
requirements = python3==3.10.12, hostpython3==3.10.12, cython==0.29.33, pygame-ce
orientation = landscape
fullscreen = 1
android.permissions = android.permission.INTERNET, android.permission.WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 24
android.accept_sdk_license = True
android.archs = arm64-v8a

# Жестко фиксируем стабильный NDK
android.ndk = 23b

# КРИТИЧЕСКИ ВАЖНО: Pygame требует SDL2
p4a.bootstrap = sdl2
android.app_main = game_android.py

[buildozer]
log_level = 2
warn_on_root = 1

# ОБХОД ОШИБКИ СЕТИ: указываем путь к уже установленному ANT в системе GitHub
android.ant_path = /usr/share/ant
