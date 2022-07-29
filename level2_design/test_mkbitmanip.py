# See LICENSE.iitm for details
# See LICENSE.vyoma for details

import random
import os
import sys
import cocotb
from cocotb.decorators import coroutine
from cocotb.triggers import Timer, RisingEdge
from cocotb.result import TestFailure
from cocotb.clock import Clock
from tabulate import tabulate

from model_mkbitmanip import *

import os

if os.path.exists("errors.txt"):
  os.remove("errors.txt")
else:
  print("The file does not exist") 

f = open("errors.txt","x")
f.close()

def Rtype(funct7, funct3, opcode):
    return ((funct7 << 25)|(funct3 << 12)|(opcode))

def Itype(funct7_imm, imm, funct3, opcode):
    return ((funct7_imm << 27)|(imm << 20)|(funct3 << 12)|opcode)

def I_func_type(funct7, imm_value1, func3, opcode):
    return ((funct7 << 25)|(imm_value1 << 20)|(func3 << 12)|opcode)

def R4type(funct2,funct3,opcode):
    return ((funct2 << 25)|(funct3 << 12)|(opcode))

def errorLog(dut, dut_output, expected_mav_putvalue, instr):
    errorEntry = list()
    errorEntry.append(f'{hex(dut_output)}')
    errorEntry.append(f'{hex(expected_mav_putvalue)}')
    errorEntry.append(f'{hex(dut.mav_putvalue_src1.value)}')
    errorEntry.append(f'{hex(dut.mav_putvalue_src2.value)}')
    errorEntry.append(f'{hex(dut.mav_putvalue_src3.value)}')
    errorEntry.append(f'{instr}')

    return errorEntry

def errorWrite(funcs_logged, errorList):
    r = open("errors.txt", 'a')
    r.write("\n\n"+funcs_logged+"\n\n")

    if(len(errorList) != 0):
        r.write(tabulate(errorList,headers=["DUT OUTPUT","EXPECTED OUTPUT","SRC1","SRC2","SRC3","INST"]))
        r.close()
        return False
    else:
        r.write(tabulate([],headers=["DUT OUTPUT","EXPECTED OUTPUT","SRC1","SRC2","SRC3","INST"]))
        r.write("\nNO Errors Detected\n")
        r.close()
        return True

# Clock Generation
@cocotb.coroutine
def clock_gen(signal):
    while True:
        signal.value <= 0
        yield Timer(1) 
        signal.value <= 1
        yield Timer(1) 

@cocotb.test()
def test_0110011_Rtype(dut):
    opcode = 0b0110011
    cocotb.fork(clock_gen(dut.CLK))

    # reset
    dut.RST_N.value <= 0
    yield Timer(10) 
    dut.RST_N.value <= 1

    test_vals = [0x0,0x1,0x55555555,0xAAAAAAAA,0x7fffffff,0xfffffffe,0xfffffff]

    operations = list()

    operations.append(Rtype(0b0100000, 0b111, opcode))    # ANDN
    operations.append(Rtype(0b0100000, 0b110, opcode))    # ORN
    operations.append(Rtype(0b0100000, 0b100, opcode))    # XNOR
    operations.append(Rtype(0b0010000, 0b001, opcode))    # SLO
    operations.append(Rtype(0b0010000, 0b101, opcode))    # SRO
    operations.append(Rtype(0b0110000, 0b001, opcode))    # ROL
    operations.append(Rtype(0b0110000, 0b101, opcode))    # ROR
    operations.append(Rtype(0b0100100, 0b001, opcode))    # SBCLR
    operations.append(Rtype(0b0010100, 0b001, opcode))    # SBSET
    operations.append(Rtype(0b0110100, 0b001, opcode))    # SBINV
    operations.append(Rtype(0b0100100, 0b101, opcode))    # SBEXT
    operations.append(Rtype(0b0010100, 0b101, opcode))    # GORC
    operations.append(Rtype(0b0110100, 0b101, opcode))    # GREV
    operations.append(Rtype(0b0010000, 0b010, opcode))    # SH1ADD
    operations.append(Rtype(0b0010000, 0b100, opcode))    # SH2ADD
    operations.append(Rtype(0b0010000, 0b110, opcode))    # SH3ADD
    operations.append(Rtype(0b0000101, 0b001, opcode))    # CLMUL
    operations.append(Rtype(0b0000101, 0b011, opcode))    # CLMULH
    operations.append(Rtype(0b0000101, 0b010, opcode))    # CLMULR
    operations.append(Rtype(0b0000101, 0b100, opcode))    # MIN
    operations.append(Rtype(0b0000101, 0b101, opcode))    # MAX
    operations.append(Rtype(0b0000101, 0b110, opcode))    # MINU
    operations.append(Rtype(0b0000101, 0b111, opcode))    # MAXU
    operations.append(Rtype(0b0100100, 0b110, opcode))    # BDEP
    operations.append(Rtype(0b0000100, 0b110, opcode))    # BEXT
    operations.append(Rtype(0b0000100, 0b100, opcode))    # PACK
    operations.append(Rtype(0b0100100, 0b100, opcode))    # PACKU
    operations.append(Rtype(0b0000100, 0b111, opcode))    # PACKH
    operations.append(Rtype(0b0000100, 0b001, opcode))    # SHFL
    operations.append(Rtype(0b0000100, 0b101, opcode))    # UNSHFL
    operations.append(Rtype(0b0100100, 0b111, opcode))    # BFP

    testInstructions = "ANDN ORN XNOR SLO SRO ROL ROR SBCLR SBSET SBINV SBEXT GORC GREV SH1ADD SH2ADD SH3ADD CLMUL CLMULH CLMULR MIN MAX MINU MAXU BDEP BEXT PACK PACKU PACKH SHFL UNSHFL BFP"

    errors = list()

    for op in operations:
        for src1_val in test_vals:
            for src2_val in test_vals:
                mav_putvalue_src1 = src1_val
                mav_putvalue_src2 = src2_val
                mav_putvalue_src3 = random.randint(0, (1<<32)-1)
                mav_putvalue_instr = op

                expected_mav_putvalue = bitmanip(mav_putvalue_instr, mav_putvalue_src1, mav_putvalue_src2, mav_putvalue_src3)
                
                dut.mav_putvalue_src1.value = mav_putvalue_src1
                dut.mav_putvalue_src2.value = mav_putvalue_src2
                dut.mav_putvalue_src3.value = mav_putvalue_src3
                dut.EN_mav_putvalue.value = 1
                dut.mav_putvalue_instr.value = mav_putvalue_instr
                yield Timer(1)

                dut_output = dut.mav_putvalue.value

                if dut_output != expected_mav_putvalue:
                    errors.append(errorLog(dut, dut_output, expected_mav_putvalue,dut.mav_putvalue_instr.value.binstr))
    assert errorWrite(testInstructions, errors)

@cocotb.test()
def test_0010011_Itype(dut):
    opcode = 0b0010011
    cocotb.fork(clock_gen(dut.CLK))

    # reset
    dut.RST_N.value <= 0
    yield Timer(10) 
    dut.RST_N.value <= 1

    test_vals = [0x0,0x1,0x55555555,0xAAAAAAAA,0x7fffffff,0xfffffffe,0xfffffff]

    operations = list()

    src1_vals = test_vals
    imm = [0b0000000,0b0000001,0b0101010,0b1010101,0b0111111,0b1111110,0b1111111]

    operations.append(Itype(0b00100, 0b0, 0b001, opcode))    # SLOI
    operations.append(Itype(0b00100, 0b0, 0b101, opcode))    # SROI
    operations.append(Itype(0b01100, 0b0, 0b101, opcode))    # RORI
    operations.append(Itype(0b01001, 0b0, 0b001, opcode))    # SBCLRI
    operations.append(Itype(0b00101, 0b0, 0b001, opcode))    # SBSETI
    operations.append(Itype(0b01101, 0b0, 0b001, opcode))    # SBINVI
    operations.append(Itype(0b01001, 0b0, 0b101, opcode))    # SBEXTI
    operations.append(Itype(0b00101, 0b0, 0b101, opcode))    # GORCI
    operations.append(Itype(0b01101, 0b0, 0b101, opcode))    # GREVI

    testInstructions = "SLOI SROI RORI SBCLRI SBSETI SBINVI SBEXTI GORCI GREVI"

    errors = list()

    for op in operations:
        for src1_val in test_vals:
            for imm_val in imm:
                mav_putvalue_src1 = src1_val
                mav_putvalue_src2 = random.randint(0, (1<<32)-1)
                mav_putvalue_src3 = random.randint(0, (1<<32)-1)

                mav_putvalue_instr = op|(imm_val<<20)
                expected_mav_putvalue = bitmanip(mav_putvalue_instr, mav_putvalue_src1, mav_putvalue_src2, mav_putvalue_src3)
                
                dut.mav_putvalue_src1.value = mav_putvalue_src1
                dut.mav_putvalue_src2.value = mav_putvalue_src2
                dut.mav_putvalue_src3.value = mav_putvalue_src3

                dut.EN_mav_putvalue.value = 1
                dut.mav_putvalue_instr.value = mav_putvalue_instr
                yield Timer(1)

                dut_output = dut.mav_putvalue.value

                if dut_output != expected_mav_putvalue:
                    errors.append(errorLog(dut, dut_output, expected_mav_putvalue,dut.mav_putvalue_instr.value.binstr))
    assert errorWrite(testInstructions, errors)

@cocotb.test()
def test_0010011_Ifunc(dut):
    opcode = 0b0010011
    cocotb.fork(clock_gen(dut.CLK))

    # reset
    dut.RST_N.value <= 0
    yield Timer(10) 
    dut.RST_N.value <= 1

    test_vals = [0x0,0x1,0x55555555,0xAAAAAAAA,0x7fffffff,0xfffffffe,0xfffffff]

    operations = list()

    operations.append(I_func_type(0b0110000, 0b00000, 0b001, opcode))    # CLZ
    operations.append(I_func_type(0b0110000, 0b00001, 0b001, opcode))    # CTZ
    operations.append(I_func_type(0b0110000, 0b00010, 0b001, opcode))    # PCNT
    operations.append(I_func_type(0b0110000, 0b00100, 0b001, opcode))    # SEXT.B
    operations.append(I_func_type(0b0110000, 0b00101, 0b001, opcode))    # SEXT.H
    operations.append(I_func_type(0b0110000, 0b10000, 0b001, opcode))    # CRC32.B
    operations.append(I_func_type(0b0110000, 0b10001, 0b001, opcode))    # CRC32.H
    operations.append(I_func_type(0b0110000, 0b10010, 0b001, opcode))    # CRC32.W
    operations.append(I_func_type(0b0110000, 0b11000, 0b001, opcode))    # CRC32C.B
    operations.append(I_func_type(0b0110000, 0b11001, 0b001, opcode))    # CRC32C.H
    operations.append(I_func_type(0b0110000, 0b11010, 0b001, opcode))    # CRC32C.W

    testInstructions = "CLZ CTZ PCNT SEXT.B SEXT.H CRC32.B CRC32.H CRC32.W CRC32C.B CRC32C.H CRC32C.W"

    errors = list()

    for op in operations:
        for src1_val in test_vals:
            mav_putvalue_src1 = src1_val
            mav_putvalue_src2 = random.randint(0, (1<<32)-1)
            mav_putvalue_src3 = random.randint(0, (1<<32)-1)

            mav_putvalue_instr = op
            expected_mav_putvalue = bitmanip(mav_putvalue_instr, mav_putvalue_src1, mav_putvalue_src2, mav_putvalue_src3)
            
            dut.mav_putvalue_src1.value = mav_putvalue_src1
            dut.mav_putvalue_src2.value = mav_putvalue_src2
            dut.mav_putvalue_src3.value = mav_putvalue_src3
            dut.EN_mav_putvalue.value = 1
            dut.mav_putvalue_instr.value = mav_putvalue_instr
            yield Timer(1)

            dut_output = dut.mav_putvalue.value

            if dut_output != expected_mav_putvalue:
                errors.append(errorLog(dut, dut_output, expected_mav_putvalue,dut.mav_putvalue_instr.value.binstr))
    assert errorWrite(testInstructions, errors)

@cocotb.test()
def test_0110011_R4type(dut):
    opcode = 0b0110011
    cocotb.fork(clock_gen(dut.CLK))

    # reset
    dut.RST_N.value <= 0
    yield Timer(10) 
    dut.RST_N.value <= 1

    test_vals = [0x0,0x1,0x55555555,0xAAAAAAAA,0x7fffffff,0xfffffffe,0xfffffff]
    operations = list()

    operations.append(R4type(0b11, 0b001, opcode))    # CMIX
    operations.append(R4type(0b11, 0b101, opcode))    # CMOV
    operations.append(R4type(0b10, 0b001, opcode))    # FSL
    operations.append(R4type(0b10, 0b101, opcode))    # FSR

    testInstructions = "CMIX CMOV FSL FSR"

    errors = list()

    for op in operations:
        for src1_val in test_vals:
            for src2_val in test_vals:
                for src3_val in test_vals:
                    mav_putvalue_src1 = src1_val
                    mav_putvalue_src2 = src2_val
                    mav_putvalue_src3 = src3_val
                    mav_putvalue_instr = op
                    expected_mav_putvalue = bitmanip(mav_putvalue_instr, mav_putvalue_src1, mav_putvalue_src2, mav_putvalue_src3)
                    
                    dut.mav_putvalue_src1.value = mav_putvalue_src1
                    dut.mav_putvalue_src2.value = mav_putvalue_src2
                    dut.mav_putvalue_src3.value = mav_putvalue_src3
                    dut.EN_mav_putvalue.value = 1
                    dut.mav_putvalue_instr.value = mav_putvalue_instr
                    yield Timer(1)

                    dut_output = dut.mav_putvalue.value

                    if dut_output != expected_mav_putvalue:
                        errors.append(errorLog(dut, dut_output, expected_mav_putvalue,dut.mav_putvalue_instr.value.binstr))
    assert errorWrite(testInstructions, errors)

@cocotb.test()
def test_0010011_FSRI_SHFLI_UNSHFLI(dut):
    opcode = 0b0010011
    cocotb.fork(clock_gen(dut.CLK))

    # reset
    dut.RST_N.value <= 0
    yield Timer(10) 
    dut.RST_N.value <= 1

    test_vals = [0x0,0x1,0x55555555,0xAAAAAAAA,0x7fffffff,0xfffffffe,0xfffffff]

    imm = [0b000000,0b000001,0b010101,0b101010,0b011111,0b111110,0b111111]

    operations = list()
    operations.append((0b1 << 26)|(0b101 << 12)|opcode)        # FSRI
    operations.append((0b000010 << 26)|(0b001 << 12)|opcode)   # SHFLI
    operations.append((0b000010 << 26)|(0b101 << 12)|opcode)   # UNSHFLI
    
    testInstructions = "FSRI SHFLI UNSHFLI"

    errors = list()

    for op in operations:
        for src1_val in test_vals:
            for src3_val in test_vals:
                for imm_val in imm:
                    mav_putvalue_src1 = src1_val
                    mav_putvalue_src2 = random.randint(0, (1<<32)-1)
                    mav_putvalue_src3 = src3_val
                    mav_putvalue_instr = op|(imm_val << 20)
                    expected_mav_putvalue = bitmanip(mav_putvalue_instr, mav_putvalue_src1, mav_putvalue_src2, mav_putvalue_src3)
                    
                    dut.mav_putvalue_src1.value = mav_putvalue_src1
                    dut.mav_putvalue_src2.value = mav_putvalue_src2
                    dut.mav_putvalue_src3.value = mav_putvalue_src3
                    dut.EN_mav_putvalue.value = 1
                    dut.mav_putvalue_instr.value = mav_putvalue_instr
                    yield Timer(1)

                    dut_output = dut.mav_putvalue.value

                    if dut_output != expected_mav_putvalue:
                        errors.append(errorLog(dut, dut_output, expected_mav_putvalue,dut.mav_putvalue_instr.value.binstr))
    assert errorWrite(testInstructions, errors)
