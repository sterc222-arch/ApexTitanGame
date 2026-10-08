[app]
title = Apex Titan
package.name = apextitan
package.domain = org.sterc222.apextitan
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,wav,ttf
version = 0.1
requirements = hostpython3==3.10.14, python3==3.10.14, pygame
orientation = portrait
fullscreen = 1

android.permissions = VIBRATE
android.api = 33
android.minapi = 21
android.archs = arm64-v8a
android.allow_backup = True
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
