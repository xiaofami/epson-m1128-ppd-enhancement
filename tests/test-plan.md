# 验证方案

## 1. PPD 静态校验

```bash
cupstestppd ppd/Epson-M1120-M1128-enhanced.ppd
```

期望：显示「通过」。允许出现原版 PPD 自带的纸张尺寸命名 / PCFileName WARN，
不允许出现 FAIL。本发布包中的 PPD 已通过此校验。

## 2. 档位可见性

```bash
lpoptions -p <队列名> -l | grep -i OutputMode
```

期望：列出 `draft`、`normal`（默认）、`high` 三项。

## 3. 输出数据流对比

生成一个简单测试图（例如 64×64 的 PPM），用 `file:` backend 捕获各档位的 ESC/P-R 输出：

```bash
sudo lpadmin -p TEST -E -v file:/tmp/test.prn \
  -P ppd/Epson-M1120-M1128-enhanced.ppd
lp -d TEST -o OutputMode=DRAFT  test.ppm
sudo cp /tmp/test.prn /tmp/draft.prn
lp -d TEST -o OutputMode=NORMAL test.ppm
sudo cp /tmp/test.prn /tmp/normal.prn
lp -d TEST -o OutputMode=HIGH   test.ppm
sudo cp /tmp/test.prn /tmp/high.prn
ls -l /tmp/{draft,normal,high}.prn
md5sum /tmp/{draft,normal,high}.prn
```

期望：

- `draft.prn` 与 `normal.prn` 大小相同（360dpi），但 md5 不同（`setq` 标志 0 vs 1）。
- `high.prn` 约为前两者的两倍（720dpi）。

## 4. 实际打印（可选）

依次用三档打印同一份文档，确认：

- Draft 明显更快、墨量更省；
- Standard 为日常质量；
- High 细节更清晰但耗时更长。

## 5. patch 可应用性

```bash
mkdir -p /tmp/ppdtest && cd /tmp/ppdtest
cp <官方M1120 PPD> Epson-M1120_Series-epson-escpr-en.ppd
patch -p1 < /path/to/patches/m1120-quality-modes.patch
cupstestppd Epson-M1120-M1128-enhanced.ppd
```

期望：patch 无冲突，校验通过。

## 清理

```bash
sudo lpadmin -x TEST
```
