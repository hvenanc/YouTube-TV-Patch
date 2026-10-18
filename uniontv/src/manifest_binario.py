"""Binary AXML helper; preserves resource indices and SDK unless requested."""
import io
import struct as st
import sys
import zipfile

OLD = 'com.google.android.youtube.tv'
NEW = 'local.youtubetv.experimental'
ANDROID = 'http://schemas.android.com/apk/res/android'

def u16(data, off):
    return st.unpack_from('<H', data, off)[0]

def u32(data, off):
    return st.unpack_from('<I', data, off)[0]

def patch_manifest(blob, api31=False, diagnostic=False, label=None):
    chunks = []
    off = 8
    while off < len(blob):
        typ, header, size = st.unpack_from('<HHI', blob, off)
        assert size >= header and off + size <= len(blob)
        chunks.append((typ, bytearray(blob[off:off + size])))
        off += size
    assert off == len(blob)
    pool = next(c for t, c in chunks if t == 1)
    header = u16(pool, 2)
    count, styles, flags, start, style_start = st.unpack_from('<5I', pool, 8)
    assert styles == 0 and style_start == 0 and not flags & 256
    strings = []
    for i in range(count):
        p = start + u32(pool, header + i * 4)
        n = u16(pool, p); p += 2
        if n & 0x8000:
            n = ((n & 0x7fff) << 16) | u16(pool, p); p += 2
        strings.append(bytes(pool[p:p + n * 2]).decode('utf-16le'))
    strings = [s.replace(OLD, NEW) for s in strings]
    strings = ['5.30.340-r4' if s == '5.30.340' else s for s in strings]
    label_index = len(strings)
    strings.append(label or ('YouTube TV - Diagnostico' if diagnostic else 'YouTube TV - Teste v2'))
    offsets, data = [], bytearray()
    for s in strings:
        encoded = s.encode('utf-16le')
        length = len(encoded) // 2
        assert length < 0x8000
        offsets.append(len(data))
        data += st.pack('<H', length) + encoded + b'\0\0'
    data += b'\0' * (-len(data) % 4)
    start = 28 + len(strings) * 4
    new_pool = (st.pack('<HHI5I', 1, 28, start + len(data), len(strings), 0,
                       flags & ~1, start, 0)
                + st.pack('<' + 'I' * len(offsets), *offsets) + data)
    result = []
    skip = 0
    for typ, chunk in chunks:
        if typ == 1:
            result.append(new_pool); continue
        if skip:
            if typ == 0x102: skip += 1
            if typ == 0x103: skip -= 1
            continue
        if typ != 0x102:
            result.append(chunk); continue
        tag = strings[u32(chunk, 20)]
        attr_start = 16 + u16(chunk, 24)
        attr_size = u16(chunk, 26)
        attr_count = u16(chunk, 28)
        assert attr_size == 20
        attrs = [bytearray(chunk[attr_start + i * attr_size:attr_start + (i + 1) * attr_size])
                 for i in range(attr_count)]
        def attr_name(a): return strings[u32(a, 4)]
        def attr_value(a):
            raw = u32(a, 8)
            if raw != 0xffffffff: return strings[raw]
            return strings[u32(a, 16)] if a[15] == 3 else u32(a, 16)
        if tag == 'meta-data':
            name = next((attr_value(a) for a in attrs if attr_name(a) == 'name'), '')
            if name in ['com.android.vending.splits', 'com.android.vending.splits.required']:
                skip = 1; continue
        kept = []
        removed_positions = []
        for index, a in enumerate(attrs, 1):
            name = attr_name(a)
            if tag == 'manifest' and name in ['requiredSplitTypes', 'splitTypes']:
                removed_positions.append(index); continue
            if tag == 'application' and name == 'extractNativeLibs':
                st.pack_into('<I', a, 8, 0xffffffff)
                a[15] = 0x12; st.pack_into('<I', a, 16, 0xffffffff)
            if tag == 'application' and name == 'label':
                st.pack_into('<I', a, 8, label_index)
                a[15] = 3; st.pack_into('<I', a, 16, label_index)
            if tag == 'uses-sdk' and name == 'minSdkVersion' and api31:
                assert u32(a, 16) == 32
                st.pack_into('<I', a, 8, 0xffffffff)
                a[15] = 0x10; st.pack_into('<I', a, 16, 31)
            kept.append(a)
        # idIndex/classIndex/styleIndex refer to 1-based attribute positions.
        for p in [30, 32, 34]:
            idx = u16(chunk, p)
            if idx:
                idx = 0 if idx in removed_positions else idx - sum(i < idx for i in removed_positions)
                st.pack_into('<H', chunk, p, idx)
        tail = chunk[attr_start + attr_count * attr_size:]
        chunk = chunk[:attr_start] + b''.join(kept) + tail
        st.pack_into('<H', chunk, 28, len(kept))
        st.pack_into('<I', chunk, 4, len(chunk))
        result.append(chunk)
    assert skip == 0
    body = b''.join(result)
    return st.pack('<HHI', 3, 8, 8 + len(body)) + body
