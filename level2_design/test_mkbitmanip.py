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
def test_0110011_simple_operations(dut):
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

    typeOfOperation = {'111':'ANDN', '110':'ORN', '100':'XNOR'}

    errors = list()

    for op in operations:
        for src1_val in test_vals:
            for src2_val in test_vals:
                mav_putvalue_src1 = src1_val
                mav_putvalue_src2 = src2_val
                mav_putvalue_instr = op
                expected_mav_putvalue = bitmanip(mav_putvalue_instr, mav_putvalue_src1, mav_putvalue_src2, 0)
                
                dut.mav_putvalue_src1.value = mav_putvalue_src1
                dut.mav_putvalue_src2.value = mav_putvalue_src2
                dut.mav_putvalue_src3.value = 0
                dut.EN_mav_putvalue.value = 1
                dut.mav_putvalue_instr.value = mav_putvalue_instr
                yield Timer(1)

                dut_output = dut.mav_putvalue.value

                if dut_output != expected_mav_putvalue:
                    errors.append(errorLog(dut, dut_output, expected_mav_putvalue,typeOfOperation[dut.mav_putvalue_instr.value.binstr[-15:-12]]))

    assert errorWrite("ANDN ORN XNOR", errors)



@cocotb.test()
def test_0110011_shift_operations(dut):
    opcode = 0b0110011
    cocotb.fork(clock_gen(dut.CLK))

    # reset
    dut.RST_N.value <= 0
    yield Timer(10) 
    dut.RST_N.value <= 1
 
    test_vals = [0x0,0x1,0x55555555,0xAAAAAAAA,0x7fffffff,0xfffffffe,0xfffffff]
    operations = list()

    operations.append(Rtype(0b0010000, 0b001, opcode))    # SLO
    operations.append(Rtype(0b0010000, 0b101, opcode))    # SRO
    operations.append(Rtype(0b0110000, 0b001, opcode))    # ROL
    operations.append(Rtype(0b0110000, 0b101, opcode))    # ROR

    errors = list()

    for op in operations:
        for src1_val in test_vals:
            for src2_val in test_vals:
                mav_putvalue_src1 = src1_val
                mav_putvalue_src2 = src2_val
                mav_putvalue_instr = op
                expected_mav_putvalue = bitmanip(mav_putvalue_instr, mav_putvalue_src1, mav_putvalue_src2, 0)
                
                dut.mav_putvalue_src1.value = mav_putvalue_src1
                dut.mav_putvalue_src2.value = mav_putvalue_src2
                dut.mav_putvalue_src3.value = 0
                dut.EN_mav_putvalue.value = 1
                dut.mav_putvalue_instr.value = mav_putvalue_instr
                yield Timer(1)

                dut_output = dut.mav_putvalue.value

                if dut_output != expected_mav_putvalue:
                    errors.append(errorLog(dut, dut_output, expected_mav_putvalue,dut.mav_putvalue_instr.value.binstr[-15:-12]))
    assert errorWrite("SLO SRO ROL", errors)


@cocotb.test()
def test_0110011_SB_operations(dut):
    opcode = 0b0110011
    cocotb.fork(clock_gen(dut.CLK))

    # reset
    dut.RST_N.value <= 0
    yield Timer(10) 
    dut.RST_N.value <= 1

    test_vals = [0x0,0x1,0x55555555,0xAAAAAAAA,0x7fffffff,0xfffffffe,0xfffffff]
    operations = list()

    operations.append(Rtype(0b0100100, 0b001, opcode))    # SBCLR
    operations.append(Rtype(0b0010100, 0b101, opcode))    # SBSET
    operations.append(Rtype(0b0110100, 0b001, opcode))    # SBINV
    operations.append(Rtype(0b0100100, 0b101, opcode))    # SBEXT
    operations.append(Rtype(0b0010100, 0b101, opcode))    # GORC
    operations.append(Rtype(0b0110100, 0b101, opcode))    # GREV

    errors = list()

    for op in operations:
        for src1_val in test_vals:
            for src2_val in test_vals:
                mav_putvalue_src1 = src1_val
                mav_putvalue_src2 = src2_val
                mav_putvalue_instr = op
                expected_mav_putvalue = bitmanip(mav_putvalue_instr, mav_putvalue_src1, mav_putvalue_src2, 0)
                
                dut.mav_putvalue_src1.value = mav_putvalue_src1
                dut.mav_putvalue_src2.value = mav_putvalue_src2
                dut.mav_putvalue_src3.value = 0
                dut.EN_mav_putvalue.value = 1
                dut.mav_putvalue_instr.value = mav_putvalue_instr
                yield Timer(1)

                dut_output = dut.mav_putvalue.value

                if dut_output != expected_mav_putvalue:
                    errors.append(errorLog(dut, dut_output, expected_mav_putvalue,dut.mav_putvalue_instr.value.binstr[-15:-12]))
    assert errorWrite("SBCLR SBSET SBINV SBEXT GORC GREV", errors)



@cocotb.test()
def test_0010011_shift_operations(dut):
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

    operations.append(Itype(0b00100,0b0, 0b001, opcode))    # SLOI
    operations.append(Itype(0b00100,0b0, 0b101, opcode))    # SROI
    operations.append(Itype(0b01100,0b0, 0b101, opcode))    # RORI

    errors = list()

    for op in operations:
        for src1_val in test_vals:
            for imm_val in imm:
                mav_putvalue_src1 = src1_val
                mav_putvalue_instr = op|(imm_val<<20)
                expected_mav_putvalue = bitmanip(mav_putvalue_instr, mav_putvalue_src1, 0, 0)
                
                dut.mav_putvalue_src1.value = mav_putvalue_src1
                dut.mav_putvalue_src2.value = 0
                dut.mav_putvalue_src3.value = 0
                dut.EN_mav_putvalue.value = 1
                dut.mav_putvalue_instr.value = mav_putvalue_instr
                yield Timer(1)

                dut_output = dut.mav_putvalue.value

                if dut_output != expected_mav_putvalue:
                    errors.append(errorLog(dut, dut_output, expected_mav_putvalue,dut.mav_putvalue_instr.value.binstr[-15:-12]))
    assert errorWrite("SLOI SROI RORI", errors)

@cocotb.test()
def test_0010011_SB_Imm_operations(dut):
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

    operations.append(Itype(0b01001, 0, 0b001, opcode))    # SBCLRI
    operations.append(Itype(0b00101, 0, 0b001, opcode))    # SBSETI
    operations.append(Itype(0b01101, 0, 0b001, opcode))    # SBINVI
    operations.append(Itype(0b01001, 0, 0b101, opcode))    # SBEXTI
    operations.append(Itype(0b00101, 0, 0b101, opcode))    # GORCI
    operations.append(Itype(0b01101, 0, 0b101, opcode))    # GREVI

    errors = list()

    for op in operations:
        for src1_val in test_vals:
            for imm_val in imm:
                mav_putvalue_src1 = src1_val
                mav_putvalue_instr = op|(imm_val<<20)
                expected_mav_putvalue = bitmanip(mav_putvalue_instr, mav_putvalue_src1, 0, 0)
                
                dut.mav_putvalue_src1.value = mav_putvalue_src1
                dut.mav_putvalue_src2.value = 0
                dut.mav_putvalue_src3.value = 0
                dut.EN_mav_putvalue.value = 1
                dut.mav_putvalue_instr.value = mav_putvalue_instr
                yield Timer(1)

                dut_output = dut.mav_putvalue.value

                if dut_output != expected_mav_putvalue:
                    errors.append(errorLog(dut, dut_output, expected_mav_putvalue,dut.mav_putvalue_instr.value.binstr[-15:-12]))
    assert errorWrite("SBCLRI SBSETI SBINVI SBEXTI GORCI GREVI", errors)

@cocotb.test()
def test_0110011__Rtype_operations(dut):
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
                        errors.append(errorLog(dut, dut_output, expected_mav_putvalue,dut.mav_putvalue_instr.value.binstr[-15:-12]))
    assert errorWrite("CMIX CMOV FSL FSR", errors)

@cocotb.test()
def test_0010011__FSRI_operations(dut):
    opcode = 0b0010011
    cocotb.fork(clock_gen(dut.CLK))

    # reset
    dut.RST_N.value <= 0
    yield Timer(10) 
    dut.RST_N.value <= 1

    test_vals = [0x0,0x1,0x55555555,0xAAAAAAAA,0x7fffffff,0xfffffffe,0xfffffff]

    operations = list()
    operations.append((0b1 << 26)|(0b101 << 12)|opcode)        # FSRI
    
    imm = [0b000000,0b000001,0b010101,0b101010,0b011111,0b111110,0b111111]

    errors = list()

    for op in operations:
        for src1_val in test_vals:
            for src3_val in test_vals:
                for imm_val in imm:
                    mav_putvalue_src1 = src1_val
                    mav_putvalue_src2 = 0
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
                        errors.append(errorLog(dut, dut_output, expected_mav_putvalue,dut.mav_putvalue_instr.value.binstr[-15:-12]))
    assert errorWrite("FSRI", errors)