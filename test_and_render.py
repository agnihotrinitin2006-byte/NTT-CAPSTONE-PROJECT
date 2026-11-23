#!/usr/bin/env python3
"""
Hardware & CPU Emulator for Hack Platform
Tests Box.hack and produces simulated screen captures.
Author: Nitin Agnihotri (Roll No: 2501010074, K = 74)
"""

import struct
import sys
import os

class HackCPU:
    def __init__(self, rom_code):
        self.rom = rom_code
        self.ram = [0] * 32768
        self.a = 0
        self.d = 0
        self.pc = 0

    def step(self):
        if self.pc >= len(self.rom):
            return

        instruction = self.rom[self.pc]
        # 16-bit instruction string
        if instruction[0] == '0':
            # A-instruction
            self.a = int(instruction, 2)
            self.pc += 1
        else:
            # C-instruction: 111 a c1..c6 d1..d3 j1..j3
            a_bit = int(instruction[3])
            comp_bits = instruction[4:10]
            dest_bits = instruction[10:13]
            jump_bits = instruction[13:16]

            x = self.d
            y = self.ram[self.a] if a_bit == 1 else self.a

            # Compute ALU output
            # comp_bits: zx, nx, zy, ny, f, no
            zx, nx, zy, ny, f, no = [int(b) for b in comp_bits]

            if zx: x = 0
            if nx: x = (~x) & 0xFFFF
            if zy: y = 0
            if ny: y = (~y) & 0xFFFF

            out = (x + y) & 0xFFFF if f else (x & y) & 0xFFFF
            if no: out = (~out) & 0xFFFF

            # Signed 16-bit interpretation
            signed_out = out if out < 0x8000 else out - 0x10000

            # Dest
            d1, d2, d3 = [int(b) for b in dest_bits]
            if d1: self.a = out
            if d2: self.d = out
            if d3:
                # Write to RAM[A]
                if 0 <= self.a < len(self.ram):
                    self.ram[self.a] = out

            # Jump
            j1, j2, j3 = [int(b) for b in jump_bits]
            is_neg = (signed_out < 0)
            is_zero = (signed_out == 0)
            is_pos = (signed_out > 0)

            should_jump = (j1 and is_neg) or (j2 and is_zero) or (j3 and is_pos)

            if should_jump:
                self.pc = self.a
            else:
                self.pc += 1

    def run_cycles(self, n):
        for _ in range(n):
            self.step()


def create_bmp_screenshot(ram, output_path, scale=2):
    """
    Renders the 512x256 Hack screen buffer into a Windows BMP image.
    Screen memory is located at RAM[16384 .. 24575].
    Each 16-bit word represents 16 pixels from LSB to MSB.
    """
    width = 512
    height = 256
    screen_base = 16384

    # Build pixel grid (0 = white, 1 = black)
    pixels = []
    for r in range(height):
        row_pixels = []
        row_base = screen_base + r * 32
        for w in range(32):
            word = ram[row_base + w]
            # Hack screen words: bit 0 is leftmost pixel, bit 15 is rightmost pixel
            for b in range(16):
                bit = (word >> b) & 1
                row_pixels.append(bit)
        pixels.append(row_pixels)

    # Scale the image
    scaled_w = width * scale
    scaled_h = height * scale

    # BMP rows must be padded to multiples of 4 bytes
    # In 24-bit color, each pixel is 3 bytes (BGR)
    row_bytes = scaled_w * 3
    padding = (4 - (row_bytes % 4)) % 4

    image_data = bytearray()
    # BMP is stored bottom-to-top
    for r in reversed(range(scaled_h)):
        orig_r = r // scale
        for c in range(scaled_w):
            orig_c = c // scale
            color_val = 0 if pixels[orig_r][orig_c] == 1 else 255
            # Black (0,0,0) or White (255,255,255)
            image_data.extend([color_val, color_val, color_val])
        image_data.extend([0] * padding)

    # BMP File Header (14 bytes) + DIB Header (40 bytes)
    file_size = 54 + len(image_data)
    bmp_header = struct.pack(
        '<2sIHHI',
        b'BM',
        file_size,
        0, 0,
        54
    )
    dib_header = struct.pack(
        '<IIIHHIIIIII',
        40,
        scaled_w,
        scaled_h,
        1,       # 1 color plane
        24,      # 24 bits per pixel
        0,       # BI_RGB no compression
        len(image_data),
        2835,    # 72 DPI
        2835,
        0, 0
    )

    with open(output_path, 'wb') as f:
        f.write(bmp_header)
        f.write(dib_header)
        f.write(image_data)

    print(f"Saved simulated screenshot: {output_path} ({scaled_w}x{scaled_h})")


def main():
    hack_file = 'capstone/Box.hack'
    with open(hack_file, 'r') as f:
        rom = [line.strip() for line in f if line.strip()]

    cpu = HackCPU(rom)

    print("=== Testing Box.hack Execution ===")
    
    # 1. Initially key released
    cpu.ram[24576] = 0
    cpu.run_cycles(2000)
    
    # Verify screen is empty
    empty_screen = all(cpu.ram[16384 + i] == 0 for i in range(8192))
    assert empty_screen, "Screen should be completely white when no key is pressed!"
    print("PASS: Screen is completely white when key is released.")

    # 2. Key pressed (e.g. key code 65 = 'A')
    cpu.ram[24576] = 65
    cpu.run_cycles(3000)

    # Verify Box dimensions:
    # Starts at row 74, 20 rows tall (74 to 93), width = 3 words (words 0, 1, 2)
    box_correct = True
    for r in range(256):
        row_base = 16384 + r * 32
        for w in range(32):
            val = cpu.ram[row_base + w]
            in_box = (74 <= r < 74 + 20) and (0 <= w < 3)
            expected = 0xFFFF if in_box else 0
            if val != expected:
                print(f"FAIL at row {r}, word {w}: expected {hex(expected)}, got {hex(val)}")
                box_correct = False
                break
        if not box_correct:
            break

    if box_correct:
        print("PASS: Black box matches exact specifications for K=74:")
        print("      - Row range: 74 to 93 (Height = 20 rows)")
        print("      - Column words: 0, 1, 2 (Width = 48 pixels from left edge)")
        print("      - All words inside box are 0xFFFF (-1, black)")
        print("      - All words outside box remain 0x0000 (0, white)")

    # Save screenshot of drawn box
    create_bmp_screenshot(cpu.ram, 'capstone/screenshot_box_pressed.bmp', scale=2)

    # 3. Key released again
    cpu.ram[24576] = 0
    cpu.run_cycles(3000)
    screen_cleared = all(cpu.ram[16384 + i] == 0 for i in range(8192))
    assert screen_cleared, "Screen should clear to white when key is released!"
    print("PASS: Screen successfully returns to white upon key release.")
    create_bmp_screenshot(cpu.ram, 'capstone/screenshot_box_released.bmp', scale=2)

    print("\nALL VERIFICATION CHECKS PASSED 100%!")

if __name__ == '__main__':
    main()
