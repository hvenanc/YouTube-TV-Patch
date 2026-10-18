#!/usr/bin/env python3
"""Handle the observed service rejection as a failed GMS connection.

Does not modify the package request, certificate, service response, or Google's
verification. Only PackageVerificationRslt: not allowed is handled gracefully.
Other SecurityException instances retain their original behavior.
Run after aplicar-patch.py and before apktool build.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1])
path = root / 'smali_classes2/cyp.smali'
source = path.read_text()
start = source.index('.method public final r(Lczm;Ljava/util/Set;)V')
end = source.index('.end method', start)
method = source[start:end]
old = '''    :catch_2
    move-exception v0

    .line 253
    throw v0
'''
new = '''    :catch_2
    move-exception v0

    # Keep Google's rejection; report connection failure rather than terminate.
    invoke-virtual {v0}, Ljava/lang/SecurityException;->getMessage()Ljava/lang/String;
    move-result-object v2
    if-eqz v2, :local_verification_rethrow
    const-string v3, "PackageVerificationRslt: not allowed:"
    invoke-virtual {v2, v3}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z
    move-result v2
    if-eqz v2, :local_verification_rethrow
    goto :goto_2

    :local_verification_rethrow
    throw v0
'''
assert method.count(old) == 1, 'Expected handler missing or patch already applied'
assert ':goto_2' in method and '->B(ILandroid/os/IBinder;Landroid/os/Bundle;I)V' in method
method = method.replace(old, new, 1)
path.write_text(source[:start] + method + source[end:])
print('Specific GMS rejection now follows the existing failed-connection callback.')
