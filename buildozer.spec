[app]

title = Pixel Adventure Metal Slopes
package.name = pixeladventure
package.domain = org.test

source.dir = .
source.include_exts = py,json,txt,png,jpg,atlas,mp3,wav,ogg

version = 0.1

# Фиксируем версии Python и Cython для совместимости с pygame
requirements = python3==3.10.12, hostpython3==3.10.12, cython==0.29.33, pygame

orientation = landscape
fullscreen = 1

android.permissions = android.permission.INTERNET, android.permission.WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 24
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

# Используем проверенную версию NDK
android.ndk = 23b

# КРИТИЧЕСКИ ВАЖНО: Pygame требует SDL2, а не Kivy
p4a.bootstrap = sdl2

# Указываем ваш главный файл
android.app_main = game_android.py

[buildozer]
log_level = 2
warn_on_root = 1
