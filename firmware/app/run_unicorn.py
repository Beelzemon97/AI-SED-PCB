"""Runs the ARM ELF in a CPU emulator (Unicorn, Cortex-M4) and prints what USART1 would send."""
import sys, struct
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
elf=ELFFile(open('ai_sed.elf','rb'))
mu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
try: mu.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
except Exception as e: print("cpu model:",e)
mu.mem_map(0x08000000,0x80000); mu.mem_map(0x20000000,0x20000)
mu.mem_map(0x40000000,0x100000); mu.mem_map(0xE0000000,0x100000)
for seg in elf.iter_segments():
    if seg['p_type']=='PT_LOAD' and seg['p_filesz']:
        mu.mem_write(seg['p_paddr'],seg.data())
out=bytearray(); cyc={'n':0}
def hook_w(uc,access,addr,size,val,ud):
    if addr==0x40011004: out.append(val&0xFF)
mu.hook_add(UC_HOOK_MEM_WRITE,hook_w,begin=0x40011004,end=0x40011004)
sp,pc=struct.unpack('<II',mu.mem_read(0x08000000,8))
mu.mem_write(0x40011000,struct.pack('<I',1<<7))  # USART1_SR: TXE always set
mu.reg_write(UC_ARM_REG_SP,sp)
# enable FPU in emulator
try:
    mu.reg_write(UC_ARM_REG_C1_C0_2, mu.reg_read(UC_ARM_REG_C1_C0_2)|(0xf<<20)); mu.reg_write(UC_ARM_REG_FPEXC,1<<30)
except Exception as e: print("fpu:",e)
done={'v':False}
def stop_hook(uc,addr,size,ud):
    if out.count(b'\n')>=19 and out.endswith(b'correct\r\n'): uc.emu_stop()
mu.hook_add(UC_HOOK_CODE,stop_hook)
try: mu.emu_start(pc|1,0,count=400_000_000)
except UcError as e: print("emu error:",e,"pc=",hex(mu.reg_read(UC_ARM_REG_PC)))
print(out.decode(errors='replace'))
