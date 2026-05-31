# multi-gpu-transcoder

A hardware-accelerated transcoder for Intel QSV, AMD AMF, and NVIDIA NVENC, and hybrid encoders for maximum compatibility and efficiency.

---

## 📋 Requirements & Quick Start
* [cite_start]**OS:** Windows 7 or above[cite: 4].
* [cite_start]**Hardware:** Intel, AMD, or NVIDIA GPU[cite: 4].
* [cite_start]**SmartScreen Warning:** If Windows shows a warning when launching, click *More info* -> *Run anyway*[cite: 86].
* [cite_start]**Temperature Throttling:** For battery preservation, install [Core Temp](https://www.alcpu.com/CoreTemp) and keep it running in the background[cite: 20, 22]. (Note: If Core Temp isn't running, this throttling is silently disabled) [cite_start][cite: 87].

---

## 🛠️ App Glossary

### Encoders
* **QSV/AMF/NVENC Transcoders:** Uses a full GPU decode/encode path. [cite_start]Fastest options[cite: 9].
* **QSV/AMF/NVENC Hybrid Transcoders:** Uses CPU decode and GPU encode path. [cite_start]Bypasses most GPU limitations[cite: 10].
* **libx264/libx265 Transcoders:** Uses a full CPU decode/encode path. [cite_start]Slowest, but most compatible[cite: 11].

### Codecs & Formats
* [cite_start]**HEVC/H.265:** Slower, but offers better compression and quality preservation[cite: 17].
* [cite_start]**AVC/H.264:** Fastest, acceptable compression, compatible with legacy hardware[cite: 17].
* [cite_start]**Pixel Formats:** `Orig` (Same as source) [cite: 13][cite_start], `8 bit` (SDR Limited Range) [cite: 14][cite_start], and `10 bit` (HDR)[cite: 15].
* [cite_start]**Quality:** Higher values reduce the bitrate (resulting in smaller file sizes but lower quality)[cite: 18].

---

## ❌ Troubleshooting Tips

* [cite_start]**Hardware-acceleration fails with 'Orig' format:** For HEVC, Intel supports 8/10/12-bit, while NVENC and AMF support 8 and 10-bit[cite: 89]. [cite_start]If your file is outside this range, enforce a pixel format conversion or use `libx265`/`libx264`[cite: 91].
* **Encoding fails midway:** This is usually an insufficient memory (RAM) issue. [cite_start]Offload your RAM and try again[cite: 92].
* **AMF 10-bit encoding fails:** Fails on AMD Adrenalin drivers below v23.30. [cite_start]Update your drivers or encode in 8-bit[cite: 93].
* **Slow first launch:** This is just extraction overhead and is expected. [cite_start]Use the `onedir` portable version for a faster launch[cite: 94].

---

## 📊 AMD AMF Extension Support

| Format | Extension | H.264/AVC | H.265/HEVC | AV1 |
| :--- | :--- | :---: | :---: | :---: |
| Matroska | `.mkv` | Y | Y | Y |
| MPEG-4 Part 14 | `.mp4` | Y | Y | Y |
| Audio Video Interleave | `.avi` | Y | Y | Y |
| MPEG transport stream | `.ts` | Y | Y | Y |
| WebM | `.webm` | n/a | n/a | Y |

* **Y**: Supported | [cite_start]**n/a**: Not applicable in specification[cite: 33, 34].
* [cite_start]*Note: Specific AMD chips are limited to certain driver versions, which can impact hardware compatibility[cite: 73].*
