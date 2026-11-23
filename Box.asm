// Box.asm - Capstone Project for Nand to Tetris I (ETCCNT301)
// School of Engineering & Technology, K.R. Mangalam University
// Student Name: Nitin Agnihotri
// Roll Number:  2501010074
// Personal Number K = 74 (Last two digits of Roll No.)
//
// Project Specifications for K = 74:
// 1. Starting Row: Row K = 74
// 2. Height: 20 rows (Row 74 to Row 93 inclusive)
// 3. Width: 16 * ((K mod 4) + 1) pixels wide from left edge
//    K mod 4 = 74 mod 4 = 2
//    Width = 16 * (2 + 1) = 48 pixels = 3 16-bit words wide per row
// 4. Memory Mapping:
//    - SCREEN base address = 16384 (0x4000)
//    - Each row = 32 words (512 pixels)
//    - Starting address for row 74 = SCREEN + 32 * 74 = 16384 + 2368 = 18752
//    - KEYBOARD address = 24576 (KBD)
//
// Operation:
//    - While any key is pressed (RAM[KBD] != 0): Draw black box (value = -1 / 0xFFFF)
//    - When key is released (RAM[KBD] == 0): Clear box to white (value = 0 / 0x0000)

(CHECK_KEY)
    // Read the keyboard register
    @KBD
    D=M
    @KEY_PRESSED
    D;JNE        // If RAM[KBD] != 0 (key is pressed), goto KEY_PRESSED

(KEY_RELEASED)
    // Key released: fill color is white (0)
    @color
    M=0
    @DRAW_INIT
    0;JMP

(KEY_PRESSED)
    // Key pressed: fill color is black (-1, all 16 bits set to 1)
    @color
    M=-1

(DRAW_INIT)
    // Calculate starting memory address for Row 74:
    // SCREEN (16384) + 32 * 74 (2368) = 18752
    @SCREEN
    D=A
    @2368
    D=D+A
    @addr
    M=D          // addr = 18752

    // Set row counter to 20 rows
    @20
    D=A
    @rows_left
    M=D

(ROW_LOOP)
    // If all 20 rows have been drawn, return to keyboard check
    @rows_left
    D=M
    @CHECK_KEY
    D;JEQ

    // Draw Word 0 (pixels 0 to 15 of current row)
    @color
    D=M
    @addr
    A=M
    M=D

    // Draw Word 1 (pixels 16 to 31 of current row)
    @addr
    M=M+1
    @color
    D=M
    @addr
    A=M
    M=D

    // Draw Word 2 (pixels 32 to 47 of current row)
    @addr
    M=M+1
    @color
    D=M
    @addr
    A=M
    M=D

    // Advance addr to Word 0 of the next row:
    // Row width is 32 words. Since addr was incremented twice (word 0 -> 1 -> 2),
    // adding 30 advances addr to word 0 of the next row (2 + 30 = 32).
    @30
    D=A
    @addr
    M=D+M

    // Decrement the row counter
    @rows_left
    M=M-1

    // Repeat for the next row
    @ROW_LOOP
    0;JMP
