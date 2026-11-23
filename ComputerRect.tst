// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/05/ComputerRect.tst

load Computer.hdl,
output-file ComputerRect.out,
compare-to ComputerRect.cmp,
output-list time%S4.4.1 RAM16K[0]%D1.7.1 RAM64K[16384]%B1.16.1 RAM64K[16416]%B1.16.1 RAM64K[16448]%B1.16.1 RAM64K[16480]%B1.16.1;

// Load Rect.hack into ROM
ROM32K load Rect.hack,

// Draw a rectangle of height 4
set RAM16K[0] 4,
set reset 1,
tick, tock;
set reset 0,

repeat 64 {
    tick, tock;
}
output;
