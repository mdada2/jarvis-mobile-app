[app]

# App Info
title = JARVIS
package.name = jarvis
package.domain = org.jarvis
version = 1.0

# Source
source.dir = .
source.include_exts = py,png,jpg,kv,json

# Requirements - MINIMAL for faster build
requirements = python3,kivy==2.3.0,requests

# UI Settings
orientation = portrait
fullscreen = 0

# Permissions - Only essential
android.permissions = INTERNET

# Android Settings - OPTIMIZED for speed
android.api = 31
android.minapi = 21
android.ndk = 25b

# Build ONLY for arm64 (faster, modern devices)
android.archs = arm64-v8a

# Skip updates for faster build
android.skip_update = True
android.accept_sdk_license = True

# Gradle
android.gradle = True

# Entry point
android.entrypoint = org.kivy.android.PythonActivity

[buildozer]
# Debug logging
log_level = 2
warn_on_root = 0
