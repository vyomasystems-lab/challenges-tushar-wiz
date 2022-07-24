# See LICENSE.vyoma for details

import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_mux(dut):
    """Test for mux2"""

    cocotb.log.info('##### CTB: Develop your test here ########')
    
    # Getting all input names with inp{x} into one list 
    mux_inp = ["inp"+str(a) for a in range(31)]
    print(mux_inp)
    errorNumbers = 0
    errorCause = list()

    # Interating over sel values
    for select in range(31):
        # Setting all inp{x} to 0
        for i in range(0,31):
            temp = getattr(dut, mux_inp[i])
            temp.value = 0
        
        # Setting one inp{x} to be equal to 2'b11 
        mux_high = getattr(dut, mux_inp[select])
        mux_high.value = 3
        
        # Selecting the inp{x} whose value has been set to 2'b11
        dut.sel.value = select

        await Timer(1, units="ns")
        dut._log.info("Sel = %s Out = %s", dut.sel.value, dut.out.value)
        
        if(dut.out.value != 3):
            errorNumbers += 1
            errorCause.append("Wrong Input Selected at sel={A} SIM_VALUE={SIM} EXP_VALUE=11\n".format(A = dut.sel.value, SIM=dut.out.value))

    for x in errorCause:
        print(x)
    assert (errorNumbers == 0), "Errors Detected"
    
        