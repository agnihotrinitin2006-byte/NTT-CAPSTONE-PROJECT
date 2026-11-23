// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/05/CPU.tst

load CPU.hdl,
output-file CPU.out,
compare-to CPU.cmp,
output-list time%S3.4.1 inM%D1.6.1 instruction%B1.16.1 reset%B2.1.2 outM%D1.6.1 writeM%B2.1.2 addressM%D2.5.2 pc%D2.5.2;

set inM 0,
set reset 0,

// A-instruction: @12345
set instruction %B0011000000111001,
eval,
output;
tick,
tock,
output;

// D = A: D-reg gets 12345
set instruction %B1110110000010000,
eval,
output;
tick,
tock,
output;

// A-instruction: @23456
set instruction %B0101101110100000,
eval,
output;
tick,
tock,
output;

// D = D - A: 12345 - 23456 = -11111
set instruction %B1110010011010000,
eval,
output;
tick,
tock,
output;

// M = D: write -11111 to M (RAM[23456])
set instruction %B1110001100001000,
eval,
output;
tick,
tock,
output;

// D;JGT: jump if D > 0 (D is -11111, so no jump)
set instruction %B1110001100000001,
eval,
output;
tick,
tock,
output;

// D;JLT: jump if D < 0 (D is -11111, jump to A: 23456)
set instruction %B1110001100000100,
eval,
output;
tick,
tock,
output;

// A-instruction: @100
set instruction %B0000000001100100,
eval,
output;
tick,
tock,
output;

// reset = 1
set reset 1,
eval,
output;
tick,
tock,
output;

// reset = 0
set reset 0,
eval,
output;
tick,
tock,
output;

// A-instruction: @0
set instruction %B0000000000000000,
eval,
output;
tick,
tock,
output;

// D = inM (inM = 12345)
set inM 12345,
set instruction %B1111110000010000,
eval,
output;
tick,
tock,
output;
