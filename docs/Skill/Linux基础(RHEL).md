> 2014-09-27

安装相关
========
## 安装事项
RHEL的经典版本：5.8和6.4

注意事项
> 从U盘安装时，GRUB引导程序默认在U盘上（`/dev/sdb`），需安装在`/dev/sda`上
>
> 新手安装时，防火墙、SElinux、kdump关闭

[Redhat网络系统安装说明](../../data/Redhat网络系统安装说明.pdf)

[老师的ule笔记.pdf](../../data/老师的ule笔记.pdf)

## Linux目录结构(FHS)
```
/           根目录
/boot       存放程序启动所必须的文件
            /boot/vmlinuz-3.2.0-61vm-generic-pae    内核文件
            /boot/grub/*                            引导程序
/var        系统中经常需要变化的一些文件
            /var/tmp 程序运行时使用的临时文件，删除可能会出错
            /var/lib;/var/lib64 库文件
            /var/log/messages   系统日志
/bin        存放系统基本用户命令，如ls,mv
/sbin       存放系统基本管理命令 s代表super，如fdisk,ip
/usr        存放系统大量的应用程序
            /usr/bin     用户命令
            /usr/sbin    管理命令
/etc        存放系统和各种程序的配置文件
            /etc/init.d  服务启动
/dev        设备文件
            ls /dev/sd*  查看所有硬盘及分区
/lib        库文件，驱动，由glibc提供
            /lib64       64位的库文件
            /usr/lib     各distribute维护的库文件
            /usr/local/lib   程序或用户创建的库文件
/tmp        临时文件
/media      光盘的默认挂载点
            /media/cdrom
/mnt        其它的挂载点
/proc       进程文件(pid)，虚拟文件系统
            du -sh /proc 统计大小为0，表示数据在内存中，不占硬盘空间
/sys        用来代替/proc的
/opt        主机额外安装软件所放的目录
/srv        一些服务启动后，这些服务所需访问的数据目录

```

## 显示系统信息
```shell
uname -a -r
lsb_release -a     #发布版本
getconf LONG_BIT   #查看操作系统位数

cat /etc/*-release
cat /proc/version
cat /proc/cupinfo
cat /proc/meminfo
cat /proc/interrupts
```

## 分区设备
```
IDE硬盘
  hda   a表示第1个       a~d
  hda1  1表示第一个分区  1~63

SCSI硬盘
  sda   a表示第1个       a~p
  sda1  1表示第一个分区  1~15 最多4个主分区或3个主分区1个扩展分区
```
使用`ls /dev/hd*`，`ls /dev/sd*`查看

## 分区建议
```
/boot ext3 200M
      swap 4096M
/home ext3 看情况（个人资料）
/usr  ext3 看情况（程序数据）
/     ext3 看情况
```

> 要记得 `/lib` 不可以与 `/` 分别放在不同的 partition

使用`sudo fdisk -l`可查看硬盘分区(partition)情况，`df -h`查看文件系统使用情况，`du -sh /path/to` 统计指定目录的大小

### 分区与格式化
```shell
parted /dev/sdb

fdisk /dev/sdb
  l  #列出分区类型
  p  #显示
  d  #删除
  n  #创建 1扇区512字节，1柱8M
  t  #改变分区类型
  w  #保存退出

mkfs -t ext3 /dev/sdb1
mkfs.vfat -F 32 /dev/sdb1  #格式化分区，不能格式化设备
sync  #确保格式化完成
```

## 快捷键
```
ctrl alt F1~F6     图形界面切换到字符界面
ctrl F7            字符界面切换到图形界面
ctrl shift +       放大窗口
ctrl -             缩小窗口
ctrl shift t       新建窗口
alt <num>          切换窗口
快捷复制            鼠标左键选中即复制 鼠标按中键即粘贴

ctrl l             清屏 或clear命令
ctrl c             中止任务执行
ctrl z             任务转至后面，挂起状态
ctrl a             shell中输入命令时，光标跳到最前
ctrl e             shell中输入命令时，光标跳到最后
ctrl u             shell中输入命令时，删除一行

ctrl s             暂停屏幕输入
ctrl q             恢复屏幕输入
ctrl d             退出终端

```

### history
```shell
!16                #运行history中第16行记录
!cd                #运行history中最近的cd命令
!!                 #运行history中上次命令
ctrl r             #进入history搜索
esc .              #使用上次命令的参数
alt .              #引用上次命令的参数，一直按. 继续向上查找参数
```

## 帮助
```shell
<command> --help
          #查找ls命令手册中有关时间与排序的条目
          ls --help|grep -E "time|sort"

man       #man是分章节的
           # 1 User Commands
           # 2 System Calls
           # 3 C Library Functions
           # 4 Devices and Special Files
           # 5 File Formats and Conventions
           # 6 Games et. Al.
           # 7 Miscellanea
           # 8 System Administration tools and Deamons
           # 3p posix手册
          #查找fopen的使用，在第3章节查找
          man 3 fopen
          #查询所有含有passwd的帮助文件
          man -k passwd

          #操作同less
          #space下一页；b上一页；enter下一行；q退出；G最后；g最前
          #?<keyword>查找光标之前；/<keyword>查找光标之后
          #n下一个关键字；shift n上一个关键字

          #将man手册转存为文本
          man ls |col -b >ls.txt  #col -b 过滤掉所有的控制字符

info <command>
          #将info手册转存为文本
          info make -o make.txt -s


```

## 启动过程
- 加载 BIOS 的硬件资讯与进行自我测试，并依据配置取得第一个可启动的装置；
- 读取并运行第一个启动装置内 MBR 的 boot Loader (亦即是 `grub`, `spfdisk` 等程序)；
- 依据 boot loader 的配置加载 Kernel ，Kernel 会开始侦测硬件与加载驱动程序；
- 在硬件驱动成功后，Kernel 会主动呼叫 `init` 程序，而 `init` 会取得 run-level 资讯；
- `init` 运行 `/etc/rc.d/rc.sysinit` 文件来准备软件运行的作业环境 (如网络、时区等)；
- `init` 运行 run-level 的各个服务之启动 (script 方式)；
- `init` 运行 `/etc/rc.d/rc.local` 文件；
- `init` 运行终端机模拟程序 `mingetty` 来启动 `login` 程序，最后就等待使用者登录啦；

runlevel:

- 0 - halt (系统直接关机)
- 1 - single user mode (单人维护模式，用在系统出问题时的维护)
- 2 - Multi-user, without NFS (类似底下的 runlevel 3，但无 NFS 服务)
- 3 - Full multi-user mode (完整含有网络功能的纯文字模式)
- 4 - unused (系统保留功能)
- 5 - X11 (与 runlevel 3 类似，但加载使用 X Window)
- 6 - reboot (重新启动)


## 关机
```shell
shutdown -h now   #关机
init 0            #也是关机,不推荐

reboot            #重启
```

文件管理
========
## 路径
```shell
pwd       #查看当前路径
cd        #回到自己home
cd~       #回到自己home
cd ~jack  #去jack的home
cd-       #切到上次目录
```

## 查看
```shell
ls
    -a    #显示所有文件，包含隐藏文件
          ls -a| sort -i     #名称排序显示
    -l    #显示详细信息，别名为ll
          #显示的 -rwx rw- --- 第一个是文件类型
          #普通- 目录d 块设备b 字符设备c 符号链接l 套接字s 管道p
    -F    #显示后缀 目录/ 符号链接@ 套接字= 管道| 可执行*

    -t    #以修改时间顺序排列查询结果
    -ut   #以访问时间顺序排列查询结果
    -ct   #以属性修改时间顺序排列查询结果
    -X    #以后缀名排序
    -S    #以文件大小排序
    -r    #逆向排序

    --time=atime|ctime

    -1    #单列显示
    -h    #人性化显示
    -i    #显示inode号
    -d    #只显示目录信息
          ls -d */       #只显示目录
          ls -ld /<dir>  #可以看到该目录的访问权限,不加d可能直接deny
    -R    #递归显示目录结构
    -F    #目录以/结尾显示
    --full-time
ls -l / | grep tmp #只看某项


cat
    -n    #给文件所有行编号
    -A    #控制字符都显示
    -s    #把多个空白行合并为一个空白行
          #使文件清空，但所有者和权限不变
          cat /dev/null > a.txt
          #列出两个文件的内容.执行对输出的搜索.统计结果行的个数
          cat file1 file2 | grep word | wc -1

od        #查看特殊格式的文件内容。通过指定该命令的不同选项可以以十进制、八进制、十六进制和ASCII码来显示文件
    -A    #指定地址基数(最左侧一栏），包括：
     d    #十进制
     o    #八进制（系统默认值）
     x    #十六进制
     n    #不打印位移值

    -t    #指定数据的显示格式，主要的参数有(除了选项c都可以跟一个十进制数n，指定每个显示值所包含的字节数)：
     c    #ASCII字符或反斜杠序列
     d    #有符号十进制数
     f    #浮点数
     o    #八进制（系统默认值为02）
     u    #无符号十进制数
     x    #十六进制数

          #od -Ax -tcx1 file.txt
          #echo /etc/passwd |od
          >0000000 062457 061564 070057 071541 073563 005144
          >0000014

          #echo /etc/passwd |od -A x -x
          >000000 652f 6374 702f 7361 7773 0a64
          >00000c

          #echo /etc/passwd |od -A x -t x1
          >000000 2f 65 74 63 2f 70 61 73 73 77 64 0a
          >00000c

          #echo /etc/passwd |od -A x -t x1 -t c    #常用 2个十六进制为一个字节
          >000000  2f  65  74  63  2f  70  61  73  73  77  64  0a
                    /   e   t   c   /   p   a   s   s   w   d  \n
          >00000c

          #系统先以十六进制并以小端表示数据，如ab表示为6261，然后再依次换算成对应的十进制25185或八进制061141

xxd
          #echo /etc/passwd |xxd
          >0000000: 2f65 7463 2f70 6173 7377 640a            /etc/passwd.

          #echo /etc/passwd |xxd -g1               #常用
          >0000000: 2f 65 74 63 2f 70 61 73 73 77 64 0a              /etc/passwd.

          #echo "0000000: 2f 65 74 63 2f 70 61 73 73 77 64 0a" |xxd -r
          >/etc/passwd

          #echo /etc/passwd |xxd -b
          >0000000: 00101111 01100101 01110100 01100011 00101111 01110000  /etc/p
          >0000006: 01100001 01110011 01110011 01110111 01100100 00001010  asswd.

          #echo /etc/passwd |xxd -c4
          >0000000: 2f65 7463  /etc
          >0000004: 2f70 6173  /pas
          >0000008: 7377 640a  swd.

          #echo /etc/passwd |xxd -i
          >0x2f, 0x65, 0x74, 0x63, 0x2f, 0x70, 0x61, 0x73, 0x73, 0x77, 0x64, 0x0a

          #xxd -i file.txt
          >unsigned char file_txt[] = {
            0x2f, 0x65, 0x74, 0x63, 0x2f, 0x70, 0x61, 0x73, 0x73, 0x77, 0x64, 0x0a
          };
          unsigned int file_txt_len = 12;

          #echo /etc/passwd |xxd -p
          >2f6574632f7061737377640a

hexdump
          #echo /etc/passwd |hexdump
          >0000000 652f 6374 702f 7361 7773 0a64
          >000000c

          #echo /etc/passwd |hexdump -C            #常用
          >00000000  2f 65 74 63 2f 70 61 73 73 77 64 0a              |/etc/passwd.|
          >0000000c

          #还原文件
          for buff in $(cat a.hex |cut -c10-58) ; do printf "\\x$buff"; done > a.txt
          awk '{for(i=2;i<=17;i++) printf "%c",strtonum("0X"$i)}' a.hex > a.txt

echo -e "\x68\x65\x6c\x6c\x6f"   #16进制转换到字符串

less      #分屏，可前翻
          #space下一页；b上一页；enter下一行；q退出；G最后；g最前
          #?<keyword>查找光标之前关键字；/<keyword>查找光标之后
          #n下一个关键字；shift n上一个关键字
more      #分屏，翻到最后直接退出，无法前翻

tail
    -f    #实时监控
head

tree      #树形显示目录
    -a    #显示所有 文件
    -d    #只显示 目录
    -f    #显示全路径
    -h    #人性化
    -C    #颜色
    -L    #层级
fdisk -l  #查看硬盘分区情况
du        #显示当前 目录 中 各子目录 占磁盘大小
    -s    #显示当前 目录 占磁盘大小
    -h    #人性化显示
    -a    #包括 文件
    --max-depth=1  #设置显示深度
df        #查看文件系统使用情况
    -h    #人性化显示
          #查看某目录所属硬盘
          df /<path> -h

nl        #向文件添加行号
wc        #统计行数，字符，字节
rev       #左右相反
tac       #cat相反
fmt       #把文本格式化成指定宽度
pr        #给文件分页 ,把文本文件转换为标有页码的版本
fold      #把输入行换行，以适应指定的宽度

stat      #文件信息查看
file      #查看文件属性
getfacl   #查看文件权限
```

## 查找
```shell
grep "<key>" <path/to/file>
    --color  #高亮
    -n       #显示行号
    -r       #递归

    -E, --extended-regexp     PATTERN is an extended regular expression (ERE)
    -F, --fixed-strings       PATTERN is a set of newline-separated fixed strings
    -G, --basic-regexp        PATTERN is a basic regular expression (BRE)
    -P, --perl-regexp         PATTERN is a Perl regular expression

    -v, --invert-match        select non-matching lines(不匹配的)
    #将配置文件中注释行和空行去掉显示
    cat /etc/dhcpd/dhcpd.conf | grep -v "^#" | grep -v "^$"

    grep "key" ./*  #查找当前目录所有文件

find <path>
    -name "pattern"
    -size +1000M
    #查找指定类型的文件，然后指定按时间排序
    find . -name *.php |xargs ls -alt
    ls -alt $(find . -name *.php)
    ls -alt `find . -name *.php`
    #统计所有c文件的行数总和，不包括空行
    find . -name "*.c" | xargs cat | grep -v ^$ | wc -l
    find . -name "*.c" | xargs cat | sed '/^$/d' | wc -l

    -i               #llignore
    -o               #or
    !                #not

du -mh --max-depth=1 |sort -nr  #查找大文件，一层层往下查
```

## 创建
```shell
touch    #已创建的不会被清空，但会更新访问时间

mkdir
         #创建多个目录
         mkdir dir1 dir2
    -p   #创建层次目录
         mkdir -p aa/bbb/ccc

ln       #创建硬连接
    -s   #创建符号连接
```

## 复制
```shell
cp <src> <dest>
    -r   #recursive，实现同时拷贝文件和文件夹
    -f   #force，强制覆盖
    -v   #verbose
    -i   #ineractive
    -a   #权限也复制

watch du <target> -h -d 0 #通过不停的监视目标目录的大小来确定复制进度
```

## 移动
```shell
mv <src> <dest>     #需要重命名，只需在同目录下执行就行

find -type f|grep 'jpg'|xargs rename 's/\.jpg$/\.png/'  #批量重命名
```

## 删除
```shell
rm       #安全的删除，建议先进入目录后再删除
    -r   #recursive
    -f   #force
rm -rf /etc/yum.repos.d/*    #清空目录
rm -rf /etc/yum.repos.d/     #删除目录
```

## 归档压缩
归档压缩其实是两个步骤，常用选项说明

```shell
-c   #create
-v   #verbose
-z   #gzip
-j   #bzip2
-f   #file指定文件
-x   #extract
```

- 归档

```shell
tar cvf ab.tar a b c dfile
```

- 解包

```shell
tar xvf ab.tar [-C /path]
```

- 压缩

```shell
gzip a b c dfile  #文件是分开压缩的
bzip2
```

- 解压

```shell
gunzip a.gz
bunzip2 a.bz2
```

- 归档压缩

```shell
tar cvzf ab.tar.gz a b c dfile
tar cvjf ab.tar.bz2 a b c dfile
```

- 解压解包

```shell
tar xvzf ab.tar.gz
tar xvjf ab.tar.bz2
```

软件安装
========

## RPM安装
软件包名，指安装时的文件名，而软件名，指系统中识别的名称
### 挂载镜像
```shell
mount -o loop /path/to/rhel.iso /mnt
```
> iso文件，即iso9660，这是光盘所使用的一种文件系统

```shell
ls /mnt/Packages
```
将看到许多`.rpm`的文件，通常格式如`<软件名>.<版本>.<OS>.<CPU>.rpm`，其中

- OS：el5,el6
- CPU：i386~i686(32位),x86_64(64位),noarch(通用)

### 安装
```shell
rpm -ivh <软件包名>
    -i      #install
    -vh     #显示安装过程信息
    --force #强制安装
```
不需要指定安装目录，默认安装于`/usr`（分区时最好单独分出来）

### 查询
- 查询已安装的软件包`-q`

```shell
rpm -qa | grep vnc   #模糊查询
rpm -q gcc           #明确知道软件名
```

- 查询软件安装位置`-l`

```shell
rpm -ql tigervnc
```

- 查询文件所属软件，方便根据文件找到软件 再安装，或根据命令找到程序`-f`

```shell
rpm -qf /path/to/file
```

- 查询已安装软件详细信息`-i`

```shell
rpm -qi <软件名>（不是包）
```

### 删除
```shell
rpm -e <软件名>（不是包）
    -e       #erase
    --nodeps #不查看依赖性关系删除，防止缺失文件不能删除
```
实在卸载不了时，可强制安装`--force`，再删除

## YUM安装
### 配置源
```shell
rm -rf /etc/yum.repos.d/*      #清空目录
vim /etc/yum.repos.d/yum.repo  #以.repo结尾
```

键入如下信息

```
[rhel6]
name=rhel6
baseurl=file:///mnt/Server
enabled=1
gpgcheck=0
```

一个文件中可存在多个五行，从上往下依次查找安装，`enabled＝0`则不查找该源

### 安装
```shell
yum -y install <软件名>  #可带通配符
yum -y groupinstall <软件组名> #如：通用桌面
```

### 查询
```shell
yum repolist
yum list        #第三列是yum源名字时，说明没装上
yum grouplist
yum search <keyword>
```

### 卸载
```shell
yum -y remove
yum -y erase
```
### 使用163源
> rhel6中使用163的centos源

```shell
wget http://mirrors.163.com/centos/6/os/x86_64/Packages/python-iniparse-0.3.1-2.1.el6.noarch.rpm
wget http://mirrors.163.com/centos/6/os/x86_64/Packages/yum-metadata-parser-1.1.2-16.el6.x86_64.rpm
wget http://mirrors.163.com/centos/6/os/x86_64/Packages/yum-3.2.29-60.el6.centos.noarch.rpm
wget http://mirrors.163.com/centos/6/os/x86_64/Packages/yum-plugin-fastestmirror-1.1.30-30.el6.noarch.rpm

rpm -aq|grep yum|xargs rpm -e --nodeps

rpm -ivh python-iniparse-0.3.1-2.1.el6.noarch.rpm
rpm -ivh yum-metadata-parser-1.1.2-16.el6.x86_64.rpm
rpm -ivh yum-3.2.29-60.el6.centos.noarch.rpm yum-plugin-fastestmirror-1.1.30-30.el6.noarch.rpm

wget http://mirrors.163.com/.help/CentOS6-Base-163.repo
mv CentOS6-Base-163.repo /etc/yum.repos.d/
vim /etc/yum.repos.d/CentOS6-Base-163.repo
  :%s/\$releasever/6/g
  :wq

yum clean all
yum makecache
yum update     #升级所有包，改变软件设置和系统设置,系统版本内核都升级
yum -y upgrade #升级所有包，不改变软件设置和系统设置，系统版本升级，内核不改变
```


## RPM vs YUM
- 两者都安装`.rpm`结尾的软件
- rpm不解决依赖关系，优先使用
- yum解决依赖关系，自动安装，需要配置源，在64位机器上默认不查找32位的软件，特殊情况下可手工rpm安装需要的软件

## 编译安装
### 安装
利用命令将源代码的包（如`.tar.gz`,`.tar.bz2`）进行解压解包

```shell
./configure --prefix=<path/to/setup>  #建议指定，删除时方便
                                      #否则分散在usr/locals各子目录
                                      #此步骤将产生配置文件
make          #编译
make install  #安装
```

### 启动
手动安装的一般在`usr/locals`目录下，如httpd，此时应该在`/usr/local/apache2`，通过`/usr/local/apache2/bin/apachectl start`来启动

### 删除
直接删除由`--prefix`指定的目录

## apt-get安装
ubuntu中使用`apt-get`

```shell
apt-cache search package 搜索包
apt-cache show package 获取包的相关信息，如说明、大小、版本等
sudo apt-get install package 安装包
sudo apt-get install package=version 安装指定版本
apt-show-versions -p packagename 查看当前特定软件版本
sudo apt-get install package - - reinstall 重新安装包
sudo apt-get -f install 修复安装"-f = ——fix-missing"
sudo apt-get remove package 删除包
sudo apt-get remove package - - purge 删除包，包括删除配置文件等
sudo apt-get update 更新源
sudo apt-get upgrade 更新已安装的包
sudo apt-get dist-upgrade 升级系统
sudo apt-get dselect-upgrade 使用 dselect 升级
apt-cache depends package 了解使用依赖
apt-cache rdepends package 是查看该包被哪些包依赖
sudo apt-get build-dep package 安装相关的编译环境
apt-get source package 下载该包的源代码
sudo apt-get clean && sudo apt-get autoclean 清理无用的包
sudo apt-get check 检查是否有损坏的依赖

dpkg -i file.deb  直接利用包管理器安装包
```

当出现`E: Sub-process /usr/bin/dpkg returned an error code (1)`

```shell
sudo mv /var/lib/dpkg/info /var/lib/dpkg/info.bak #现将info文件夹更名
sudo mkdir /var/lib/dpkg/info                     #新建一个info文件夹
sudo apt-get update
```

[更新源](http://wiki.ubuntu.org.cn/%E6%BA%90%E5%88%97%E8%A1%A8)

更新后需要`sudo apt-get update`

不能成功时，删除`/var/lib/apt/lists/partial/`下的失败项

## 搜索程序
```shell
which          #定位一个命令，搜索磁盘上命令，不能找到内置命令
whereis        #定位一个命令的二进制、源文件、手册

type           #查看是否是内置命令

apropos        #查看相关名字命令的说明 同man -k
whatis         #查看相关名字命令的说明

locate         #搜索文件，需要配置/etc/updatedb.conf（运行updatedb）
slocate

ldd            #列出程序的动态依赖关系 ldd /bin/cp
```

## curl使用
```shell
curl http://www.linuxidc.com

#指定输出文件
curl -o page.html http://www.linuxidc.com
#指定代理
curl -x 123.45.67.89:1080 -o page.html http://www.linuxidc.com
#保存cookie
curl -x 123.45.67.89:1080 -o page.html -D cookie0001.txt http://www.linuxidc.com
#使用cookie
curl -x 123.45.67.89:1080 -o page1.html -D cookie0002.txt -b cookie0001.txt http://www.linuxidc.com
#指定referer
curl -A "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)" -x 123.45.67.89:1080 -e "mail.linuxidc.com" -o page.html -D cookie0001.txt http://www.linuxidc.com

#下载文件
curl -O http://cgi2.tky.3web.ne.jp/~zzh/screen1.JPG
#文件名匹配下载
curl -O http://cgi2.tky.3web.ne.jp/~zzh/screen[1-10].JPG
#下载多个目录下的文件
curl -O http://cgi2.tky.3web.ne.jp/~{zzh,nick}/[001-201].JPG

#302跟踪
curl -L -O http://download.savannah.gnu.org/releases/nmh/nmh-1.1-RC4.tar.gz

#断点续传，比如我们下载screen1.JPG中，突然掉线了，我们就可以这样开始续传
curl -c -O http://cgi2.tky.3wb.ne.jp/~zzh/screen1.JPG
#分块下载
curl -r 0-10240 -o "zhao.part1" http:/cgi2.tky.3web.ne.jp/~zzh/zhao1.mp3 &\
curl -r 10241-20480 -o "zhao.part1" http:/cgi2.tky.3web.ne.jp/~zzh/zhao1.mp3 &\
curl -r 20481-40960 -o "zhao.part1" http:/cgi2.tky.3web.ne.jp/~zzh/zhao1.mp3 &\
curl -r 40961- -o "zhao.part1" http:/cgi2.tky.3web.ne.jp/~zzh/zhao1.mp3

cat zhao.part* > zhao.mp3

#ftp下载
curl -u name:passwd ftp://ip:port/path/file
curl ftp://name:passwd@ip:port/path/file

#上传文件
curl -T localfile -u name:passwd ftp://upload_site:port/path/                #ftp
curl -T localfile http://cgi2.tky.3web.ne.jp/~zzh/abc.cgi                    #http put

#提交表单
curl -d "user=nickwolfe&password=12345" http://www.linuxidc.com/login.cgi    #http post

#表单中上传文件
curl -F upload=@localfile -F nick=go http://cgi2.tky.3web.ne.jp/~zzh/up_file.cgi


-G --get get请求
-I 取得head信息
-F --form表单提交
    -F description='aa'
    -F media=@test.jpg #上传文件
-d --data 提交数据
    -d '{"media_id":"61224425"}' #json数据
    -X POST --data "data=xxx" example.com/form.cgi #表单
    -X POST --data-urlencode "date=April 1" example.com/form.cgi
    -G --data-urlencode "port=4546" --data-urlencode "content=content" example.com/form.cgi #url编码
-H --header 请求时加入头部信息
    -H "Host:man.linuxde.net" -H "accept-language:zh-cn"
-i --include 输出时带出header
--cookie "user=root;pass=123456"
    --cookie-jar cookie_file #cookie在文件中
-A "Mozilla/5.0"
    --user-agent "Mozilla/5.0"
-k 允许不使用证书到SSL站点
-o [文件名] #相当于wget
-L 自动跳转到新网址
-v 显示一次http通信的整个过程，包括端口连接和http request头信息
    --trace output.txt www.sina.com
    --trace-ascii output.txt www.sina.com
-X http动词
    -X POST
```

用户管理
========
## 创建
```shell
useradd <username>
useradd -u <uid> <username>
useradd -g <gid> <username>             #创建时指定主属组
useradd -G <gid>[,<gid>...] <username>  #创建时指定附属组
```

## 创建sudo用户
```shell
sudo adduser rootzyx
sudo adduser rootzyx sudo
sudo usermod -aG sudo rootzyx
```

## 查看
```shell
id <username>
```

出现类似`uid=502(jim) gid=502(jim) 组=502(jim),0(root)`

- uid:user identify,数字，可能出现uid相同，但用户名不同的情况，以uid为准
- gid:group identify,数字
- 组:主属组+附属组,数组，通过`usermod -G root jim`给jim设置 __附属组__
> 但可能会使得以前执行过的`gpasswd -a`命令失效

```shell
cat /etc/passwd | grep <username>

```

出现类似`jim:x:502:502::/home/jim:/bin/bash`的信息，依次为

- 用户名
- 密码占位，删除后用户就没密码，虽然不能改密码，但能置空密码（可通过删除root的此信息，达到进入root账户）
- uid
- gid
- 描述字段
- 家目录
- 登录shell

> `/etc/shadow`才是真正存储密码的地方

## 修改
```shell
usermod -u <uid> <username>   #修改用户id
usermod -g <gid> <username>   #修改用户主属组
usermod -G <gid>[,<gid>...] <username>   #修改用户附属组
```

## 切换用户
```shell
su - <username>  #加载环境变量 如.profile
su <username>    #不会加载环境变量，不推荐使用
```
同理，在arm开发中，出现`-/bin/sh /path/to/script`中的`-`，也是用于加载环境设置的


## 设置密码
```shell
passwd [<username>]   #不加<username>给自己重设
                      #root用户能设置简单的密码，其他用户不行
```

## 删除账户
```shell
userdel -r <username>
        -r #家目录删除
```

## 查看登录信息
实时的登录

```shell
whoami
who
w
ps u
users

```

登录日志

```shell
last <username> <tty>
finger <username>
```

发信息

```shell
write <username> <tty>
wall
```

审核登录用户

```
who /var/log/wtmp 
```

组管理
======
添加账户时，就会产生一个同名的组，这个组称为用户的 __主属组__

## 添加组
```shell
groupadd <groupname>
```

## 查看组
```shell
cat /etc/group
```
格式为`组名:组密码占位（目前无用）:gid:组员（数组）`

## 切换组
```shell
newgrp <groupname>  #临时切换到用户的某个附属组，exit退出
```

## 添加用户进组
```shell
gpasswd -a <username> <groupname>
```

## 删除用户出组
```shell
gpasswd -d <username> <groupname>
```

## 删除组
```shell
groupdel <groupname>
```

文件权限
=========
## 查看
```shell
ls -l <file>
```

得到`- rwx rw- ---`，第一个字符表示文件类型: 普通- 目录d 块设备b 字符设备c 符号链接文件l 套接字文件s 管道文件p；剩下的分成三组，简称`ugo`权限：第一组代表user权限；第二组代表group权限；第三组代表others权限

## 修改
```shell
chmod u-x a.txt
chmod g+x a.txt
chmod o+w a.txt
chmod u-x,g+x,o+w a.txt
chmod u+w-x a.txt
```
以数字方式修改 read:r=4 write:w=2 excute:x=1

```shell
chmod 744 a.txt
```
> 对于root用户，x权限同属主，rw的设置是无效的，依然能读能写

### suid
表示设置文件在 __执行阶段__(权限仅对二进位程序(binary program)有效，不能够用在 shell script 上面) 具有 __文件所有者__ 的权限

[参考](http://vbird.dic.ksu.edu.tw/linux_basic/0220filemanager_4.php#suid)

如`ll /bin/ping`，得到`-rwsr-xr-x`，其中`s`就是`suid`，普通用户也是能使用`ping`的(此处为root)的权限

如普通用户无法通过`cat`查看`/ect/shadow`，但修改了`cat`的权限`chmod u+s /bin/cat`后，就可以了

### sgid
[参考](http://vbird.dic.ksu.edu.tw/linux_basic/0220filemanager_4.php#sgid)

如`ll /usr/bin/locate`，得到`-rwx--s--x`，其中`s`就是`sgid`

- 对二进制程序，运行者在运行过程中将会获得该程序群组的支持，上面普通用户将得到`slocate`群组支持
- 针对目录
  + 使用者若对於此目录具有 r 与 x 的权限时，该使用者能够进入此目录
  + 使用者在此目录下的有效群组(effective group)将会变成该目录的群组
  + 若使用者在此目录下具有 w 的权限(可以新建文件)，则使用者所创建的新文件，该新文件的群组与此目录的群组相同。

### skicky
[参考](http://vbird.dic.ksu.edu.tw/linux_basic/0220filemanager_4.php#sbit)

只针对 __目录__ 有效，当使用者在该目录下创建文件或目录时，仅有自己与 root 才有权力删除该文件

## 修改文件所属者/组
间接修改了权限

```shell
chown <username> <file>   #修改文件所属者
chown .<groupname> <file> #修改文件所组，前面加点
chown <username>:<groupname> <file> #同时修改文件所属者与组
chgrp <groupname> <file>  #修改文件所组
```


进程控制
========
## 查看进程
```shell
ps      #当前终端上进程
   a    #所有终端上进程，-a则为只显示非终端上进程
   ax   #所有进程，包括非终端上进程
   aux  #把进程启动的用户(及起始时间)包含进来
   e    #显示shell环境信息
   f    #格式化父子进程的显示
   l    #较长、较详细的将该 PID 的的资讯列出
   j    #job的格式
   axjf #连同部分程序树状态

ps -l
   #F：代表这个程序旗标 (process flags)，说明这个程序的总结权限
       #4 表示此程序的权限为 root;
       #1 则表示此子程序仅进行复制(fork)而没有实际运行(exec)
   #S：代表这个程序的状态 (STAT)，主要的状态有
       #R (Running)：该程序正在运行中；
       #S (Sleep)：该程序目前正在睡眠状态(idle)，但可以被唤醒(signal)。
       #D ：不可被唤醒的睡眠状态，通常这支程序可能在等待 I/O 的情况(ex>列印)
       #T ：停止状态(stop)，可能是在工作控制(背景暂停)或除错 (traced) 状态；
       #Z (Zombie)：僵尸状态，程序已经终止但却无法被移除至内存外。
   #UID/PID/PPID：代表『此程序被该 UID 所拥有/程序的 PID 号码/此程序的父程序 PID 号码』
   #C：代表 CPU 使用率，单位为百分比；
   #PRI/NI：Priority/Nice 的缩写，数值越小代表该程序越快被 CPU 运行
   #ADDR/SZ/WCHAN：
       #ADDR 是 kernel function，指出该程序在内存的哪个部分，如果是个 running 的程序，一般就会显示『 - 』
       #SZ 代表此程序用掉多少内存
       #WCHAN 表示目前程序是否运行中，同样的， 若为 - 表示正在运行中
   #TTY：登陆者的终端机位置，若为远程登陆则使用动态终端介面 (pts/n)；
   #TIME：使用掉的 CPU 时间，注意，是此程序实际花费 CPU 运行的时间，而不是系统时间；
   #CMD：就是 command 的缩写，造成此程序的触发程序之命令为何

ps aux
   #USER：该 process 属於那个使用者帐号的？
   #PID ：该 process 的程序识别码。
   #%CPU：该 process 使用掉的 CPU 资源百分比；
   #%MEM：该 process 所占用的实体内存百分比；
   #VSZ ：该 process 使用掉的虚拟内存量 (Kbytes)
   #RSS ：该 process 占用的固定的内存量 (Kbytes)
   #TTY ：该 process 是在那个终端机上面运行，若与终端机无关则显示 ?，
          #tty1-tty6 是本机上面的登陆者程序，若为 pts/0 等等的，则表示为由网络连接进主机的程序。
   #STAT：该程序目前的状态，状态显示与 ps -l 的 S 旗标相同 (R/S/T/Z)
   #START：该 process 被触发启动的时间；
   #TIME ：该 process 实际使用 CPU 运行的时间。
   #COMMAND：该程序的实际命令为何？

pstree
   -p   #列出每个 process 的 PID
   -u   #列出每个 process 的所属帐号名称
```

## 查看运行时系统状态
```shell
top
   -d   #后面可以接秒数，就是整个程序画面升级的秒数。默认是 5 秒；
   -n   #与 -b 搭配，意义是，需要进行几次 top 的输出结果
   -p   #指定某些个 PID 来进行观察监测而已

vmstat
   -a   #使用 inactive/active(活跃与否) 取代 buffer/cache 的内存输出资讯；
   -f   #启动到目前为止，系统复制 (fork) 的程序数；
   -s   #将一些事件 (启动至目前为止) 导致的内存变化情况列表说明；
   -S   #后面可以接单位，让显示的数据有单位。例如 K/M 取代 bytes 的容量；
   -d   #列出磁碟的读写总量统计表
   -p   #后面列出分割槽，可显示该分割槽的读写总量统计表
   #procs
        #r ：等待运行中的程序数量
        #b：不可被唤醒的程序数量
        #这两个项目越多，代表系统越忙碌 (因为系统太忙，所以很多程序就无法被运行或一直在等待而无法被唤醒之故)。
   #memory
        #swpd：虚拟内存被使用的容量；
        #free：未被使用的内存容量；
        #buff：用於缓冲内存；
        #cache：用於高速缓存。
        #这部份则与 free 是相同的。
   #swap
        #si：由磁碟中将程序取出的量；
        #so：由於内存不足而将没用到的程序写入到磁碟的 swap 的容量。
        #如果 si/so 的数值太大，表示内存内的数据常常得在磁碟与主内存之间传来传去，系统效能会很差！
   #io
        #bi：由磁碟写入的区块数量；
        #bo：写入到磁碟去的区块数量。
        #如果这部份的值越高，代表系统的 I/O 非常忙碌！
   #system
        #in：每秒被中断的程序次数；
        #cs：每秒钟进行的事件切换次数；
        #这两个数值越大，代表系统与周边设备的沟通非常频繁！ 这些周边设备当然包括磁碟、网络卡、时间钟等。
   #cup
        #us：非核心层的 CPU 使用状态；
        #sy：核心层所使用的 CPU 状态；
        #id：闲置的状态；
        #wa：等待 I/O 所耗费的 CPU 状态；
        #st：被虚拟机器 (virtual machine) 所盗用的 CPU 使用状态 (2.6.11 以后才支持)。

vmstat -a <延迟> <总计侦测次数> #CPU/内存等资讯
vmstat -fs                     #内存相关
vmstat -S <单位>               #配置显示数据的单位
vmstat -d                      #与磁碟有关
vmstat -p <分割槽>             #与磁碟有关

free    #内存空间
   -m   #字节单位为M
   -t   #在输出的最终结果，显示实体内存与 swap 的总量

```


## 杀死进程
```shell
ps aux | grep <keyword>         #查到进程pid
ps aux | egrep '(cron|syslog)'  #找出与 cron 与 syslog 这两个服务有关的PID
pidof sshd                      #查找sshd的进程pid

kill -9 <pid>
```

`kill -l` 列出所有信号：

- -9 强制
- -15 默认
- -19 挂起
- -18 唤醒

```shell
w               #看到所有登录系统的账户，查看是否异常
killall -9 sshd #杀死进程名称为sshd的进程，
                #即把所有通过ssh登录到系统的账户登出

pkill -9 httpd  #杀死进程名称为httpd的进程
```

## 后台任务
- 在命令尾处键入`&`把作业发送到后台
- 也可以把正在运行的命令发送到后台运行，首先键入`Ctrl+Z`挂起作业（此时是挂起状态），然后键入`bg`移动后台继续执行
- `bg %jobnumber` 或`bg %name`
- `fg %jobnumber` 把后台作业带到前台来
- `kill -18 pid` 也是唤醒
- `kill %jobnumber` 删除后台作业
- `jobs -l`将PID显示 `-r`运行中显示 `-s`显示停止
- `disown %jobnumber`从后台列表中移除任务，并没有终止
- `nohup command &` 如果你正在运行一个进程，而且你觉得在退出帐户时该进程还不会结束，那么可以使用`nohup`命令。该命令可以在你退出帐户之后继续运行相应的进程。


Linux其它
==========
## 重定向
```shell
>           #输出重定向 1> 的简写
            ls > /dev/null  #丢掉输出
            ls > /dev/pts/2 #输出到另一个终端
>>          #输出重定向追加
2>          #错误重定向
2>>         #错误重定向追加

&>          #标准与错误一起重新向
            ls > 0.txt 2>&1  #同上
>> 2>>      #标准与错误一起重新向追加

<           #输入重定向
            cat < /dev/zero -A

<<          #输入重定向，并定义结束符
            cat << EOF  #打开文件缓冲区，输入完后，最后输入'EOF'

            #下载ftp上内容，这类 交互性 的东西也可以写成脚本
            lftp 192.168.1.245 << EOF
             > get somefile
             > EOF

tee         #在管道过程中产生分支
            grep -v "a" file | tee file1 | grep -v "b" file

xargs
            find . -name *.php |xargs ls -alt
            #等同于
            ls -alt $(find . -name *.php)

            -n 能确定命令使用的参数个数,下面一次传递一个参数
            ls *.php | xargs -n 1 ls -alt

```

> `except`可用于写交互性的脚本

## 环境变量
```shell
env     #查看当前用户的环境变量
```

一般情况下，环境变量由以下几个文件顺序进行加载

- `/etc/profile`
    - `/etc/profile.d/*.sh`
- `~/.bash_profile`
    - `~/.bashrc`
        - `/etc/bashrc`

非登录shell情况如 `su tom`，先

- `~/.bash_profile`
    - `~/.bashrc`
        - `/etc/bashrc`

然后`/etc/profile.d/*.sh`

没有`/etc/profile`

```shell
vim /etc/profile
export LC_ALL=zh_CN.GB18030       #设置语言信息
export PS1='\u@\h:\w\$'           #修改命令行提示符

vim /etc/sysconfig/i18n
LANG="zh_CN.GB18030"              #当前系统的语言环境变量设置
SUPPORTED="zh_CN.GB18030:zh_CN:zh:en_US.UTF-8:en_US:en"  #系统支持哪些字符集
SYSFONT="latarcyrheb-sun16"       #系统终端字符的字体

yum install "@Chinese Support"
```

设置时区与同步时间

```shell
cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
ntpdate cn.pool.ntp.org
```

## Shell相关
```shell
alias                             #查看别名，别名的优先级高
    alias la="ls -a"              #设置别名

unalias la                        #取消别名
\<command>                        #不使用别名时，直接使用原始命令

<command1>&&<command2>            #顺序执行，前面的不出错，后面的才执行
<command1>||<command2>            #顺序执行，前面的出错，后面的才执行
<command1>;<command2>             #顺序执行，不管前面结果，后面照样执行

{}                                #命令的展开
                                  mkdir dir{5..8}
                                  mkdir dir{a..d}
                                  mkdir dir{a,d}
                                  #相当于括号外面 * 括号里现
                                  cp /abc{0,1}  #cp /abc0 /abc1

#保持不变，防止shell翻译
                                  touch "a b"
                                  touch a\ b
                                  touch a' 'b

echo -n                           #不换行，默认换行
echo -e "a\tb\tc"                 #翻译转义，否则原样输出

echo ${PAGER:-more}               #如果变量PAGER定义则其非空，则使用，否则使用字符串more

```

## Shell脚本
```shell
$1~$9                #位置变量
$*                   #具体参数数组，同$@
$#                   #共几个参
$$                   #PID
$?                   #上次命令执行的返回值，0为正常，非0为异常

test                 #if后面的条件都是 test 条件，可简写成 [ .. ]
    -f               #是否是文件
    -r               #是否可读
    -w               #是否可写
    -u               #是否具有suid
    -ot              #是否比某文件旧
    -gt              #数字比较 great than
    -a               #and

for((i=1;i<255;i++)); do
  ping -c1 192.168.1.$i > /dev/null 2>&1
  if [ $? -eq 0 ]; then
    echo "192.168.1.$i is running"
  fi
done

#双重[[ .. ]] 解决单层 [ .. ] 不能逻辑运算和正则匹配的问题
[[ !cmd ]]
[[ cmd && cmd ]]
[[ cmd || cmd ]]
[[ $z =~ "o" ]]

```

## 数学运算
```shell
bc
                                  # echo "(6+3)*2" |bc
                                  # echo "3+4;5*2;5^2;18/4" |bc
                                  # echo "scale=2;15/4" |bc
                                  # echo "ibase=16;A7" |bc
                                  # echo "ibase=2;11111111" |bc
                                  # echo "ibase=16;obase=2;B5-A4" |bc
                                  # bc calc.txt

expr
                                  # expr 6 + 3
                                  > 9
                                  # expr 2 /* 3    （有转义符号）
                                  > 6

                                  # a=3
                                  # expr $a+5      （无空格）
                                  > 3+5
                                  # expr $a + 5    （有空格）
                                  > 8
                                  # expr length "abc"
                                  > 3
                                  # expr substr "abcdefgh" 2 3  (从1开始计数)
                                  > bcd
                                  # expr index "abcdef" cd      (从1开始计数)
                                  > 3

echo
                                  # echo $((3+5))
                                  > 8
                                  # x=2;y=3
                                  # echo $(($x+$y))
                                  > 5
                                  # echo $x+$y | bc
                                  > 5
                                  # echo $[$x+$y]
                                  > 5

let
                                  # let x=$x+1
                                  # echo $x
                                  > 3

akw
                                  # awk 'BEGIN{a=3+2;print a}'
                                  > 5
                                  # awk 'BEGIN{a=(3+2)*2;print a}'
                                  > 10
```


## 杂项
```shell
mount -l                          #查看目前所有挂载
mount /dev/sdb /media             #挂载U盘、光盘
      /dev/sr0 /mnt
umount /dev/sdb                   #取消挂载U盘
                                  #多取消几次 防止被多次挂载了
sudo fdisk -l | grep NTFS         #挂载ntfs的u盘
mount -t ntfs-3g <NTFS Partition> <Mount Point>

sed -n '5,10p' /etc/passwd        #只查看文件的第5行到第10行。
uniq                              # -d 只显示重复的行 -u 只显示唯一的行
sort names | uniq -d              #显示在names文件中哪些行出现了多次
     -r                           #正常排序的反序
     -n                           #按数字次序排序
     -f                           #大小写混合在一起排序


tr                                #翻译
                                  #转换大小写
                                  cat /etc/passwd | tr [a-z] [A-Z]
                                  #计算
                                  echo "1 2 3 4 5" | tr " " "+" | bc
                                  #删除文件file中出现的换行'\n'、制表'\t'字符
                                  cat file | tr -d "\n\t" > new_file
                                  #删除空行 -s 删除所有重复出现字符序列，只保留第一个；即将重复出现字符串压缩为一个字符串。
                                  cat file | tr -s "\n" > new_file
                                  #把路径变量中的冒号":"，替换成换行符"\n"
                                  echo $PATH | tr -s ":" "\n"

dd                                #快速创建大文件
                                  #dd if=/dev/zero of=test bs=1M count=1000
                                  #创建空洞文件
                                  #dd if=/dev/zero of=test bs=1M count=0 seek=100000
                                  #把第一个硬盘的前 512 个字节存为一个文件：
                                  dd if=/dev/hda of=disk.mbr bs=512 count=1
                                  #修复硬盘(直接使用标准IO导致I/O错误时)
                                  dd if=/dev/sda of=/dev/sda


split                             #按行数或字节数拆分文件
csplit                            #由正则来分割文件

strip                             #将编译链接的可执行文件进行剪切，去掉头部信息，通过nm将不能查看到稳中各种符号

locale                            #查看系统当前locale环境变量

lsusb                             #检查USB

iwconfig                          #检测无线
iwlist

stty -echo                        #禁止回显
stty echo                         #打开回显

stty igncr                        #忽略回车符
stty -igncr                       #恢复回车符


insmod
rmmod
lsmod
dmesg

taskset                           #将进程分配给指定的CPU执行


mknod <filenm> c 80 0

debian kernel api has doc

sudo dpkg-reconfigure gdm
sudo /etc/init.d/lightdm start
echo exec gnome-session > ~/.xinitrc
sudo /etc/init.d/gdm start        #代替startx
```


网络配置
========
[常用网络命令](http://vbird.dic.ksu.edu.tw/linux_server/0140networkcommand_1.php)

## 查看网卡
```shell
ifconfig eth0
ip addr show      #或简写成 ip add sh
```

## 启动网卡
```shell
ifconfig eth0 up
ifconfig eth0 down
ifdown eth0
ifup eth0
```

## 临时设置网卡
```shell
ifconfig eth0 <ip> netmask <ip> up
ip addr add <ip> netmask 255.255.255.0 dev eth0
ip addr add <ip/24> dev eth0    #等同于上面，24个1（二进制）即255.255.255.0

ifconfig eth0:0 192.168.50.50   # eth0:0 那就是在该实体网卡上，再仿真一个网络接口，一张网络卡上面设定多个 IP
```

## 查看网关
```shell
route -n
ip route show
```

## 临时设置网关
```shell
route add default gw <ip>
```

## 临时设置DNS
```shell
vim /etc/resolv.conf

nameserver 202.106.0.46 #最多三个wh

#查询域名对应ip
host baidu.com
nslookup baidu.com
dig baidu.com
```

## 永久的网络设置
```shell
vim /etc/sysconfig/network-scripts/ifcfg-eth{0,1..}

ONBOOT                      #是否启用网卡
NM_CONTROLLED               #是否受networkmanager(gui)控制
BOOTPROTO=dhcp|none|static  #获取ip方式

NETMASK=255.255.255.0
PREFIX=24

GETEWAY
DNS1
DNS2
```

## 重启网卡
```shell
service network restart
```

## ubuntu下设置
```shell
sudo vim /etc/network/interfaces

    # The primary network interface
    auto eth0
    iface eth0 inet static
    address 192.168.3.90
    gateway 192.168.3.2
    netmask 255.255.255.0
    network 192.168.3.0
    broadcast 192.168.3.255

sudo /etc/init.d/networking restart

sudo nm-connection-editor & #图形化配置
```

## 其它
```shell
lsof -i:80                    #查看80端口是否启动
mii-tool eth0                 #eth0网卡是否有效
ping <ip>
    -c1                       #ping一个包

netstat -ntlp
    -n                        #以网络IP地址代替名称，显示出网络连接情形
    -t                        #显示TCP协议的连接情况，-u是UDP
    -l                        #正在listening的
    -p                        #显示程序名字
    -a                        #将目前系统上所有的连线、监听、Socket 数据都列出来

service iptables stop         #关闭防火墙
iptables -F                   #关闭防火墙
setenforce 0                  #关闭SElinux

nslookup <domain>             #根据域名查看ip，附带检查dns效果

system-config-network         #GUI方式配置，RHEL6有问题
                              #可把它关闭`/etc/init.d/NetWorkManager stop`
```

查看指定端口

```
# 查看哪些进程打开了指定端口port（对于守护进程必须以root用户执行才能查看到）
lsof -i:<port>

# 查看哪些进程打开了指定端口port，最后一列是进程ID（此方法对于守护进程作用不大）
netstat -nap|grep <port>

sudo lsof -i tcp:80  #查看占用80端口的进程
sudo netstat -an | grep 80 #查看80端口是否被监听
sudo netstat -anp tcp | grep smbd  #查看smbd占用端口号
```

> 常用服务端口号，可通过`grep 3306 /etc/services`查看某端口的服务，小于1024的端口要启动时，启动者身份必须是root才行

> - tcp
>>   - ftp-data 20
>>   - ftp 21
>>   - ssh 22
>>   - telnet 23
>>   - smtp 25
>>   - dns 53
>>   - http 80
>>   - pop3 110
>>   - https 443
>
> - udp
>>   - dhcp 67 68


> windows下网络配置查看
>
> `ipconfig [/release] [/renew] [/all]`

## 服务的防火墙
任何以 xinetd 管理的服务，都可以透过 `/etc/hosts.allow`, `/etc/hosts.deny`来配置防火墙，它们也是 `/usr/sbin/tcpd` 的配置文件，这两个文件的判断依据是allow为优先

基本上只要一个服务受到 xinetd 管理，或者是该服务的程序支持 TCP Wrappers 函式的功能时，那么该服务的防火墙方面的配置就能够以 `/etc/hosts.{allow,deny}` 来处

```shell
ldd $(which sshd httpd)
#有无支持tcp wrappers需要看是否依赖libwrap.so
#sshd 有支持，但是 httpd 则没有支持
```

例：只允许 140.116.0.0/255.255.0.0 与 203.71.39.0/255.255.255.0 这两个网域，及 203.71.38.123 这个主机可以进入我们的 rsync 服务器；此外，其他的 IP 全部都挡掉！

```shell
vim /etc/hosts.allow
rsync:  140.116.0.0/255.255.0.0
rsync:  203.71.39.0/255.255.255.0
rsync:  203.71.38.123
rsync:  LOCAL

vim /etc/hosts.deny
rsync: ALL  #利用 ALL 配置让所有其他来源不可登陆
```


服务配置
========
## daemon守护进程
相关目录

- `/etc/init.d/*`启动脚本放置处
- `/etc/sysconfig/*`各服务的初始化环境配置文件
- `/etc/xinetd.conf`, `/etc/xinetd.d/*`super daemon 配置文件
- `/etc/*`各服务各自的配置文件
- `/var/lib/*`各服务产生的数据库
- `/var/run/*`各服务的程序之 PID 记录处

## 查看所有服务
```shell
#找出目前系统开启的『网络服务』有哪些
netstat -tulp

#找出所有的有监听网络的服务 (包含 socket 状态）
netstat -lnp

#观察所有的服务状态
service --status-all
service --status-all | grep httpd
```

## 开机启动服务
`chkconfig`： 管理系统服务默认启动启动与否

```shell
#列出目前系统上面所有被 chkconfig 管理的服务
chkconfig --list |more

#显示出目前在 run level 3 为启动的服务
chkconfig --list | grep '3:on'

#让 atd 这个服务在 run level 为 3, 4, 5 时启动：
chkconfig --level 345 atd on
```


## SSH
代替了telnet，后者通信时使用明文，不安全，另外也不能使用root用户登录
### 安装
```shell
yum install -y *openssh*
```
### 启动
```shell
service sshd start      #redhat专有
/etc/init.d/sshd start  #linux通用，并可借助tab得到智能感知
```

### 登录
```shell
ssh <username>@<ip>        #如果不写<username>，默认是root用户

#设置rsa以后连接时，不需要再输入密码
ssh-keygen                 #产生密钥对
ssh-copy-id -i <sshhostip> #输入相应登录密码后，将放置对方 /.ssh/authorized_keys中

```

> 出现ssh连接"Host key verification failed ... The authenticity of host can't be established"

```shell
vim /etc/ssh/ssh_config
  StrictHostKeyChecking no
  UserKnownHostsFile /dev/null
```

> 有关加密
>
> - 对称加密（机密性）：des 3des aes rc4/5；算法简单，适合大量加密
> - 单向加密（完整性）：md5 sha1 sha2；算法简单，不占用计算资源。又称哈希加密，具有不可逆，定长输出，雪崩效应，对应的shell命令有`md5sum` `sha1sum` `sha224sum`等
> - 非对称加密（身份认证，密钥传输）：rsa dsa；不适合大量加密，有公钥和私钥，公钥是私钥中的一部分
>> - 身份认证：自己用私钥加密，发送给他人，他人用公钥解密，可保证发送人的身份有效，又称数字签名
>> - 密钥传输：他人用公钥加密 对称加密用的密钥，传输给具有私钥的人，保证密钥不被窃取
>>> - 还可以使用密钥交换，又称IKE技术（dh算法）

### 远程拷贝
```shell
scp <file> <self_ip>:/path
```

## TFTP
arm板开发时会使用，平时意义不大
### 安装
```shell
yum install *tftp* -y
```
### 配置
```shell
vim /etc/xineted.d/tftp
```

- 其中`server_args = -s /var/lib/tftpboot`表示下载的目录，`-s`表示能下载，`-c`表示能上传
- 其中` disable = yes`改成`no`表示开启服务

为了防止权限问题，可执行

```shell
chmod 777 /var/lib/tftpboot -R
```

### 启动
```shell
chkconfig tftp on       #未修改配置的启动方式
service xineted restart #修改过配置文件后启动方式
```

如果怕安全机制影响，可执行

```shell
service iptables stop  #关闭防火墙
setenforce 0           #关闭SElinux
```

### 客户端连接
```shell
tftp <ip>       #进入命令提示符
 > get <file>   #指定名字，默认下载到当前目录
 > put <file>   #默认上传当前目录中文件
```

## VSFTPD
### 安装
```shell
yum install -y lftp    #客户端
yum install -y vsftpd  #服务器端
```

### 配置
修改文件夹权限

```shell
chmod 777 -R /var/ftp
```

修改配置文件

```shell
vim /etc/vstftpd/vstftpd.conf
```

找到`anon_upload_enable=yes`和`anon_mkdir_write_enable=yes`，前者表示可上传文件，后者表示可上传目录，需要时，可以去掉注释

### 启动
```shell
service vsftpd start
```
### 客户端连接
```shell
lftp <ip>  #进入命令提示符
 > ls                           #可浏览
 > get <file> -o /path/to/file  #下载到指定目录
 > put /path/to/file            #上传指定目录中文件
 > mirror <dir> /path/to/dir    #下载目录
 > mirror -R /path/to/dir       #上传目录
```

## NFS
全称为network file system
> ext3(linux) fat32(windows) ntfs(windows) 均是本地文件系统；cifs (samba协议）共享文件系统，用于windows与linux共享文件；nfs是linux间使用的共享文件系统

### 安装
```shell
yum install -y nfs-utils
yum install -y rpcbind
```

### 配置
```shell
vim /etc/exports
```

可以文件中指定共享的描述，如

`/tmp *(rw,async,no_root_squash)`，分别代表对于该目录，可读写，异步传输，取消root的权限压制

也可以描述为`/tmp <ip>[</网段>]`表示只对某ip网段才能访问

### 启动
```shell
service nfs restart
service rpcbind restart
```
### 客户端挂载
客户端也需要启动上述的服务，然后使用`mount`进行挂载

```shell
mount -t nfs <ip>:/tmp /opt
```

## DHCP
### 安装
```shell
yum install -y dhcp
```

### 配置
```shell
vim /etc/dhcp/dhcpd.conf

subnet 172.24.40.0 netmask 255.255.255.0{
    range 172.24.40.100 172.24.40.200;
    option routers 172.24.40.254;             #getway
    option domain-name "uplooking.com";
    option domain-name-servers 202.106.0.46;  #dns
}
```

### 启动
```shell
/etc/init.d/dhcpd start
```

### 客户端续约
```shell
dhclient eth0
```

## DNS
### 概述
FQDN是完全限定域名，准备的描述出主机所在的位置。DNS是倒置的树状结构的 分布式 数据库系统，存储着FQDN名和ip地址的对应关系，负责它们之间的解析

一个局域网内最好只有一个DNS

> 客户端存放DNS主机IP的配置在`/etc/resolv.conf`

### 安装
```shell
yum install -y bind
```

### 配置
```shell
vim /etc/named.conf       #负责domain <-> zonefile
vim /var/named/xxx.zone   #负责subdomain <-> ip
```

### 启动
```shell
/etc/init.d/bind start
```

## SAMBA
samba的用户名必须与Linux系统的用户名一致，但密码可以不同，即必须先有linux的用户，然后使用`smbpasswd -a <username>`增加同名用户

### 配置
`/etc/samba/smb.conf`

```
[global]
  workgroup = WORKGROUP
  display charset = UTF-8
  unix charset = UTF-8
  dos charset = cp936
[Public]
  path = /home/zyx/Public
  available = yes
  browseable = yes
  public = yes
  writable = yes
  valida users = zyx
  create mask = 0664
  directory mask = 0775
  force user = zyx
  force group = zyx
```

Linux常用简介
==================
## Linux文件管理命令
- `ls` 显示文件名
- `cat` 显示文本文件内容
- `rm` 删除文件
- `less` 分屏显示文件
- `cp` 复制文件
- `mv` 更改文件名
- `grep` 查找字符串
- `head` 显示文件头部
- `tail` 显示文件尾部
- `sort` 按顺序显示文件内容
- `uniq` 忽略文件中的重复行
- `diff` 比较两个文件
- `diffstat` diff结果的统计信息
- `file` 测试文件内容
- `echo` 显示文本
- `date` 显示日期和时间
- `script` 记录Linux会话信息
- `apropos` 搜索关键字
- `locate` 搜索文件
- `rmdir` 删除目录
- `chattr` 改变文件的属性
- `cksum` 文件的CRC校验
- `cmp` 比较文件差异
- `split` 分割文件
- `dirname` 显示文件除名字外的路径
- `find` 查找目录或者文件
- `findfs` 通过列表或用户ID查找文件系统
- `ln` 链接文件或目录
- `lndir` 链接目录内容
- `lsattr` 显示文件属性
- `od` 输出文件内容
- `paste` 合并文件的列
- `stat` 显示inode内容
- `tee` 读取标准输入到标准输出并可保存为文件
- `tmpwatch` 删除临时文件
- `touch` 更新文件目录时间
- `tree` 以树状图显示目录内容
- `umask` 指定在建立文件时预设的权限掩码
- `chmod` 设置文件或目录的访问权限
- `chgrp` 改变文件或目录所属的群组
- `chown` 改变文件的拥有者或群组
- `more` 查看文件的内容
- `md` sum：MD5函数值计算和检查
- `awk` 模式匹配语言
- `wc` 输出文件中的行数、单词数、字节数
- `comm` 比较排序文件
- `join` 将两个文件中指定栏位内容相同的行连接起来
- `fmt` 编排文本文件
- `tr` 转换字符
- `col` 过滤控制字符
- `colrm` 删除指定的行
- `fold` 限制文件列宽
- `iconv` 转换给定文件的编码
- `dc` 任意精度的计算器
- `expr` 求表达式变量的值
- `strings` 显示文件中的可打印字符
- `xargs` 从标准输入读入参数
- `sum` 计算文件的校验和，以及文件占用的块数
- `setfacl` 设定文件访问控制列表
- `getfacl` 获取文件访问控制列表
- `chacl` 更改文件或目录的访问控制列表

## Linux磁盘管理命令
- `df` 显示报告文件系统磁盘使用信息
- `du` 显示目录或者文件所占的磁盘空间
- `dd` 磁盘操作
- `fdisk` 磁盘分区
- `mount` 挂载文件系统
- `umount` 卸载文件系统
- `mkfs` 建立各种文件系统
- `mkfs` ext2：建立一个Ext2/Ext3文件系统
- `mkbootdisk` 建立启动盘
- `fsck` 检查文件系统
- `blockdev` 从命令行调用区块设备控制程序
- `hdparm` 设置磁盘参数
- `mkswap` 建立交换分区
- `swapon` 使用交换空间
- `swapoff` 关闭系统交换分区
- `sync` 写入磁盘
- `e` label：设置卷标
- `badblocks` 检查磁盘
- `quota` 显示磁盘已使用的空间与限制
- `quotacheck` 检查磁盘的使用空间与限制
- `quotaoff` 关闭磁盘空间限制
- `quotaon` 开启磁盘空间限制
- `quotastats` 显示磁盘空间限制
- `repquota` 检查磁盘空间限制的状态
- `mdadm` RAID设置工具
- `tune` fs：文件系统调整
- `mkisofs` 建立ISO 9660映象文件
- `cfdisk` 磁盘分区
- `sfdisk` 硬盘分区工具程序
- `parted` 磁盘分区工具
- `mkinitrd` 建立要载入ramdisk的映象文件
- `ssm` 命令行集中存储管理工具
- 使用xfs管理命令
- LVM命令列表

## Linux进程管理命令
- `accton` 打开或关闭进程统计
- `lastcomm` 显示以前使用过的命令的信息
- `sa` 报告、清理并维护进程统计文件
- `at` 定时运行命令
- `atq` 显示目前使用at命令后待执行的命令队列
- `atrm` 删除at命令中待执行的命令队列
- `batch` 在系统负载水平允许的时候执行命令
- `bg` 后台运行命令
- `fg` 挂起程序
- `jobs` 显示后台程序
- `kill` 杀掉进程
- `crontab` 设置计时器
- `ps` 查看权限
- `pstree` 显示进程状态树
- `top` 显示进程
- `nice` 改变优先权等级
- `renice` 修改优先权等级
- `sleep` 暂停进程
- `nohup` 用户退出系统之后继续工作
- `pgrep` 查找匹配条件的进程
- `fuser` 用文件或者套接口表示进程
- `chkconfig` 设置系统的各种服务
- `strace` 跟踪一个进程的系统调用或信号产生的情况
- `ltrace` 跟踪进程调用库函数的情况
- `vmstat` 报告虚拟内存统计信息
- `mpstat` 监测CPU（包括多CPU）性能
- `iostat` 监测I/O性能
- `sar` 系统活动情况报告
- `pidof` 查找正在运行进程的进程ID（PID）
- `ntsysv` 设置系统服务

## Linux网络管理命令
- `arp` 管理系统中的ARP高速缓存
- `arpwatch` 监听ARP记录
- `arping` 发送ARP请求到一个相邻主机
- `arpd` 收集免费arp信息的一个守护进程
- `finger` 查找并显示用户信息
- `ifconfig` 设置网络接口
- `iwconfig` 设置无线网卡
- `iw` 新一代无线网络配置工具
- `hostname` 显示主机名
- `ifup` 激活网络设备
- `ifdown` 禁用网络设备
- `mii` tool：调整网卡模式
- `route` 设置路由表
- `netstat` 查看网络连接
- `ping` 检测主机的连通性
- `minicom` 设置调制解调器
- `pppd` 建立PPP连接
- `pppstats` 显示PPP连接状态
- `chat` 拨号命令
- `traceroute` 检查数据包所经过的路由
- `tracepath` 追踪连接到目标地址所经过的路由
- `rcp` 远程复制
- `tcpdump` 网络数据分析器
- `ipcalc` IP地址计算器
- `netreport` 监视网络状态
- `ip` 网络集成命令工具
- `pppoe` setup：设置ADSL
- `pppoe` start：激活ADSL连接
- `pppoe` stop：断开ADSL连接
- `pppoe` status：检测ADSL连接状态
- `wget` 下载文件
- `ngrep` 监控网络接口
- `lsof` 查看打开的文件
- `ethtool` 查询及设置网卡参数
- `netconf` 设置各项网络功能
- `tc` 显示和维护流量控制设置
- `telnet` 远程登录
- `rlogin` 远程登录命令
- `rsh` 远程登录的Shell
- `usernetctl` 让普通用户控制网络接口
- `nmcli` NetworkManager命令行网络接口配置工具
- `nmtui` 基于Curses的用户界面nmtui
- `nc` netcat，Linux下用于调试和检查网络的工具包
- `lnstat` 显示Linux系统的网络状态
- `ss` 显示网络状态信息
- `rexec` 在指定的远程Linux系统主机上执行命令

## Linux用户管理命令
- `useradd` 建立用户
- `userdel` 删除用户
- `usermod` 修改已有用户的信息
- `passwd` 设置密码
- `chage` 密码老化
- `groupadd` 添加组
- `groupdel` 删除组账户
- `groupmod` 修改组
- `vipw` 编辑/etc/passwd文件
- `vigr` 编辑/etc/group文件
- `newgrp` 转换组
- `groups` 显示组
- `gpasswd` 添加组
- `whoami` 显示当前用户名称
- `who` 显示登录用户
- `id` 显示用户信息
- `su` 切换身份
- `pwck` 检测账户
- `grpck` 检测用户组账号信息的完整性
- `chsh` 设置Shell
- `chfn` 修改用户信息
- `ac` 显示用户在线时间的统计信息
- `grpconv` 开启群组的投影密码
- `grpunconv` 关闭群组的投影密码
- `lastlog` 显示最近登录用户的用户名、登录端口和登录时间
- `logname` 显示当前用户的名称
- `users` 显示当前登录到系统的用户
- `lastb` 显示登录系统失败用户的相关信息

## Linux的备份和压缩命令
- `tar` 备份文件
- `dump` 备份文件系统
- `cpio` copy in/out）：建立、还原备份文件
- `restore` 还原备份下来的文件或整个文件系统（一个分区）
- `bunzip` ：解压缩.bz2文件
- `bzip` ：解压缩.bz2文件
- `bzgrep` 使用正则表达式搜索.bz2压缩包中的文件
- `unzip` 解压缩.zip文件
- `bzip` recover：修复损坏的.bz2文件
- `gzip` 压缩文件
- `compress` 压缩、解压文件
- `gzexe` 压缩执行文件
- `lha` 压缩或解压缩文件
- `unarj` 解压缩文件
- `zip` 压缩文件
- `zipinfo` 显示压缩文件的信息

## Linux系统管理命令
- `apmd` 高级电源管理
- `apmsleep` APM进入休眠状态
- `apropos` 查找使用手册的名字和相关描述
- `arch` 输出主机的体系结构
- `alias` 设置别名
- `cd` 切换目录
- `clear` 清空终端屏幕
- `clock` 系统RTC时间设置
- `cal` 显示日历
- `chroot` 改变根目录
- `date` 显示或设置系统时间
- `dmesg` 显示开机信息
- `dircolors` 设置ls命令在显示目录或文件时所用的色彩
- `depmod` 分析模块
- `echo` 显示文本行
- `exec` 执行完命令后交出控制权
- `exit` 退出Shell
- `eject` 弹出介质
- `enable` 启动或关闭Shell命令
- `fc` 修改或执行命令
- `fgconsole` 显示虚拟终端的数目
- `free` 显示内存信息
- `fwhois` 显示用户的信息
- `getty` 设置终端模式
- `gitps` 显示程序情况
- `logwatch` 可定制和可插入式的日志监视系统
- `logsave` 把一个命令的输出输出到一个指定的日志文件中
- `GRUB` 引导加载程序
- `halt` 关闭系统
- `history` 显示历史命令
- `hwclock` 显示与设定硬件时钟
- `init` 进程处理初始化
- `last` 显示登录用户信息
- `lilo` 引导管理器
- `login` 登录系统
- `local` 显示本地支持的语言系统信息
- `logout` 退出系统
- `logrotate` 处理Log文件
- `lsmod` 显示Linux内核的模块信息
- `man` 格式化和显示在线手册
- `manpath` 设置man手册的查询路径
- `modinfo` 显示内核信息
- `modprobe` 自动处理可载入模块
- `pmap` 显示程序的内存信息
- `procinfo` 显示系统状态
- `pwd` 显示工作目录
- `reboot` 重新启动系统
- `rlogin` 远程登录
- `rmmod` 删除模块
- `rpm` 软件包管理
- `shutdown` 令：系统关机命令
- `suspend` 暂停执行Shell
- `nproc` 打印当前进程可用的处理器数
- `tload` 显示系统负载
- `uname` 显示系统信息
- `authconfig` 配置系统的认证信息
- `declare` 显示或者设定Shell变量
- `export` 设置或者显示环境变量
- `hostid` 打印出当前主机的标识
- `insmod` 载入模块
- `rdate` 显示其他主机的日期与时间
- `runlevel` 显示执行等级
- `set` 设置Shell
- `setenv` 查询或显示环境变量
- `setserial` 设置或显示串口的相关信息
- `setup` 设置公用程序
- `symlinks` 维护符号链接的工具程序
- `swatch` 系统监控程序
- `sync` 将内存缓冲区内的数据写入磁盘
- `startx` 启动X Window
- `sysctl` 设置系统核心参数
- `timeconfig` 设置时区
- `ulimit` 控制Shell程序的资源
- `unalias` 删除别名
- `unset` 删除变量或函数
- `up` date：软件包升级
- `uptime` 告知系统运行了多长时间
- `mouseconfig` 设置鼠标相关参数
- `bind` 显示或设置键盘按键及其相关的功能
- `kbdconfig` 设置键盘类型
- `snapscreenshot` 命令行截图
- `mt` 磁带机控制
- `cdrecord` CD刻录工具
- `dvdrecord` DVD刻录工具
- `lspci` 查看硬件插槽
- `sane` find-scanner：扫描仪搜索
- `scanimage` 检测扫描仪型号
- `mtools` 命令集
- `whereis` 查找文件
- `ytalk` 与其他用户交谈
- `apt` 软件包在线管理
- `yum` 在线管理软件包
- `vlock` 锁定终端
- `wait` 等待程序返回状态
- `watch` 将结果输出到标准输出设备
- `rsync` 远程数据同步工具
- `&` 将任务放在后台执行
- `screen` 多重视窗管理程序
- `lsb` release：显示LSB和特定版本的相关信息
- `lscpu` 查看 CPU 信息
- `blkid` 查看块设备
- `journalctl` 日志管理
- `lsblk` 列出块设备
- `systemd` 服务管理命令组
- `GRUB2`

## Linux服务器管理命令

### DNS服务器管理命令
- `named` 域名服务器管理命令
- `rndc` DNS服务器控制
- `named` checkconf：检查DNS配置
- `named` checkzone：检查区域文件的合法性
- `dig` 发送域名查询信息包到域名服务器
- `nslookup` 交互式查询名称服务器
- `host` 使用域名服务器查询主机名字
- `dnssec` keygen：DNSSEC密钥生成工具
- `dnssec` signkey：DNSSEC密钥集签名工具
- `dnssec` makekeyset：DNSSEC区域签名工具
- `dnssec` signzone：DNSSEC区域签名工具
- `dlint` Bind DNS服务器辅助工具
- `dnstop` Bind DNS服务器辅助工具

### NFS服务器管理命令
- `nfsd` 启动停止NFS服务器
- `portmap` 将RPC程序号转换为因特网端口号
- `rpcinfo` 报告远程过程调用（RPC）服务器的状态
- `showmount` 显示远程已安装文件系统的所有客户机的列表
- `umount` 删除当前已挂载的远程文件系统
- `mount` 将已命名的文件系统连接到指定的挂载点
- `automount` 安装自动安装点
- `mountall` 挂载一组文件系统
- `exportfs` 重新分享/etc/exports变更的目录资源

### Samba服务器管理命令
- `testparm` 检查smb.conf配置文件的内部正确性
- `smbd` samba daemon)：Samba服务器程序
- `smbclient` 类似FTP操作方式的访问SMB/CIFS服务器资源的客户端
- `smbstatus` 报告当前Samba的连接状态
- `smbmount` 装载一个smbfs文件系统
- `smbpasswd` 设置用户的SMB密码

### SSH服务器管理命令
- `sshd` OpenSSH守护进程
- `ssh` keygen：生成、管理和转换认证密钥
- `ssh` SSH命令行登录工具
- `sftp` 安全互动FTP
- `scp` 将文件复制到远程主机或本地主机
- `squid` 代理服务器squid守护进程

### DHCP服务器管理命令
- `dhcpd` DHCP服务器守护进程
- `dhclient` DHCPv6客户端守护进程
- `dhcp` c：DHCPv6客户端守护进程

### E-mail服务器管理命令
- `sendmail` 为本地或网络交付传送邮件
- `mail` E-mail管理程序
- `mailq` 显示待寄邮件的清单
- `mailstats` 显示关于邮件流量的统计信息
- `mutt` 电子邮件管理程序

### Linux防火墙管理工具iptables和firewalld
- `iptables` Linux防火墙管理工具
- `ip` tables：IPv6版本的iptables工具
- `iptables` save：iptables列表存储
- `iptables` restore：装载由iptables-save保存的规则集
- `firewall` cmd：下一代防火墙管理工具
- `arptables` 管理ARP包过滤的软件

### SELinux管理命令
- `setenforce` 设置SELinux模式
- `getenforce` 查看SELinux模式
- `setsebool` 设置SELinux布尔值
- `getsebool` 查看SELinux布尔值
- `togglesebool` 翻转SELinux布尔值
- `sestatus` SELinux状态查看工具
- `avcstat` 显示AVC统计信息
- `audit` why：转换审计消息
- `audit` allow：生成策略允许规则
- `load` policy：装载策略
- `semanage` 管理SELinux策略
- `semodule` 管理策略模块
- `chcat` 改变语境类别
- `restorecon` 恢复文件安全语境
- `chcon` 改变文件安全语境
- `setfiles` 设置文件安全语境
- `seinfo` 提取策略的规则数量统计信息
- `sesearch` 搜索policy.conf或二进制策略中特别的类型
- `checkmodule` 编译策略模块
- `sealert` SELinux信息诊断客户端工具
- `selinuxenabled` 查询系统的SELinux是否启用


### 虚拟化管理命令
- `xen` 拟化管理命令
- KVM/Qemu虚拟机管理命令

## Linux打印管理命令
- `cupsd` 通用打印程序守护进程
- `cupsaccept` 指示打印系统接受发往指定目标打印机的打印任务
- `lpadmin` 配置LP打印服务
- `lp` 打印文件
- `lpstat` 显示行式打印机的状态信息
- `lpr` 排队打印作业
- `lprm` 从打印队列中删除任务
- `lpc` 控制打印机
- `lpq` 检查假脱机队列
- `lpinfo` 显示驱动和设备
- `lpmove` 将作业从一个队列移动到另一个队列
- `cancel` 取消已存在的打印任务
- `cupsdisable` 禁用指定的打印机或类
- `cupsreject` 指示打印系统拒绝发往指定目标打印机的打印任务
- `cupsenable` 启动指定的打印机

## Linux库应用命令
- `ldconfig` 配置查找共享库
- `nm` 列举目标文件中的符号名
- `ar` 建立修改文件或从文件中抽取成员
- `strip` 去除目标文件中的无用信息
- `objdump` 展开目标文件、静态库和共享库中的信息
- `ldd` 显示共享库的依赖情况
- `patch` 令：修补文件
- `ld` 连接器

## Linux开发应用命令
- `as` 标准GNU汇编程序
- `nasm` 汇编器
- `gcc` C/C++编译器
- `make` 维护和编译软件或软件包
- `gdb` GUN调试器
- `gdbserver` 远端GNU服务器
- `autoconf` 产生配置脚本
- `autoheader` 为configure产生模板头文件
- `autoreconf` 更新已经生成的配置文件
- `autoscan` 产生初步的configure.in文件
- `autoupdate` 更新configure.in文件
- `automake` 自动生成Makefile.in的工具
- `aclocal` 生成aclocal.m4文件
- `configure` 生成Makefile文件


Vim编辑器
=========
## 模式切换
任何模式，多按几次`ESC`即进入`命令模式`：

- `v`进入`可视模式`
- `Shift v`进入`可视行模式`
- `Ctrl v`进入`可视块模式`
- `： /`进入`提示符模式`
- `i o a`等进入`插入模式`


## 命令模式
多按几次`ESC`即进入命令模式，以下操作均在命令模式下进行

### 光标移动
```shell
h              光标向左移动一个字符
20h            光标向左移动20个字符
l              光标向右移动一个字符

j              光标向下移动一行
20j            光标向下移动20行
k              光标向上移动一行

Ctrl + f       屏幕『向下』移动一页，相当于 [Page Down]按键 #(常用)
Ctrl + b       屏幕『向上』移动一页，相当于 [Page Up] 按键 #(常用)

n[Space]       光标会向后面移动 n 个字符距离
n[Enter]       光标向下移动 n 行 #(常用)

G              移动到这个档案的最后一行 #(常用)
nG             移动到这个档案的第 n 行 #(常用)
gg             移动到这个档案的第一行，相当于 1G 啊！ #(常用)

```

### 定位单词
```
w              到下一个单词的开头  #(常用)
e              到下一个单词的结尾  #(常用)
b              到前一个单词的开头  #(常用)

%              匹配括号移动，包括 (, {, [    需要把光标先移到括号上 #(常用)
* 和 #         匹配光标当前所在的单词，移动光标到下一个（或上一个）匹配单词  #(常用，可用查找配合使用)

0              到行头
^              到本行的第一个非blank字符
$              到行尾
fa             到下一个为a的字符处，你也可以fs到下一个为s的字符。
t,             到逗号前的第一个字符。逗号可以变成其它字符。
3fa            在当前行查找第三个出现的a。
F 和 T         和 f 和 t 一样，只不过是相反方向。

dt"            删除所有的内容，直到遇到双引号(组合用法)

```

### 编辑操作
```shell
x              在一行字当中，x 为向后删除一个字符 (相当于 [del] 按键) #(常用)
X              为向前删除一个字符(相当于 [backspace] ) #(常用)

nx             n为数字，连续向后删除 n 个字符
nX             n为数字，连续删除光标前面的 n 个字符

dd             删除光标所在的那一整行 #(常用)
ndd            n为数字。删除光标所在行向下n行，例如 20dd 则是删除 20 行
d1G            删除光标所在行到第一行的所有数据(组合用法)
dG             删除光标所在行到最后一行的所有数据
d$             删除光标所在处，到该行的最后一个字符
d0             那个是数字的 0 ，删除光标所在处，到该行的最前面一个字符
:n1,n2 d       将 n1 行到 n2 行之间的内容删除 #(注意有冒号)

yy             复制光标所在的那一行 #(常用)
nyy            n为数字。复制光标所在行向下n行，例如 20yy 则是复制 20 行
y1G            复制光标所在行到第一行的所有数据(组合用法)
yG             复制光标所在行到最后一行的所有数据
y$             复制光标所在的那个字符到该行行尾的所有数据
y0             复制光标所在的那个字符到该行行首的所有数据
:n1,n2 d       将 n1 行到 n2 行之间的内容复制 #(注意有冒号)

p              将复制的数据，粘贴在光标的下一行 #(常用)
P              将复制的数据,粘贴到光标的上一行

ddp            上下两行的位置交换(组合用法)

J              将光标所在行与下一行的数据结合成同一行 #(常用)

u              撤销 #(常用)
Ctrl + r       撤销的撤销 #(常用)

```

## 提示符模式
### 查找替换
```shell
/string        向光标之下寻找一个名称为string字符串 #(常用)
?string        向光标之上寻找一个名称为string字符串 #(常用)

n              正向查找，搜索出的string,可以理解成next #(常用)
N              反向查找，搜索出的string,可以理解成Not next #(常用)

:g/str/s/str1/str2/g        第一个g表示对每一个包括s1的行都进行替换，第二个g表示对每一行的所有进行替换
包括str的行所有的str1都用str2替换

:n1,n2s/string1/string2/g   n1是查找的开始行数,n2是查找结束的行数,string1是要查找的字符串,string2是替换的字符串 #(常用)

:2,7s/ddd/fff/g             在第2行,第7行之间，将ddd替换成fff
:1,$s/string1/string2/gc    从第一行到最后一行寻找并替换，在替换前给用户确认 (confirm)

:%s/f $/for/g               将每一行尾部的“f ”（f键和空格键）替换为for，命令之前的"%"指定该命令将作用于所有行上. 不指定一个范围的话, ":s"将只作用于当前行.


:%s/^[^#]/#&                将不是#开头的加上#
```


### 文件操作
```shell
vi +n FileName  打开文件 FileName,并将光标置于第 n 行首。
vi + FileName   打开文件 FileName,并将光标置于最后一行
vi –r FileName  在上次正用 vi 编辑 FileName 发生系统崩溃后,恢复FileName。

:%!xxd          按十六进制查看当前文件
:%!xxd -r       从十六进制返回正常模式
```

### 保存退出
```shell
:w              将编辑的数据写入硬盘档案中 #(常用)
:w!             文件为『只读』时,强制写入,到底能否写入跟用户对档案的权限有关

:q              离开 vi  #(常用)
:q!             若曾修改过档案，又不想储存，使用 ! 为强制离开不储存档案。

:wq             储存后离开 #(常用)
:wq!            强制储存后离开

:ZZ             若档案没有更动，则不储存离开，若档案已经被更动过，则储存后离开!

:e!             重新编辑当前文件,忽略所有的修改

:w [filename]   另存为
:r [filename]   在编辑的数据中，读入另一个档案的数据。亦即将这个档案内容加到光标所在行后面

```

### 运行shell
```shell
:! command         暂时离开 vi 到指令列模式下执行 command 的显示结果！例如 『:! cat ./test』即可在 vi 当中察看当前文件夹中的test文件中的内容

:n1,n2 w! Command  将文件中n1行到n2行的内容作为 Command的输入并执行之，若不指定 n1、n2，则将整个文件内容作为 Command 的输入。

:r! Command        将命令 Command 的输出结果放到当前行。

```

### 设置环境
```
:set nu         显示行号
:set nonu
:syntax on
:set tabstop=4
```

也可在当前用户home目录下，新建.vimrc文件，将配置写入其中（无须set前面的冒号）

## 插入模式
在命令模式下，键入以下将会进入插入模式

```shell
i               在光标前插入 #(常用)
I               在光标行首字符前插入 #(常用)
a               在光标后插入
A               在光标行尾字符后插入 #(常用)
o               在当前行后插入一个新行 #(常用)
O               在当前行前插入一个新行
r               替换当前字符,接着键字的字符作为替换字符
R               替换当前字符及其后的字符，直至按 ESC 键

```

## 代码相关
- 格式化，可视模式，选择后，按`=`
- 代码自动补全，编辑模式，`ctrl p`，`ctrl n｜p`上下选择，`ctrl y`确认选择
- 查找变量或函数的声明，命令模式，`gd`
- 代码折叠，提示符模式`:set fdm=indent｜syntax`，以下是命令模式下
    - zc      折叠
    - zC      对所在范围内所有嵌套的折叠点进行折叠
    - zo      展开折叠
    - zO      对所在范围内所有嵌套的折叠点展开

<!-- http://blog.163.com/stu_shl/blog/static/599375092011639354090/ -->

- 调试语法错误
    + 做好Makefile
    + 在项目当前目录进入vim
    + `:cope`
    + `:set mouse=a`
    + `:make`

- 导航代码，在项目当前目录执行`ctags -R .`
    + 方法1 `vim -t somefun`
    + 方法2 `vim`中在光标置于方法处`ctrl ]`进入方法实现，`ctrl o`返回
        * `:ts`命令就能列出一个列表供用户选择
        * `:tp`为上一个tag标记文件
        * `:tn`为下一个tag标记文件。
        * 若当前tags文件中用户所查找的变量或函数名只有一个，`:tp,:tn`命令不可用

- 导航系统头文件，`#include <stdio.h>`光标停在`stdio.h`位置，按`gf`进入头文件，`ctrl o`返回


Sublime快捷键
=============
## 编辑器
```shell
ctrl k b               #切换显示左侧文件夹
ctrl p                 #搜索项目中的文件
ctrl shift p           #控制面板
alt shift <num>        #分屏显示
f11                    #全屏
```

## 查找
```shell
ctrl f                 #当前文件查找
ctrl shift f           #项目或文件夹查找
ctrl h                 #替换
```

## 编辑
```shell
ctrl shift <up|down>   #选中行上下移动
ctrl ]                 #当前行缩进
ctrl [                 #去除当前行缩进
shift tab              #去除缩进

ctrl enter             #在当前行后 插入一行
ctrl shift enter       #在当前行前 插入一行
ctrl j                 #合并选择的多行
ctrl t                 #词互换(首先选择好两个词)

ctrl k k               #从光标处删除至行尾
ctrl k backspace       #从光标处删除至行首

ctrl k u               #大写
ctrl k l               #小写

f9                     #行排序（按a-z）

ctrl y                 #恢复撤销
```

## 选择复制
```shell
ctrl d                 #选择单词，重复可增加选择下一个相同的单词
                       #ctrl f调出查找，把'Aa'选中，则本快捷大小写敏感
ctrl k d               #选择单词，过滤当前，移到下一个相同单词
ctrl shift d           #复制上一行整行
ctrl x                 #剪切当前行 可当删除使用
alt f3                 #选择所有相同的词
ctrl l                 #选择行，重复可依次增加选择下一行
#按住ctrl 左键选择代码，可选不连续代码
#鼠标中键框选代码，可选矩形区代码
#直接在当前行任意位置 ctrl c，复制的是整行
```

## 代码相关
```shell
ctrl r                 #列出所有method
ctrl shift v           #粘贴并自动格式化

ctrl /                 #注释/取消注释 选中的行
ctrl shift /           #注释/取消注释 当前块

ctrl m                 #光标移动至括号内开始或结束的位置
ctrl shift m           #选择当前括号内内容（继续按则选择父括号）
ctrl shift j           #选择当前括号内内容，与上有差异（继续按则选择父括号）

ctrl shift [           #当前括号 折叠代码
ctrl shift ]           #当前括号 展开代码
ctrl k 0               #展开所有代码
ctrl k 1               #代码折叠至一层
ctrl k 2               #代码折叠至二层

alt .                  #闭合当前标签
alt f2                 #增删标记 按f2可来回切

ctrl b                 #编译
f7                     #运行

```

Xcode快捷键
=============
## 编辑
```shell
cmd [|]                #左右缩进
cmd opt [|]            #当前行上下移动

ctrl f                 #前移光标
ctrl b                 #后移光标
ctrl p                 #光标到上一行
ctrl n                 #光标到下一行
ctrl a                 #光标到行首
ctrl e                 #光标到行尾
opt left|right         #光标前进 后退一个单词
#以上加上shift就会选择

mouse three click      #选中当前行

ctrl d                 #删除光标右侧字符 同 fn delete
ctrl k                 #删除光标处到行尾
cmd delete             #删除光标处到行首

ctrl cmd space         #标准表情

```

## 代码相关
```shell
esc                    #当前单词重新补全
cmd r                  #运行
cmd /                  #注释
cmd shift j            #转到定义
cmd opt left|right     #折叠

ctrl i                 #当前格式化
cmd shift o            #显示open quikly
opt mouse dclick       #文档

```



<script>

(function(){
    if(typeof expand_toc !== 'function') setTimeout(arguments.callee,500);
    else expand_toc('md_toc',1);
})();

</script>

<!--


"trim_trailing_white_space_on_save": true,
"ensure_newline_at_eof_on_save": true,


-->
