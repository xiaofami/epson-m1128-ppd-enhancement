# EPSON M1120 / M1128 打印质量三档增强 PPD

> 语言 / Language: [中文](#中文) | [English](#english)

<a id="中文"></a>

## 中文

给爱普生官方 GPL 驱动（`epson-inkjet-printer-escpr`）的 M1120 系列 PPD 补上
**快速 / Draft** 档，使 Linux 打印对话框的「打印质量」选项与 Windows 驱动一致，
只有 **Draft / Standard / High** 三档，不再有多余或缺失的档位。

### 效果

| Linux 档位 | 底层行为 | Windows 对应档位 |
|---|---|---|
| **Draft (fast)** / 快速 | 360dpi，`setq` 质量标志 = 0 | Draft / 经济 |
| **Standard** / 标准（默认） | 360dpi，`setq` 质量标志 = 1 | Standard / 标准 |
| **High** / 高 | 720dpi | High / 高 |

实测（A4 测试图）：Standard 输出 1,376,047 字节，High 输出 2,779,868 字节（约 2×）。
底层虽还支持一个 `SUPERDRAFT` 后缀，但实测它与 `DRAFT` 输出逐字节相同，
属冗余别名，因此本补丁不暴露它。

### 为什么需要它

- 官方 PPD 只提供 `High` 和 `Normal` 两档，缺少快速档。
- 驱动中的 filter 二进制实际支持 `_DRAFT` / `_SUPERDRAFT` / `_NORMAL` 质量后缀，
  wrapper 会把「介质类型 + 输出模式」拼成 `<MediaType>_<OutputMode>` 传给 filter。
- 也就是说引擎原生支持快速档，只是官方 PPD 没有暴露出来。
- 本补丁只改 PPD 文本（配置层），不修改或重新分发任何驱动二进制。

### 依赖

- **爱普生官方驱动**：`epson-inkjet-printer-escpr` >= 1.7.7（请从你的 Linux 发行版安装）
- **CUPS** 2.x
- **适用机型**：EPSON M1120 Series（包括 M1128、M1129；USB ID `04b8:00ac`）
- 其他架构（如 arm64）只要装有对应架构的同版本驱动，本 PPD 同样适用（PPD 是纯文本，架构无关）

### 安装

**方法 A：直接使用现成 PPD（最简单）**

```bash
sudo cp ppd/Epson-M1120-M1128-enhanced.ppd \
        /usr/share/ppd/epson-inkjet-printer-escpr/
sudo lpadmin -p <你的打印机队列名> \
        -P /usr/share/ppd/epson-inkjet-printer-escpr/Epson-M1120-M1128-enhanced.ppd
```

`<你的打印机队列名>` 可用 `lpstat -p` 查看（本例中为 `EPSON-M1120-Series`）。

**方法 B：从官方 PPD 生成**

```bash
find /usr/share/cups/model /usr/share/ppd -name '*M1120*escpr*.ppd' 2>/dev/null
python3 build_enhanced_ppd.py <找到的官方PPD路径> ./out.ppd
```

**方法 C：应用 patch（供发行版打包者）**

```bash
cd <官方PPD所在目录>
patch -p1 < /path/to/patches/m1120-quality-modes.patch
```

### 验证

```bash
cupstestppd ppd/Epson-M1120-M1128-enhanced.ppd
lpoptions -p <队列名> -l | grep OutputMode
```

应显示「通过」及三个档位；详细方法见 `tests/test-plan.md`。

### 文件结构

```
.
├── README.md                      本文件（中英双语）
├── LICENSE                        GPL-2.0 全文
├── AUTHORS                        修改者声明
├── build_enhanced_ppd.py          生成脚本（主交付物）
├── patches/
│   └── m1120-quality-modes.patch  统一 diff，便于审查与合入
├── ppd/
│   └── Epson-M1120-M1128-enhanced.ppd   生成好的完整 PPD
├── docs/
│   ├── installation.md            详细安装与回滚说明
│   ├── quality-mapping.md         三档对应关系与实测证据
│   └── technical-background.md    技术背景与限制说明
└── tests/
    └── test-plan.md               验证方法
```

### 许可证与声明

- 本项目整体以 **GPL-2.0-or-later** 发布，与上游爱普生驱动一致（见 `LICENSE`）。
- 上游 PPD 版权归 **Seiko Epson Corporation**；本项目的修改部分由 **Hy4 flash** 贡献，
  作者不主张版权。
- 本项目**不捆绑、不重新分发**任何爱普生二进制文件（libescpr.so、filter 等）。
  用户需自行从发行版安装官方驱动。
- 本项目为第三方修改，**与 Seiko Epson Corporation 无关联、未获其背书**；
  请勿使用 EPSON 商标或 logo 宣传本补丁。
- 按「原样」提供，无明示或暗示担保；使用风险自负。

### 致谢

感谢 Seiko Epson Corporation 以 GPL 发布 ESC/P-R Linux 驱动，
以及各 Linux 发行版维护者的打包工作。

---

<a id="english"></a>

## English

An enhanced PPD for the Epson M1120 series that adds a **Draft / fast** quality mode,
so the Linux print quality options match the Windows driver exactly:
**Draft / Standard / High** — no missing or redundant entries.

### Features

| Linux mode | Under the hood | Windows equivalent |
|---|---|---|
| **Draft (fast)** | 360dpi, `setq` quality flag = 0 | Draft |
| **Standard** (default) | 360dpi, `setq` quality flag = 1 | Standard |
| **High** | 720dpi | High |

Measured on an A4 test image: Standard produces 1,376,047 bytes, High 2,779,868 bytes (~2x).
The underlying driver also supports a `SUPERDRAFT` suffix, but its output is byte-for-byte
identical to `DRAFT`, so this patch does not expose it.

### Why

- The stock PPD only offers `High` and `Normal` — no fast mode.
- The filter binary actually supports `_DRAFT` / `_SUPERDRAFT` / `_NORMAL` quality suffixes;
  the wrapper concatenates the media type and output mode as `<MediaType>_<OutputMode>`.
- The engine supports fast printing natively; the stock PPD simply never exposed it.
- This patch only changes the PPD (configuration layer); no driver binaries are modified
  or redistributed.

### Requirements

- **Epson official driver**: `epson-inkjet-printer-escpr` >= 1.7.7 (from your distro)
- **CUPS** 2.x
- **Supported models**: EPSON M1120 Series (M1128, M1129; USB ID `04b8:00ac`)
- Architecture-independent: works on x86-64, arm64, etc., as long as the matching
  driver for that architecture is installed.

### Installation

**Option A: use the bundled PPD (easiest)**

```bash
sudo cp ppd/Epson-M1120-M1128-enhanced.ppd \
        /usr/share/ppd/epson-inkjet-printer-escpr/
sudo lpadmin -p <YOUR_QUEUE> \
        -P /usr/share/ppd/epson-inkjet-printer-escpr/Epson-M1120-M1128-enhanced.ppd
```

Find your queue name with `lpstat -p` (e.g. `EPSON-M1120-Series`).

**Option B: generate from the stock PPD**

```bash
find /usr/share/cups/model /usr/share/ppd -name '*M1120*escpr*.ppd' 2>/dev/null
python3 build_enhanced_ppd.py <stock.ppd> ./out.ppd
```

**Option C: apply the patch (for distro packagers)**

```bash
cd <dir-with-stock-ppd>
patch -p1 < /path/to/patches/m1120-quality-modes.patch
```

### Verification

```bash
cupstestppd ppd/Epson-M1120-M1128-enhanced.ppd
lpoptions -p <QUEUE> -l | grep OutputMode
```

Expect a "PASS" result and three quality modes. See `tests/test-plan.md` for details.

### License and disclaimer

- Distributed under **GPL-2.0-or-later**, matching the upstream Epson driver (`LICENSE`).
- Upstream PPD copyright: **Seiko Epson Corporation**. Modifications contributed by
  **Hy4 flash**, who waives any copyright claim over them.
- This project does **not** bundle or redistribute any Epson binaries (libescpr.so, filters, etc.).
- This is a third-party modification, **not affiliated with or endorsed by Seiko Epson**.
  Do not use EPSON trademarks or logos to promote this patch.
- Provided "as is", without warranty of any kind.

### Credits

Thanks to Seiko Epson Corporation for releasing the ESC/P-R Linux driver under the GPL,
and to Linux distribution maintainers for their packaging work.
