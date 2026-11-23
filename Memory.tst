// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/05/Memory.tst

load Memory.hdl,
output-file Memory.out,
compare-to Memory.cmp,
output-list time%S3.4.1 in%D1.6.1 load%B2.1.2 address%B1.15.1 out%D1.6.1;

// Read RAM[0]
set in -1,
set load 0,
set address 0,
eval,
output;

// Write RAM[0] = 333
set in 333,
set load 1,
set address 0,
tick,
output;
tock,
output;

// Read RAM[0]
set in -1,
set load 0,
set address 0,
eval,
output;

// Read RAM[100]
set address 100,
eval,
output;

// Write RAM[100] = 444
set in 444,
set load 1,
set address 100,
tick,
output;
tock,
output;

// Read RAM[100]
set in -1,
set load 0,
set address 100,
eval,
output;

// Read Screen[0] (address 16384)
set address 16384,
eval,
output;

// Write Screen[0] = 555
set in 555,
set load 1,
set address 16384,
tick,
output;
tock,
output;

// Read Screen[0]
set in -1,
set load 0,
set address 16384,
eval,
output;

// Read Keyboard (address 24576)
set address 24576,
eval,
output;
