// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/05/ComputerAdd.tst

load Computer.hdl,
output-file ComputerAdd.out,
compare-to ComputerAdd.cmp,
output-list time%S4.4.1 ARegister[0]%D1.7.1 DRegister[0]%D1.7.1 PC[]%D0.4.0 RAM16K[0]%D1.7.1;

// Load Add.hack into ROM
ROM32K load Add.hack,

// Reset the computer
set reset 1,
tick, tock;
set reset 0,

// Run 14 clock cycles to compute RAM[0] = 2 + 3 = 5
repeat 14 {
    tick, tock;
}

output;
