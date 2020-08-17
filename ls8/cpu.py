"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.PC = 0
        self.IR = None
        self.FL = None
        self.ram = [None] * 256
        self.reg = [0] * 8
        self.running = False 
        self.reg[7] = 0xF4

        self.functionDict = {}
        self.functionDict[0b00000001] = self.hlt
        self.functionDict[0b10000010] = self.ldi
        self.functionDict[0b01000111] = self.prn
        self.functionDict[0b10100010] = self.mul
        self.functionDict[0b01000101] = self.push
        self.functionDict[0b01000110] = self.pop
        self.functionDict[0b1010000] = self.call
        self.functionDict[0b00010001] = self.ret
        self.functionDict[0b10100000] = "ADD"
        self.functionDict[0b10100111] = "CMP"
        self.functionDict[0b01010101] = self.jeq
        self.functionDict[0b01010110] = self.jne
        self.functionDict[0b01010100] = self.jmp


    def load(self):
        """Load a program into memory."""

        address = 0
        
        # For now, we've just hardcoded a program:
        
        filename = sys.argv[1]

        with open(filename) as f:
            for line in f:
                line = line.split("#")[0].strip()
                if line == "":
                    continue
                else:
                    self.ram[address] = int(line, 2)
                    address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        op = self.functionDict[op]
        if op == "ADD":
            print(f"In ALU Adding {self.reg[reg_a]} with {self.reg[reg_b]}")
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == "CMP":
            print("Running CMP")
            val1 = self.reg[reg_a]
            val2 = self.reg[reg_b]
            if val1 == val2:
                self.FL = 0b1
            elif val1 > val2:
                self.FL = 0b10
            elif val2 > val1:
                self.FL = 0b100
            print("CMP done")
            self.PC += 3
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.PC,
            self.FL,
            #self.ie,
            self.ram_read(self.PC),
            self.ram_read(self.PC + 1),
            self.ram_read(self.PC + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def run(self):
        """Run the CPU."""
        self.running = True
        
        while self.running:
            self.IR = self.ram_read(self.PC) 
            operand_a = self.ram_read(self.PC + 1)
            operand_b = self.ram_read(self.PC + 2)
            print(f'Running instruction {bin(self.IR)}')
            is_alu_command = (self.IR >> 5) & 0b001
            
            if is_alu_command:
                print("running ALU")
                self.alu(self.IR, operand_a, operand_b)
            
            else:
                print("running func")
                self.functionDict[self.IR]()

    def hlt(self):
        print("Halting..")
        self.running = False

    def ldi(self):
        operand_a = self.ram_read(self.PC + 1)
        operand_b = self.ram_read(self.PC + 2)
        print(f"LDI: reg[{operand_a}] = {operand_b}")
        self.reg[operand_a] = operand_b
        self.PC += 3

    def prn(self):
        operand_a = self.ram_read(self.PC+1)
        print(f"PRN {self.reg[operand_a]}")
        self.PC += 2

    def mul(self):
        operand_a = self.ram_read(self.PC + 1)
        operand_b = self.ram_read(self.PC + 2)
        savedVal = self.reg[operand_a]
        self.reg[operand_a] *= self.reg[operand_b] 
        
        print(f"Multipled {operand_a}: {savedVal} with {operand_b}: {self.reg[operand_b]} => {self.reg[operand_a]}")
        self.PC += 3

    def push(self):
        operand_a = self.ram_read(self.PC + 1)
      
        self.reg[7] -= 1
        value = self.reg[operand_a]
        SP = self.reg[7]
        print(f"PUSH: ram[SP]: {self.ram[SP]} is now {value}")
        self.ram[SP] = value
        self.PC += 2

    def pop(self):
        operand_a = self.ram_read(self.PC + 1)
        SP = self.reg[7]
        value = self.ram_read(SP)
        print(f"POP: reg[op_a]: {self.reg[operand_a]} is now {value}")
        self.reg[operand_a] = value
        self.reg[7] += 1
        self.PC += 2

    def call(self):
        operand_a = self.ram_read(self.PC + 1)
        nextInstr = self.PC + 2
        print(f"Saving next instruction index {nextInstr}")
        self.reg[7] -= 1
        SP = self.reg[7]
        self.ram[SP] = nextInstr
        print(f"Moving PC to {self.reg[operand_a]}")
        self.PC = self.reg[operand_a]

    def ret(self):
        print(f"RET: Grabbing instruction")
        SP = self.reg[7]
        value = self.ram_read(SP)
        print(f'Setting PC to {value}')
        self.PC = value

    def add(self):
        operand_a = self.ram_read(self.PC + 1)
        operand_b = self.ram_read(self.PC + 2)
        self.alu("ADD", operand_a, operand_b)
        self.PC += 3