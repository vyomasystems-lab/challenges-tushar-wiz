# Level 3 Design - Tushar Upadhyay

![](https://imgur.com/7LwwvpD.png)

## Verification Environment
For the level 3 design, I chose the fixed point multiplier from the Fixed Point Math Library(https://opencores.org/projects/verilog_fixed_point_math_library). This design is completely open source with an LGPL license.  
Fxpmath (python module) is used to verify the fixed point multiplier block. Fxpmath is dependent on NumPy; hence we install both Fxpmath and NumPy. 
  
The Clock generation block.
```
    clock = Clock(dut.i_clk, 10, units="us")  # Create a 10us period clock on port clk
    cocotb.start_soon(clock.start())          # Start the clock
```
  
Two lists are created, `A_list` and `B_list`, which contain all the values for the multiplicand and multiplier. The list contains some manual inputs and random inputs with constraints. The `random.uniform()` function append a random float between a given range.
```
A_list , B_list = [0,256,-255], [0,256,-255]

# No Overflow Inputs
for i in range(100):
    A_list.append(random.uniform(-256, 255))
    B_list.append(random.uniform(-256, 255))

# Random Inputs, Random Overflow
for i in range(100):
    A_list.append(random.uniform(-65536, 65535))
    B_list.append(random.uniform(-65536, 65535))
```

The lists are iterated and inputted to the DUT.  
The DUT stores the number in 32 bits. The MSB represents the sign(1 for -ve and 0 for +ve). 31 bits are for the magnitude, where the trailing 15 bits are for the fraction. The DUT does not follow the 2's complement rule to store negative numbers. Rather it stores the sign bit separately and the magnitude separately.  
Fxp(values, signed, N, Q) creates a fixed point number.
```
    for i in range(len(A_list)):
        A_fxp = Fxp(abs(A_list[i]),False,31,15)                 # Fixed point number is generated with only magnitude
        B_fxp = Fxp(abs(B_list[i]),False,31,15)

        A = int((str(int(A_list[i] < 0)) + A_fxp.bin()),2)      # sign bit is inserted
        B = int((str(int(B_list[i] < 0)) + B_fxp.bin()),2)

        dut.i_start.value = 0
        dut.i_multiplicand.value = 0
        dut.i_multiplier.value = 0
        await RisingEdge(dut.i_clk)

        dut.i_start.value = 1
        dut.i_multiplicand.value = A
        dut.i_multiplier.value = B

        await RisingEdge(dut.o_complete)                        # We wait for the operation to complete
        dut.i_start.value = 0
        await RisingEdge(dut.i_clk)
        
        binaryString = Fxp(A_fxp * B_fxp ,False,31,15)          # Multiply the two numbers in fixed point without sign

        if(binaryString.status['overflow'] == True):            # Condition for overflow in the fxpmath lib
            assert dut.o_overflow.value == 1, "Overflow Not Detected\n"
        else:                                                   # If no overflow we equate the input and output
            finalValString = (str(int(A_list[i] * B_list[i] < 0))+binaryString.bin())
            errorString = "Value or Sign Error\nEXP={EXP}\nSIM={SIM}\n".format(EXP=finalValString, SIM=dut.o_result_out.value.binstr)
            assert dut.o_result_out.value.binstr ==  finalValString, errorString
```

> For the competition purpose, a bug is inserted into the design with the file name `qmults_bugged.v` 
> The original file with no errors is saved as `qmults.v`

## Test Scenario
```
i_multiplicand  = 0b00000000100000000000000000000000  
i_multiplier    = 0b00000000100000000000000000000000
o_overflow (SIM)= 0b0
o_overflow (EXP)= 0b1
```
We see that the overflow flag is not raised for this operation even though it is impossible to store it in 32 bits.
![](https://imgur.com/WJFmy7P.png)

## Design Bug
```
83| if (reg_working_result[2*N-2:N-1+Q] > 0)            // Check for an overflow
84|     reg_overflow <= 1'b0;                       <== BUG
85| end
```
The overflow register is not set to 1 in case the overflow is detected.

## Design Fix
```
83| if (reg_working_result[2*N-2:N-1+Q] > 0)            // Check for an overflow
84|     reg_overflow <= 1'b1;
85| end
```
We fix line 84 and set it to 1 if overflow occurs.

![](https://imgur.com/obS88Od.png)
## Verification Strategy
The inputs given to the DUT are a mix of manual and constrained random inputs. As soon as the `i_start` bit is set to 1, the multiplication starts. At the rising edge of the `o_complete` signal, we switch `i_start` to 0, and at the next rising edge of the clock cycle, we evaluate the output. 

## Is the verification complete ?
The verification done here uses edge cases and random inputs. The module has a parameter where we can reduce or increase the number of bits used for multiplication. However, the tests are only done with N as 32 and Q as 15. Where N is the total number of bits and Q is the number of bits for representing fractions. With 200 inputs for multiplicand and multiplier each, the verification of the module can be deemed complete.