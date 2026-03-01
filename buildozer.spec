[app]
title           = Evolucao Real
package.name    = evolucaoreal
package.domain  = com.evolucaoreal

source.dir      = .
source.include_exts = py,png,jpg,kv,atlas,json
source.include_patterns = game/*.py

version         = 2.0.0

requirements    = python3,kivy==2.3.0

orientation     = portrait

android.build_tools_version = 33.0.0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api         = 33
android.minapi      = 21
android.ndk         = 25b
android.archs       = arm64-v8a

android.presplash_color  = #030512
android.allow_backup     = True
android.release_artifact = apk

[buildozer]
log_level = 2
warn_on_root = 1
