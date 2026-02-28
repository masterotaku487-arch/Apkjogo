[app]
title           = Evolucao Real
package.name    = evolucaoreal
package.domain  = com.seuapp

source.dir      = .
source.include_exts = py,png,jpg,kv,atlas,json

version         = 1.0.0

requirements    = python3,kivy==2.3.0

orientation     = portrait

# ✅ CORREÇÃO: forçar build-tools estável (sem licença preview)
android.build_tools_version = 33.0.0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api         = 33
android.minapi      = 21
android.ndk         = 25b
android.archs       = arm64-v8a

android.presplash_color  = #0A0A17
android.allow_backup     = True
android.release_artifact = apk

[buildozer]
log_level = 2
warn_on_root = 1
