> 2015-05-09

ARM版本
=======

```
内核版本   Soc版本号           芯片型号
  V4      arm7                S3C44B0
  V4T     arm920T             S3C2410/2440/2416
  V5      arm10
  V6      arm1176             S3C6410
          arm1136
          arm1156
  V6K     arm11MP

  V7      arm-cortex-a
              a8              S5PV210              平板2核
                              S5PC100              手机2核
              a9              Exynos4418           平板4核
                              Exynos4412           手机4核
                              Imax6Q               4核
                              OMAP4460             2核
              a7              Exynos5410(a7+a15)   低性能低功耗
                              全志A10/A20/A31
              a15             Exynos5410(a7+a15)   高性能高功耗
                              Exynos5250/5450
              a53/57          高能骁龙815/410       64位
                              iphone5S             64位
          arm-cortex-m
              m3              STM32f10x
              m0/m0+                               低功耗
              m4              STM32F40x            增加了浮点运算dsp
              m7              STM32F7xx            物联网 低功耗
          arm-cortex-r
              r4/r6
```

用sd卡刷机
===============
## 查看sd卡
```shell
fdisk -l
```

将会出现下面的描述，表示位于/dev/sdb

```
Disk /dev/sdb: 7948 MB, 7948206080 bytes
```

## 对sd卡进行分区
exynos4412的bootloader必须在该sd卡起始偏移512字节

```
 /dev/sdb #整个sd卡是个线性空间
 [512bytes-bootloader---|-----分区-rom----------|-]
                        /dev/sdb1 #此部分才是可以挂载的
```

```shell
fdisk /dev/sdb
```

```
Command (m for help): d
Selected partition 1

Command (m for help): d
No partition is defined yet!

Command (m for help): p

Disk /dev/sdb: 7948 MB, 7948206080 bytes
81 heads, 10 sectors/track, 19165 cylinders
Units = cylinders of 810 * 512 = 414720 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disk identifier: 0x00000000

   Device Boot      Start         End      Blocks   Id  System

Command (m for help): n
Command action
   e   extended
   p   primary partition (1-4)
p
Partition number (1-4): 1
First cylinder (1-19165, default 1): 3
Last cylinder, +cylinders or +size{K,M,G} (3-19165, default 19165):
Using default value 19165

Command (m for help): p

Disk /dev/sdb: 7948 MB, 7948206080 bytes
81 heads, 10 sectors/track, 19165 cylinders
Units = cylinders of 810 * 512 = 414720 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disk identifier: 0x00000000

   Device Boot      Start         End      Blocks   Id  System
/dev/sdb1               3       19165     7761015   83  Linux

Command (m for help): t
Selected partition 1
Hex code (type L to list codes): b
Changed system type of partition 1 to b (W95 FAT32)

Command (m for help): w
The partition table has been altered!

Calling ioctl() to re-read partition table.

WARNING: Re-reading the partition table failed with error 16: 设备或资源忙.
The kernel still uses the old table. The new table will be used at
the next reboot or after you run partprobe(8) or kpartx(8)

WARNING: If you have created or modified any DOS 6.x
partitions, please see the fdisk manual page for additional
information.
Syncing disks.
```

- `d`是删除分区，`p`是打印信息，`n`是创建分区；
- First cylinder是表示分区起始柱面（一柱面大约8M），此处填3，前面部分用于存放bootloader（此处有可能是起始扇区，一扇区大约512字节，计算时需要注意）
- 此时默认文件格式是linux的，通过`t`，再输入`b`，得到fat32格式
- 输入`w`退出

接下来格式化该sd卡的sdb1分区

```shell
mkfs.vfat -F 32 /dev/sdb1
```

## 烧写sd卡
拷贝光盘B中images文件夹到sdb1

```
cp -rf images /media/F4C9-ED1D/
```

解压`tools.tar.bz2`，得到可执行文件`write4412boot`，执行它，本质是将boot烧写到指定位置

```
./write4412boot /media/F4C9-ED1D/images/Superboot4412.bin /dev/sdb
```

## 配置FriendlyARM.ini
配置FriendlyARM.ini，用于指定刷何种操作系统。然后将sd卡放入开发板，切换为非Emmc启动，重新启动，刷机完成后，切换回Emmc即可


Uboot烧制与调试
================
> Uboot中使用16进，即使不加0x，也是16进制

## 交叉编译器
得到`arm-linux-gcc.tar.tgz`文件，进行解压

配置环境变量，将其下的`bin`的绝对地址加入到`PATH`中

```shell
vim ~/.bashrc
    PATH=/path/to/arm-linux-gcc/4.5.1/bin:$PATH

source ~/.bashrc #或 . ~/.bashrc 以确保当前终端就可用
```

取得当前版本

```shell
arm-linux-gcc -v
```

> 缺库`ld-linux.so.2`时，进行`yum install ld-linux.so.2`

> 如果ubuntu系统出现`/bin/bash` 命令找不到错误，`sudo apt-get install ia32-libs`

## 配置minicom
板子开发需要用到串口调试，原理是开发板与PC通过串口连接，双方通过`/dev/ttyS0`(PC上真实串口)或`/dev/ttyUSB0`(PC机上使用USB转串口时)文件进行读写。使用`minicom`能方便这一过程

```shell
minicom -s
```

- 选择`Serial port setup`
- 在弹出窗口中，选择`A`，输入`/dev/ttyS0`或`/dev/ttyUSB0`
- 选择`E`，确保为`115200 8N1`
- 选择`F/G`，关闭硬件/软件控制
- 回车，退出弹窗，然后选择`Save setup as dfl`
- 最后，选择`Exit from Minicom`

## Uboot流程
得到`uboot201210.tar.tgz`文件，进行解压

- `./arch`是所支持的架构，如x86,arm等
- `./arch/arm/cpu/armv7/exynos/`本开发板的cpu
- `./board/samsung/tiny4412/`本开发板的board BSP

uboot的第一阶段执行流程：

1. `./arch/arm/cpu/Start.S` #它与具体cpu型号无关
2. `./board/samsung/tiny4412/lowlevel_init.S` #开发中对板子的修改，需要编写它
3. `./board/samsung/tiny4412/clock_init_tiny4412.S`
4. `./board/samsung/tiny4412/mem_init_tiny4412.S`
5. `./board/samsung/tiny4412/tiny4412.c`

第二阶段则执行`./arch/arm/cpu/armv7/exynos/`下的相关代码，如`clock.c,nand.c`等

## Make相关
在解压的当前目录

```shell
vim Makefile
    160 CROSS_COMPILE ?=arm-linux-
```

会在`config.mk`中被使用到

```shell
vim config.mk
    104 AS      = $(CROSS_COMPILE)as
    105 LD      = $(CROSS_COMPILE)ld
    106 CC      = $(CROSS_COMPILE)gcc
    107 CPP     = $(CC) -E
    108 AR      = $(CROSS_COMPILE)ar
    109 NM      = $(CROSS_COMPILE)nm
    110 LDR     = $(CROSS_COMPILE)ldr
    111 STRIP   = $(CROSS_COMPILE)strip
    112 OBJCOPY = $(CROSS_COMPILE)objcopy
    113 OBJDUMP = $(CROSS_COMPILE)objdump
    114 RANLIB  = $(CROSS_COMPILE)RANLIB
```

执行make配置，`vim boards.cfg`查看开发板型号、cpu、board之间的一些对应表

```shell
make tiny4412_config
```

关闭MMU功能，并修改提示符

```shell
vim include/configs/tiny4412.h
    311 //#define CONFIG_ENABLE_MMU
    312 #undef CONFIG_ENABLE_MMU
    255 #define CONFIG_SYS_PROMPT  "[zyx@Uboot]# "
```

修改链接地址，本开发板中DDR地址位于`0x40000000`-`0x80000000`，默认情况下是开启MMU的，所以链接地址是`0xc3e00000`

```shell
vim board/samsung/tiny4412/config.mk
    CONFIG_SYS_TEXT_BASE = 0x43e00000
```

接下来make文件，使用4个任务同时进行

```shell
make -j4
```

> 缺库`libz.so.1`时，`yum install zlib.i686`

## 烧制Uboot
上述make完成后，会产生`u-boot`一个可执行文件

```shell
file u-boot
```

```
u-boot: ELF 32-bit LSB shared object, ARM, version 1 (SYSV), statically linked, not stripped
```

可以看到是ARM架构的ELF文件，它的组成示意如下

```
u-boot=[ELF head][u-boot.bin]
```

`[ELF head]`用于记录它的依赖包等情况，后面`[u-boot.bin]`，而烧制uboot时，还没有操作系统，无法认识`[ELF head]`，只能使用`[u-boot.bin]`部分，其实刚才make后，就生成了一个无`[ELF head]`的一个文件`u-boot.bin`

> 可以使用`hexdump -C`去看一下，两者确实只差一个`[ELF head]`

开发板不能直接使用刚才的`u-boot.bin`，必须在它之前加上三星的安全与签名等模块，切换到`./sd_fuse/tiny4412`，执行`sd_fusing.sh`将自动加上（该脚本需要分析一下，大量使用了`dd`）

```shell
cd uboot_tiny4412/sd_fuse/tiny4412
./sd_fusing.sh /dev/sdb
sync
```

> 如果提示`Block device size ??? is too large`，去修改`sd_fusing.sh`第二段，将`if [ ${BDEV_SIZE} -gt 32000000 ]; then`数字部分调大点

## 调试Uboot
1. 把sd卡插入开发板
2. 开发板切换为sd卡启动
3. 用串口把开发板和pc链接
4. 检查`minicom`的配置
5. 给开发板上电，在`minicom`中观察启动信息

```shell
minicom
```

- `ctrl+a`进入菜单项，`w`切换是否自动换行，`q`退出

常用命令如下

```
?       - alias for 'help'
base    - print or set address offset
bdinfo  - print Board Info structure
boot    - boot default, i.e., run 'bootcmd'
bootd   - boot default, i.e., run 'bootcmd'
bootelf - Boot from an ELF image in memory
bootm   - boot application image from memory
bootp   - boot image via network using BOOTP/TFTP protocol
bootvx  - Boot vxWorks from an ELF image
chpart  - change active partition
cmp     - memory compare
coninfo - print console devices and information
cp      - memory copy
crc32   - checksum calculation
dcache  - enable or disable data cache
dnw     - dnw     - initialize USB device and ready to receive for Windows serv)

echo    - echo args to console
editenv - edit environment variable
emmc    - Open/Close eMMC boot Partition
env     - environment handling commands
exit    - exit script
ext2format- ext2format - disk format by ext2

ext2load- load binary file from a Ext2 filesystem
ext2ls  - list files in a directory (default /)
ext3format- ext3format - disk format by ext3

false   - do nothing, unsuccessfully
fastboot- fastboot- use USB Fastboot protocol

fatformat- fatformat - disk format by FAT32

fatinfo - fatinfo - print information about filesystem
fatload - fatload - load binary file from a dos filesystem

fatls   - list files in a directory (default /)
fdisk   - fdisk for sd/mmc.

go      - start application at address 'addr'
help    - print command description/usage
icache  - enable or disable instruction cache
iminfo  - print header information for application image
imxtract- extract a part of a multi-image
itest   - return true/false on integer compare
loadb   - load binary file over serial line (kermit mode)
loads   - load S-Record file over serial line
loady   - load binary file over serial line (ymodem mode)
loop    - infinite loop on address range
md      - memory display
mm      - memory modify (auto-incrementing address)
mmc     - MMC sub system
mmcinfo - mmcinfo <dev num>-- display MMC info
movi    - movi  - sd/mmc r/w sub system for SMDK board
mtdparts- define flash/nand partitions
mtest   - simple RAM read/write test
mw      - memory write (fill)
nfs     - boot image via network using NFS protocol
nm      - memory modify (constant address)
ping    - send ICMP ECHO_REQUEST to network host
printenv- print environment variables
reginfo - print register information
reset   - Perform RESET of the CPU
run     - run commands in an environment variable
saveenv - save environment variables to persistent storage
setenv  - set environment variables
showvar - print local hushshell variables
sleep   - delay execution for some time
source  - run script from memory
test    - minimal test like /bin/sh
tftpboot- boot image via network using TFTP protocol
true    - do nothing, successfully
usb     - USB sub-system
version - print monitor version
```

- `md`查看内存，`.b`以8位查看(char,2个16进制)，`.w`以16位查看(short,4个16进制)，`.l`以32位查看(int,8个16进制)
- `fdisk`针对sd卡与Emmc查看创建分，`-p`查看，`-c`创建，<device_num>通过启动画面可看到sd与Emmc对应的设备号，如`MMC Device 0: 30608 MB`
- >创建分区是为Android定制的，它有四个分区，`system:data:cache:storage`，前三个是linux文件格式是ext2的(0x83)，而`storage`是fat32的(0x0c)，`kernel/bootloader/ramdisk`存在于 __未划__ 的分区中(分区是会按柱面对齐)
- 格式化不同文件格式的分区，需要不同的`format`，如`fatformat mmc 1:1`或`ext3format mmc 1:4`
- 不同的linux提供的VFS，在这里，针对不同的文件格式分区，需要不同的`ls`，如`fatls mmc 0 /images`或`ext2ls mmc 1:2 /`
- `fatload/ext2load`将rom中的文件load指定的内存地址，方便被`bootm`引导执行
> `fatload mmc 0 0x50000000 /images/linux/zimage`，`bootm 0x50000000`

- `bdinfo`显示板子参数

```
arch_number = 0x00001200    开发板id，bootloader中内核id必须与此一致
boot_params = 0x40000100    开发板启动参数的地址，bootloader传给内核的，(/proc/cmdline 是x86的启动参数)
DRAM bank   = 0x00000000    内存开始地址与大小
-> start    = 0x40000000
-> size     = 0x10000000
DRAM bank   = 0x00000001
-> start    = 0x50000000
-> size     = 0x10000000
DRAM bank   = 0x00000002
-> start    = 0x60000000
-> size     = 0x10000000
DRAM bank   = 0x00000003
-> start    = 0x70000000
-> size     = 0x0FF00000
ethaddr     = 00:40:5c:26:0a:5b
ip_addr     = 192.168.0.20
baudrate    = 0 bps
TLB addr    = 0x3FFF0000
relocaddr   = 0x43E00000    uboot的链接地址，也是uboot的运行地址
reloc off   = 0x00000000
irq_sp      = 0x43CFBF58
sp start    = 0x43CFBF50
FB base     = 0x00000000
```

## 下载文件到开发板
- uart 串口方式
- fatload

```
[zyx@Uboot] # fatload mmc 0:1 0x50000000 /doc/arm.bin
Partition1: Start Address(0x7d82), Size(0x3bbc57b)
reading /doc/arm.bin

688 bytes read
[zyx@Uboot] # go 50000000
## Starting application at 0x50000000 ...
## Application terminated, rc = 0x1
```

- tftp 网络方式
    + pc端安装tftp服务，并存在arm.bin裸机程序
    + 开发板执行`tftp 0x50000000 arm.bin`写入指定地址0x50000000
    + 开发板需要`setenv serverip 192.168.4.254`,`setenv ipaddr 192.168.4.20`,`saveenv`
- dnw  USB方式
    + pc端安装dnw发送端（切换到`tools/dnw-linux`下进行`make`，出现警告要修复，`vim src/driver/secbulk.c`,`to_write = min((int)len, BULKOUT_BUFFER_SIZE);`，再运行`make install`）
    + 如果想卸载:.....[看一下Makefile]
    + pc与开发板通过usb连接
    + 开发板`dnw 0x50000000`，pc执行`dnw arm.bin`，开发板`go 50000000`

```
[zyx@Uboot] # dnw 50000000
Insert a OTG cable into the connector!
OTG cable Connected!
Now, Waiting for DNW to transmit data
Download Done!! Download Address: 0x50000000, Download Filesize:0x2b0
Checksum is being calculated.
Checksum O.K.
```

```
[root@localhost class]# dnw arm.bin
load address: 0x57E00000
Writing data...
100%  0x000002BA bytes (0 K)
speed: 0.004160M/S
```

```
[zyx@Uboot] # go 50000000
## Starting application at 0x50000000 ...
## Application terminated, rc = 0x1
```

## Uboot环境变量
```shell
printenv           #简写pr
echo $bootdelay
```

```
baudrate=115200
bootcmd=movi read kernel 0 40008000;movi read rootfs 0 41000000 100000;bootm 400
bootdelay=3
ethaddr=00:40:5c:26:0a:5b
gatewayip=192.168.0.1
ipaddr=192.168.0.20
netmask=255.255.255.0
serverip=192.168.0.10
```

```shell
setenv bootdelay 10   #临时有效
setenv bootdelay      #删除
saveenv               #保存在sd卡中
```

- `bootargs`内核参数 uboot值将放到`bdinfo`的`boot_params = 0x40000100`地址中，供内核使用，包含 文件系统位置，驱动选择参...
- `bootcmd`自动操作(倒计时结束后执行的操作)，如`set bootcmd "echo $bootdelay;fatls mmc 0:1;fdisk -p 1;" `

## shell脚本
pc上编写脚本test.sh，需要额外加一个头，方便uboot识别

```shell
uboot_tiny4412/tools/mkimage -A arm -O linux -T script -C none -n "uboot_script" -d test.sh test.img
```

下载到开发板

```shell
dnw 50000000
source 50000000
```

编译内核
========
## 给x86下的换内核

```shell
[root@pc]xz -d linux-3.10.5.tar.xz
[root@pc]tar -xvf linux-3.10.5.tar
[root@pc]cd linux-3.10.5
[root@pc]make menuconfig
[root@pc]vim .config
  124 CONFIG_SYSFS_DEPRECATED_V2=y
[root@pc]make dep
[root@pc]make clean
[root@pc]make bzImage
[root@pc]make modules
[root@pc]make modules_install
[root@pc]make install
[root@pc]reboot
```

## 编译内核
```shell
tar -xvf linux3.5.tar.bz2
cd linux-3.5_for_qt4
cp exynos4412_config .config
make -j4
#编译完成的内核在<linux_src>/arch/arm/boot/zImage
```

由于ddr位于`0x40000000`-`0x80000000`，内核必须下载至少`0x40008000`位置

```
zImage
---------------              至少0x40008000
16k translation table
16k bootargs 位于0x40000100
---------------              内存起始0x40000000
```

```shell
[zyx@Uboot]# dnw 40008000
[root@pc]#dnw <linux_src>/arch/arm/boot/zImage
[zyx@Uboot]# bootm 40008000
```

会运行内核，但由于找不到根目录，将会异常

busybox
==========
## 编译busybox
使用busybox来制作文件系统，挂载根目录

> android使用toolbox

```shell
[root@pc]tar -xvf busybox-1.21.1.tar.bz2
[root@pc]cd busybox-1.21.1
[root@pc]make defconfig
[root@pc]make menuconfig
#如果出现ncurse相关错误  yum install ncurse*
```

具体配置如下，需将busybox编译成静态库，并设置好arm编译器前缀，并勾选必要的内核使用的命令

![img](../../imgs/busybox_config_01.png)

![img](../../imgs/busybox_config_02.png)

![img](../../imgs/busybox_config_03.png)

![img](../../imgs/busybox_config_04.png)

![img](../../imgs/busybox_config_05.png)

```shell
[root@pc]make -j4
[root@pc]make install
[root@pc]cd _install/
[root@pc]mkdir home root var mnt tmp sys dev proc #创建必要目录
[root@pc]cp ../examples/bootfloppy/etc/ . -rf     #复制etc
[root@pc]cp ~/class_t/4.5.1/arm-none-linux-gnueabi/lib/ . -rf  #复制lib
```

分析`busybox-1.21.1/init/`目录下文件，这是`init`进程的源代码

嵌入式系统由`linuxrc`启动，调用`init.d/rcS`

## 搭建nfs服务
将busybox中的`_install`目录下文件复制到nfs的指定目录

```shell
[root@pc _install]mkdir /tomcat_root
[root@pc _install]chmod 777 /tomcat_root
[root@pc _install]cp * /tomcat_root -rf
[root@pc _install]cd /tomcat_root
[root@pc]vim etc/profile #登录用户时执行
    echo "#######################"
    echo "#######################"
    echo "#######################"
    echo "#######################"
    echo "Welcom To My FileSystem"
    echo "#######################"
    echo "#######################"
    echo "#######################"
    echo "#######################"
    #在/dev/下创建设备节点
    mdev -s
    #export是确保子进程也能使用
    export PATH=/bin:/sbin:/usr/bin:/usr/sbin
    #\W会被替换为当前工作路径
    export PS1="[root@uplooking \W]# "
    export HOME=/root
[root@pc]vim etc/init.d/rcS     #由init进程执行，不修改
[root@pc]vim etc/fstab          #mount -a时使用，在etc/init.d/rcS中
    proc   /proc proc   defaults  0 0
    sysfs  /sys  sysfs  defaults  0 0
    tmpfs  /tmp  tmpfs  defaults  0 0
```

配置nfs服务器

```shell
[root@pc]vim /etc/exports
    #no_root_squash表示root用户进入后，还是root权限，sync表示每次创建更新就会同步
    /tomcat_root *(rw,no_root_squash,sync)
```

关闭防火墙，启动服务

```shell
[root@pc]service iptables stop
[root@pc]setup #永久关闭
   --->防火墙设置
    [ ]开启防火墙
[root@pc]setenforce 0 #关闭selinux
[root@pc]vim /etc/selinux/config #永久关闭
    SELINUX=disabled
[root@pc]service nfs restart
```

## 网络文件系统作根
本着先使用网络系统，再使用本地系统的原则进行

```shell
[zyx@Uboot]set bootargs root=/dev/nfs nfsroot=192.168.4.118:/tomcat_root ip=192.168.4.119 console=ttySAC0 lcd=S70
[zyx@Uboot]save
```

> uboot中相关的网络也配置好（gatewayip,serverip,ipaddr等）

用网线把开发板和pc链接，并配置pc与开发板处于同一网段（pc如果是虚拟机时，需要使用桥接模式）

```
[zyx@Uboot]dnw 40008000
[root@pc]dnw <linux_src>/arch/arm/boot/zImage

[zyx@Uboot]dnw 41000000
[root@pc]dnw ramdisk-u.img

[zyx@Uboot]bootm 40008000 41000000

#如果成功minicom会出现如下shell，可运行busybox命令
[root@uplooking \]#
```

## 制作本地根
- 内核：zImage
- 根：rootfs.img

需要把 根目录 变成 镜像

```shell
./tools/linux_tools/make_ext4fs -s -l 512M -L linux rootfs.img /tomcat_root/

#  -s 按实际大小来算
#  -l 镜像最大大小 分区是512M
#  -L linux linux系统
#  -a root  android系统
```

产生的`rootfs.img`大约30M

将`linux_images.tar.bz2`解压到sd卡的`images\`中

把`zImage`和`rootfs.img`复制到sd卡`images\Linux\`中

```shell
cp linux-3.5_for_qt4/arch/arm/boot/zImage /media/88DE-4A63/images/Linux/
cp /rootfs.img /media/88DE-4A63/images/Linux/
```

修改刷机配置文件`FriendlyARM.ini`

```shell
vim FriendlyARM.ini
Linux-BootLoader = Superboot4412.bin
Linux-Kernel = Linux/zImage
Linux-CommandLine = root=/dev/mmcblk0p1 rootfstype=ext4 console=ttySAC0,115200 init=/linuxrc  ctp=2 skipcali=y lcd=S70
Linux-RamDisk = Linux/ramdisk-u.img
Linux-RootFs-InstallImage = Linux/rootfs.img

#Linux-CommandLine 就是 bootargs
#Linux-RootFs-InstallImage = Linux/rootfs.img 将根解压到 root=/dev/mmcblk0p1中
#加一个lcd=S70 | HD70   普通|高清屏
#Linux-RamDisk是一个临时根，是uboot作的
```

烧制sd卡

```shell
tools/write4412boot /media/88DE-4A63/images/Superboot4412.bin /dev/sdb
```

刷完切换为emmc启动

> 由于负载不大，所以启动时，内核会关闭CPU3,CPU2,CPU1，只保留CPU0

## 挂载nfs目录
开发板中

```shell
ifconfig eth0 192.168.4.119
mount -t nfs -o nolock,rw 192.168.4.118:/tomcat_root /mnt
chroot /mnt/
#切换mnt下目录为根
#缺任何命令时，ln /bin/busybox /bin/chroot -s
exit #退出刚才切入的根
```

fastboot刷机
============
制作启动SD卡(下面使用Fusing_Tool,也可使用`dd`来制作)

```shell
x210_Fusing_Tool uboot_inand.bin /dev/sdb
```

安装`android-tools`

```shell
[root@pc]fastboot devices     #查看当前连接的设备
[root@pc]fastboot flash <xx>  #烧录具体镜像
[root@pc]fastboot reboot      #重启系统
```

进入uboot

```shell
[zyx@Uboot]fastboot
[root@pc]fastboot flash bootloader android4.0/uboot.bin    #烧uboot
[root@pc]fastboot flash kernel android4.0/zImage-android   #烧linux kernel
[root@pc]fastboot flash system android4.0/x210.img         #烧android rom
[root@pc]fastboot reboot
```


存储器
=========
- ROM：read only memory 只读存储器
- RAM：ramdom access memory 随机访问存储器
- IROM：internal rom 内部ROM，指的是集成到SoC内部的ROM
- IRAM：internal ram 内部RAM，指的是集成到SoC内部的RAM
- DRAM：dynamic ram 动态RAM
- SRAM：static ram 静态RAM
- SROM：static rom？ sram and rom？
- ONENAND/NAND:
- SFR：special function register

## 内存
内存需要直接地址访问，所以是通过地址总线&数据总线的总线式访问方式连接的（好处是直接访问，随机访问；坏处是占用CPU的地址空间，大小受限）

内部存储器 用来运行程序的 RAM （DRAM SRAM DDR）

- SRAM  静态内存  特点就是容量小、价格高，优点是不需要软件初始化直接上电就能用
- DRAM  动态内存  特点就是容量大、价格低，缺点就是上电后不能直接使用，需要软件初始化后才可以使用。

单片机中：内存需求量小，而且希望开发尽量简单，适合全部用SRAM

嵌入式系统：内存需求量大，而且没有NorFlash等可启动介质

PC机：    内存需求量大，而且软件复杂，不在乎DRAM的初始化开销，适合全部用DRAM

## 外存
外存是通过CPU的外存接口来连接的（好处是不占用CPU的地址空间，坏处是访问速度没有总线式快，访问时序较复杂）

外部存储器 用来存储东西的 ROM （硬盘 Flash（Nand iNand···· U盘、SSD） 光盘）

- NorFlash: 特点是容量小，价格高，优点是可以和CPU直接总线式相连，接到SROM bank，CPU上电后可以直接读取，所以一般用作启动介质。
- NandFlash: 分为SLC和MLC，跟硬盘一样，特点是容量大，价格低，缺点是不能总线式访问，也就是说不能上电CPU直接读取，需要CPU先运行一些初始化软件，然后通过时序接口读写。Nand读写以页，但擦除以块（大于页）进行
- eMMC/iNand/moviNand: eMMC（embeded MMC）iNand是SanDisk公司出产的eMMC，moviNand是三星公司出产的eMMC
- oneNAND: 三星公司出的一种Nand
- SD卡/TF卡/MMC卡
- eSSD: embeded SSD
- SATA硬盘: 机械式访问、磁存储原理、SATA是接口

单片机：   很小容量的NorFlash + 很小容量的SRAM

嵌入式系统：因为NorFlash很贵，随意现在很多嵌入式系统倾向于不用NorFlash，而直接用：外接的大容量Nand + 外接大容量DRAM + SoC内置SRAM

PC机：很小容量的BIOS（NorFlash）+ 很大容量的硬盘（类似于NandFlash）+ 大容量的DRAM

S5PV210启动过程
=================
## S5PV210地址映射
![img](../../imgs/arm01.png)

![img](../../imgs/arm02.png)

![img](../../imgs/arm03.png)

## S5PV210启动过程
S5PV210使用的存储方案是：外接的大容量Nand + 外接大容量DRAM + SoC内置SRAM

210内置了一块96KB大小的SRAM（叫iRAM），同时还有一块内置的64KB大小的NorFlash（叫iROM）。210的启动过程大致是：

- 第一步：CPU上电后先从内部IROM中读取预先设置的代码（BL0），执行。这一段IROM代码首先做了一些基本的初始化（CPU时钟、关看门狗···）（这一段IROM代码是三星出厂前设置的，三星也不知道我们板子上将来接的是什么样的DRAM，因此这一段IROM是不能负责初始化外接的DRAM的，因此这一段代码只能初始化SoC内部的东西）；然后这一段代码会判断我们选择的启动模式（我们通过硬件跳线可以更改板子的启动模式），然后从相应的外部存储器去读取第一部分启动代码（BL1，大小为16KB）到内部SRAM。
> - BL0做了什么
>     + 关看门狗
>     + 初始化指令cache
>     + 初始化栈
>     + 初始化堆
>     + 初始化块设备复制函数device copy function
>     + 设置SoC时钟系统
>     + 复制BL1到内部IRAM（16KB）
>     + 检查BL1的校验和
>     + 跳转到BL1去执行

- 第二步：从IRAM去运行刚上一步读取来的BL1（16KB），然后执行。BL1负责初始化NandFlash，然后将BL2读取到IRAM（剩余的80KB）然后运行
- 第三步：从IRAM运行BL2，BL2初始化DRAM，然后将OS读取到DRAM中，然后启动OS，启动过程结束。

![img](../../imgs/arm04.png)

![img](../../imgs/arm05.png)

![img](../../imgs/arm06.png)

![img](../../imgs/arm07.png)

- 210内部有iROM和iRAM，因此启动时分两个阶段：内部启动阶段和外部启动阶段。对于内部启动阶段各种S5PV210的开发板都是相同的，对于外部启动阶段，不同开发板会有不同。
- S5PV210出厂时内置了64KB iROM和96KB iRAM。iROM中预先内置烧录了一些代码（称为iROM代码），iRAM属于SRAM（不需软件初始化，上电即可使用）。210启动时首先在内部运行iROM代码，然后由iROM代码开启外部启动流程。设计成iROM和iRAM是为了支持多种外部设备启动。
- 使用iROM启动的好处：降低BOM成本。因为iROM可以使SOC从各种外设启动，因此可以省下一块boot rom（专门用来启动的rom，一般是norflash）；支持各种校验类型的nand；可以在不使用编程器的情况下使用一种外部存储器运行程序来给另一种外部存储器编程烧录。这样生产时就不用额外购买专用编程器了，降低了量产成本

## OMpin识别外部启动介质
![img](../../imgs/arm08.png)

![img](../../imgs/arm09.png)

![img](../../imgs/arm10.png)

> 拨码开关设置我们只需动OM5即可，其他几个根本不需要碰。需要SD启动时OM5打到GND，需要USB启动时OM5打到VCC

EXYNOS4412启动过程
===============
## 板子示意
![img](../../imgs/arm26.png)

- 每个CPU有32k指令缓存和32k数据缓存，4个CPU共用1M L2缓存
- linux中可通过`taskset`来给进程指定CPU运行
- NEON是图形协处理器
- CPU与外设通过AXI总线连接
- arm是内存外设统一编址，通过地址总线（指针）访问
- MultiFormat CODEC常用是JPEG和YUV格式
- MIPI是诺基亚制定的一个标准
- 写驱动时，比如LED，并不直接操作它，而只驱动display controller
- Audio DSP用于变音
- AC-97最多16声道，而3-ch.PCM只有3声道
- CPU及所有外设，均过过clock gating和power gating来控制
- 本板子没的外接电源芯片，所以一直以最高电压工作
- DMAC，用于数据搬运，不占用CPU的时钟
- PPMU用于监测负载
- USB 2.0 OTG是小型usb接口
- UART串口
- key matrix矩阵键盘
- DRAM Controller用于产生时序，用于硬件间通信
- SROM Controller控制Norflash
- Emmc的分区在驱动中，不在系统中
- 本板子外设电压使用1.8V
- 推挽输出 vs 拉高电阻？？？？？ 晶振

## EXYNOS4412地址映射
![img](../../imgs/arm23.png)

- SMC静态内存控制器
- DMC动态内存控制器

## EXYNOS4412启动过程
![img](../../imgs/arm24.png)

![img](../../imgs/arm25.png)

- 刚开始寄存器pc=0，指向iROM中0地址的代码，读取预先设置的指令去执行
- 然后从相应的外部存储器去读取第一部分启动代码（BL1,bootloader的前16K）到内部SRAM，然后运行BL1代码
- BL1代码会初始化DRAM，并加载整个bootloader到DDR
- bootloader负责将OS加载到DDR中，然后启动OS（它会把bootloader的空间给覆盖）

> 好像比S5PV210启动过程少了BL2过程？？


ARM架构
=========
> 参照[ARM_Architecture_Reference_Manual.pdf](../../data/ARM_Architecture_Reference_Manual.pdf) p39

arm约定

- `Byte` 8 bits
- `Halfword` 16 bits
- `Word` 32 bits

大部分arm core提供

- ARM 指令集（32-bit）32位机是指数据总线，寄存器大小，与地址总线无关
- Thumb 指令集（16-bit ）
- Thumb2指令集（16 & 32bit）

## 处理器工作模式
a8共有7种模式(a9还有一个安全模式)

- `User` : 非特权模式，大部分任务执行在这种模式

- `FIQ` :   当一个高优先级（fast) 中断产生时将会进入这种模式(linux内核并未使用)
- `IRQ` :   当一个低优先级（normal) 中断产生时将会进入这种模式
- `Supervisor` :当复位或软中断指令执行时将会进入这种模式
- `Abort` : 当存取异常时将会进入这种模式
- `Undef` : 当执行未定义指令时会进入这种模式

- `System` : 使用和User模式相同寄存器集的特权模式(linux内核并未使用)

> 除User（用户模式）是Normal（普通模式）外，其他6种都是Privilege（特权模式）
>
> Privilege中除Sys模式外，其余5种为异常模式。
>
> 各种模式的切换，可以是程序员通过代码主动切换（通过写CPSR寄存器）；也可以是CPU在某些情况下自动切换。
>
> 各种模式下权限和可以访问的寄存器不同。

操作系统中一般用软中断指令实现系统调用，操作系统陷入内核时是在svc模式工作

```plain
软件：用户态------------------------------->内核态--------->用户态
     open---->syscall---->swi/svc--------->sys_open------>open
硬件：user模式----------------------------->svc模式------->user模式
```

[ARM_Architecture_Reference_Manual.pdf](../../data/ARM_Architecture_Reference_Manual.pdf) P54

- linux kernal要求启动时，需要在svc模式，所以uboot也是在svc模式下工作，我们写的裸板程序也是在svc下
- linux内核使用high vector address，除了reset，其它的都使用high vector address，因为normal address对应的物理地址在irom中，不能被修改
- arm 11支持implementation defined 向量表中断 能直接跳转到中断处理函数（向量中断处理器只能单核），arm a9多核，所以不支持，只能自己做路由
- 在执行`swi`时，通过`lr`得上一条指令`swi <no>`，通过字面解析得到no


## 寄存器
![img](../../imgs/arm11.png)

ARM总共有37个寄存器，但是每种模式下最多只能看到18个寄存器，其他寄存器虽然名字相同但是在当前模式不可见。

对r13这个名字来说，在ARM中共有6个名叫r13（又叫sp）的寄存器，但是在每种特定处理器模式下，只有一个r13是当前可见的，其他的r13必须切换到他的对应模式下才能看到。这种设计叫影子寄存器（banked register）

![img](../../imgs/arm12.png)

![img](../../imgs/arm14.png)

### 寄存器别名

```table
Reg#|  APCS|  意义
----|------|------
r0  |a1    | 工作寄存器
r1  |a2    | "
r2  |a3    | "
r3  |a4    | "
r4  |v1    | 必须保护
r5  |v2    | "
r6  |v3    | "
r7  |v4    | "
r8  |v5    | "
r9  |v6    | "
r10 |sl    | 栈限制
r11 |fp    | 桢指针
r12 |ip    | 内部过程调用寄存器
r13 |sp    | 栈指针
r14 |lr    | 连接寄存器
r15 |pc    | 程序计数器
```

### r13(sp)
stack pointer 栈指针寄存器

内存的布局，sp指向当前正在运行的进程的栈地址，意味着进程切换时，也需要cpu去修改sp指向

```plain
4G--------
   kernel
3G--------

        <-------sp 当前正在运行的进程的栈地址（进程切换时，也会修改sp）
        ----4   sp-1
        ----4   sp-1
        <-------sp

  -------heap
  -------xxx.so
  -------rodata
  -------data
  -------text
   application
0G--------
```

### r14(lr)/r15(pc)
link register 链接寄存器，用于程序返回

process counter，程序指针，PC指向哪里，CPU就会执行哪条指令（所以程序跳转时就是把目标地址代码放到PC中）。整个CPU中只有一个PC

> 在流水线中，PC指向下被取指的指令，而非正在执行的指令

```plain
a(){
  ------------    进入a函数时，将LR的值保存在[SP]中（保证嵌套时，LR不会被覆盖）
  ------------
  ------------    函数结束时，把LR值恢复，PC=LR的值，则执行函数返回后的代码
}

b(){
  ------------
  ------------
  a();            先将下一条指令放在LR中，然后改变PC，使PC=a，则执行a函数
  ------------
```

> - arm在函数传参、返回值、保存返回地址，均使用寄存器，只有局部变量使用栈
> - 而x86中上述的值均使用栈来保存

### cpsr
程序状态寄存器 整个CPU中只有一个

![img](../../imgs/arm15.png)

![img](../../imgs/arm13.png)

- `N` 当程序出现了负操作会Set N，否则Clear N
- `Z` 当程序出现了0操作会Set Z，否则Clear Z
- `C` 如果是加法产生了进位会Set C，否则Clear C; 如果是减法产生了借位会Clear C，否则Set C
- `V` 如果出现溢出会Set V，否则Clear V
- `Q` 如果运算发生了饱和会Set Q，否则Clear Q
- `J` 如果Arm执行的是java指令，则J==1
- `E` 如果E==1,说明当前运行模式是大端，否则是小端
- `A` 终止禁止位，如果A==1就不会发生终止
- `I` 中断禁止位，如果I==1处理器就不会响应中断
- `F` 快速中断禁止位，如果F==1处理器就不会响应快速中断
- `T` 如果T==1,说明处理器正在执行thumb指令，否则就是arm指令
- `M[4:0]` 表示当前处理器的运行模式

> 用户模式只能修改cpsr的NZCVQ

![img](../../imgs/arm16.png)

### spsr
整个CPU中有5个，分别在5种异常模式下，作用是当从普通模式进入异常模式时，用来保存之前普通模式下的cpsr的，以在返回普通模式时恢复原来的cpsr。

## 流水线
- arm9   5级流水线
- arm11  8级流水线
- a8     13级流水线
- a9     12级流水线

流水线多了，最怕指令跳转导致的流水线重新构建，arm对此增加了预取指判断

## 指令集
- arm指令集     32位
- thumb指令集   16位     armV7 m系列
- thumb2指令集  32/16位
- java字节码

## 哈佛与冯诺依曼
程序和数据都放在内存中，且不彼此分离的结构称为冯诺依曼结构。譬如Intel的CPU均采用冯诺依曼结构。程序和数据分开独立放在不同的内存块中，彼此完全分离的结构称为哈佛结构。譬如大部分的单片机（MCS51、ARM9等）均采用哈佛结构。

冯诺依曼结构中程序和数据不区分的放在一起，因此安全和稳定性是个问题，好处是处理起来简单。哈佛结构中程序（一般放在ROM、flash中）和数据（一般放在RAM中）独立分开存放，因此好处是安全和稳定性高，缺点是软件处理复杂一些（需要统一规划链接地址等）

- 哈佛（安全性高，性能高）

```
  cpu_core  --->  I-cache(一级 指令cache)
                                      ------> cache(二级统一cache)----->  ddr
            --->  D-cache(一级 数据cache)
```

- 冯诺依曼

```
  cpu_core  --->  cache(一级统一cache) ------> cache(二级统一cache)----->  ddr
```

- a8单核 自带二级cache

```
   a8_core-->D-cache         |
                 ---->cache--|->ddr
          -->I-cache         |
```

- a9多核 不带二级cache，方便多个核共享一个二级cache

```
   a9_core-->D-cache |
          -->I-cache |
   a9_core-->D-cache |
          -->I-cache |
                 ----|->cache---->ddr
   a9_core-->D-cache |
          -->I-cache |
   a9_core-->D-cache |
          -->I-cache |
```

- cpu = cpu_core + mmu + 协处理器 + cache + tcm...
    + cache 通过行，组等方式访问
    + tcm 紧耦合性内存 通过地址访问（指针） 与访问寄存器一样快
    + 协处理器: cp11(浮点VFP) cp10(图形NEON) cp14(DEBUG) cp15(控制CTRL)....
    + 协处理器和MMU、cache、TLB等处理有关，功能上和操作系统的虚拟地址映射、cache管理等有关。


## 异常
正常工作之外的流程都叫异常；异常会打断正在执行的工作，并且一般我们希望异常处理完成后继续回来执行原来的工作；中断是异常的一种

所有的CPU都有 __异常向量表__，这是CPU设计时就设定好的，是硬件决定的。当异常发生时，CPU会自动动作（PC跳转到异常向量处处理异常，有时伴有一些辅助动作）

- 当异常产生时, ARM core:
    + 拷贝 `cpsr` 到 `spsr_<mode>`
    + 设置适当的 `cpsr` 位：
        * 改变处理器状态进入 arm 态
        * 改变处理器模式进入相应的异常模式
        * 设置中断禁止位禁止相应中断 (如果需要)
    + 保存返回地址到 `lr_<mode>`
    + 设置 `pc` 为相应的异常向量
- 返回时, 异常处理需要:
    + 从 `spsr_<mode`>恢复`cpsr`
    + 从`lr_<mode>`恢复`pc`
    + Note:这些操作只能在 ARM 态执行.

![img](../../imgs/arm21.png)

> 以上说的是CPU设计时提供的异常向量表，一般成为一级向量表。有些CPU为了支持多个中断，还会提供二级中断向量表，处理思路类似于一级中断向量表

ARM汇编指令
============
- [ARM指令集详解](http://blog.csdn.net/velanjun/article/details/8719090)
- [ARM指令集.pdf](../../data/ARM指令集.pdf)

> 内嵌汇编编译器：armcc(keil内部集成)， gcc

编译过程

1. `gcc   x.c  x.s`  优化在此发生，为了防止优化，请使用`volatile`
1. `as    x.s  x.o`
1. `ld    x.o  x`

## 指令格式
`<opcode>{<cond>}{S} <Rd>,<Rn>{,<opcode2>}`

> 其中，`<>`内的项是必须的，`{}`内的项是可选的

- `opcode`  指令助记符，如ldr，str 等
- `cond`  执行条件，如eq，ne 等
- `S`  是否影响cpsr 寄存器的值，书写时影响cpsr，否则不影响
- `Rd`  目标寄存器
- `Rn`  第一个操作数的寄存器
- `operand2`  第二个操作数


## 寻址方式
- 寄存器寻址 `mov r1, r2` @`r1 = r2;`
- 立即寻址 `mov r0, #0xFF00` @`r0 = #0xFF00;`
- 寄存器移位寻址 `mov r0, r1, lsl #3` @`r1 = r1 * 8; r0 = r1`
- 寄存器间接寻址 `ldr r1, [r2]` @`r1 = *r2;`
- 基址变址寻址 `ldr r1, [r2, #4]` @`r1 = *(r2 + 4);`
- 多寄存器寻址 `ldmia r1!, {r2-r7, r12}` @`r2 = *r1; r1 += 4; r3 = *r1;...`
- 堆栈寻址 `stmfd sp!, {r2-r7, lr}` @`*sp = r2; sp -= 4; *sp = r3;...`
- 相对寻址 `beq <label>` @`if (cpsr_Z) label();`


## 指令后缀

### 操作数长度
- `b`（byte）功能不变，操作长度变为8位
- `h`（half word）功能不变，长度变为16位

### 操作数有符号
- `s`（signed）功能不变，操作数变为有符号，如 `ldr ldrb ldrh ldrsb ldrsh`

### 影响cpsr标志位
- `s`（s标志）功能不变，影响cpsr标志位，如 `movs adds adcs`

### 条件执行
![img](../../imgs/arm22.png)

常用的是`eq ne ge gt le lt`

### 索引后缀
> i icrement; a after; b before; d decrement

- `ia` 事后递增，先传输，再地址+4，比较常用，如`stmia/ldmia`
- `ib` 事前递增，先地址+4，再传输
- `da` 事后递减，先传输，再地址-4
- `db` 事前递减，先地址-4，再传输

`ldmia r6，{r0，r4，r7} @*r6 = r0; *(r6+4) = r4; *(r6+8) = r7`

### 栈后缀
地址基址必须使用`sp`（r13），它只是索引后缀的另一种描述

> f full; d descending; e empty; a ascending

- 满栈（full stack）栈指针指向栈顶元素（即最后一个入栈的数据元素），每次存入时需要先移动栈指针再存入，取出时可以直接取出，然后再移动栈指针
- 空栈（empty stack）栈指地指向空位，每次存入时可以直接存入然后栈指针移动，而取出时需要先移动
- 增栈（ascending stack）栈指针移动时向地址增加的方向移动
- 减栈（descending stack）栈指针移动时向地址减小的方向移动

- `fd` 满递减栈，入栈时先地址-4，再传输，出栈时先输出，再地址+4，比较常用，如`stmfd/ldmfd`
- `fa` 满递增栈，入栈时先地址+4，再传输
- `ed` 空递减栈，入栈时先传输，再地址-4
- `ea` 空递增栈，入栈时先传输，再地址+4

`stmfd sp!，{r0-r5，lr}`把`r0-r5`和`lr`保存到栈中

`ldmfd sp!，{r0-r5，pc}`把数据出栈到`r0-r5`和`pc`中

### `!`后缀
指令地址表达式中含`!`后缀，则基址寄存器中的地址会发生变化

`基址寄存器中的值（指令执行后）= 指令执行前的值 + 地址偏移量`

> `!`后缀必须紧跟在地址表达式后面，而地址表达式要有明确的地址偏移量。

> `!`后缀不能用于r15(pc)的后面

### `^`后缀
`ldmfd sp!，{r0-r6，pc}^`，在目标寄存器中有`pc`时，同时把spsr拷贝到cpsr中，并强制处理器回到用户模式（一般用于异常模式返回）

## 数据传输指令
- `mov` 给一个寄存器赋值

```asm
mov r0, #10  @r0 = 10
mov r0, r1   @r0 = r1
```

- `movt` 给一个寄存器的高16位赋值，把一个16位的op2 放到r0的[31-16]，r0的[15-0]不变，注意：op2 不能大于16位，但可以不符合立即数规则，如op2 可以是0x1234，op1 必须是可读可写的

```asm
movt r0, #10
movt r0, r1
```

- `mvn` 把一个数值按位取反后赋值给一个寄存器

```asm
mvn r0，#0xff  @r0 = ~0xff
mvn r0， r1    @r0 = ~r1
```

## 算术指令
- `add` 计算两个数值的加法

```asm
add r0，r0，#10  @r0 = r0 + 10
add r0，r0，r1   @r0 = r0 + r1
```

- `adc` 带进位的加法

```asm
adc r0，r0，#10  @r0 = r0 + 10 + c
adc r0，r0，r1   @r0 = r0 + r1 + c
```

- `sub` 计算两个数值的减法

```asm
sub r0，r0, #10   @r0 = r0 – 10
sub r0, r0, r1    @r0 = r0 - r1
```

- `sbc` 带借位的减法

```asm
sbc r0, r0, #10   @r0 = r0 – 10 - !c
sbc r0, r0, r1    @r0 = r0 – r1 - !c
```

- `rsb` 反转减法

```asm
rsb r0, r0, r1    @r0 = r1 – r0
rsb r0, r0, #10   @r0 = 10 - r0
```

- `rsc` 带借位的反转减法

```asm
rsc r0, r0, r1    @r0 = r1 – r0 - !c
rsc r0, r0, #10   @r0 = 10 – r0 - !c
```

## 乘法指令
- `mul` 乘法

```asm
mul r0, r1, r2  @r0 = r1 * r2
```

- `mla` 乘加

```asm
mul r0, r1, r2, r3  @r0 = r1 * r2 + r3
```

- `mls` 乘减

```asm
mls r0, r1, r2, r3  @r0 = r3 – r1 * r2
```

- `umull`
- `umlal`
- `smull`
- `smlal`

## 位操作指令
- `orr` 按位或

```asm
orr r0, r0, r1   @r0 = r0 | r1
orr r0, r0, #10  @r0 = r0 | 10
```

- `eor` 按位异或

```asm
eor r0, r0, #10   @r0 = r0 ^ 10
eor r0, r0, r1    @r0 = r0 ^ r1
```

- `and` 按位与

```asm
and r0, r0, r1    @r0 = r0 & r1
and r0, r0, #10   @r0 = r0  & 10
```

- `bic` 位取反/位清除

```asm
bic r0, r0, r1    @r0 = r0 & (~r1)
bic r0, r0, #10   @r0 = r0 & (~10)
```

- `lsr` 逻辑右移

```asm
r0, lsr r1    @r0 >>> r1
r0, lsr #10   @r0 >>> 1
```

- `lsl` 逻辑左移

```asm
r0, lsl r1   @r0 <<< r1
r0, lsl #1   @r0 <<< 1
```

- `asr` 算术右移

```asm
r0, asr r1  @r0 >> r1
r0, asr #1  @r0 >> 1
```

- `ror` 循环右移

```asm
r0, ror r1   @(r0 >>> r1) | (r0 <<< (32 – r1))
r0, ror #1   @(r0 >>> 1) | (r0 <<< (32 – 1))
```

- `rev` 大小端转换

```asm
rev r0, r1   @把r1进行大小端转换，结果放到r0
```

- `rev16` 16位大小端转换

```asm
rev16 r0, r1  @把r1的每个16位进行大小端转换，结果放到r0
```

- `revsh` 16位大小端转换并有符号扩展

```asm
revsh r0, r1  @把r1的低16位进行大小端转换，并扩展为一个32位的有符号数
```

- `rbit` 位反转

```asm
rbit r0, r1  @把r1进行位顺序翻转，结果放到r0
```

- `uxtb16` 无符号8 位扩展16位

```asm
uxtb16 r0，r1  @把r1中的两个8 位数无符号扩展为两个16位数，结果放到r0
```

- `uxtb` 无符号8 位扩展32位

```asm
uxtb8 r0，r1  @把r1中的8 位数无符号扩展为一个32位数，结果放到r0
```

- `uxth` 无符号16位扩展32位

```asm
uxth r0，r1  @把r1中的16位数无符号扩展为一个32位数，结果放到r0
```

- `sxtb16` 有符号8 位扩展16位

```asm
sxtb16 r0，r1  @把r1中的两个8 位数有符号扩展为两个16位数，结果放到r0
```

- `sxtb` 有符号8 位扩展32位

```asm
sxtb8 r0，r1  @把r1中的8 位数有符号扩展为一个32位数，结果放到r0
```

- `sxth` 有符号16位扩展32位

```asm
sxth r0，r1  @把r1中的16位数有符号扩展为一个32位数，结果放到r0
```

## 比较指令

- `cmp` 比较

```asm
cmp r0, r1   @r0 – r1 影响cpsr标志位
cmp r0, #10  @r0 – 10 影响cpsr标志位
```

- `cmn` 负数比较指令，指令使用寄存器rn 与值加上operand2 的值，根据操作的结果更新cpsr中的相应条件标志位，以便后面的指令根据相应的条件标志来判断是否执行

- `teq` 比较（按位异或）

```asm
teq r0, r1   @r0 ^ r1 影响cpsr标志位
teq r0, #10  @r0 ^ 10 影响cpsr标志位
```

- `tst` 比较（按位与）

```asm
tst r0, r1   @r0 & r1 影响cpsr标志位
tst r0, #10  @r0 & 10 影响cpsr标志位
```

## cpsr访问指令
- `mrs` 读cpsr
- `msr` 写cpsr

## 软中断指令
- `swi` 软中断 `swi 10`  产生软中断异常 软中断指令用来实现操作系统中系统调用
- `svc` 等同于swi  `svc 10`  产生软中断异常

## 访存指令
- `ldr` 把数据从内存加载的寄存器(单个字/半字/字节访问)

```asm
ldr r0, addr            @r0 = *addr
ldr r0, =addr           @r0 = addr
ldr r1, [r0]            @r1 = *r0
ldr r1, [r0, #4]        @r1 = *(r0 + 4)
ldr r1, [r0, #4]!       @r1 = *(r0 + 4); r0 += 4
ldr r1, [r0], #4        @r1 = *r0; r0 += 4
```

- `str` 把数据从寄存器保存的内存(单个字/半字/字节访问)

```asm
str r0, addr            @*addr = r0
str r1, [r0]            @*r0 = r1
str r1, [r0, #4]        @*(r0 + 4) = r1
str r1, [r0, #4]!       @*(r0 + 4) = r1; r0 += 4
str r1, [r0], #4        @*r0 = r1; r0 += 4
```

- `ldm` 把数据从内存加载的寄存器(多字批量访问)

```asm
ldmfd sp!, {r0-r12, lr}  @从满递减栈中把值取到寄存器
```

- `stm` 把数据从寄存器保存的内存(多字批量访问)

```asm
stmfd sp!, {r0-r12, lr}  @把寄存器的值放到满递减栈中
stmia sp, {r0-r12}       @事后递增方式把13个寄存器值放到sp指向内存中
```

- `swp{cond}{B} Rd,Rm,[Rn]` 寄存器和存储器交换，用于将一个内存单元（该单元地址放在寄存器Rn中）的内容读取到一个寄存器Rd中，同时将另一个寄存器Rm 的内容写入到该内存单元中。使用swp 可实现信号量操作

```asm
swp r1,r2,[r0]  @r1 = [r0]; [r0] = r2;
swp r1,r1,[r0]  @temp = r1; r1 = [r0]; r[0] = temp;将r1的内容与r0指向的存储单元的内容进行交换
```

- `push` 压栈

```asm
push {r0-r12, lr}  @把寄存器的值放到满递减栈中
```

- `pop` 出栈

```asm
pop {r0-r12, lr}  @从满递减栈中把值取到寄存器
```

## 跳转指令
- `b` 跳转

```asm
b lable  @跳到lable 处执行
```

- `bl` 跳转并保存返回地址

```asm
bl lable  @保存下一条指令的地址到lr，并跳转到lable 处执行
```

- `bx` 跳转（可切换状态）

```asm
bx r0  @跳转到r0所指的位置执行
```

## 前导零计
- `clz` 计算一个数值高位零的个数

```asm
clz r0, r1  @计算r1中开头的零的个数，把计算结果放到r0
```

## 饱和
- `qadd` 饱和加法

```asm
qadd r0, r0, r1  @运算结果的饱和到[0x80000000,0x7fffffff]
```

- `qadd8` 饱和8位加法，每一个操作数都是寄存器，不影响q 位

```asm
qadd8 r0, r0, r1  @r1和r2的每一个字节分别相加，饱和到[-2^7, 2^7-1]
```

- `qadd16` 饱和16位加法，每一个操作数都是寄存器，不影响q 位

```asm
qadd16 r0, r0, r1  @r1和r2的每一个16位相加，饱和到[-2^15, 2^15-1]
```

- `qsub` 饱和减法

```asm
qsub r0, r0, r1  @运算的结果饱和到[0x80000000,0x7fffffff]
```

- `qsub16` 饱和16位减法，每一个操作数都是寄存器，不影响q 位

```asm
qsub16 r0, r0, r1  @r1和r2的每一个16位分别相减，饱和到[-2^15, 2^15-1]
```

- `qsub8` 饱和8 位减法，每一个操作数都是寄存器，不影响q 位

```asm
qsub8 r0, r0, r1  @r1和r2的每一个字节分别相减，饱和到[-2^7, 2^7-1]
```

- `ssat` 有符号饱和

```asm
ssat r0, #sat, r1  @1<=sat<=32
@把r1饱和到[-2^(sat-1), 2^(sat-1)-1]，结果放到r0，如果饱和会置位q
@注意：把r1饱和到sat 个位，饱和后符号不变
```

- `ssat16` 有符号16位饱和

```asm
ssat16 r0, #sat, r1  @1<=sat<=16
@把r1中的每一个16位饱和到[-2^(sat-1), 2^(sat-1)-1]，结果放到r0，如果饱和会置位q
@注意：把r1中的每一个16位饱和到sat 个位，饱和后符号不变
```

- `usat` 无符号饱和

```asm
usat r0, #sat, r1  @0<=sat<=31
@把r1饱和到[0, 2^sat-1]，结果放到r0，如果饱和会置位q
@注意：负数饱和到0
```

- `usat16` 无符号16位饱和

```asm
usat16 r0, #sat, r1  @0<=sat<=31
@把r1中的两个16位分别饱和到[0, 2^sat-1]，结果放到r0，如果饱和会置位q
@注意：负数饱和到0
```

## 协处理器cp15操作
- `mrc/mcr`

语法`mcr{<cond>}   p15, <opcode_1>, <Rd>, <Crn>, <Crm>, {<opcode_2>}`

```asm
mrc p15, 0, r0, c1, c0, 0
orr r0, r0, #1
mcr p15, 0, r0, c1, c0, 0
```

> [ARM CP15协处理器](http://www.cnblogs.com/gaomaolin_88/archive/2010/07/16/1779183.html)

## 伪指令
伪指令经过编译后不会生成机器码，它的意义在于指导编译过程。它与具体的编译器相关。

- 常见gun伪指令

```asm
.global _start                     @ 给_start外部链接属性(别的文件可以访问)

.section .text                     @ 指定当前段为代码段

.ascii .byte .short .long .word .quad .float .string
                                   @ 数据类型，定义变量时使用
IRQ_STACK_START:
  .word 0x0badc0de                 @ 等价于unsigned int IRQ_STACK_START = 0x0badc0de;

.align 4                           @ 以2**4，即16字节对齐 (不填充)

.balignl 16 0xdeadbeef             @ b表示位填充 align表示对齐 l表示以4字节为单位填充
                                   @ 16表示16字节对齐 填充内容是0xdeadbeef

.equ                               @ 类似于C中宏定义，可使用#define来代替
```

- 偶尔用到伪指令

```asm
.end                               @ 标识文件结束

.include                           @ 头文件包含

.arm                               @ 声明以下为arm指令
.code32

.thumb                             @ 声明以下为thubm指令
.code16
```

- 重要的伪指令

```asm
ldr                                @ 大范围的地址加载指令

adr                                @ 小范围的地址加载指令

adrl                               @ 中等范围的地址加载指令

nop                                @ 空操作，用于消耗时钟周期
```

- ARM中有一个`ldr`指令，立即数前面是`#`，还有一个`ldr`伪指令，立即数前面是`=`（或者op2直接是一个符号），伪指令不用考虑非法立即数（涉及arm文字池）。__一般情况下都使用伪指令__
- `adr`编译时会被1条`sub`或`add`指令替代，而`ldr`编译时会被一条`mov`指令替代或者文字池方式处理
- `adr`总是以`pc/r15`为基准来表示地址，因此指令本身和运行地址有关(相对地址)，可以用来检测程序当前的运行地址在哪里，即加载的地址在 __运行时__ 确定
- `ldr`加载的地址和链接时给定的地址有关，由链接脚本决定，即加载的地址在 __链接时__ 确定
- 我们可以通过`adr`和`ldr`加载的地址比较来判断当前程序是否在链接时指定的地址运行


ARM汇编示例
===========
##　绑定寄存器
- 立即数，被编译到指令当中的数据:
    + 本身小于等于255 (一条指令32位，所以指令中的数据就最大可以存8位)
    + 经过循环右移偶数位之后小于等于255
    + 按位取反之后符合上面
    + 0x000000ff 0x00ff0000 0xf000000f 均是合法的，而0x000001ff非法

```c
#include <stdio.h>

int main(void){
  register unsigned int a asm("r0");
  asm volatile(
    "mov r0, #4\n"
    :
    :
    :"r0"
  );
  printf("r0 = %x\n", a);
  return 0;
}
```

## 输入输出变量
- 输出变量，对于汇编而言的，汇编对这个变量只能写不能读
- 输入变量，对于汇编而言的，汇编对这个变量只能读不能写
- 输入变量，输出变量，输入输出变量的具体寄存器名由编译时指定，可通过`arm-linux-gcc -S`来生成汇编查看
- `=`:代表输出变量
- `+`:代表输入输出变量
- `r`:操作方式是寄存器
- `m`:操作方式是内存
- `&`:代表输出变量和输入变量　__不共用__ 寄存器
- 三个冒号，第一行用于声明　`输出`　或　`输入输出`　变量；第二行用于声明　`输入`　变量；第三行用于　__保护__ 上面代码块中显示使用过的寄存器，使用内存的需要标识`memory`

- 声明输入输出变量，使用 `下标` 来访问

```c
#include <stdio.h>

int main(void){
  int in = 40;
  int out = 23;

  asm volatile(
    "mov %0, %1\n"
    :"=&r"(out) //声明输出变量
    :"r"(in) //声明输入变量
    :
  );
  printf("in = %d\n", in);
  printf("out = %d\n", out);
  return 0;
}
```

对应汇编如下，将下标转换为寄存器

```asm
#APP
@ 7 "03in_out.c" 1
  mov r4, r3

@ 0 "" 2
  str r4, [fp, #-20]
```

- 声明输入输出变量，使用 `名称` 来访问

```c
#include <stdio.h>

int main(void){
  int a = 5;
  int b = 6;
  int c; //temp

  asm volatile(
    "mov %[c], %[a]\n"
    "mov %[a], %[b]\n"
    "mov %[b], %[c]\n"

    :[a]"+r"(a),[b]"+r"(b),[c]"+r"(c)
    :
    :
  );
  printf("a = %d\n", a);
  printf("b = %d\n", b);
  return 0;
}
```

## 64位加法
- 除了`比较指令`和直接操作`cpsr`的指令，其他指令要影响`cpsr`标志位就必须加`s`
- 利用`adds`和`adc`，`adds`后有进位，`cpsr_C`的标志位就为1
- 如果要实现更大位的相加，`adc`也可以使用`s`后缀

```c
#include <stdio.h>

int main(void){
  int a, b;

  //0x0000000400000005
  //0x00000008ffffffff
  //0x0000000d00000004
  asm volatile(
    "mov r0, #5\n"
    "mvn r1, #0\n"       //r1=~0;
    "adds %0, r0, r1\n"  //cpsr_C=1
    "mov r0, #4\n"
    "mov r1, #8\n"
    "adc %1, r0, r1\n"   //%1=r0+r1+C
    :"=&r"(a), "=&r"(b)
    :
    :"r0", "r1"
  );

  printf("%#010x%08x\n", b, a);
  return 0;
}
```

## 64位减法
- arm本身没有减法，减法是通过加法和补码（取反+1）配合得到的
- 利用`subs`和`sbc`，`subs`有借位后，`cpsr_C`的标志位就为0

```c
#include <stdio.h>

int main(void){
  int a, b;

  //0x0000000900000004
  //0x0000000400000005
  //0x00000004ffffffff

  __asm__ __volatile__(
    "mov r0, #4\n"
    "mov r1, #5\n"
    "subs %0, r0, r1\n"   //clear C
    "mov r0, #9\n"
    "mov r1, #4\n"
    "sbc %1, r0, r1\n"    //%1=r0-r1-!C
    :"=&r"(a), "=&r"(b)
    :
    :"r0", "r1"
  );

  printf("%#010x%08x\n", b, a);
  return 0;
}
```

## 乘加/乘减
- 方便数学上的西格玛计算

```c
#include <stdio.h>

int main(void){
#if 0
       i = 0;
  c =  ∑    i * i
       i<100

  i = 0;
  while(i < 100)｛
  　　　mla r2, r0, r0, r2
  　　　i++;
  ｝
#endif
  int a;

  asm volatile(
    "mov r0, #3\n"
    "mov r1, #4\n"
    "mov r2, #5\n"
    //"mla %0, r0, r1, r2\n"  //%0=r2+r0*r1
    "mls %0, r0, r1, r2\n"    //%0=r2-r0*r1
    :"=&r"(a)
    :
    :"r0", "r1", "r2"
  );

  printf("a = %d\n", a);
  return 0;
}
```

## 位操作
- 清零操作`bic`

比如有个控制LED的寄存器，第`n`位为`1`则该位对应的灯亮

```
LENCON |= 1 << n;              #c语言
orr LENCON, LENCON, 1 << n     #汇编
```

如果想第`n`与`n+1`位为零，即相邻两位要清零，相邻两位表达为`bin11`，即十进制的`3`

```
LEDCON &= ~(3 << n);          #c语言

mvn r0, 3 << n                #汇编1
and LEDCON, LEDCON, r0

bic LEDCON, LEDCON, 3 << n    #汇编2
```

- bit反转`rbit`

```c
int main(void){
  int bic, rbit = 0x12345678;

  asm volatile(
    "mov r0, #0xff\n"
    "mov r1, #(3 << 2)\n"  //1100  3 << 2
    "bic %0, r0, r1\n"     //%3=r0&(~r1)
    "rbit %1, %1\n"
    :"=r"(bic), "+r"(rbit)
    :
    :"r0", "r1"
  );

  printf("bic = %x\n", bic);
  printf("rbit = %x\n", rbit);

  return 0;
}
```

- 左移右移
    + `lsl` 逻辑左移
    + `lsr` 逻辑右移
    + `asr` 算术右移，空出位以符号位补充，不存在算术左移，`asl`将翻译成`lsl`
    + `ror` 循环右移


## 大小端转换
```c
#include <stdio.h>

int main(void){
  int a = 0x12345678;

  //htonl  ntohl
  asm volatile(
    "rev %0, %0\n"     //32位
    :"+r"(a)
  );

  printf("a = %x\n", a);

  a = 0x1234;
  //htons ntohs
  asm volatile(
    "rev16 %0, %0\n"   //16位
    :"+r"(a)
  );

  printf("a = %x\n", a);
  return 0;
}

```

## 读写cpsr
- `mrs`读`cpsr`
- `msr`写`cpsr`，user模式只能修改`NZCVQ`位

```c
#include <stdio.h>

int main(void){
  int c;
  asm volatile(
    "mrs %0, cpsr\n"  //%0=cpsr
    :"=&r"(c)
  );

  printf("c = %x\n", c);

  //N=0 Z=0 C=0 V=0 Q
  asm volatile(
    "mov r0, #3\n"
    "adds r0, r0, #0\n"
    :::"r0"
  );

  asm volatile(
    "mrs %0, cpsr\n"  //%0=cpsr
    :"=&r"(c)
  );

  printf("c = %x\n", c);

  asm volatile(
    "mrs r0, cpsr\n"
    "mvn r1, #0\n"
    "orr r0, r0, r1\n"
    "msr cpsr, r0\n"  //cpsr=r0
    :::"r0", "r1"
  );

  asm volatile(
    "msr cpsr, #0xff\n"
  );

  asm volatile(
    "mrs %0, cpsr\n"  //%0=cpsr
    :"=&r"(c)
  );

  printf("c = %x\n", c);
  return 0;
}
```

## 内存操作
### 普通变量
- `m`:操作方式是内存，`"m"(a)`表示`a`的地址作为输入变量
- 第三行冒号，使用内存的需要标识`memory`

```c
  int a = 4;
  asm volatile(
    "ldr r0, %0\n"   //r0=*addr  %0是a的地址
    "add r0, r0, #1\n"
    "str r0, %0\n"   //*addr=r0
    :
    :"m"(a)
    :"r0", "memory"
  );
  printf("a = %d\n", a);
```

### 数组操作1
```c
  int b[3] = {0, 1, 2};

  asm volatile(
    "add %0, %0, #1\n"
    "add %1, %1, #1\n"
    "add %2, %2, #1\n"
    :"+r"(b[0]), "+r"(b[1]), "+r"(b[2])
    :
    :
  );

  int i;
  for(i = 0; i < 3; i++)
    printf("b[%d] = %d\n", i, b[i]);
```

### 数组操作2
```c
  int b[3] = {0, 1, 2};

  asm volatile(
    "mov r0, %0\n"
    "ldr r1, [r0]\n"   //r1=*r0
    "add r1, r1, #4\n"
    "str r1, [r0]\n"   //*r0=r1

    "add r0, r0, #4\n" //地址移4位
    "ldr r1, [r0]\n"
    "add r1, r1, #4\n"
    "str r1, [r0]\n"

    "add r0, r0, #4\n"
    "ldr r1, [r0]\n"
    "add r1, r1, #4\n"
    "str r1, [r0]\n"
    :
    :"r"(b)
    :"r0", "r1"
  );

  int i;
  for(i = 0; i < 3; i++)
    printf("b[%d] = %d\n", i, b[i]);
```

### 数组操作3
```c
  int b[3] = {0, 1, 2};

  asm volatile(
    "mov r0, %0\n"

    "ldr r1, [r0]\n"     //r1=*r0
    "add r1, r1, #3\n"
    "str r1, [r0], #4\n" //*r0=r1 r0+=4 修改值后 直接地址移动　上面两条指令合并成一条

    "ldr r1, [r0]\n"     //r1=*r0
    "add r1, r1, #3\n"
    "str r1, [r0], #4\n" //*r0=r1 r0+=4

    "ldr r1, [r0]\n"     //r1=*r0
    "add r1, r1, #3\n"
    "str r1, [r0], #4\n" //*r0=r1 r0+=4
    :
    :"r"(b)
    :"r0", "r1"
  );

  int i;
  for(i = 0; i < 3; i++)
    printf("b[%d] = %d\n", i, b[i]);
```

### 数组操作4
```c
  int b[3] = {0, 1, 2};

  asm volatile(
    "mov r0, %0\n"
    "ldr r1, [r0]\n"
    "add r1, r1, #2\n"
    "str r1, [r0]\n"

    "ldr r1, [r0, #4]\n"   //r1=*(r0+4) 不改变数据基地址,通过位移来访问
    "add r1, r1, #2\n"
    "str r1, [r0, #4]\n"

    "ldr r1, [r0, #8]\n"   //r1=*(r0+8)
    "add r1, r1, #2\n"
    "str r1, [r0, #8]\n"
    :
    :"r"(b)
    :"r0", "r1"
  );

  int i;
  for(i = 0; i < 3; i++)
    printf("b[%d] = %d\n", i, b[i]);
```

### 数组操作5
```c
  int b[3] = {0, 1, 2};

  asm volatile(
    "mov r0, %0\n"
    "ldr r1, [r0]\n"
    "add r1, r1, #5\n"
    "str r1, [r0]\n"

    "ldr r1, [r0, #4]!\n"    //r0+=4 r1=*r0 直接地址移动　再取值　也是两条指令合并成一条
    "add r1, r1, #5\n"
    "str r1, [r0]\n"

    "ldr r1, [r0, #4]!\n"    //r0+=4 r1=*r0
    "add r1, r1, #5\n"
    "str r1, [r0]\n"
    :
    :"r"(b)
    :"r0", "r1"
  );

  int i;
  for(i = 0; i < 3; i++)
    printf("b[%d] = %d\n", i, b[i]);
```

## 栈操作
- c语言中入栈采用FD(满递减模式)，即`[sp]`的指向是有效空间，当需要入栈时，先`sp=sp-1`，然后再把值放到`[sp]`中；而出栈，则先出栈，后`sp=sp+1`

### 内存方式读写栈
- 因为`[sp]`指向的内容是有效空间，这种方式容易造成程序错误

```c
  int a;

  asm volatile(
    "ldr %0, [sp]\n"
    "mov r0, #10\n"
    "str r0, [sp]\n"
    :"=&r"(a)
    :
    :"r0"
  );

  printf("a = %x\n", a);
```

### push/pop操作栈
- 入栈和出栈时寄存器需要保持从小到大的次序（否则会有警告），__低地址__ 空间的值对应 __小号__ 的寄存器（低地址空间的先出栈）

```c
  int a, b, c;

  asm volatile(
    "mov r0, #1\n"
    "mov r1, #2\n"
    "mov r2, #3\n"
    "push {r0-r2}\n"
    "pop {r3-r4, r5}\n"
    "mov %0, r3\n"
    "mov %1, r4\n"
    "mov %2, r5\n"
    :"=&r"(a), "=&r"(b), "=&r"(c)
    :
    :"r0", "r1", "r2", "r3", "r4", "r5"
  );

  printf("a = %x\n", a);
  printf("b = %x\n", b);
  printf("c = %x\n", c);
```

### stmfd/ldmfd操作栈
明确指出使用满递减的方式操作栈

- stmfd (ST: Store, M: Multiple, F: FULL, D: Descending)
- ldmfd (LD: Load, M: Multiple, F: FULL, D: Descending)

```c
  int a, b, c;

  asm volatile(
    "mov r0, #1\n"
    "mov r1, #2\n"
    "mov r2, #3\n"
    "stmfd sp!, {r0-r2}\n"
    "ldmfd sp!, {r3-r4, r5}\n"
    "mov %0, r3\n"
    "mov %1, r4\n"
    "mov %2, r5\n"
    :"=&r"(a), "=&r"(b), "=&r"(c)
    :
    :"r0", "r1", "r2", "r3", "r4", "r5"
  );

  printf("a = %x\n", a);
  printf("b = %x\n", b);
  printf("c = %x\n", c);
```

## 原子操作
- c语言中类型修饰符为`atomic_t`
- 汇编中使用`ldrex`和`strex`，并依据`cmp`来判断是否修改成功，不成功则重新执行
- 内核调度的是线程（不是进程），类似锁、互斥量都是由汇编中原子操作来支持

```c
atomic_t a;

atomic_add(a, 1);

int atomic_add(int a, int b){
  asm volatile(
    "again:\n"
    "ldrex r0, %0\n"
    "add r0, r0, %1\n"
    "strex r1, r0, %0\n"
    "cmp r1, #0\n"
    "bne again\n"
    :
    :"m"(a), "r"(b)
    :
  );
}
```

## 比较指令与条件执行
- 比较指令是不需要加`s`就能影响`cpsr`位的指令
- 比较指令完成后，一般就需要条件执行
- `cmp`做减法去影响cpsr位；`cmn`做加法去影响cpsr位；
- 一般语句都可加条件执行的后缀`[ne|eq|lt|gt|le|ge]`，如`mov`可以为`movne`

```c
if(a > b)     //cmp a, b       @转化为 a - b,将修改cpsr 中的 NZ 位
  c = 7       //movgt c, #7    @N==0 Z==0
else if(a == b)
  c = 9       //moveq c, #9    @Z==1
else
  c = 10      //movlt c, #10   @N==1
```

```c
  int a = 5, b = 6, c;

  asm volatile(
    "mov r0, #1\n"
    "mov r1, #2\n"
    "cmp r0, r1\n"
    "movgt %0, #7\n"
    "moveq %0, #9\n"
    "movlt %0, #10\n"
    :"=&r"(c)
    :"r"(a), "r"(b)
    :"r0", "r1"
  );

  printf("c = %d\n", c);
```

## 跳转指令
```c
  int a;
  asm volatile(
    "mov %0, #3\n"
    "b end\n"
    "mov %0, #4\n"  //不会被执行到
    "end:\n"
    :"=&r"(a)
  );
```

- 跳转到指定label
- `b/bl/bx`最多只能跳转的范围[-32M, +32M-4]

```c
int main(void){
  int a;
  asm volatile(
    "mov r0, #1\n"
    "mov r1, #2\n"
    "bl nihao\n"         //先把下一条指令的地址保存在lr中,然后再跳转
    "mov %0, r0\n"
    :"=&r"(a)::"r0", "r1"
  );

  printf("a = %d\n", a);
  return 0;
}

asm (                   //可以位于函数外部,此处不需要加volatile
  "nihao:\n"
  "add r0, r0, r1\n"
  //"mov pc, lr\n"      //把lr的值放入pc,实现了跳转
  "bx lr\n"             //等价于上面的语句
);
```

## 汇编中调用C函数
- 利用上面的跳转指令来实现函数调用
- 根据APCS（arm过程调用标准），用来约束汇编和C/C++相互调用
    + 传参数：`r0`, `r1`, `r2`, `r3` 如果参数个数大于4个，那么超过4个的参数放到栈（越靠后的参数越先入栈）
    + 要求必须用满递减栈
    + 返回值：如果返回值是32位则放到`r0`；如果64位则高32位放到`r1`，低32位放到`r0`

```c
#include <stdio.h>
int main(void){
  int a;
  asm volatile(
    "mov r0, #5\n"
    "mov r1, #6\n"
    "push {r0, r1}\n"    //超过4个参数的,做入栈处理
    "mov r0, #1\n"       //该句以及下面三句,即将参数放在相应寄存器上
    "mov r1, #2\n"
    "mov r2, #3\n"
    "mov r3, #4\n"
    "bl nihao\n"         //先把下一条指令的地址保存在lr中,然后在跳转
    //pop {r0, r1}       //函数执行完成后,需清理参数,做出栈处理,此处有bug,会覆盖寄存器值
    "add sp, sp, #8\n"   //正确做法是,将sp+8
    "mov %0, r0\n"
    :"=&r"(a)::"r0", "r1"
  );

  printf("a = %d\n", a);
  return 0;
}

int nihao(int a, int b, int c, int d, int e, int f){
  printf("a = %d\n", a);
  printf("b = %d\n", b);
  printf("c = %d\n", c);
  printf("d = %d\n", d);
  printf("e = %d\n", e);
  printf("f = %d\n", f);
  return a + b + c + d + e + f;
}
```

## 未定义指令
将产生一条`SIGILL        4       Core    Illegal Instruction`信号

```c
#include <stdio.h>

int main(void){
  //内嵌的指令是处在代码段
  asm volatile(
    ".word 0x77777777\n"
  );

  return 0;
}
```

## 选择排序

<!-- run -->

```c
#include <stdio.h>

void sort(int *, int);
int main(){
    int i;
    int arr[] = {3,5,7,4,2,1,9,6};
    int len = sizeof(arr) / sizeof(int);
    sort(arr, len);
    for(i = 0; i < len; i++){
        printf("%d ", arr[i]);
    }
    printf("\n");
    return 0;
}

void sort(int *arr, int len){
    int idx, i, j, temp;
    for(i = 0; i < len - 1; i++){
        idx = i;
        for(j = i + 1; j < len; j++){
            if(arr[j] < arr[idx])
                idx = j;
        }
        if(i != idx){
            temp = arr[i];
            arr[i] = arr[idx];
            arr[idx] = temp;
        }
    }
}
```

将其中算法部分改成汇编如下：

```c

```

ARM汇编生成
===========
## 局部变量

```c
#include <stdio.h>
int myadd();
int main(void){
                     //stmfd sp!, {fp, lr}
                     //add fp, sp, #4
    myadd();         //bl  myadd
    return 0;        //mov r3, #0
                     //mov r0, r3
                     //ldmfd sp!, {fp, pc}
}

int myadd(){
                     //str fp, [sp, #-4]!      @*(sp-4)=fp;sp-=4; 相当于push {fp}
                     //add fp, sp, #0          @fp=sp; 保存sp指向
                     //sub sp, sp, #20         @sp-=20; 修改sp指向,基地址为fp,之间为局部变量空间

    int a = 12;      //mov r3, #12             @r3=12;
                     //str r3, [fp, #-8]       @*(fp-8)=r3; 修改变量a的值
    int b = 34;      //mov r3, #34             @r3=34;
                     //str r3, [fp, #-12]      @*(fp-12)=r3; 修改变量b的值
    int c = a + b;   //ldr r2, [fp, #-8]       @r2=*(fp-8);
                     //ldr r3, [fp, #-12]      @r3=*(fp-12);
                     //add r3, r2, r3          @r3=r2+r3;
                     //str r3, [fp, #-16]      @*(fp-16)=r3; 修改变量c的值

                     //mov r0, r3              @r0=r3; r0为返回值寄存器
                     //add sp, fp, #0          @sp=fp; 恢复sp指向,回收局部变量空间
                     //ldmfd sp!, {fp}         @fp=*sp;sp+=4; 相当于pop {fp}
                     //bx  lr                  @返回lr指向
}
```

## 普通参数
```c
int myadd(int a, int b){
                     //str fp, [sp, #-4]!
                     //add fp, sp, #0
                     //sub sp, sp, #20

                     //str r0, [fp, #-16]      @*(fp-16)=r0; 将参数放到栈空间
                     //str r1, [fp, #-20]      @*(fp-20)=r1;

    int c = a + b;   //ldr r2, [fp, #-16]      @加载栈数据到寄存器
                     //ldr r3, [fp, #-20]
                     //add r3, r2, r3
                     //str r3, [fp, #-8]       @*(fp-8)=r3; 修改变量c的值

                     //mov r0, r3
                     //add sp, fp, #0
                     //ldmfd sp!, {fp}
                     //bx  lr
}
```

## >4个参数
```c
int myadd(int a, int b, int c, int d, int e, int f);
int main(void){
                          //stmfd sp!, {fp, lr}
                          //add fp, sp, #4
                          //sub sp, sp, #8

                          //str r3, [sp, #0]  @赋第6位参数
                          //mov r3, #6
                          //str r3, [sp, #4]  @赋第5位参数
                          //mov r0, #1        @1-4位参数放寄存器
                          //mov r1, #2
                          //mov r2, #3
                          //mov r3, #4
    myadd(1,2,3,4,5,6);   //bl  myadd

    return 0;             //mov r3, #0
                          //mov r0, r3
                          //sub sp, fp, #4
                          //ldmfd sp!, {fp, pc}
}

int myadd(int a, int b, int c, int d, int e, int f){
                          //str fp, [sp, #-4]!
                          //add fp, sp, #0
                          //sub sp, sp, #20

                          //str r0, [fp, #-8]  @把前4个参数由寄存器放到栈空间
                          //str r1, [fp, #-12]
                          //str r2, [fp, #-16]
                          //str r3, [fp, #-20]

    return a + b + c + d + e + f;

                          //ldr r2, [fp, #-8]
                          //ldr r3, [fp, #-12]
                          //add r2, r2, r3   @r2+=b

                          //ldr r3, [fp, #-16]
                          //add r2, r2, r3   @r2+=c

                          //ldr r3, [fp, #-20]
                          //add r2, r2, r3   @r2+=d

                          //ldr r3, [fp, #4] @剩下参数就存在栈空间,原先由sp指向,现可由fp寻得
                          //add r2, r2, r3   @r2+=e

                          //ldr r3, [fp, #8]
                          //add r3, r2, r3   @r2+=f

                          //mov r0, r3
                          //add sp, fp, #0
                          //ldmfd sp!, {fp}
                          //bx  lr
}
```

见下图

```plain
               stmfd sp!, {fp, lr}
      ├──────┤
      │ *lr  │
      ├──────┤
      │ *fp  │
sp   >├──────┤
      │  6   │                                   str r3, [sp, #4]
fp   >├──────┤ add fp, sp, #4
      │  5   │                 str r3, [sp, #0]
sp   >├──────┤ sub sp, sp, #8
      │ *fp  │ myadd(): str  fp, [sp, #-4]!                      ldmfd  sp!, {fp} @fp的值得到恢复
sp fp>├──────┤ add  fp, sp, #0                   add  sp, fp, #0
      │  ??  │ lr??
    -4├──────┤
      │  1   │                 str r0, [fp, #-8]
    -8├──────┤
      │  2   │                 str r1, [fp, #-12]
   -12├──────┤
      │  3   │                 str r2, [fp, #-16]
   -16├──────┤
      │  4   │                 str r3, [fp, #-20]
sp -20├──────┤ sub  sp, sp, #20
      │      │

```

## 参数指针
```c
#include <stdio.h>

void myswap(int *a, int *b){
                    //str fp, [sp, #-4]!
                    //add fp, sp, #0
                    //sub sp, sp, #20

                    //str r0, [fp, #-16]  @将参数的值（本身是地址）放到栈空间
                    //str r1, [fp, #-20]

                    //ldr r3, [fp, #-16]  @r3=*(fp-16) 先得到参数a 指针（地址）
                    //ldr r3, [r3, #0]    @r3=*(r3)    再解引用 得到指针指向的 值
    int c = *a;     //str r3, [fp, #-8]   @把解引用后的值放到栈空间（c的空间）

                    //ldr r3, [fp, #-20]  @处理参数b 指针（地址）
                    //ldr r2, [r3, #0]    @解引用b 得到 值 加载到r2
                    //ldr r3, [fp, #-16]  @将第一个参数a指针值（地址） 加载到寄存器r3
    *a = *b;        //str r2, [r3, #0]    @把r2的值存储到r3指向地址

                    //ldr r3, [fp, #-20]  @将第二个参数b指针值（地址） 加载到寄存器r3
                    //ldr r2, [fp, #-8]   @将c空间的值 加载到寄存器r2
    *b = c;         //str r2, [r3, #0]    @把r2的值存储到r3指向地址

                    //add sp, fp, #0
                    //ldmfd sp!, {fp}
                    //bx  lr
}

int main(void){
                    //stmfd sp!, {fp, lr}
                    //add fp, sp, #4
                    //sub sp, sp, #8

                    //mov r3, #12
    int a = 12;     //str r3, [fp, #-8]

                    //mov r3, #34
    int b = 34;     //str r3, [fp, #-12]

                    //sub r2, fp, #8    @计算a的栈空间地址 放入r2
                    //sub r3, fp, #12   @计算b的栈空间地址 放入r3
                    //mov r0, r2        @传参
                    //mov r1, r3
    myswap(&a, &b); //bl  myswap

    return 0;       //mov r3, #0
                    //mov r0, r3
                    //sub sp, fp, #4
                    //ldmfd sp!, {fp, pc}
}
```



## 循环
```c
void myloop(){
  stmfd sp!, {fp, lr}
  add fp, sp, #4
  sub sp, sp, #8
  mov r3, #0
  str r3, [fp, #-8]
  b .L3
.L4:
  bl  mycall
  ldr r3, [fp, #-8]
  add r3, r3, #1
  str r3, [fp, #-8]
.L3:
  ldr r3, [fp, #-8]
  cmp r3, #9
  ble .L4
  sub sp, fp, #4
  ldmfd sp!, {fp, pc}

    int i;
    for(i = 0; i < 10; i++)
        mycall();
}
```

## 数组

裸板程序
=========
## 项目组成
```plain
.
├── hardware.c
├── include
│   ├── common.h
│   └── hardware.h
├── ld.lds
├── main.c
├── Makefile
└── start.s

```

- 每多一个硬件程序，就多一个`c`文件和一个在`inclue`中的`h`文件
- `start.s`是汇编程序，使用`.global`用于声明为全局符号（将来通过`nm`查看时，类型为`T`，否则为`t`），通过`stmfd sp!, {r0-r12, lr}`保持现场，将来`ldmfd sp!, {r0-r12, pc}`用于恢复现场，`bl main`则跳转到`main()`

```asm
.global _start
_start:

        b reset
reset:
        stmfd sp!, {r0-r12, lr}
        bl main
        ldmfd sp!, {r0-r12, pc}
```

## Makefile
```make
TARGET          :=arm
BIN             :=$(TARGET).bin
START           :=start.o main.o
OBJS            :=hardware.o chip_id.o led.o
LD_ADDR         :=0x50000000
LD_LDS          :=./ld.lds
###########################################
CROSS_COMPILE   :=arm-linux-

CC              :=$(CROSS_COMPILE)gcc
AS              :=$(CROSS_COMPILE)as
LD              :=$(CROSS_COMPILE)ld
OBJCOPY         :=$(CROSS_COMPILE)objcopy
OBJDUMP         :=$(CROSS_COMPILE)objdump
NM              :=$(CROSS_COMPILE)nm

RM              :=rm -rf

CFLAGS          :=-I./include -Wall
LDFLAGS         :=
############################################
all:$(TARGET)
        $(OBJCOPY) -O binary $< $(BIN)
        $(NM) $< >System.map
        $(RM) $<

$(TARGET):$(START) $(OBJS)
        $(LD) $^ -o $@ -Ttext $(LD_ADDR)
clean:
        $(RM) $(START) $(OBJS) $(BIN)
```

- 由于在uboot中需要`dwn 5000 0000`，并`go 5000 0000`，此处在链接时，需要指定`-Ttext`为`0x50000000`
- 此处没有写`.o`文件的依赖，这是make的自动推导出来的，先去找`.s`，如果有就直接`as`，否则就找`.c`，找到后`gcc`
- `nm`用于产生符号表，一般命名为`System.map`，可通过`strip`将符号去掉，减少文件空间
- `objcopy`用于将链接后产生的可执行文件转化为二进制

## 借用函数
通过uboot的`System.map`查找函数的地址，通过函数指针强制转换

```c
#define udelay(us) (((void (*)(int))0x43e25e88)(us))
#define printf(...) (((int (*)(const char *, ...))0x43e11434)(__VA_ARGS__))
```

## 跑马灯(GPIO输出)
- 头文件

> `GPM4CON`是配置寄存器，`GPM4DAT`是数据寄存器

```c
#ifndef __LED_H__
#define __LED_H__

extern void led_init(void);
extern void led_on(int no);
extern void led_off(int no);

#define GPM4CON (*(volatile unsigned int *)(0x11000000 + 0x2e0))
#define GPM4DAT (*(volatile unsigned int *)(0x11000000 + 0x2e4))

#endif
```

- 实现文件

> 查询Exynos 4412手册GPIO章节 P284

```c
#include <common.h>
#include <led.h>

void led_init(void){
    GPM4CON &= ~0xffff; //配置 GPM4CON[0]~GPM4CON[3] 清零
    GPM4CON |= 0x1111;  //设置为输出

    GPM4DAT |= 0xf;     //初始灯灭 0为开 1为灭
}

void led_on(int no){
    if(no > 3 || no < 0) return;
    GPM4DAT &= ~(1 << no); //no位 为0
}

void led_off(int no){
    if(no > 3 || no < 0) return;
    GPM4DAT |= (1 << no); //no位 为1
}
```

- 调用程序

```c
#include <common.h>
#include <led.h>

int main(void){
    int count = 100;
    led_init();

    while(count--){
        led_on(count % 4);
        udelay(500000);
        led_off(count % 4);
        udelay(500000);
    }
    return 0;
}
```

## LCD
### 概述
![img](../../imgs/display_contorller01.png)

```plain
open(/dev/fb0);    //dev/fb1 dev/fb2 ...
v2=mmap(fd,...);
------------------------------------------------------------------------
mem子系统             fb子系统
 修改页表(v2->p1)       n个屏幕结构体
                       n个驱动（需要在mem中分配空间,得虚拟地址v1[内核用 >3G的位置]和物理地址p1[dma]）
------------------------------------------------------------------------
display controller  --> (24bit data线 rgb各8)-->    lcd
   dma（直接访问）       (4bit time时序线)

```

- 上层为用户态，中层为内核，下层为硬件
- 用户态`open(/dev/fb0)`得到的`fd`再做`mmap()`后（在进程的虚拟地址空间中分配空间[mem子系统找 0~3G位置]，得到显存地址`v2`
- 内核层需要两个子系统，`framebuffer`与`memory`，fb子系统负责管理fb设备，需要在内核中注册，每个设备对应一个屏幕结构体，对应一个驱动；驱动用到的内存，需要`mem`子系统给分配（内核用 >3G的位置），将得到两个内存地址，一个物理地址`p1`(用于dma)，一个虚拟地址`v1`(自己使用)，并修改页表，使用`v2`对应`p1`
- 由`display controller`通过 24位数据线 与 4位时序线 连接`lcd`

- 像素点格式
    - RGB888------>[8|8R|8G|8B]  大小为 480 * 800 * 4  可用`int`表示
    - RGB565------>[5R|6G|5B]    大小为 480 * 800 * 2  可用`short`表示

- 800*400屏算xy坐标，`v2`是显示地址
    - `(int *)v2 + y*800 + x`
    - `(short *)v2 + y*800 + x`

- 混合方式
    - 存在平面 alpha值存在寄存器中(更常用)
    - 像素混合 alpha存在像素点中

- `display controller`有窗口管理器(管理图层 FIFO 混合)
    - 对于android
        + 第一层是桌面（不可alpha混合）
        + 第二层是图标（可alpha混合 值为0~15）
        + 第三层是应用启动后界面
        + 更多的图层由软件解决计算后放到某一层
    - 每一层还有3个buffer 供dma访问 用于提高播放影片体验
    - buffer用于硬件加速 局部显示（每一层都注册为一个设备）
    - dma中有5个通道，前3个可以直接从 `local path`或`显存`取数据，后两个只能从`显存`取数据
        + 一般通道对应同号窗口

### 设置GPIO
```c
void gpio_for_lcd(void){
  //把gpio初始化为lcd功能
  GPF0CON = 0x22222222;
  GPF1CON = 0x22222222;
  GPF2CON = 0x22222222;
  GPF3CON &= ~0xffff;
  GPF3CON |= 0x2222;
}
```

### 设置时钟
设置分频器与选择器，得到33.3mhz

```c
void clock_for_lcd(void){
  CLK_DIV_LCD &= ~0xf;
  CLK_DIV_LCD |= 7;
  CLK_SRC_LCD0 &= ~0xf;
  CLK_SRC_LCD0 |= 6;

  CLK_SRC_MASK_LCD |= 1;

  CLK_GATE_IP_LCD |= 1;

  LCDBLK_CFG |= 1 << 1;

  while(CLK_DIV_STAT_LCD & 1);
}
```


### 4条时序线
> 是移植LCD分辨率需要注意的(更常用)，只需修改代码中的`time_for_lcd()`

- `VCLK` 发送频率 一个像素点一个信号 33.3Mhz
- `HSYNC` 行同步信号
- `VSYNC` 垂直同步信号 一帧（屏）数据
- `VDEN` 通知是否发送有效点

```plain
每行的空像素点
  1       2        有效800     3
  HSPW+1  HBPW+1   HOZVAL+1    HFPD+1

每屏的空行
  1 VSPW+1
  2 VBPD+1
  有效480  LINEVAL+1
  3 VFPD+1
```

![img](../../imgs/display_contorller02.png)

见[SEC_Exynos4412_Users+Manual_Ver.1.00.00.pdf](../../data/SEC_Exynos4412_Users+Manual_Ver.1.00.00.pdf) P1148

![img](../../imgs/display_contorller03.png)

见[S700-AT070TN92.pdf](../../data/S700-AT070TN92.pdf) P13

```c
void time_for_lcd(void){
  //VCLK = 33.3M
  VIDCON0 = (2 << 6) | 3;

  //VS HS需要翻转
  //VDEN高电平有效，不需要翻转
  //VCLK 上升沿
  VIDCON1 = (1 << 9) | (1 << 7) | (1 << 6) | (1 << 5);

  //VSPW+1 = tvpw = 10
  //VBPD+1 = tvb-tvpw = 13
  //LINEVAL+1 = tvd = 480
  //VFPD+1 = tvfp = 22
  //HSPW+1 = hpw = 20
  //HBPD+1 = thb-hpw = 26
  //HOZVAL+1 = thd = 800
  //HFPD+1 = thfp = 210
  VIDTCON0 = (12 << 16) | (21 << 8) | (9);
  VIDTCON1 = (25 << 16) | (209 << 8) | (19);
  VIDTCON2 = (479 << 11) | 799;
}
```

### 配置窗口
> 窗口0不需要设置alpha,窗口1需要

```c
void win0_init(unsigned int addr){
#ifdef BPP565
  WINCON0 = (1 << 16) | (5 << 2) | 1;
  VIDOSD0C = (800 * 480 * 2) >> 2;
#else
  WINCON0 = (1 << 15) | (11 << 2) | 1;
  VIDOSD0C = (800 * 480 * 4) >> 2;
#endif
  //channel0
  SHADOWCON &= ~(1 << 10);
  SHADOWCON &= ~(1 << 5);
  SHADOWCON |= 1;

  //channel0 ----> win0
  WINCHMAP2 &= ~(7 << 16);
  WINCHMAP2 |= (1 << 16);

  //win0 ---> channel0
  WINCHMAP2 &= ~(7 << 0);
  WINCHMAP2 |= (1 << 0);

  VIDOSD0A = 0;
  VIDOSD0B = (799 << 11) | (479);

  //win0 buffer0
  VIDW00ADD0B0 = addr;
  VIDW00ADD1B0 = addr + VIDOSD0C * 4;
}

void win1_init(unsigned int addr){
#ifdef BPP565
  WINCON1 = (1 << 16) | (5 << 2) | 1;
  VIDOSD1D = (800 * 480 * 2) >> 2;
#else
  WINCON1 = (1 << 15) | (11 << 2) | 1;
  VIDOSD1D = (800 * 480 * 4) >> 2;
#endif
  //channel1 
  SHADOWCON &= ~(1 << 11);
  SHADOWCON &= ~(1 << 6);
  SHADOWCON |= 1 << 1;

  //channel1 ----> win1
  WINCHMAP2 &= ~(7 << 19);
  WINCHMAP2 |= (2 << 19);

  //win1 ---> channel1
  WINCHMAP2 &= ~(7 << 3);
    WINCHMAP2 |= (2 << 3);
  
  VIDOSD1A = 0;
  VIDOSD1B = (799 << 11) | (479);

  VIDOSD1C = 0x777 << 12;
  //alpha0 ---> [12----23]
  //alpha1 ---> [0----11]

  //win1 buffer0
  VIDW01ADD0B0 = addr;
  VIDW01ADD1B0 = addr + VIDOSD1D * 4;
}
```

- `ENLOCAL_F [22]`需选择dma模式  `SEC_Exynos4412_Users+Manual_Ver.1.00.00.pdf` P1879
- `WINCON0[15:18]`用于swap `SEC_Exynos4412_Users+Manual_Ver.1.00.00.pdf` P1806
    - BPP888 BSWP=0 HWSWP=0 WAWP=1
    - BPP565 BSWP=0 HWSWP=1 WAWP=0
- 通道与窗口需要双向选择
- `VIDOSD0C`是显存大小
- 制作framebuffer所需的图像
    - `mkimage`(bmp jpeg --> rgb[888/565])[依赖libjpeg.so.6]
    - `./mkimage mm/20.jpg 20_888.raw`，然后供dnw下载

- 同样去配置第2、3、n个窗口，它们可以配置alpha

### 画点
```c
void draw_point(unsigned int addr, int x, int y, int r, int g, int b){
#ifdef BPP565
  unsigned short *v = (void *)addr;
  *(v + 800 * y + x) = (r << 11) | (g << 5) | (b);
#else
  unsigned int *v = (void *)addr;
  *(v + 800 * y + x) = (r << 16) | (g << 8) | (b);
#endif
}
```

### 有关亮度
亮度可由像素或背光控制

背光控制一般使用PWM控制MP1518，而friendly arm使用单片机控制，4412通过gpio来通信

## MMU
[DDI0388I_cortex_a9_r4p1_trm.pdf](../../data/DDI0388I_cortex_a9_r4p1_trm.pdf) P109

[DEN0013C_cortex_a_series_PG.pdf](../../data/DEN0013C_cortex_a_series_PG.pdf) P141

- 一个进程一个页表
- 页表也存在内存中（它本身通过cp15的c2 (ttbr) 访问物理内存）
- 段映射 一级映射 共4k个32bit条目  虚拟地址的高12位作为数组下标（负责1M内存）
  + 物理地址也按1M分段
  + 虚拟地址低20位与物理地址低20位 一样

- linux 用4k 小页映射
- 分页是管理机制与硬件无关
- 页表里存物理地址，虚拟地址是偏移地址
- 二级页表有256个条目
    - 虚拟地址与物理地址低12位一样
    - 高12位一级查询，中8位二级查询
- 查表由硬件完成

### 段映射代码

```c
#include <common.h>
#include <mmu.h>

//va=0x12345678
//pa=0x02200044
//0x123xxxxx---->0x022xxxxx
//功能：通过修改（或创建）页表的一个条目来实现va到pa的映射
void mmap_section(unsigned int *ttb, unsigned int *va, unsigned int *pa){
    int index = ((unsigned int)va) >> 20;
    int section = ((unsigned int)pa) >> 20;

    //ttb[index] = ((unsigned int)pa & 0xfff00000) | 2;
    ttb[index] = (section << 20) | 2;
}

void page_table_create(unsigned int *ttb){
  //pa[0x40000000, 0x80000000]
  //pa[0x10000000, 0x14000000] 
  unsigned int pa, va;

  for(va = 0; va < 0x80000000; va += 0x100000) {
    pa = va;
    mmap_section(ttb, (void *)va, (void *)pa);
  }

  //domain域 16个域，并不做权限检查
  //32[3031|||....||67|45|23|01]
  //参考DDI0406C_arm_architecture_reference_manual.pdf P1541 P1708 
  __asm__ __volatile__(
    "mrc p15, 0, r0, c3, c0, 0\n"
    "orr r0, r0, #3\n"
    "mcr p15, 0, r0, c3, c0, 0\n"
    "mcr p15, 0, %0, c2, c0, 0\n"
    :
    :"r"(ttb)
    :"r0"
  );  
}

//参考DDI0388I_cortex_a9_r4p1_trm.pdf P74
void mmu_enable(void){
  __asm__ __volatile__(
    "mrc p15, 0, r0, c1, c0, 0\n" 
    "orr r0, r0, #1\n"
    "mcr p15, 0, r0, c1, c0, 0\n"
    :::"r0"
  );
}

void mmu_disable(void){
  __asm__ __volatile__(
    "mrc p15, 0, r0, c1, c0, 0\n" 
    "bic r0, r0, #1\n"
    "mcr p15, 0, r0, c1, c0, 0\n"
    :::"r0"
  );
}


int main(void){
  int *p = (void *)0x71288888;

  *p = 300;
  //物理地址==虚拟地址
  //0x712xxxxx--->0x712xxxxx
  page_table_create((void *)0x60000000);
  //va=0x123xxxxx
  //pa=0x712xxxxx 
  mmap_section((void *)0x60000000, (void *)0x12345678, (void *)0x71234568);

  mmu_enable();

  printf("i am ok\n");

  printf("%d\n", *(int *)0x12388888);
  printf("%d\n", *(int *)0x71288888);

  return 0;
}
```

## 未定义异常
```asm
.global _start
_start:

  b reset         @0x50000000---->0xffff0000
  b unde          @0x50000004---->0xffff0004  需要通过mmu将其映射到高端向量表
                  @指令格式为 [cond 4|opcode 4| 24 offset] offset可正负跳转 前后可跳转8M指令 32M字节
reset:            @svc_mode 启动时为svc模式
  stmfd sp!, {r0-r12, lr}

  @设置高端向量表
  mrc p15, 0, r0, c1, c0, 0
  orr r0, r0, #(1 << 13)
  mcr p15, 0, r0, c1, c0, 0

  bl main
  ldmfd sp!, {r0-r12, pc}
unde:                         @unde_mode
  mov sp, #0x51000000         @设置栈的起始地始，该空间手工分配
  stmfd sp!, {r0-r12, lr}     @保存现场到栈中
                              @bl do_unde ;do_unde是一个c语言的unde处理函数，但此时不能使用相对跳转，只能使用绝对跳转
  mov lr, pc                  @将pc放入lr;该处使用绝对跳转,不像bl可以直接将pc放入到lr,需手工完成
  ldr pc, _unde_handler       @pc=do_unde
  ldmfd sp!, {r0-r12, lr}     @从栈中恢复现场
  movs pc, lr                 @从未定义异常模式返回
_unde_handler:                @为了确保得到函数的绝对地址
  .word do_unde

```

```c
void *memcpy(void *dest, const void *src, int count){
    char *tmp = dest;
    const char *s = src;

    while (count--)
        *tmp++ = *s++;
    return dest;
}

void do_unde(void){
  int c;

  __asm__ __volatile__(
    "mrs %0, cpsr\n"
    :"=&r"(c)
  );

  printf("%s %x\n", __FUNCTION__, c);
}

int main(void){
  page_table_create((void *)0x60000000);
  //0xfffxxxxx---->0x712xxxxx
  //0xffffxxxx---->0x712fxxxx
  mmap_section((void *)0x60000000, (void *)0xfff00000, (void *)0x71234568);
  mmu_enable();
  
  //通过内存拷贝，将处理指令，拷贝到高端向量表指定的地方
  memcpy((void *)0xffff0000, (void *)0x50000000,  50 * 4); 

  __asm__ __volatile__(   //在代码段写入无效指令
    ".word 0x77777777\n"
  );

  printf("i am ok\n");

  return 0;
}
```

## 软中断
```asm
.global _start
_start:

  b reset  @0x50000000----->0xffff0000
  b unde   @0x50000004----->0xffff0004
  b swi    @0x50000008----->0xffff0008
reset:    
  stmfd sp!, {r0-r12, lr}

  @设置高端向量表
  mrc p15, 0, r0, c1, c0, 0
  orr r0, r0, #(1 << 13)
  mcr p15, 0, r0, c1, c0, 0

  bl main
  ldmfd sp!, {r0-r12, pc}
swi:                                @svc_mode
  mov sp, #0x52000000 
  stmfd sp!, {r0-r12, lr}
  ldr r0, [lr, #-4]                 @r0=*(lr - 4) 得到lr中指令的前一条指令
  bic r0, r0, #0xff000000           @取它的低24位，根据APCS，r0可用于传参
  mov lr, pc
  ldr pc, _swi_handler
  ldmfd sp!, {r0-r12, lr}
  movs pc, lr
_swi_handler:
  .word do_swi
unde:                 
  mov sp, #0x51000000
  stmfd sp!, {r0-r12, lr}
  mov lr, pc
  ldr pc, _unde_handler@pc=do_unde
  ldmfd sp!, {r0-r12, lr}
  movs pc, lr
_unde_handler:
  .word do_unde
```

```c
void *memcpy(void *dest, const void *src, int count){
    char *tmp = dest;
    const char *s = src;

    while (count--)
        *tmp++ = *s++;
    return dest;
}

void myread(void){
  printf("myread\n");
}

void myopen(void){
  printf("myopen\n");
}

void myclose(void){
  printf("myclose\n");
}

void (*vector[])(void) = {myopen, myread, myclose};

//r0 r1 r2 r3 ---- sp
void do_swi(int no){//这里就可以得到swi的编号
  int c;

  void (*handler)(void) = vector[no];
  handler();

  __asm__ __volatile__(
    "mrs %0, cpsr\n"
    :"=&r"(c)
  );

  printf("%s %x\n", __FUNCTION__, c);
}

void do_unde(void){
  int c;

  __asm__ __volatile__(
    "mrs %0, cpsr\n"
    :"=&r"(c)
  );

  printf("%s %x\n", __FUNCTION__, c);
}
//假设上面是内核态程序
//----------------------------------------------
//假设下面是用户态程序
int main(void){
  page_table_create((void *)0x60000000);
  //0xfffxxxxx---->0x712xxxxx
  //0xffffxxxx---->0x712fxxxx
  mmap_section((void *)0x60000000, (void *)0xfff00000, (void *)0x71234568);
  mmu_enable();

  memcpy((void *)0xffff0000, (void *)0x50000000,  50 * 4); 
  //open--------swi---------------->sys_open
  //usr---------------------------->svc
  
  //svc
  __asm__ __volatile__(
    ".word 0x77777777\n"
    "swi 0\n"//[cond 4|4 opcode| no 24]
    "swi 1\n"
    "swi 2\n"
  );

  printf("i am ok\n");

  return 0;
}
```

## 中断处理

- 用户态是看不到中断的，只在内核
- 中断控制器
    - GIC：多核系统使用   arm-a9
    - VIC：有向量表      arm-a8 arm11
    - NVIC：可嵌套，有向量表（实时系统）  arm-m

- 中断优先级 越小越优先

- 中断分类（指GIC控制器）
    - SGI 软件（CPU）产生的中断[0,15] * 4，也需要走GIC，一个CPU相关于16个中断源，向其它CPU发中断
        - 用于CPU间交互，不同于swi
    - PPI 私有中断[16,31] * 4
    - SPI 共享中断[32,1024]

- 中断状态
    - pending
    - active
    - inactive


### WDT重启
```asm
.global _start
_start:

  b reset           @0x50000000----->0xffff0000
  b unde            @0x50000004----->0xffff0004
  b swi             @0x50000008----->0xffff0008
  .word 0x00,0x00,0x00     @填入空间
  b irq             @0x50000018----->0xffff0008
reset:  @svc_mode
  stmfd sp!, {r0-r12, lr}

  @设置高端向量表
  mrc p15, 0, r0, c1, c0, 0
  orr r0, r0, #(1 << 13)
  mcr p15, 0, r0, c1, c0, 0

  bl main
  ldmfd sp!, {r0-r12, pc}
irq:  @irq_mode
  mov sp, #0x52000000
  stmfd sp!, {r0-r12, lr}
  mov lr, pc
  ldr pc, _irq_handler
  ldmfd sp!, {r0-r12, lr} 
  subs pc, lr, #4
_irq_handler:
  .word do_irq
swi:  @svc
  @mov sp, #0x52000000
  stmfd sp!, {r0-r12, lr}
  ldr r0, [lr, #-4]@r0=*(lr - 4)
  bic r0, r0, #0xff000000
  mov lr, pc
  ldr pc, _swi_handler
  ldmfd sp!, {r0-r12, lr}
  movs pc, lr
_swi_handler:
  .word do_swi
unde:@unde_mode
  mov sp, #0x51000000
  stmfd sp!, {r0-r12, lr}
  mov lr, pc
  ldr pc, _unde_handler
  ldmfd sp!, {r0-r12, lr}
  movs pc, lr
_unde_handler:
  .word do_unde
```

PCLK当作133M

```c
void wdt_init(int ms){
  //133M / 133 / 64 = 15625hz
  WTCON = (132 << 8) | (2 << 3);
  WTCNT = 16 * ms;  
  WTDAT = 16 * ms;
}

void wdt_enable(void){
  WTCON |= 1 << 5;
}

void wdt_disable(void){
  WTCON &= ~(1 << 5);
}

void wdt_feed(int ms){
  WTCNT = 16 * ms;
}

void wdt_reset_init(int ms){
  wdt_init(ms);
  WTCON &= ~7;
  WTCON |= 1;

  AUTOMATIC_WDT_RESET_DISABLE = 0;
  MASK_WDT_RESET_REQUEST = 0;
}


int main(void){
  page_table_create((void *)0x60000000);
  mmu_enable();

  memcpy((void *)0xffff0000, (void *)0x50000000,  50 * 4); 

  wdt_reset_init(4000);// < 65535 / 16
  wdt_enable();
  uart_init(0);

  while(1){  //指定时间内未feed则重启
    wdt_feed(4000); 
    ugetchar();
    printf("feed ok\n");
  } 

  return 0;
}
```

### WDT中断
asm部分同前

```c
static struct irq_info irq_vector[128];

void request_irq(int irq_no, void (*handler)(struct irq_info *i), int flag){
  irq_vector[irq_no].flag = flag;
  irq_vector[irq_no].irq_no = irq_no; 
  irq_vector[irq_no].handler = handler;
}

void do_irq(void){
  //1.能够知道是谁产生了中断
  //2.通知gic把中断状态切换到active
  //3.每次中断中只能读一次
  int id;

  id = ICCIAR_CPU0;   

  irq_vector[id & 0x3ff].handler(irq_vector + (id & 0x3ff));  

  //1.通知中断控制器把中断设置为inactive
  ICCEOIR_CPU0 = id;
}

void wdt_init(int ms){
  //133M / 133 / 64 = 15625hz
  WTCON = (132 << 8) | (2 << 3);
  WTCNT = 16 * ms;  
  WTDAT = 16 * ms;
}

void wdt_enable(void){
  WTCON |= 1 << 5;
}

void wdt_disable(void){
  WTCON &= ~(1 << 5);
}

void do_wdt(struct irq_info *i){
  printf("wdt wdt flag = %d\n", i->flag);
  WTCLRINT = 1; //重置中断源
}

void wdt_irq_init(int ms){
  wdt_init(ms);
  WTCON &= ~7;
    WTCON |= 1 << 2;
  //根据Exynos4412手册9.2章节，看门狗的中断ID为75
  //gic 
  //1.使能cpu接口
  ICCICR_CPU0 = 1;
  //2.设置门槛
  ICCPMR_CPU0 = 0xff;
  //3.使能中断分配器
  ICDDCR = 1; 
  //4.打开相应的中断
  ICDISER2_CPU0 |= 1 << (75 - 64);
  //5.设置中断优先级
  ICDIPR18_CPU0 &= ~(0xff << 24);
  ICDIPR18_CPU0 |= 0x12 << 24;
  //6.选择目标cpu
  ICDIPTR18_CPU0 &= ~(0xff << 24);
  ICDIPTR18_CPU0 |= 1 << 24;
  
  request_irq(75, do_wdt, 100);
  
  #if 0
  //所有arm都支持
  __asm__ __volatile__(
    "mrs r0, cpsr\n"
    "bic r0, r0, #(1 << 7)\n"
    "msr cpsr, r0\n"
    :::"r0"
  );
  #endif
  //>=V6的cpu才支持
  __asm__ __volatile__("cpsie i");
}

int main(void){
  page_table_create((void *)0x60000000);
  mmu_enable();

  memcpy((void *)0xffff0000, (void *)0x50000000,  50 * 4); 

  wdt_irq_init(1000);// < 65535 / 16
  wdt_enable();

  return 0;
}
```

SPI中断源

> linux处理中断
> - 上半部分 响应中断 安排任务
> - 下半部分 处理任务（内核软中断 工作队列 tasklet）

## SGI中断
不需要清中断

```c
void do_sgi0(struct irq_info *i){
  printf("sig0 sig0 ... %d\n", i->flag);
}

void sgi_init(void){
  //cpu0_sgi0
  //gic
  //1.使能cpu接口
  ICCICR_CPU0 = 1;
  //2.设置门槛
  ICCPMR_CPU0 = 0xff;
  //3.使能中断分配器
  ICDDCR = 1; 
  //4.打开中断
  #define ICDISER0_CPU0 (*(volatile unsigned int *)(0x10490000 + 0x0100))
  ICDISER0_CPU0 |= 1;//enable cpu0_sgi0
  //5.设置中断优先级
  #define ICDIPR0_CPU0 (*(volatile unsigned int *)(0x10490000 + 0x0400))
  ICDIPR0_CPU0 &= ~0xff;
  ICDIPR0_CPU0 |= 0x23;
  //6.选择目标cpu
  #define ICDIPTR0_CPU0 (*(volatile unsigned int *)(0x10490000 + 0x0800))
  ICDIPTR0_CPU0 &= ~0xff;
  ICDIPTR0_CPU0 |= 1;//cpu0

  request_irq(0, do_sgi0, 300);

  __asm__ __volatile__("cpsie i");
}

void sgi_generate(int irq_no){
  #define ICDSGIR (*(volatile unsigned int *)(0x10490000 + 0x0F00))
  ICDSGIR = (1 << 16) | irq_no;
}

int main(void){
  page_table_create((void *)0x60000000);
  mmu_enable();

  memcpy((void *)0xffff0000, (void *)0x50000000,  50 * 4); 

  sgi_init();
  
  while(1){
    sgi_generate(0);  
    udelay(1000000);      
  }

  return 0;
}
```

## 外部中断
```c
void do_eint(struct irq_info *i){//有bug，需根据位来判断
  switch((EXT_INT43_PEND >> 2) & 0xf){
    case 1:
      printf("button0 %d\n", i->flag);
      break;
    case 2:
      printf("button1 %d\n", i->flag);
      break;
    case 4:
      printf("button2\n");
      break;
    case 8:
      printf("button3\n");
      break;
    default:
      break;
  }
  
  EXT_INT43_PEND = EXT_INT43_PEND; //清中断
}

//通过电路图 eint26-29  gpx3_2-5
void eint_init(void){
  GPX3CON |= 0xffff << 8;
  //eint43[2,3,4,5]
  EXT_INT43CON &= ~(0xffff << 8);
  EXT_INT43CON |= 0x2222 << 8;
  EXT_INT43_MASK &= ~(0xf << 2);
  EXT_INT43_PEND = EXT_INT43_PEND;

  request_irq(64, do_eint, 200);

  //gic 
  //1.使能cpu接口
  ICCICR_CPU0 = 1;
  //2.设置门槛
  ICCPMR_CPU0 = 0xff;
  //3.使能中断分配器
  ICDDCR = 1; 
  //4.使能中断
  #define ICDISER2_CPU0 (*(volatile unsigned int *)(0x10490000 + 0x0108))
  ICDISER2_CPU0 |= 1;
  //5.设置优先级
  #define ICDIPR16_CPU0 (*(volatile unsigned int *)(0x10490000 + 0x440))
  ICDIPR16_CPU0 &= ~0xff;
  //6.选择目标cpu
  #define ICDIPTR16_CPU0 (*(volatile unsigned int *)(0x10490000 + 0x840))
  ICDIPTR16_CPU0 &= ~0xff;
  ICDIPTR16_CPU0 |= 1;

  __asm__ __volatile__("cpsie i");
}

int main(void){
  page_table_create((void *)0x60000000);
  mmu_enable();

  memcpy((void *)0xffff0000, (void *)0x50000000,  50 * 4); 

  eint_init();
  
  return 0;
}
```


<script>

(function(){
    if(typeof expand_toc !== 'function') setTimeout(arguments.callee,500);
    else expand_toc('md_toc',1);
})();

</script>


<!--
ifconfig eth0 192.168.4.119
mount -t nfs -o nolock,rw 192.168.4.118:/tomcat_root /mnt

cd uboot_tiny4412/sd_fuse/tiny4412
./sd_fusing.sh /dev/sdb
sync

tools/write4412boot /media/88DE-4A63/images/Superboot4412.bin /dev/sdb

http://codepad.org/



监控 jpeg
yuv（vs rgb）压缩视频 每4个像素点存一个Y，u和v每一像素存一个
yuv420
摄像头uvc标准
工控
  omap 飞思卡尔

锁是通过硬件来实现的

gcc -m32 编译成32位
smp.c切换CPU






4412手册27章
rtc需要单独32768hz晶振(XTAL)
  寄存器使用bcd码 真实时间
  alarm寄存器 时间与真实时间一样时，则产生中断

手册其中BCDDAYWEEK BCDDAY地址反了

main 也接受 start.s中的r0 为参
main
传参不能破坏r0
链接地址 链接脚本






模数转换 adc
不支持数模转换

0v-1.8v  - - - - - >  0-0xfff


APB 133M
PCLK 就是APB 不是66M(6410的)


ADCDLY 延迟 保证采样稳定




time4
TCNT0减到0产生中断
TCMP0信号翻转
一是定时
二是产生信号



死区 用于缓冲 类似十字路口 有一段时间均为红灯















iic   eeprom
      ft5206  触摸屏
      mma7660 重力传感

多主系统
每个iic设备 7 位地址
半双工
有时钟线，波特率可变
抢主 谁先发出0谁就是主
发送数据 从高位到低位
软件寻址

内核写eeprom驱动时
  不需要理解iic驱动
  只需写eeprom driver 使用iic core中的 `i2c_transfer`
  用户态使用/dev/eeprom

USB ehci轮询
是单主系统

otg 可做主（与打印机连）可做从（与PC连）
连接前确定下来，工作中不可切换


串口 一对一
全双工
提前确定波特率 无时钟线


spi     nrf24l01 无线
线：
  MOSI
  MISO
  SCLK
  CS 片选(硬件寻址)
spi不能交叉连接



spi icc均高位先发








android
part1 18~32
part2 33~


./gen-img.sh(研究)
三个镜像
ramdisk.img
system.img
userdata.img[4 8 16g]

+内核




只有汇编可以操作内核（但C/C++直接可以编译成汇编）


ramdisk- - ->/
           /system 系统目录（用户不能uninstall）除非root后rm
           /data   家目录

c语言必须以动态库方式出现
  HAL NDK *.so

Native executable本地程序只能在命令行下运行


gperf 产生高效C++代码

out目录
  /target  arm平台
  /host    x86平台

  /taget/production/4412
  目录 －>   img
  root ramdisk
  data userdata
  system system

    
     system/app 自带软件apk
     system/framework jar包
     system/lib .so

     system/bin 部分是toolsbox提供
                其它用busybox提供


刷机
  mkfs.vfat -F 32 /dev/sdb1 -n sdname


  光盘里android_image_arch    p1
  +编译出镜像

  dd seek=1 默认输出跳过512字节 p2

  zImage p3

adb
  adb devices 看到android开发板
  adb shell [cmd]
  exit
  adb kill-server
  adb start-server


根目录在内存里
  ramdisk 在这里创建文件重启将无
> mount -o remount, rw /system
  只读分区再次挂载为读写

有自己的分区
  data
  system



@pc: abd remount 重新全部挂载成rw


adb push file /system/
adb pull /system/file ./

本地程序
arm-linux-gcc 使用 -static
否则
  androidsrc (需要android源码)
    Android.mk
    mmm /dir/to/dev
      将产生到out/../bin/
    adb push 
  ndk (add path) p4
    ndk-build
    



du -sh file
-->
