import random
import cocotb
from cocotb.decorators import coroutine
from cocotb.triggers import Timer, RisingEdge
from cocotb.result import TestFailure
from cocotb.clock import Clock
from fxpmath import Fxp

@cocotb.test()
async def mult_range(dut):
    clock = Clock(dut.i_clk, 10, units="us")  # Create a 10us period clock on port clk
    cocotb.start_soon(clock.start())          # Start the clock

    # Manual Inputs
    A_list , B_list = [0,256,-255], [0,256,-255]

    # No Overflow Inputs
    for i in range(100):
        A_list.append(random.uniform(-256, 255))
        B_list.append(random.uniform(-256, 255))

    # Random Inputs, Random Overflow
    for i in range(100):
        A_list.append(random.uniform(-65536, 65535))
        B_list.append(random.uniform(-65536, 65535))

    for i in range(len(A_list)):
        A_fxp = Fxp(abs(A_list[i]),False,31,15)
        B_fxp = Fxp(abs(B_list[i]),False,31,15)

        A = int((str(int(A_list[i] < 0)) + A_fxp.bin()),2)
        B = int((str(int(B_list[i] < 0)) + B_fxp.bin()),2)

        dut.i_start.value = 0
        dut.i_multiplicand.value = 0
        dut.i_multiplier.value = 0
        await RisingEdge(dut.i_clk)

        dut.i_start.value = 1
        dut.i_multiplicand.value = A
        dut.i_multiplier.value = B

        await RisingEdge(dut.o_complete)
        dut.i_start.value = 0
        await RisingEdge(dut.i_clk)
        
        binaryString = Fxp(A_fxp * B_fxp ,False,31,15)

        
        if(binaryString.status['overflow'] == True):
            errorString = "Overflow not Detected Error\nA={A}\nB={B}\n".format(A=dut.i_multiplicand.value.binstr, B=dut.i_multiplier.value.binstr)
            assert dut.o_overflow.value == 1, errorString
        else:
            finalValString = (str(int(A_list[i] * B_list[i] < 0))+binaryString.bin())
            errorString = "Value or Sign Error\nA={A}\nB={B}\nEXP={EXP}\nSIM={SIM}\n".format(A=dut.i_multiplicand.value.binstr, B=dut.i_multiplier.value.binstr, EXP=finalValString, SIM=dut.o_result_out.value.binstr)
            print("SIM = "+ dut.o_result_out.value.binstr)
            print("EXP = "+ finalValString)
            assert dut.o_result_out.value.binstr ==  finalValString, errorString
