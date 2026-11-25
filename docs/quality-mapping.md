# 打印质量三档对应关系与实测证据

## 对应关系

| Linux 档位 | 传给 filter 的参数 | ESC/P-R 底层 | 输出大小 | Windows 档位 |
|---|---|---|---:|---|
| DRAFT / 快速 | `PLAIN_DRAFT` | 360dpi，`setq` 标志 = 0 | 1,376,047 B | Draft / 经济 |
| NORMAL / 标准（默认） | `PLAIN_NORMAL` | 360dpi，`setq` 标志 = 1 | 1,376,047 B | Standard / 标准 |
| HIGH / 高 | `PLAIN_HIGH` | 720dpi | 2,779,868 B | High / 高 |

Windows 驱动 UI 有三档：Draft / Standard / High。本补丁使 Linux 与其一一对应。

## 实测方法

用 CUPS 的 `file:` backend 捕获驱动输出的 ESC/P-R 数据流：

```bash
sudo lpadmin -p TEST -E -v file:/tmp/test.prn -P ppd/Epson-M1120-M1128-enhanced.ppd
lp -d TEST -o OutputMode=DRAFT  test.ppm
lp -d TEST -o OutputMode=NORMAL test.ppm
lp -d TEST -o OutputMode=HIGH   test.ppm
```

比较输出大小与 md5：DRAFT 与 NORMAL 大小相同但 md5 不同，HIGH 约为两倍。

## 字节级证据

DRAFT 与 NORMAL 的输出只在 ESC/P-R `setq` 命令里有一个字节不同：

```
偏移 0x78（setq 命令内）：
  NORMAL:  ... 1b 71 09 00 00 00 73 65 74 71 00 01 01 00 ...
  DRAFT :  ... 1b 71 09 00 00 00 73 65 74 71 00 00 01 00 ...
                                                      ^ 质量标志 0/1
```

## 关于被移除的 SUPERDRAFT

驱动 filter 二进制中还存在 `_SUPERDRAFT` 后缀。实测其输出与 `_DRAFT`
**逐字节完全相同**（md5 一致），因此本补丁不暴露它——多余的档位只会让用户误解。
