# Level 1 Design 2 - Tushar Upadhyay

![](https://imgur.com/V6Qslza.png)

## Verification Environment

First a dictionary is created containing all possible states for the finite state machine if it stores the last four bits of a sequence.
```
stateDict = {"0000":0, "0100":0, "1000":0, "1100":0,            # IDLE              0th state
             "0001":1, "0011":1, "0111":1, "1001":1, "1111":1,  # xxx1 = SEQ_1      1st state
             "0010":2, "0110":2, "1010":2, "1110":2,            # xx10 = SEQ_10     2nd state
             "0101":3, "1101":3,                                # x101 = SEQ_101    3rd state
             "1011":4}                                          # 1011 = SEQ_1011   4th state
```

An input sequence is created filled with 256 random 0s and 1s. Then a specific list is also added for edge cases where 2 sequences are adjacent to each other.
(Seed is set to 10 so that we get the same sequence every run making easier for the judges)
```
    random.seed(10)
    seq = list()
    for _ in range(256):
        seq.append(random.randint(0, 1))
    seq.append([1,0,1,1,1,0,1,1,0,1,0,1,1,1,1,0,1,1])
```

The `lastCycleFour`(list) and `lastCycleFourStr`(string) variables remember the last 4 bits that were inputted to the sequence detector. The correct state is determined by using the variable `lastCycleFourStr` and putting it in the `stateDict`. `lastCycleState`.
Every cycle the assert statement checks if the `current_state`(internal register of DUT) and the state modelled by the python testbench are equal; an error gets raised if not.
As the sequence detection must be overlapping with only non-sequence bits we erase the `lastCycleFour` list to `[0,0,0,0]` whenever the sequence is detected.  
```
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
```

## Test Scenario
- Test Inputs: inp_bit=1 reset=0 inp_bit(previous cycle) = 1
- Expected Output: seq_seen = 0 current_state(internal register) = 1
- Observed Output: seq_seen = 0 current_state(internal register) = 0

![](https://imgur.com/RQtAgO0.png)

The `next_state` should be `SEQ_1` when the input bit is 1 and the `current_state` is `SEQ_1`

## Design Bug
Based on the above test input and analysing the design, we see the following

```
48|    if(inp_bit == 1)
49|        next_state = IDLE;                           <== BUG
50|    else
```

## Design Fix
We Update design and change line 40 to 
```
49|  next_state = SEQ_1;
```

## Test Scenario
- Test Inputs: inp_bit=1 reset=0 inp_bit(previous cycle) = 0
- Expected Output: seq_seen = 0 current_state(internal register) = 2
- Observed Output: seq_seen = 0 current_state(internal register) = 0
![](https://imgur.com/NFuWg09.png)

The `next_state` should be `SEQ_10` when the input bit is 0 and the `current_state` is `SEQ_101`

## Design Bug
Based on the above test input and analysing the design, we see the following

```
64|    else
65|      next_state = IDLE;                         <==BUG
66|  end
```


## Design Fix

```
65|      next_state = SEQ_10; 
```
## Test Scenario
- Test Inputs: inp_bit=1 reset=0 inp_bit(previous cycle) = 1
- Expected Output: seq_seen = 0 current_state(internal register) = 1
- Observed Output: seq_seen = 0 current_state(internal register) = 0
![](https://imgur.com/Sz0uOB0.png)

The `next_state` should be `SEQ_1` when the input bit is 1 and the `current_state` is `SEQ_1011`

## Design Bug
Based on the above test input and analysing the design, we see the following
```
67| SEQ_1011:
68|     begin
69|         next_state = IDLE;                                  <==BUG
70|     end
```

## Design Fix

```
69|    if(inp_bit == 1)
70|      next_state = SEQ_1;
71|    else
72|      next_state = IDLE;
```

![](https://imgur.com/JAEcnLP.png)
All tests passed!

## Verification Strategy
The verification strategy is to keep giving in random inputs to the DUT while reading the internal register `current_state` that holds the value of the FSM state. As a sequence detector is an FSM, comparing the predicted state(by modeling it python) and the state of the DUT allows one to easily find abnormalities in the design. 

## Is the verification complete ?
The inputs given to the DUT are random with a manually inputted sequence. The manually inputted sequence ensures the edge case where two sequences are inputted back to back. To increase coverage, the random sequence's length was increased to 1024 values, ensuring that the FSM of the sequence detector works perfectly, turning the `seq_seen` bit to 1 every time the sequence is detected.