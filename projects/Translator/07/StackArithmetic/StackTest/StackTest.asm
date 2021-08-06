// StackArithmetic/StackTest/StackTest.vm
// push constant 17
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 17
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
// eq
@SP
AM=M-1
D=M
M=0
A=A-1
D=M-D
M=0
@eq_StackTest_10
D;JNE
@SP
A=M
A=A-1
M=-1
(eq_StackTest_10)
// push constant 17
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 16
@16
D=A
@SP
A=M
M=D
@SP
M=M+1
// eq
@SP
AM=M-1
D=M
M=0
A=A-1
D=M-D
M=0
@eq_StackTest_13
D;JNE
@SP
A=M
A=A-1
M=-1
(eq_StackTest_13)
// push constant 16
@16
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 17
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
// eq
@SP
AM=M-1
D=M
M=0
A=A-1
D=M-D
M=0
@eq_StackTest_16
D;JNE
@SP
A=M
A=A-1
M=-1
(eq_StackTest_16)
// push constant 892
@892
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 891
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
// lt
@SP
AM=M-1
D=M
M=0
A=A-1
D=M-D
M=0
@lt_StackTest_19
D;JGE
@SP
A=M
A=A-1
M=-1
(lt_StackTest_19)
// push constant 891
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 892
@892
D=A
@SP
A=M
M=D
@SP
M=M+1
// lt
@SP
AM=M-1
D=M
M=0
A=A-1
D=M-D
M=0
@lt_StackTest_22
D;JGE
@SP
A=M
A=A-1
M=-1
(lt_StackTest_22)
// push constant 891
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 891
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
// lt
@SP
AM=M-1
D=M
M=0
A=A-1
D=M-D
M=0
@lt_StackTest_25
D;JGE
@SP
A=M
A=A-1
M=-1
(lt_StackTest_25)
// push constant 32767
@32767
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 32766
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
// gt
@SP
AM=M-1
D=M
M=0
A=A-1
D=M-D
M=0
@gt_StackTest_28
D;JLE
@SP
A=M
A=A-1
M=-1
(gt_StackTest_28)
// push constant 32766
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 32767
@32767
D=A
@SP
A=M
M=D
@SP
M=M+1
// gt
@SP
AM=M-1
D=M
M=0
A=A-1
D=M-D
M=0
@gt_StackTest_31
D;JLE
@SP
A=M
A=A-1
M=-1
(gt_StackTest_31)
// push constant 32766
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 32766
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
// gt
@SP
AM=M-1
D=M
M=0
A=A-1
D=M-D
M=0
@gt_StackTest_34
D;JLE
@SP
A=M
A=A-1
M=-1
(gt_StackTest_34)
// push constant 57
@57
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 31
@31
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 53
@53
D=A
@SP
A=M
M=D
@SP
M=M+1
// add
@SP
AM=M-1
D=M
M=0
A=A-1
M=D+M
// push constant 112
@112
D=A
@SP
A=M
M=D
@SP
M=M+1
// sub
@SP
AM=M-1
D=M
M=0
A=A-1
M=M-D
// neg
@SP
A=M-1
M=-M
// and
@SP
AM=M-1
D=M
M=0
A=A-1
M=D&M
// push constant 82
@82
D=A
@SP
A=M
M=D
@SP
M=M+1
// or
@SP
AM=M-1
D=M
M=0
A=A-1
M=D|M
// not
@SP
A=M-1
M=!M
