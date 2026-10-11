import struct
import sys
import zlib


def dmg_rom(source, out):
    rom = bytearray(32768)
    with open(source, "rb") as f:
        rom[0x100:0x150] = f.read(0x150)[0x100:0x150]
    rom[0x134:0x144] = bytes(16)
    rom[0x143:0x150] = bytes(13)
    check = 0
    for byte in rom[0x134:0x14D]:
        check = (check - byte - 1) & 0xFF
    rom[0x14D] = check
    with open(out, "wb") as f:
        f.write(rom)


def chunk(kind, data):
    body = kind + data
    return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))


def big_png(size, out):
    width = height = int(size)
    pattern = bytes((x * 7 + (x >> 8) * 13) & 255 for x in range(width + 256))
    packer = zlib.compressobj(1)
    with open(out, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0)))
        parts = []
        for y in range(height):
            parts.append(b"\x00" + pattern[y % 256 :][:width])
            if len(parts) == 256:
                f.write(chunk(b"IDAT", packer.compress(b"".join(parts))))
                parts = []
        f.write(chunk(b"IDAT", packer.compress(b"".join(parts)) + packer.flush()))
        f.write(chunk(b"IEND", b""))


if sys.argv[1:2] == ["dmg"] and len(sys.argv) == 4:
    dmg_rom(sys.argv[2], sys.argv[3])
elif sys.argv[1:2] == ["png"] and len(sys.argv) == 4:
    big_png(sys.argv[2], sys.argv[3])
else:
    sys.exit("usage: make_assets.py dmg SOURCE.gb OUT.gb | make_assets.py png SIZE OUT.png")
