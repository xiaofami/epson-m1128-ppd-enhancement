#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (C) 2026 Hy4 flash
#
# 基于爱普生官方 GPL 驱动 epson-inkjet-printer-escpr 的 PPD，生成
# EPSON M1120 / M1128 三档打印质量增强版 PPD。
#
# 修改内容：
#   1) 新增 OutputMode DRAFT，使打印对话框出现 Draft / Standard / High 三档，
#      与 Windows 驱动 UI 一致（底层的 SUPERDRAFT 与 DRAFT 输出相同，不暴露）。
#   2) 为所有语言补全 DRAFT 翻译，通过 cupstestppd 校验。
#   3) NickName 标注为增强版，并在 PPD 头部加入修改声明。
#
# 用法: python3 build_enhanced_ppd.py <官方M1120 PPD> <输出PPD>

import re
import sys

# 各语言中 "DRAFT/快速" 的译法，键为 PPD 中的语言前缀
DRAFT_LABELS = {
    "en": "Draft (fast)",
    "nl": "Concept (snel)",
    "fr": "Brouillon (rapide)",
    "de": "Entwurf (schnell)",
    "it": "Bozza (veloce)",
    "ja": "下書き (高速)",
    "pt": "Rascunho (rápido)",
    "pt_PT": "Rascunho (rápido)",
    "es": "Borrador (rápido)",
    "ko": "초안 (빠름)",
    "zh_TW": "草稿 (快速)",
    "zh_CN": "快速",
    "ru": "Черновик (быстро)",
}

MOD_NOTICE = (
    '*% Modified PPD for EPSON M1120 / M1128: adds DRAFT quality mode.\n'
    '*% Based on the GPL-licensed Epson ESC/P-R driver PPD (Copyright Seiko Epson Corporation).\n'
    '*% Modifications Copyright (C) 2026 Hy4 flash, GPL-2.0-or-later.\n'
    '*% Not affiliated with or endorsed by Seiko Epson Corporation.\n'
)


def build(src_path: str, dst_path: str) -> None:
    s = open(src_path, encoding="utf-8").read()

    anchor = '*OutputMode NORMAL/Standard: "<</HWResolution[360 360]/cupsCompression 1>>setpagedevice"\n'
    assert anchor in s, "找不到 OutputMode NORMAL 选项锚点"
    s = s.replace(
        anchor,
        anchor
        + '*OutputMode DRAFT/Draft (fast): "<</HWResolution[360 360]/cupsCompression 0>>setpagedevice"\n',
        1,
    )

    # 为所有已有 OutputMode NORMAL 翻译的语言插入 DRAFT 翻译
    pattern = re.compile(r"^\*([A-Za-z_]+)\.OutputMode NORMAL/[^\n]*\n", re.MULTILINE)
    langs = set(pattern.findall(s))
    assert "en" not in langs, "英文翻译不应有语言前缀"

    def add_translation(match: re.Match) -> str:
        line = match.group(0)
        lang = match.group(1)
        label = DRAFT_LABELS.get(lang, "Draft (fast)")
        return line + f"*{lang}.OutputMode DRAFT/{label}: \"\"\n"

    s = pattern.sub(add_translation, s)

    s = s.replace(
        '*NickName: "EPSON M1120 Series , Epson Inkjet Printer Driver (ESC/P-R) for Linux"',
        '*NickName: "EPSON M1120/M1128 Series - Enhanced (Draft/Standard/High)"',
        1,
    )

    # PPD 注释必须放在 *PPD-Adobe 首行之后
    first_line_end = s.find("\n") + 1
    assert s.startswith('*PPD-Adobe:'), "不是有效的 PPD 文件"
    s = s[:first_line_end] + MOD_NOTICE + s[first_line_end:]

    open(dst_path, "w", encoding="utf-8").write(s)
    print(f"wrote {dst_path}; languages with DRAFT translation: {len(langs)}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: build_enhanced_ppd.py <base.ppd> <out.ppd>")
    build(sys.argv[1], sys.argv[2])
