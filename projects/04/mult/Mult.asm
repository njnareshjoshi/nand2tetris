// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

// Put your code here.

@100
D=A
@R0
M=D

@21
D=A
@R1
M=D

@R0
D=M

@R2
M=D

@R1
D=M

@R3
M=D

(LOOP)
	@R0
	D=M

	@R2
	D=D+M
	M=D

	@R3
	D=M-1
	M=D

	@LOOP
	D-1;JGT

	@END
	0;JMP


(END)
	@END
	0;JMP