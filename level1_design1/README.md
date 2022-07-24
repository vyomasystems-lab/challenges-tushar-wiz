# Level 1 Design 1 - Tushar Upadhyay

![](https://imgur.com/zJyFqQU.png)

## Verification Environment

The test 
The values are assigned to the input port using 

Creates a list of strings with string of input names (inp0,inp1,inp2,inp3....,inp30)
```
  mux_inp = ["inp"+str(a) for a in range(31)]
  print(mux_inp)
```
This loop goes over all the specified values of the select line that is 0 to 30. It selects the input that correspond to variable `select` and the sets the value of the `inp{select}`.  

Example -  
When `select` is 5. We set all inputs (inp0, inp1, inp2, ... inp30) to 0 except inp5. Rather we set inp5 to 3. Then we set dut.sel.value to 5. If dut.out.value comes out to be 3 we know that the input is connected correctly to the corresponding dut.sel.value.
```
for select in range(31):
  
  for i in range(0,31):
      temp = getattr(dut, mux_inp[i])
      temp.value = 0
  
  mux_high = getattr(dut, mux_inp[select])
  mux_high.value = 3

  dut.sel.value = select
  await Timer(1, units="ns")
  dut._log.info("Sel = %s Out = %s", dut.sel.value, dut.out.value)
```
  
This block of code checks for errors and logs all the errors inside a list which gets printed at the end.
```
if(dut.out.value != 3):
    errorNumbers += 1
    errorCause.append("Wrong Input Selected at sel={A} SIM_VALUE={SIM} EXP_VALUE=11\n".format(A = dut.sel.value, SIM=dut.out.value))
```

All the errors get printed and if the number of errors are greater than 0, the assert keyword gets activated which displays that the source file has failed the test.
```
for x in errorCause:
    print(x)
assert (errorNumbers == 0), "Errors Detected"
```

## Test Scenario
- Test Inputs: inp0=0, inp1=0, inp2=0, inp3=0, inp4=0, inp5=0, inp6=0, inp7=0, inp8=0, inp9=0, inp10=0, inp11=0, inp12=`2'b11`, inp13=0, inp14=0, inp15=0, inp16=0, inp17=0, inp18=0, inp19=0, inp20=0, inp21=0, inp22=0, inp23=0, inp24=0, inp25=0, inp26=0, inp27=0, inp28=0, inp29=0, inp30=0, sel=`5'b01100`
- Expected Output: out=`2'b11`
- Observed Output in the DUT dut.sel=`2'b00`

## Test Scenario
- Test Inputs: inp0=0, inp1=0, inp2=0, inp3=0, inp4=0, inp5=0, inp6=0, inp7=0, inp8=0, inp9=0, inp10=0, inp11=0, inp12=0, inp13= `2'b11` , inp14=0, inp15=0, inp16=0, inp17=0, inp18=0, inp19=0, inp20=0, inp21=0, inp22=0, inp23=0, inp24=0, inp25=0, inp26=0, inp27=0, inp28=0, inp29=0, inp30=0, sel=`5'b01101`
- Expected Output: out=`2'b11`
- Observed Output in the DUT dut.sel=`2'b00`

![](https://imgur.com/WTAQbGg.png)

## Design Bug
Based on the above test input and analysing the design, we see the following

```
39|  5'b01011: out = inp11;
40|  5'b01101: out = inp12;   <== BUG
41|  5'b01101: out = inp13;
```
In the design there is no case for 5'b01100 and the case for 5'b01101 is repeated twice. Both the failures above can be fixed by fixing this bug.

## Design Fix
We Update design and change line 40 to 
```
40|  5'b01100: out = inp12;
```
By making this change we fix both the errors listed above.
![](https://imgur.com/pfP90Pt.png)

## Test Scenario
- Test Inputs: inp0=0, inp1=0, inp2=0, inp3=0, inp4=0, inp5=0, inp6=0, inp7=0, inp8=0, inp9=0, inp10=0, inp11=0, inp12=0, inp13=0, inp14=0, inp15=0, inp16=0, inp17=0, inp18=0, inp19=0, inp20=0, inp21=0, inp22=0, inp23=0, inp24=0, inp25=0, inp26=0, inp27=0, inp28=0, inp29=0, inp30=`2'b11`, sel=`5'b01100`
- Expected Output: out=`2'b11`
- Observed Output in the DUT dut.sel=`2'b00`

Output mismatches for the above inputs proving that there is a design bug

## Design Bug
Based on the above test input and analysing the design, we see the following

```
57|    5'b11101: out = inp29;   <== BUG
58|    default: out = 0;        
59| endcase
```
In the design there is no case for 5'b11110.

## Design Fix
We Update design and change line 40 to 
```
57|  5'b11101: out = inp29;
58|  5'b11110: out = inp30;
59|  default: out = 0;
```
After fixing this bug we see all the errors have been resolved and the run passes without any errors.

![](https://imgur.com/jC5Qqkr.png)

## Verification Strategy
Verification strategy is to go over all the select lines possible one by one while inputing a number only to the corresponding input that is selected. If we see that the output is not equal to the input we can conclude that there is a bug at the particular select value.

## Is the verification complete ?
This verification makes sure that the inputs are connected correctly to the corresponding select lines. Also that all the inputs are of 2 bit width.