#!/usr/bin/env python3
"""Apply the experimental patch to an apktool-decoded 7.27.302 base APK.

Usage: python3 aplicar-patch.py DECODED_DIR ARM_SPLIT_APK
Run apktool build and sign the resulting APK afterwards.
"""
import json
from pathlib import Path
import re
import sys
import zipfile

root = Path(sys.argv[1])
split = Path(sys.argv[2])
old_package = 'com.google.android.youtube.tv'
new_package = 'local.youtubetv.experimental'
proxy_class = 'Lcobalt/org/chromium/content/browser/webcontents/WebContentsObserverProxy;'
contents_class = 'Lcobalt/org/chromium/content/browser/webcontents/WebContentsImpl;'
proxy = root / 'smali_classes2/cobalt/org/chromium/content/browser/webcontents/WebContentsObserverProxy.smali'
text = proxy.read_text()
if 'localAdPatchInject' in text:
    raise SystemExit('Patch already applied; decode a fresh copy.')
assert f'.method public constructor <init>({contents_class})V' in text
assert 'versionName: 7.27.302' in (root / 'apktool.yml').read_text()
assert '.field public b:J' in (root / 'smali_classes2/cobalt/org/chromium/content/browser/webcontents/WebContentsImpl.smali').read_text()
payload = Path(__file__).with_name('adblock-experimental.js').read_text()
text = text.replace('# instance fields', '# instance fields\n.field private localAdContents:' + contents_class, 1)
constructor = f'.method public constructor <init>({contents_class})V'
start = text.index(constructor)
pos = text.index('invoke-direct {p0}, Lbdw;-><init>()V', start)
end = pos + len('invoke-direct {p0}, Lbdw;-><init>()V')
text = text[:end] + f'\n\n    iput-object p1, p0, {proxy_class}->localAdContents:{contents_class}' + text[end:]
hooks = [
    '.method public primaryPageChanged(',
    '.method public final documentLoadedInPrimaryMainFrame(',
    '.method public final didFinishLoadInPrimaryMainFrame(',
]
for hook in hooks:
    start = text.index(hook)
    match = re.search(r'    \.locals \d+\n', text[start:])
    assert match
    end = start + match.end()
    text = text[:end] + f'\n    invoke-direct {{p0}}, {proxy_class}->localAdPatchInject()V\n' + text[end:]
text += f'''
.method private localAdPatchInject()V
    .locals 4

    :try_start_localad
    iget-object v2, p0, {proxy_class}->localAdContents:{contents_class}
    if-eqz v2, :localad_done
    iget-wide v0, v2, {contents_class}->b:J
    const-wide/16 v2, 0x0
    cmp-long v2, v0, v2
    if-eqz v2, :localad_done
    const-string v2, {json.dumps(payload, ensure_ascii=True)}
    const/4 v3, 0x0
    invoke-static {{v0, v1, v2, v3}}, Lorg/jni_zero/GEN_JNI;->cobalt_org_chromium_content_browser_webcontents_WebContentsImpl_evaluateJavaScript(JLjava/lang/Object;Ljava/lang/Object;)V
    :try_end_localad
    .catch Ljava/lang/Exception; {{:try_start_localad .. :try_end_localad}} :localad_error
    goto :localad_done
    :localad_error
    move-exception v0
    const-string v1, "LocalTvAdPatch"
    const-string v2, "Experimental injection failed"
    invoke-static {{v1, v2, v0}}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I
    :localad_done
    return-void
.end method
'''
proxy.write_text(text)

# Make a separate test app. Keep class names, JNI symbols, SDK requirements,
# playback libraries, and Google's original resource package IDs intact.
manifest = root / 'AndroidManifest.xml'
xml = manifest.read_text().replace(old_package, new_package)
xml = re.sub(r' android:(?:requiredSplitTypes|splitTypes)="[^"]*"', '', xml)
xml = re.sub(r'\s*<meta-data android:name="com.android.vending.splits(?:\.required)?"[^>]*/>', '', xml)
xml = xml.replace('android:extractNativeLibs="false"', 'android:extractNativeLibs="true"')
xml = xml.replace('android:label="@string/app_name"', 'android:label="YouTube TV - Teste"', 1)
manifest.write_text(xml)
updated = 0
for path in root.glob('smali*/**/*.smali'):
    source = path.read_text()
    # Package-name strings are used for internal intents and permissions.
    changed = re.sub(r'"' + re.escape(old_package) + r'(?=[".])', '"' + new_package, source)
    if changed != source:
        path.write_text(changed)
        updated += 1
with zipfile.ZipFile(split) as archive:
    libraries = [n for n in archive.namelist() if n.startswith('lib/armeabi-v7a/') and n.endswith('.so')]
    assert len(libraries) == 6, libraries
    for name in libraries:
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(archive.read(name))
print(f'Applied experimental patch; updated package literals in {updated} files; merged {len(libraries)} libraries.')
