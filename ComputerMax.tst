// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/05/ComputerMax.tst

load Computer.hdl,
output-file ComputerMax.out,
compare-to ComputerMax.cmp,
output-list time%S4.4.1 ARegister[0]%D1.7.1 DRegister[0]%D1.7.1 PC[]%D0.4.0 RAM16K[0]%D1.7.1 RAM16K[1]%D1.7.1 RAM16K[2]%D1.7.1;

// Load Max.hack into ROM
ROM32K load Max.hack,

// First test: RAM[0]=3, RAM[1]=5 => RAM[2]=5
set RAM16K[0] 3,
set RAM16K[1] 5,
set reset 1,
tick, tock;
set reset 0,

repeat 14 {
    tick, tock;
}
output;

// Second test: RAM[0]=23456, RAM[1]=12345 => RAM[2]=23456
set RAM16K[0] 23456,
set RAM16K[1] 12345,
set reset 1,
tick, tock;
set reset 0,

repeat 14 {
    tick, tock;
}
output;
