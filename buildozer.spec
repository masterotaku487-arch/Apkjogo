[app]

# ── Informações do app ──────────────────────────────────────
title           = Evolucao Real
package.name    = evolucaoreal
package.domain  = com.seuapp

source.dir      = .
source.include_exts = py,png,jpg,kv,atlas,json
source.include_patterns = assets/*

version         = 1.0.0

# ── Dependências ────────────────────────────────────────────
requirements    = python3,kivy==2.3.0,kivymd

# ── Orientação ──────────────────────────────────────────────
orientation     = portrait

# ── Android ─────────────────────────────────────────────────
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api         = 33
android.minapi      = 21
android.ndk         = 25b
android.sdk         = 33
android.archs       = arm64-v8a, armeabi-v7a
android.allow_backup= True
android.release_artifact = apk

# Cor da tela de splash (hex sem #)
android.presplash_color  = #0A0A17
android.window_softinput_mode = adjustResize

# ── iOS (futuro) ─────────────────────────────────────────────
#ios.kivy_ios_url = https://github.com/kivy/kivy-ios
#ios.kivy_ios_branch = master

# ── Build ────────────────────────────────────────────────────
[buildozer]
log_level = 2
warn_on_root = 1
