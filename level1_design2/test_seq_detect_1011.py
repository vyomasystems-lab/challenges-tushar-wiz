# See LICENSE.vyoma for details

# SPDX-License-Identifier: CC0-1.0

import os
import random
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge

@cocotb.test()
async def test_seq_bug1(dut):
    """Test for seq detection """

    clock = Clock(dut.clk, 10, units="us")  # Create a 10us period clock on port clk
    cocotb.start_soon(clock.start())        # Start the clock

    # reset
    dut.reset.value = 1
    await FallingEdge(dut.clk)  
    dut.reset.value = 0
    await FallingEdge(dut.clk)

    cocotb.log.info('#### CTB: Develop your test here! ######')
    stateDict = {"0000":0, "0100":0, "1000":0, "1100":0,           # IDLE              0th state
                "0001":1, "0011":1, "0111":1, "1001":1, "1111":1,  # xxx1 = SEQ_1      1st state
                "0010":2, "0110":2, "1010":2, "1110":2,            # xx10 = SEQ_10     2nd state
                "0101":3, "1101":3,                                # x101 = SEQ_101    3rd state
                "1011":4}                                          # 1011 = SEQ_1011   4th state


    random.seed(10)
    seq = list()
    
    for _ in range(1024):
        seq.append(random.randint(0, 1))
    seq += [1,0,1,1,1,0,1,1,0,1,0,1,1,0,1,1,1,1]
    lastCycleState = 0
    lastCycleFour = [0,0,0,0]
    for x in seq:
        dut.inp_bit.value = x        
        await RisingEdge(dut.clk)
        
        dut._log.info("last four values = %s",lastCycleFour)
        dut._log.info("seq_seen = %s",dut.seq_seen.value)
        dut._log.info("current_state = %d", dut.current_state.value.integer)
        lastCycleFourStr = ''.join([str(elem) for elem in lastCycleFour])
        dut._log.info("Correct State = %d",stateDict[lastCycleFourStr])
        
        if(lastCycleFourStr == "1011"):
            if(dut.seq_seen.value != 1):
                print("ERROR --> Sequence detected but seq_seen=0 EXP=1")
            lastCycleFour = [0,0,0,0]
        else:
            errorStr = "\n\nState should have been {LASTCYCLESTATE} --> {EXP} \t And not {LASTCYCLESTATE} --> {SIM} when PrevBit={INP_LAST}\nInput Bit={INP}".format(LASTCYCLESTATE=lastCycleState ,SIM=dut.current_state.value.integer, EXP=stateDict[lastCycleFourStr], INP_LAST=lastCycleFour[-1], INP=dut.inp_bit.value.integer)
            assert dut.current_state.value == stateDict[lastCycleFourStr], errorStr

        lastCycleState = dut.current_state.value.integer
        lastCycleFour.pop(0)
        lastCycleFour.append(x)

        print()
