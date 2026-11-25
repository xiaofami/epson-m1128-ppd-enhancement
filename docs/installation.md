# 安装、验证与回滚

## 前置条件

1. 确认打印机型号：本补丁适用于 EPSON M1120 Series（M1128 / M1129）。
2. 已安装爱普生官方驱动（从发行版软件源安装，版本 >= 1.7.7）：

```bash
dpkg -l epson-inkjet-printer-escpr   # Debian / Ubuntu / 银河麒麟
rpm -q epson-inkjet-printer-escpr    # Fedora / openSUSE
```

3. 确认 CUPS 正在运行：`systemctl is-active cups`

## 安装

### 方法 A：使用随附 PPD

```bash
# 1. 备份当前生效的 PPD（以便回滚）
sudo cp /etc/cups/ppd/<队列名>.ppd /etc/cups/ppd/<队列名>.ppd.bak

# 2. 安装增强 PPD 到系统 PPD 目录
sudo mkdir -p /usr/share/ppd/epson-inkjet-printer-escpr
sudo cp ppd/Epson-M1120-M1128-enhanced.ppd \
        /usr/share/ppd/epson-inkjet-printer-escpr/

# 3. 应用到队列
sudo lpadmin -p <队列名> \
  -P /usr/share/ppd/epson-inkjet-printer-escpr/Epson-M1120-M1128-enhanced.ppd

# 4. 确认生效
sudo grep '^\*OutputMode ' /etc/cups/ppd/<队列名>.ppd
```

应看到三行：`HIGH`、`NORMAL`、`DRAFT`。

### 方法 B：从官方 PPD 生成

适合想跟随官方驱动版本升级的场景：

```bash
find /usr/share/cups/model /usr/share/ppd -iname '*M1120*escpr*.ppd' 2>/dev/null
python3 build_enhanced_ppd.py <官方PPD路径> ./out.ppd
cupstestppd ./out.ppd
sudo lpadmin -p <队列名> -P ./out.ppd
```

### 方法 C：patch（打包者）

```bash
cd <官方PPD目录>
patch -p1 < patches/m1120-quality-modes.patch
```

## 使用

打印对话框「打印质量 / OutputMode」现在有三档：

- **Draft (fast) / 快速** —— 最快，草稿
- **Standard / 标准** —— 默认，日常使用
- **High / 高** —— 720dpi，高质量（数据量约 2 倍）

命令行：

```bash
lp -d <队列名> -o OutputMode=DRAFT  文件
lp -d <队列名> -o OutputMode=HIGH   文件
```

## 回滚

```bash
sudo cp /etc/cups/ppd/<队列名>.ppd.bak /etc/cups/ppd/<队列名>.ppd
sudo systemctl restart cups
```

或重新安装发行版提供的官方 PPD。

## 常见问题

- **队列名怎么查？** `lpstat -p`，本例为 `EPSON-M1120-Series`。
- **打印质量只有两档？** 说明队列还在用官方 PPD，请重新执行方法 A 的第 3 步。
- **cupstestppd 有 WARN？** 纸张尺寸命名（如 `4X6FULL`）和 `PCFileName` 的 WARN 来自原版 PPD，不影响使用；只要没有 FAIL 即可。
- **驱动升级后档位消失？** 升级会覆盖 PPD，重新应用本补丁即可（方法 B 最适合此场景）。
