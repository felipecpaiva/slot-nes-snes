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


def nes_rom(out, battery=False):
    rom = bytearray(16 + 0x4000 + 0x2000)
    rom[0:7] = b"NES\x1a\x01\x01" + bytes([2 if battery else 0])
    program = bytes(
        [0xA9, 0x3F, 0x8D, 0x06, 0x20, 0xA9, 0x00, 0x8D, 0x06, 0x20, 0xA2, 0x20, 0xA9, 0x16]
        + [0x8D, 0x07, 0x20, 0xCA, 0xD0, 0xFA, 0x4C, 0x14, 0xC0]
    )
    rom[16 : 16 + len(program)] = program
    rom[16 + 0x3FFC : 16 + 0x3FFE] = b"\x00\xc0"
    with open(out, "wb") as f:
        f.write(rom)


def snes_rom(out):
    rom = bytearray(0x8000)
    rom[0:10] = bytes([0x78, 0x18, 0xFB, 0xA9, 0x0F, 0x8D, 0x00, 0x21, 0x80, 0xFE])
    rom[0x7FC0:0x7FD5] = b"SLOT COST TEST".ljust(21)
    rom[0x7FD5:0x7FDC] = bytes([0x20, 0x00, 0x05, 0x00, 0x01, 0x33, 0x00])
    for vector in range(0x7FE0, 0x8000, 2):
        rom[vector : vector + 2] = b"\x00\x80"
    rom[0x7FDC:0x7FE0] = bytes([0xFF, 0xFF, 0x00, 0x00])
    total = sum(rom) & 0xFFFF
    rom[0x7FDC:0x7FE0] = struct.pack("<HH", total ^ 0xFFFF, total)
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


def bezel_png(width, height, out):
    rows = []
    for y in range(height):
        row = bytearray([0])
        for x in range(width):
            edge = min(x, y, width - 1 - x, height - 1 - y)
            if edge < 24:
                row += bytes((40 + edge * 5, 90 + y % 64, 200 - x % 128, 255))
            else:
                row += bytes((0, 0, 0, 0))
        rows.append(bytes(row))
    with open(out, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)))
        f.write(chunk(b"IDAT", zlib.compress(b"".join(rows))))
        f.write(chunk(b"IEND", b""))


if sys.argv[1:2] == ["dmg"] and len(sys.argv) == 4:
    dmg_rom(sys.argv[2], sys.argv[3])
elif sys.argv[1:2] == ["nes"] and len(sys.argv) in (3, 4):
    nes_rom(sys.argv[2], sys.argv[3:] == ["battery"])
elif sys.argv[1:2] == ["snes"] and len(sys.argv) == 3:
    snes_rom(sys.argv[2])
elif sys.argv[1:2] == ["png"] and len(sys.argv) == 4:
    big_png(sys.argv[2], sys.argv[3])
elif sys.argv[1:2] == ["bezel"] and len(sys.argv) == 5:
    bezel_png(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
else:
    sys.exit(
        "usage: make_assets.py dmg SOURCE.gb OUT.gb | make_assets.py nes OUT.nes [battery]"
        " | make_assets.py png SIZE OUT.png"
        " | make_assets.py bezel WIDTH HEIGHT OUT.png"
    )
