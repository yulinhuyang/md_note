> 2014-12-31

<!-- 信息的表示与处理
=============== -->


程序的机器级表示
===============
## 程序编码

### 代码示例
```c
int accum = 0;
int sum(int x, int y){
    int t = x + y;
    accum += t;
    return t;
}
```

使用`gcc -O1 -S code.c`得到的`code.s`

```assembly
sum:
    pushl   %ebp
    movl    %esp, %ebp
    movl    12(%ebp), %eax
    addl    8(%ebp), %eax
    addl    %eax, accum
    popl    %ebp
    ret
```

使用`gcc -O1 -c code.c`得到的`code.o`，再执行`objdump -d code.o`进行反汇编

```
code.o:     file format elf32-i386

Disassembly of section .text:

00000000 <sum>:
   0:   55                      push   %ebp
   1:   89 e5                   mov    %esp,%ebp
   3:   8b 45 0c                mov    0xc(%ebp),%eax
   6:   03 45 08                add    0x8(%ebp),%eax
   9:   01 05 00 00 00 00       add    %eax,0x0
   f:   5d                      pop    %ebp
  10:   c3                      ret

```

反汇编使用的指令与GCC生成的汇编有些差别，它省略了指令结尾的`l`，这些后缀是大小指示符，在大多数情况下可以忽略，另外，`addl    %eax, accum`对应此处的`add    %eax,0x0`，即`accum`的地址是`0x0`，这需要等链接完成后，才能得到真实地址


### 格式的注解
```c
int simple(int *xp, int y){
    int t = *xp + y;
    *xp = t;
    return t;
}
```

对应的`simple.s`

```assembly
  .file "simple.c"
  .text
.globl simple
  .type simple, @function
simple:
  pushl   %ebp              @ save frame pointer
  movl    %esp, %ebp        @ create new frame pointer
  movl    8(%ebp), %edx     @ retrieve xp
  movl    12(%ebp), %eax    @ retrieve y
  addl    (%edx), %eax      @ add *xp to get t
  movl    %eax, (%edx)      @ store t at xp
  popl    %ebp              @ restore frame pointer
  ret
  .size simple, .-simple
  .ident  "GCC: (GNU) 4.1.2 20080704 (Red Hat 4.1.2-54)"
  .section  .note.GNU-stack,"",@progbits
```

所有以`.`开头的行都是指导汇编器和链接器的命令，通常可以忽略这些行。

也可产生相应的Intel格式`gcc -O1 -S -masm=intel simple.c`


```assembly
simple:
  push  ebp
  mov ebp, esp
  mov edx, DWORD PTR [ebp+8]
  mov eax, DWORD PTR [ebp+12]
  add eax, DWORD PTR [edx]
  mov DWORD PTR [edx], eax
  pop ebp
  ret
```

- Intel代码省略了指示大小的后缀，看到的指令`mov`，而不是`movl`
- Intel代码省略了寄存器前面的`%`符号
- Intel代码用不同方式来描述存储器中位置，是`DWORD PTR [ebp+8]`，而不是`8(%ebp)`
- 在带有多个操作数的指令情况下，__列出操作数的顺序相反__

## 数据格式

- 字节  8bit
- 字    16bit
- 双字  32bit
- 四字  64bit

```table
C声明           | Intel数据类型 | 汇编代码后缀 | 大小（字节）
----------------|--------------|-------------|-----------
char            |字节           | b           |   1
short           |字             | w           |   2
int             |双字           | l           |   4
long int        |双字           | 1           |   4
long long int   |—              | —           |   4
char *          |双字            | l           |   4
float           |单精度          | s           |   4
double          |双精度          | l           |   8
long double     |扩展精度        | t           |  10/12
```

大多数GCC生成的汇编代码指令都有一个字符后缀，表明操作数的大小，如数据传送指令有三个变种：`movb`传送字节，`movw`传送字，`movl`传送双字，也使用后缀`l`表示4字节整数和8字节双精度浮点数，这不会产生歧义，因为浮点数使用完全不同的指令的寄存器

## 访问信息
一个IA32中央处理单元包含一组8个存储32位值的寄存器，它们以`%e`开头

![img](../../imgs/csapp_01.png)

字节操作指令可以独立的读或写前4个寄存器的2个低位字节，如`%ax`则表示16位，其中还可以细分`%ah`表示高8位，`%al`表示低8位

### 操作数指示符

源数据值可以以常数形式给出，或从寄存器或存储器中读出，结果可以存放在寄存器或存储器中

- 立即数(immediate)，也就是常数值，在ATT格式中，是`$`后用一标准C表示的整数，如`$-577`或`$0x1F`，任何能放进32位的字里的数值都可以用做立即数，不过汇编在可能时使用一个或两个字节的编码
- 寄存器(register)，表示某个寄存器的内容，对 __双字__ 操作来说，可以是8个32位寄存器（如`%eax`）中的一个，对 __字__ 操作来说，可以是8个16位寄存器（如`%ax`）中的一个，或者对 __字节__ 操作来说，可以是8个单字节寄存器元（如`%al`）素中的一个。E<sub>a</sub>来表示任意寄存器a，用引用R[E<sub>a</sub>]来表示它的值，将寄存器看成一个数组R，用寄存器标识作为索引
- 存储器(memory)引用，它会根据计算出来的地址，访问某个存储器位置，将存储器看成一个很大的字节数组，用符号M<sub>b</sub>[Addr]表示对存储器中从地址Addr开始的b个字节值的引用，为了方便通常省去下方的b

![img](../../imgs/csapp_02.png)

上图表示多种不同的寻址模式，允许不同形式的存储器引用，Imm(E<sub>b</sub>,E<sub>i</sub>,s)表示：一个立即数偏移Imm，一个基址寄存器E<sub>b</sub>，一个变址寄存器E<sub>i</sub>和一个比例因子s，这里s必须是1、2、4、8。然后有效地址被计算为Imm+R[E<sub>b</sub>]+R[E<sub>i</sub>]*s

练习

![img](../../imgs/csapp_03.png)

![img](../../imgs/csapp_04.png)

- 9(%eax,%edx) => M[9 + R[%eax] + R[%edx]] => M[9 + 0x100 + 0x3] => M[0x10C] => 0x11
- 0xFC(,%ecx,4) => M[0xFC + R[%ecx] * 4] => M[0xFC + 0x1 * 4] => M[0xFC + 0x4] => M[0x100] => 0xFF
- (%eax,%edx,4) => M[R[%eax] + R[%edx] * 4] => M[0x100 + 0x3 * 4] => M[0x10C] => 0x11

### 数据传送指令
指令类，指令执行一样的操作，只不过操作数的大小不同，如`MOV`类由三条指令组成：`movb`、`movw`、`movl`，不同的只是它们分别是在大小为1,2,4个字节的数据上进行操作

![img](../../imgs/csapp_05.png)

![img](../../imgs/csapp_06.png)

`MOV`类中，IA32有一条限制，__传送指令的两个操作数不能都指向存储器位置__，下面是mov指令的五种可能组合，记住，每一个是源操作数，第二个是目的操作数

```assembly
movl $0x4050,%eax         @ Immediate--Register, 4 bytes
movw %bp,%sp              @ Register--Register, 2 bytes
movb (%edi,%ecx),%ah      @ Memory--Register, 1 byte
movb $-17,(%esp)          @ Immediate--Memory, 1 byte
movl %eax,-12(%ebp)       @ Register--Memory, 4 bytes
```

`MOVS`和`MOVZ`指令类将一个较小的源数据复制到一个较大的数据位置，高位用符号位扩展(`MOVS`)或零扩展(`MOVZ`)进行填充，用符号位扩展，目的位置的所有高位用源值的最高位数值进行填充，用零扩展时，则所有高位用零填充。这两个类中每个都有三条指令，包括了所有源大小为1和2个字节，目的大小为2和4个的情况

```assembly
@ Assume initially that %dh = CD, %eax = 98765432
movb %dh,%al      @ %eax = 987654CD  不改变其他三个字节
movsbl %dh,%eax   @ %eax = FFFFFFCD  高三位全为符号扩展，CD符号位为1，高位全部为1
movzbl %dh,%eax   @ %eax = 000000CD  高三位全为0
```

`pushl`和`popl`将数据压入程序栈或出栈(__栈本身在存储器中__)，__栈向下增长__，栈顶元素是栈中最低的，压栈是减少栈指针(寄存器`%esp`)的值(`R[%esp]`)，并将数据存放到 __存储器__(`M[R[%esp]]`)中

![img](../../imgs/csapp_07.png)

```assembly
pushl %eax
@ 等价于
subl $4,%esp        @ Decrement stack pointer
movl %eax,(%esp)    @ Store %eax on stack
```

```assembly
popl %edx
@ 等价于
movl (%esp),%edx    @ Read %edx from stack
addl $4,%esp        @ Increment stack pointer
```

因为栈和程序代码以及其他形式的程序数据都是放在同样的存储器中，所以程序可以用标准的存储器寻址方法访问栈内任意位置，如，栈顶元素是双字，`movl 4(%esp),%edx`会将第二个双字从栈中复制到寄存器`%edx`

根据操作数，确定指令后缀

```assembly
movl %eax, (%esp)
movw (%eax), %dx
movb $0xFF, %bl
movb (%esp,%edx,4), %dh
pushl $0xFF
movw %dx, (%eax)
popl %edi
```

IA32中即使操作数是一个字节或者单字的，__存储器的引用也总是用双字长寄存器__ (如`movw %dx, (%eax)`中的`(%eax)`)给出

以下是常见的一些错误指令

```assembly
movb $0xF, (%bl)     @ Cannot use %bl as address register
movl %ax, (%esp)     @ Mismatch between instruction suffix and register ID, use movw
movw (%eax),4(%esp)  @ Cannot have both source and destination be memory references
movb %ah,%sh         @ No register named %sh
movl %eax,$0x123     @ Cannot have immediate as destination
movl %eax,%dx        @ Destination operand incorrect size
movb %si, 8(%ebp)    @ Mismatch between instruction suffix and register ID, use movw
```

### 数据传送示例

```c
int exchange(int *xp, int y){
    int x = *xp;
    *xp = y;
    return x;
}
```

```assembly
@ xp at %ebp+8, y at %ebp+12
movl 8(%ebp), %edx    @ Get xp
                      @ By copying to %eax below, x becomes the return value
movl (%edx), %eax     @ Get x at xp
movl 12(%ebp), %ecx   @ Get y
movl %ecx, (%edx)     @ Store y at xp
```

- `movl 8(%ebp), %edx`，将`xp`的值，放入`%edx`，即`R[%edx] = xp`
- `movl (%edx), %eax`，将`M[R[%edx]]`，即`*xp`指向的值，放入`%eax`，即`R[%eax]=*xp`，`R[%eax]`将变成返回值
- `movl 12(%ebp), %ecx`，将`y`的值，放入`%ecx`，即`R[%ecx] = y`
- `movl %ecx, (%edx)`，将`R[%ecx]`，放入`M[R[%edx]]`，完成`*xp = y`

C语言中所谓的"指针"其实就是地址，间接引用指针是将该指针放在一个寄存器中，然后在存储器引用中使用这个寄存器，其次，像x这样的局部变量通常是保存在寄存器中，而不是存储器中，寄存器访问比存储器访问要快得多

```c
src_t v;
dest_t *p;
*p = (dest_t) v;
```

设`v`存储在寄存器`%eax`适当命名的部分中，也就是`%eax`,`%ax`,`%al`，而指针`p`存储在寄存器`%edx`中，当执行 __既涉及大小变化又涉及符号改变的强制类型转换__ 时，操作应该先改变符号

```table
src_t         |dest_t           |Instruction
--------------|-----------------|---------------
int           | int             |  movl   %eax,(%edx)
char          | int             |  movsbl %al,(%edx)
char          | unsigned        |  movsbl %al,(%edx)
unsigned char | int             |  movzbl %al,(%edx)
int           | char            |  movb   %al,(%edx)
unsigned      | unsignedchar    |  movb   %al,(%edx)
unsigned      | int             |  movl   %eax,(%edx)
```

练习

已知`void decode1(int *xp, int *yp, int *zp);`并且汇编如下，写出等效C代码

```assembly
@ xp at %ebp+8, yp at %ebp+12, zp at %ebp+16
movl 8(%ebp), %edi    @ Get xp
movl 12(%ebp), %edx   @ Get yp
movl 16(%ebp), %ecx   @ Get zp
movl (%edx), %ebx     @ Get y
movl (%ecx), %esi     @ Get z
movl (%edi), %eax     @ Get x
movl %eax, (%edx)     @ Store x at yp
movl %ebx, (%ecx)     @ Store y at zp
movl %esi, (%edi)     @ Store z at xp
```

等效于

```c
void decode1(int *xp, int *yp, int *zp){
    int tx = *xp;
    int ty = *yp;
    int tz = *zp;
    *yp = tx;
    *zp = ty;
    *xp = tz;
}
```

## 算术和逻辑操作
![img](../../imgs/csapp_10.png)

除了`leal`没有变种外，大多数操作都为指令类，如`ADD`，具有`addb`,`addw`,`addl`等变种

### 加载有效地址
指令`leal`实际上是`movl`指令的变形，但它不是从指定位置（存储器）读入数据，而是将有效地址写入到目的操作数（__必须是寄存器__），第一个操作数看上去是一个存储器引用，但实际上它 __根本没用引用存储器__，以后用C语言的地址操作符`&`说明这种计算

假如`%eax`的值为x，`%ecx`的值为y，则

```assembly
leal 6(%eax),%edx             @ 6 + x
leal (%eax,%ecx),%edx         @ x + y
leal (%eax,%ecx,4),%edx       @ x + 4y
leal 7(%eax,%eax,8),%edx      @ 7 + 9x
leal 0xA(,%ecx,4),%edx        @ 10 + 4y
leal 9(%eax,%ecx,2),%edx      @ 9 + x + 2y
```

> 利用`leal`可以达到，寄存器内容相加的功能，代替`add`部分功能？

### 一元操作和二元操作
一元操作，只有一个操作数，既是源又是目的，__操作数可以是一个寄存器，也可以是一个存储器位置__

二元操作，第二个操作数，既是源又是目的，对于不可交换的操作来说，有点奇特，如`subl %eax, %edx`使`%edx`的值减去`%eax`，__第一个操作数可以是立即数、寄存器或是存储器位置，第二个操作数可以是寄存器或存储器位置__，但不能两者同时是存储器位置

练习

![img](../../imgs/csapp_11.png)

![img](../../imgs/csapp_12.png)

### 移位操作
先给出移位量，然后第二项给出的是要移位的位数，因为只允许进行0到31位的移位（所以只考虑 __移位量的低5位__）。

移位量可以是一个 __立即数__，或者放在单字节 __寄存器`%cl`__中

左移两个指令`SAL`和`SHL`，两者效果是一样的，都是将右边填上0

右移指令不同，`SAR`执行 __算术移位__，填上符号位，而`SHR`执行 __逻辑移位__，填上0

移位的操作的目的操作数可以是一个寄存器或者一个存储器位置

练习

```c
int shift_left2_rightn(int x, int n){
  x <<= 2;
  x >>= n;
  return x;
}
```

```assembly
movl 8(%ebp), %eax    @ Get x
sall $2, %eax         @ x <<= 2
movl 12(%ebp), %ecx   @ Get n
sarl %cl, %eax        @ x >>= n   使用%cl，即%ecx的低字节
```

补码运算是实现有符号整数运算的一种比较好的方法

```c
int arith(int x, int y, int z){
    int t1 = x+y;
    int t2 = z*48;
    int t3 = t1 & 0xFFFF;
    int t4 = t2 * t3;
    return t4;
}
```

```assembly
@ x at %ebp+8, y at %ebp+12, z at %ebp+16
movl  16(%ebp), %eax            @ z
leal  (%eax,%eax,2), %eax       @ z*3
sall  $4, %eax                  @ t2 = z*48
movl  12(%ebp), %edx            @ y
addl  8(%ebp), %edx             @ t1 = x+y
andl  $65535, %edx              @ t3 = t1&0xFFFF
imull %edx, %eax                @ Return t4 = t2*t3
```

指令2和指令3用`leal`和移位指令的组合来实现表达式`z*48`

> `xor %edx, %edx`，实现了`movl $0, %edx`的功能，但前者指令只需2个字节，后者需要5个字节

### 特殊的算术操作
![img](../../imgs/csapp_14.png)

描述了指令支持产生两个32位数字的全64位乘积以及整数除法

`imull`和`mull`要求一个参数 __必须在寄存器`%eax`__ 中，而另一个作为源操作数给出，然后乘积放在寄存器`%edx`(高32位)和`%eax`(低32位)中

> `imull`虽然可以用于两个不同的乘法操作，但通过操作数的数目上，可以分辨想用哪条指令

下面希望将全64位乘积作为8个字节存放在栈顶

```assembly
@ x at %ebp+8, y at %ebp+12
movl  12(%ebp), %eax      @ Put y in %eax
imull 8(%ebp)             @ Multiply by x
movl  %eax, (%esp)        @ Store low-order 32 bits
movl  %edx, 4(%esp)       @ Store high-order 32 bits
```

存储两个寄存器的位置对小端机器(__低位字节的先输出__)来说是对的，寄存器`%edx`中的高位，存放在相对于`%eax`中低位偏移量为4的地方，栈是向低地址方向增长的，__低位在栈顶__

`idivl`将寄存器`%edx`(高32位)和`eax`(低32位)中的64位数作为被除数，而除数作为指令的操作数给出，指令将 __商存储在`eax`__中，将 __余数存储在`%edx`__ 中

```assembly
@ x at %ebp+8, y at %ebp+12
movl  8(%ebp), %edx       @ Put x in %edx
movl  %edx, %eax          @ Copy x to %eax
sarl  $31, %edx           @ Sign extend x in %edx
idivl 12(%ebp)            @ Divide by y
movl  %eax, 4(%esp)       @ Store x / y
movl  %edx, (%esp)        @ Store x % y
```

第1行的传送指令和第3行的算术移位指令联合起来，就是根据x的符号将寄存器`%edx`设置为全零或全一，第2行传送指令将x复制到`%eax`，因此有了将寄存器`%edx`和`eax`联合起来 __存放x的64位符号扩展__ 的版本

也可使用`cltd`指令，它将`eax`符号扩展到`%edx`，改进入如下

```assembly
@ x at %ebp+8, y at %ebp+12
movl  8(%ebp),%eax     @ Load x into %eax
cltd                   @ Sign extend into %edx
idivl 12(%ebp)         @ Divide by y
movl  %eax, 4(%esp)    @ Store x / y
movl  %edx, (%esp)     @ Store x % y
```

无符号除法是`divl`指令，通常事先将寄存器`%edx`设置为0，如上面的改成计算x和y无符号商和余数

```assembly
@ x at%ebp+8,y at %ebp+12
movl 8(%ebp),%eax      @ Load x into %eax
movl $0,%edx           @ Set high-order bits to 0
divl 12(%ebp)          @ Unsigned divide by y
movl %eax, 4(%esp)     @ Storex/y
movl %edx, (%esp)      @ Storex%y
```

考虑下面C函数，`num_t`是用`typedef`声明的数据类型

```c
void store_prod(num_t *dest, unsigned x, num_t y) {
    *dest = x*y;
}
```

gcc产生的汇编如下：

```assembly
@ dest at %ebp+8, x at %ebp+12, y at %ebp+16
movl  12(%ebp), %eax             @ Get x
movl  20(%ebp), %ecx             @ Get y_h
imull %eax, %ecx                 @ Compute s = x * y_h   即 %ecx存乘积的低32位
mull  16(%ebp)                   @ Compute t = x * y_l   即 %edx存乘积的高32位, %eax存低32位
leal  (%ecx,%edx), %edx          @ Add s to t_h          用leal做了一下加法
movl  8(%ebp), %ecx              @ Get dest
movl  %eax, (%ecx)               @ Store t_l
movl  %edx, 4(%ecx)              @ Store s + t_h
```

第4行使用无符号运算，并且程序是在64位数据上进行操作，可以确定`num_t`为`unsigned long long`

![img](../../imgs/csapp_15.png)

## 控制
### 条件码
除了整数寄存器，CPU还维护着一组 __单个位__ 的条件码(condition code)寄存器

- `CF`进位标志，最近的操作使最高位产生了进位，可以用来检查无符号操作数的溢出
- `ZF`零标志，最近的操作得出的结果为0
- `SF`符号标志，最近的操作得到的结果为负
- `OF`溢出标志，最近的操作导致一个补码溢出－正溢出或负溢出

假设用一条`add`完成了`t=a+b`的功能，变量a,b,t都是整型

- `CF`:`(unsigned) t < (unsigned) a`
- `ZF`:`(t == 0)`
- `SF`:`(t < 0)`
- `OF`:`(a < 0 == b < 0) && ( t < 0 != a < 0)`

![img](../../imgs/csapp_10.png)

该图中，除了`leal`不会设置条件码，其它指令都会设置条件码

- `xor`，`CF`和`OF`会设置成0
- 移位操作，`CF`将设置为最后一个被移出的位，而`OF`设置为0
- `inc`和`dec`会设置`OF`和`ZF`，但不会改变`CF`

![img](../../imgs/csapp_16.png)

`CMP`指令根据它们的两个操作数之差来设置条件码，除了只设置条件码而不更新目标寄存器之外，它与`SUB`行为是一样的，如果两个操作数相等，将`ZF`标志设置为1

同理，`TEST`指令的行为对应`AND`

`testl %eax, %eax`用来检查`%eax`是负、零、正数，或其中的一个操作数是一个掩码，用来指示哪些位应该被测试

<hr/>

```assembly
@c
```

```c
//
```

<!--
%eax  %ax  %ah  %al
%ecx  %cx  %ch  %cl
%edx  %dx  %dh  %dl
%ebx  %bx  %bh  %bl
%esi  %si
%edi  %di
%esp  %sp
%ebp  %bp

movl    movw    movb
movsbw  movsbl  movswl
movzbw  movzbl  movzwl
pushl   popl
leal
inc     dec     neg     not
add     sub     imul    xor    or    and
sal     shl     sar     shr
imull   mull
cltd
idivl   divl





zh 147 238

en 185 311

 -->



