#!/usr/bin/env python3
"""Version-specific patch for the supplied YouTube TV 5.30.340 ARMv7 APKs.

prepare DECODED_DIR
package BASE_APK SPLIT_APK PATCHED_DEX_APK OUTPUT_UNSIGNED_APK
"""
import hashlib
from pathlib import Path
import re
import sys
import zipfile
import manifest_binario

OLD_PACKAGE = 'com.google.android.youtube.tv'
NEW_PACKAGE = 'local.youtubetv.uniontv'
BASE_SHA = '570f5f4f85740f9a71056de87552d7adfbe639845fa77a745c493933090954a7'
COBALT_SHA = 'a3bc2715219e534f7d06d2d36321d9e0d51133c6ff80f97ef5f4ae16d94a7719'
STARTUP_SHA = '9ce14385832aabc7fd36569d89ceeef0e2dc589c8136386396fa6ba580a09300'
STARTUP_OFFSET = 0x853944
STARTUP_LENGTH = 22137

def prepare(root):
    root = Path(root)
    assert 'versionName: 5.30.340' in (root / 'apktool.yml').read_text()
    path = root / 'smali/bwh.smali'
    source = path.read_text()
    start = source.index('.method public final p(Lbww;Ljava/util/Set;)V')
    end = source.index('.end method', start)
    method = source[start:end]
    old = '    :catch_2\n    move-exception v0\n\n    .line 260\n    throw v0\n'
    new = '''    :catch_2
    move-exception v0
    invoke-virtual {v0}, Ljava/lang/SecurityException;->getMessage()Ljava/lang/String;
    move-result-object v2
    if-eqz v2, :uniontv_rethrow
    const-string v3, "PackageVerificationRslt: not allowed:"
    invoke-virtual {v2, v3}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z
    move-result v2
    if-eqz v2, :uniontv_rethrow
    goto :goto_4
    :uniontv_rethrow
    throw v0
'''
    assert method.count(old) == 1, 'Unexpected version or patch already applied'
    assert ':goto_4' in method and '->y(ILandroid/os/IBinder;Landroid/os/Bundle;I)V' in method
    path.write_text(source[:start] + method.replace(old, new, 1) + source[end:])
    count = 0
    for path in root.glob('smali*/**/*.smali'):
        src = path.read_text()
        changed = re.sub(r'"' + re.escape(OLD_PACKAGE) + r'(?=[".])', '"' + NEW_PACKAGE, src)
        if src != changed:
            path.write_text(changed)
            count += 1
    print('Prepared DEX: specific GMS failure callback and package strings in', count, 'files.')

def patch_native(data):
    assert hashlib.sha256(data).hexdigest() == COBALT_SHA, 'Unexpected native library'
    original = data[STARTUP_OFFSET:STARTUP_OFFSET + STARTUP_LENGTH]
    assert hashlib.sha256(original).hexdigest() == STARTUP_SHA
    assert data[STARTUP_OFFSET + STARTUP_LENGTH] == 0
    replacement = Path(__file__).with_name('cobalt-startup-patched.js').read_bytes()
    assert len(replacement) == STARTUP_LENGTH and b'\0' not in replacement
    result = data[:STARTUP_OFFSET] + replacement + data[STARTUP_OFFSET + STARTUP_LENGTH:]
    assert len(result) == len(data)
    assert result[:STARTUP_OFFSET] == data[:STARTUP_OFFSET]
    assert result[STARTUP_OFFSET + STARTUP_LENGTH:] == data[STARTUP_OFFSET + STARTUP_LENGTH:]
    return result

def package(base_path, split_path, dex_path, output):
    assert hashlib.sha256(Path(base_path).read_bytes()).hexdigest() == BASE_SHA
    manifest_binario.NEW = NEW_PACKAGE
    with zipfile.ZipFile(base_path) as base, zipfile.ZipFile(split_path) as split, \
         zipfile.ZipFile(dex_path) as dex, zipfile.ZipFile(output, 'w') as out:
        for info in base.infolist():
            name = info.filename
            if name.startswith('META-INF/') and name.upper().endswith(('.SF', '.RSA', '.DSA', '.EC', 'MANIFEST.MF')):
                continue
            if name == 'stamp-cert-sha256': continue
            data = base.read(name)
            if name == 'AndroidManifest.xml':
                data = manifest_binario.patch_manifest(data, label='YouTube TV UnionTV r4')
            elif name.endswith('.dex'):
                data = dex.read(name)
            out.writestr(info, data)
        libraries = 0
        for info in split.infolist():
            if not info.filename.startswith('lib/armeabi-v7a/') or not info.filename.endswith('.so'):
                continue
            data = split.read(info.filename)
            if info.filename == 'lib/armeabi-v7a/libcobalt.so': data = patch_native(data)
            out.writestr(info, data)
            libraries += 1
        assert libraries == 8
    with zipfile.ZipFile(base_path) as base, zipfile.ZipFile(output) as out:
        assert out.testzip() is None
        for name in base.namelist():
            if name == 'resources.arsc' or name.startswith(('res/', 'assets/')):
                assert base.read(name) == out.read(name), name
    print('Packaged', output, '- original resources and SDK preserved; 8 ARMv7 libraries.')

if __name__ == '__main__':
    if sys.argv[1] == 'prepare': prepare(sys.argv[2])
    elif sys.argv[1] == 'package': package(*sys.argv[2:])
    else: raise SystemExit(__doc__)
