# 技术背景与限制

## 驱动结构

爱普生 ESC/P-R Linux 驱动的打印链路：

```
应用 → CUPS → [pdftopdf / pdftoraster] → epson-escpr-wrapper
     → epson-escpr → libescpr.so → ESC/P-R 数据流 → 打印机
```

- `epson-escpr-wrapper` 读取 PPD 中的选项，把「介质类型 + 输出模式」拼成
  `<MediaType>_<OutputMode>`，再调用 `epson-escpr`。
- `epson-escpr` 调用 `libescpr.so` 把 CUPS raster 转换成 ESC/P-R。
- 质量档位最终体现为 ESC/P-R 数据流中的 `setq` 命令参数。

## 本补丁的原理

官方 PPD 只声明了 `HIGH` / `NORMAL` 两个 OutputMode 选项。
本补丁增加 `DRAFT` 选项（设置 `cupsCompression 0`），wrapper 会拼出
`PLAIN_DRAFT` 传给 filter，filter 据此选择快速档。

## 为什么只改 PPD

- 上游 `epson-inkjet-printer-escpr` 以 GPL 发布，官方还提供完整 C 源码包，
  但本补丁没必要动源码——改动配置层即可达到目的。
- 不碰二进制，意味着：无重新分发闭源库的风险、可跟随发行版驱动升级、
  跨架构（x86-64 / arm64）通用。

## 限制

- 本补丁不改变半色调算法或色彩配置，因此「High」档的画质与 Windows 驱动的
  高质量档在算法层面未必逐像素一致；它只是打开驱动原本就支持的档位。
- 适用于 M1120 系列（M1128/M1129）。其他机型的 PPD 可能需要适配。
- 若发行版的驱动版本过旧（PPD 结构不同，例如用 `Quality` 而非 `OutputMode`），
  本 patch 不能直接套用；建议升级驱动到 >= 1.7.7。

## 参考

- 爱普生官方驱动源码/下载：`http://download.ebz.epson.net/dsc/search/01/search/?OSC=LX`
- 上游手册：`https://download.ebz.epson.net/man/linux/escpr.html`
