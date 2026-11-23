#!/usr/bin/env python3
"""
Hack Assembler for Nand to Tetris (Project 6 & Capstone)
Author: Nitin Agnihotri
Roll No: 2501010074 (K = 74)
Special Feature (K mod 3 = 2):
  Detects and prints a warning whenever the same label is defined more than once.
"""

import sys
import os
import re

# Predefined Symbols in Hack Platform
INITIAL_SYMBOLS = {
    'SP': 0,
    'LCL': 1,
    'ARG': 2,
    'THIS': 3,
    'THAT': 4,
    'SCREEN': 16384,
    'KBD': 24576,
    'R0': 0, 'R1': 1, 'R2': 2, 'R3': 3,
    'R4': 4, 'R5': 5, 'R6': 6, 'R7': 7,
    'R8': 8, 'R9': 9, 'R10': 10, 'R11': 11,
    'R12': 12, 'R13': 13, 'R14': 14, 'R15': 15
}

# Computation bit encodings (a + c1..c6)
COMP_TABLE = {
    # a = 0
    "0":   "0101010",
    "1":   "0111111",
    "-1":  "0111010",
    "D":   "0001100",
    "A":   "0110000",
    "!D":  "0001101",
    "!A":  "0110001",
    "-D":  "0001111",
    "-A":  "0110011",
    "D+1": "0011111",
    "A+1": "0110111",
    "D-1": "0001110",
    "A-1": "0110010",
    "D+A": "0000010",
    "A+D": "0000010",
    "D-A": "0010011",
    "A-D": "0000111",
    "D&A": "0000000",
    "A&D": "0000000",
    "D|A": "0010101",
    "A|D": "0010101",

    # a = 1 (A replaced by M)
    "M":   "1110000",
    "!M":  "1110001",
    "-M":  "1110011",
    "M+1": "1110111",
    "M-1": "1110010",
    "D+M": "1000010",
    "M+D": "1000010",
    "D-M": "1010011",
    "M-D": "1000111",
    "D&M": "1000000",
    "M&D": "1000000",
    "D|M": "1010101",
    "M|D": "1010101",
}

# Destination bit encodings (d1 d2 d3)
DEST_TABLE = {
    None:  "000",
    "":    "000",
    "M":   "001",
    "D":   "010",
    "MD":  "011",
    "DM":  "011",
    "A":   "100",
    "AM":  "101",
    "AD":  "110",
    "AMD": "111",
    "ADM": "111",
}

# Jump bit encodings (j1 j2 j3)
JUMP_TABLE = {
    None:  "000",
    "":    "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111",
}


def clean_line(line: str) -> str:
    """Removes comments and extraneous whitespace from a line."""
    comment_idx = line.find("//")
    if comment_idx != -1:
        line = line[:comment_idx]
    return line.strip()


class HackAssembler:
    def __init__(self, filename: str):
        self.filename = filename
        self.symbol_table = dict(INITIAL_SYMBOLS)
        self.label_declared_lines = {}  # Tracks where each label was first declared
        self.next_var_address = 16
        self.instructions = []  # Tuples of (cleaned_line, original_line_num)
        self.warnings = []

    def pass_one(self):
        """
        First reading:
        - Reads the file line-by-line.
        - Records labels like (LABEL) and associates them with ROM addresses.
        - Extra Feature (K mod 3 = 2):
          Detects and prints a warning if the same label is declared more than once.
        """
        rom_address = 0
        with open(self.filename, 'r', encoding='utf-8') as f:
            for line_no, raw_line in enumerate(f, start=1):
                line = clean_line(raw_line)
                if not line:
                    continue

                # Check for label declaration (Xxx)
                if line.startswith('(') and line.endswith(')'):
                    label = line[1:-1].strip()
                    if label in self.label_declared_lines:
                        # Extra Feature (K mod 3 = 2): Warning on duplicate label definition
                        prev_line, prev_rom = self.label_declared_lines[label]
                        warn_msg = (
                            f"[WARNING] Line {line_no}: Label '({label})' is declared again! "
                            f"(First declared on line {prev_line} pointing to ROM address {prev_rom})"
                        )
                        print(warn_msg, file=sys.stderr)
                        self.warnings.append(warn_msg)
                    else:
                        self.symbol_table[label] = rom_address
                        self.label_declared_lines[label] = (line_no, rom_address)
                else:
                    # Regular instruction (A- or C-instruction)
                    self.instructions.append((line, line_no))
                    rom_address += 1

    def assemble_a_instruction(self, line: str, line_no: int) -> str:
        """Translates @value into a 16-bit binary string (0vvvvvvvvvvvvvvv)."""
        val_str = line[1:].strip()
        if val_str.isdigit():
            addr = int(val_str)
        else:
            # Symbol (predefined, label, or variable)
            if val_str in self.symbol_table:
                addr = self.symbol_table[val_str]
            else:
                # New variable: allocate next available RAM address
                addr = self.next_var_address
                self.symbol_table[val_str] = addr
                self.next_var_address += 1

        if addr > 32767:
            raise ValueError(f"Line {line_no}: Address {addr} exceeds Hack 15-bit address space limit.")
        return f"{addr:016b}"

    def assemble_c_instruction(self, line: str, line_no: int) -> str:
        """Translates dest=comp;jump into a 16-bit binary string (111accccccdddjjj)."""
        dest_part = None
        jump_part = None
        comp_part = line

        # Parse dest
        if '=' in comp_part:
            dest_part, comp_part = comp_part.split('=', 1)
            dest_part = dest_part.strip()
            comp_part = comp_part.strip()

        # Parse jump
        if ';' in comp_part:
            comp_part, jump_part = comp_part.split(';', 1)
            comp_part = comp_part.strip()
            jump_part = jump_part.strip()

        if comp_part not in COMP_TABLE:
            raise ValueError(f"Line {line_no}: Invalid computation '{comp_part}' in instruction: {line}")
        if dest_part not in DEST_TABLE:
            raise ValueError(f"Line {line_no}: Invalid destination '{dest_part}' in instruction: {line}")
        if jump_part not in JUMP_TABLE:
            raise ValueError(f"Line {line_no}: Invalid jump '{jump_part}' in instruction: {line}")

        comp_bits = COMP_TABLE[comp_part]
        dest_bits = DEST_TABLE[dest_part]
        jump_bits = JUMP_TABLE[jump_part]

        return f"111{comp_bits}{dest_bits}{jump_bits}"

    def pass_two(self) -> list:
        """
        Second reading:
        - Converts each instruction into its 16-bit binary representation.
        - Resolves variables and assigns memory addresses.
        """
        machine_code = []
        for line, line_no in self.instructions:
            if line.startswith('@'):
                code = self.assemble_a_instruction(line, line_no)
            else:
                code = self.assemble_c_instruction(line, line_no)
            machine_code.append(code)
        return machine_code

    def assemble(self, output_filename: str = None) -> list:
        """Runs the two passes and writes the .hack output file."""
        self.pass_one()
        machine_code = self.pass_two()

        if output_filename is None:
            base, _ = os.path.splitext(self.filename)
            output_filename = base + ".hack"

        with open(output_filename, 'w', encoding='utf-8') as f:
            for code in machine_code:
                f.write(code + "\n")

        print(f"Assembly successful: '{self.filename}' -> '{output_filename}' ({len(machine_code)} instructions)")
        return machine_code


def main():
    if len(sys.argv) < 2:
        print("Usage: python assembler.py <source.asm> [output.hack]")
        print("Note: Nitin Agnihotri (Roll: 2501010074, K=74, K mod 3 = 2)")
        print("Feature: Prints warning on duplicate label definitions.")
        sys.exit(1)

    asm_file = sys.argv[1]
    hack_file = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(asm_file):
        print(f"Error: File '{asm_file}' not found.", file=sys.stderr)
        sys.exit(1)

    assembler = HackAssembler(asm_file)
    assembler.assemble(hack_file)


if __name__ == '__main__':
    main()
