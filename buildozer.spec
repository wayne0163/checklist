[app]
title = 交易前清单
package.name = checklistapp
package.domain = com.checklistapp
version = 0.1.0
source.dir = .
source.include_exts = py,kv,md,png,jpg,ttf

requirements = python3,kivy==2.3.0,kivymd==1.1.1,plyer==2.1.0
orientation = portrait
fullscreen = 1

# Build for common Android ABIs to improve install success on friends' devices
android.archs = arm64-v8a, armeabi-v7a

# Android 图标（可选）
# icon.filename = assets/icon.png

[buildozer]
log_level = 2

[android]
android.api = 33
android.minapi = 24
android.sdk = 33
# 若需直接写外部存储，建议后续接入 SAF（androidstorage4kivy）
# android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
# targetSandboxVersion 等高级设置按需开启
