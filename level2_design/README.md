# Level 2 - Tushar Upadhyay

![](https://imgur.com/ZhBRtaD.png)

## Verification Environment

Verifying a big processor gives out many errors; hence, we require a separate file for logging all errors. This block of code is responsible for creating the file and removing it from a previous run if it exists. The file is created in the same directory as the python file.
```
if os.path.exists("errors.txt"):
  os.remove("errors.txt")
else:
  print("The file does not exist") 
f = open("errors.txt","x")
f.close()
```
These functions are defined making it easier for the user to create R-type, R4-type and I-type instructions.
```
def Rtype(funct7, funct3, opcode)
def Itype(funct7_imm, imm, funct3, opcode)
def I_func_type(funct7, imm_value1, func3, opcode)
def R4type(funct2,funct3,opcode)
```
Constructs a list with errors in a tabulated form.
```
def errorLog(dut, dut_output, expected_mav_putvalue, instr)
```
Writes all the errors to the text file.
```
def errorWrite(funcs_logged, errorList):
```
Different tests are defined for different types of instruction where different formats of inputs to the DUT are required. Namely,
```
test_0110011_Rtype 
test_0010011_Itype             
test_0010011_Ifunc              
test_0110011_R4type
test_0010011_FSRI_SHFLI_UNSHFLI
```
All of these tests have slightly different codes, but by the majority, all of these tests are coded similarly.
Hence we will only be evaluating `test_0110011_Rtype` in this document (other functions can be understood by reading the comments in the source code itself).  
`opcode` stores the opcode for the group of instructions
```
opcode = 0b0110011
cocotb.fork(clock_gen(dut.CLK))

# reset
dut.RST_N.value <= 0
yield Timer(10) 
dut.RST_N.value <= 1
```

`test_vals` contains all the values inputted to the DUT as operands.  
`operations` is a list that contains all the instructions that need to be executed.  
`errors` list stores all the errors when the testbench runs.  
`testInstructions` String that is appended to the `errors.txt` file to indicate the Instructions on which the tests were performed.
```
    test_vals = [0x0,0x1,0x55555555,0xAAAAAAAA,0x7fffffff,0xfffffffe,0xfffffff]

    operations = list()

    operations.append(Rtype(0b0100000, 0b111, opcode))    # ANDN
    operations.append(Rtype(0b0100000, 0b110, opcode))    # ORN
    operations.append(Rtype(0b0100000, 0b100, opcode))    # XNOR
    ...
    ...
    testInstructions = "ANDN ORN XNOR ... "
    errors = list()
```
The **for** loops iterate all the instructions stored in `operations` and all the values stored in `test_vals`, and input it to the DUT. Src1 and Src2 both iterate over `test_vals` while Src3 which is not used by Rtype instructions, is fed with random values to ensure the design works fine.  
After every calculation, the expected and actual values are equated; if not, they get appended to the `errors` list.  
At the end the `errors` list is passed to the `errorWrite` function which writes all the errors to the `errors.txt` file.
```
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
```

**Format of `errors.txt`**
The first line lists all the instructions tested, and if errors are found, they are listed in the table below. Else a "NO Errors Detected" is written.
Example - 
```
CMIX CMOV FSL FSR

DUT OUTPUT    EXPECTED OUTPUT    SRC1    SRC2    SRC3    INST
------------  -----------------  ------  ------  ------  ------
NO Errors Detected
```

## Test Scenario
Errors logged in the `errors.txt`
```
DUT OUTPUT    EXPECTED OUTPUT    SRC1        SRC2        SRC3                                    INST
------------  -----------------  ----------  ----------  ----------  --------------------------------
0x1           0x3                0x1         0x0         0xa4094c5d  01000000000000000111000000110011
0x3           0x1                0x1         0x1         0xaf8b282e  01000000000000000111000000110011
0x3           0x1                0x1         0x55555555  0xc5ce72d1  01000000000000000111000000110011
0x1           0x3                0x1         0xaaaaaaaa  0x96643cb1  01000000000000000111000000110011
0x3           0x1                0x1         0x7fffffff  0xbd0d1f0a  01000000000000000111000000110011
0x1           0x3                0x1         0xfffffffe  0x4df9b24d  01000000000000000111000000110011
0x3           0x1                0x1         0xfffffff   0x52a4db3b  01000000000000000111000000110011
0x1           0xaaaaaaab         0x55555555  0x0         0xbd54ba8f  01000000000000000111000000110011
0x3           0xaaaaaaa9         0x55555555  0x1         0xfbc19e36  01000000000000000111000000110011
0xaaaaaaab    0x1                0x55555555  0x55555555  0x1f204ee3  01000000000000000111000000110011
0x1           0xaaaaaaab         0x55555555  0xaaaaaaaa  0x4427cf24  01000000000000000111000000110011
0xaaaaaaab    0x1                0x55555555  0x7fffffff  0xb35e1e78  01000000000000000111000000110011
0xaaaaaaa9    0x3                0x55555555  0xfffffffe  0xd8b185ff  01000000000000000111000000110011
0xaaaaaab     0xa0000001         0x55555555  0xfffffff   0x3df120bc  01000000000000000111000000110011
0x1           0x155555555        0xaaaaaaaa  0x0         0x2c051ddb  01000000000000000111000000110011
0x1           0x155555555        0xaaaaaaaa  0x1         0x454484c1  01000000000000000111000000110011
0x1           0x155555555        0xaaaaaaaa  0x55555555  0xb7689680  01000000000000000111000000110011
0x155555555   0x1                0xaaaaaaaa  0xaaaaaaaa  0x2e840171  01000000000000000111000000110011
0x55555555    0x100000001        0xaaaaaaaa  0x7fffffff  0x15871d88  01000000000000000111000000110011
0x155555555   0x1                0xaaaaaaaa  0xfffffffe  0x11dcfa34  01000000000000000111000000110011
0x15555555    0x140000001        0xaaaaaaaa  0xfffffff   0x8d738a3f  01000000000000000111000000110011
0x1           0xffffffff         0x7fffffff  0x0         0xfde26c34  01000000000000000111000000110011
0x3           0xfffffffd         0x7fffffff  0x1         0x5c9f96cf  01000000000000000111000000110011
0xaaaaaaab    0x55555555         0x7fffffff  0x55555555  0x2ec9e068  01000000000000000111000000110011
0x55555555    0xaaaaaaab         0x7fffffff  0xaaaaaaaa  0x6ad4fd3   01000000000000000111000000110011
0xffffffff    0x1                0x7fffffff  0x7fffffff  0x31aaa926  01000000000000000111000000110011
0xfffffffd    0x3                0x7fffffff  0xfffffffe  0x58c01b60  01000000000000000111000000110011
0x1fffffff    0xe0000001         0x7fffffff  0xfffffff   0x476c1557  01000000000000000111000000110011
0x1           0x1fffffffd        0xfffffffe  0x0         0x6c2e1809  01000000000000000111000000110011
0x1           0x1fffffffd        0xfffffffe  0x1         0xd5bccc1f  01000000000000000111000000110011
0xaaaaaaa9    0x155555555        0xfffffffe  0x55555555  0x7f3b713   01000000000000000111000000110011
0x155555555   0xaaaaaaa9         0xfffffffe  0xaaaaaaaa  0x2b64a58e  01000000000000000111000000110011
0xfffffffd    0x100000001        0xfffffffe  0x7fffffff  0xb2744227  01000000000000000111000000110011
0x1fffffffd   0x1                0xfffffffe  0xfffffffe  0xd156573a  01000000000000000111000000110011
0x1ffffffd    0x1e0000001        0xfffffffe  0xfffffff   0xc5386ae3  01000000000000000111000000110011
0x1           0x1fffffff         0xfffffff   0x0         0xc7926252  01000000000000000111000000110011
0x3           0x1ffffffd         0xfffffff   0x1         0x38ac6aa6  01000000000000000111000000110011
0xaaaaaab     0x15555555         0xfffffff   0x55555555  0x8f738978  01000000000000000111000000110011
0x15555555    0xaaaaaab          0xfffffff   0xaaaaaaaa  0x4051e119  01000000000000000111000000110011
0x1fffffff    0x1                0xfffffff   0x7fffffff  0x94dd2733  01000000000000000111000000110011
0x1ffffffd    0x3                0xfffffff   0xfffffffe  0x59b5b1c6  01000000000000000111000000110011
0x1fffffff    0x1                0xfffffff   0xfffffff   0xee6bd625  01000000000000000111000000110011
```

All of these are errors are logged for the **`ANDN`** instruction

![](https://imgur.com/bRAGCqF.png)

## Design bug
As per the tests the **`ANDN`** instruction contains a design bug.

## Verification Strategy
To reduce the testing time, the inputs generated to the DUT are all edge cases and are not random inputs. Otherwise, the real-time execution would take a tremendous amount of time. The same inputs are given to the DUT and the model python file and are equated at the end.

## Is the verification complete ?
While testing, an assumption is made that rs1, rs2, rs3, and rd fields in an instruction do not cause any change to the output. All the operands are only taken from the `mav_putvalue_src1`, `mav_putvalue_src2` and `mav_putvalue_src3`. The inputs are tested over a small range of 49 to 343 different values of each instruction (depending on the test function). With the small range, the inputs are such that, every bit of the input assumes a value of 0 or 1 over the tests. Therefore, the verification is complete with the assumption made.