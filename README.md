# multi-gpu-transcoder

A hardware-accelerated transcoder for Intel QSV, AMD AMF, and NVIDIA NVENC, and hybrid encoders for maximum compatibility and efficiency.

---

## 📋 Requirements & Quick Start
* [cite_start]**OS:** Windows 7 or above[cite: 4].
* [cite_start]**Hardware:** Intel, AMD, or NVIDIA GPU[cite: 4].
* **SmartScreen Warning:** Expected for unsigned software. [cite_start]Click *More info* -> *Run anyway*[cite: 86].
* [cite_start]**Temperature Throttling:** For battery preservation over performance, install [Core Temp](https://www.alcpu.com/CoreTemp) and ensure it's running in the background[cite: 20, 22]. [cite_start]If it isn't running, throttling is silently disabled[cite: 87]. [cite_start]Note that all modern chips have native integrated throttling systems[cite: 21].

---

## 🛠️ App Glossary

### Encoders
* **QSV/AMF/NVENC Transcoders:** Use a full GPU decode/encode path. [cite_start]Fastest encoders[cite: 9].
* **QSV/AMF/NVENC Hybrid Transcoders:** Use a CPU decode/GPU encode path. Bypasses all/most GPU limitations. [cite_start]Very fast encoders[cite: 10].
* **libx264/libx265 Transcoders:** Use a full CPU decode/encode path. [cite_start]Slowest, most compatible encoders[cite: 11].

### Codecs & Pixel Formats
* [cite_start]**HEVC/H.265:** Slower, but offers better compression and quality preservation[cite: 17].
* [cite_start]**AVC/H.264:** Fastest, acceptable compression, compatible with legacy hardware[cite: 17].
* [cite_start]**Pixel Formats:** `Orig` (Same as source, including 12-bit+ and 5-bit-), `8 bit` (SDR Limited Range), and `10 bit` (HDR)[cite: 13, 14, 15].
* **Quality:** Controls the bitrate (and file size). [cite_start]A higher value reduces the bitrate[cite: 18].

---

## 📊 Hardware & Driver Support Matrix

### 1. Intel Quick Sync Video (QSV) Support
| Platform Name | Graphics Generation | Adds Support For... |
| :--- | :--- | :--- |
| Ironlake / Sandy Bridge | gen5 / gen6 | MPEG-2, H.264 decode. VC-1 decode; [cite_start]H.264 encode. [cite: 26] |
| Ivy Bridge / Bay Trail / Haswell | gen7 / gen7 / gen7.5 | JPEG decode; [cite_start]MPEG-2 encode. [cite: 26] |
| Broadwell / Braswell | gen8 / gen8 | VP8 decode. H.265 decode; [cite_start]JPEG, VP8 encode. [cite: 26] |
| Skylake | gen9 | [cite_start]H.265 encode. [cite: 26] |
| Apollo Lake | gen9 | [cite_start]VP9, H.265 Main10 decode. [cite: 26] |
| Kaby Lake / Coffee Lake | gen9.5 / gen9.5 | VP9 profile 2 decode; [cite_start]VP9, H.265 Main10 encode. [cite: 26] |
| Gemini Lake / Cannon Lake / Ice Lake | gen10 / gen11 | H.265 8-bit 422/444 decode/encode; [cite_start]VP9 8/10-bit 444 decode/encode[cite: 26]. |
| Tiger Lake / Rocket Lake | gen12 / gen12 | AV1 8/10-bit; H.265 12-bit decode; [cite_start]VP9 12-bit decode[cite: 26]. |
| DG1 / SG1 / Alder Lake / Raptor Lake | gen12 | [cite_start]VP8 encode removed[cite: 26]. |
| DG2 | gen12 | [cite_start]AV1 encode[cite: 26]. |

---

### 2. AMD Advanced Media Framework (AMF) Support

#### Decoder Container Support
| Format | Extension | H.264/AVC | H.265/HEVC | AV1 |
| :--- | :--- | :---: | :---: | :---: |
| Matroska | `.mkv` | Y | Y | Y |
| MPEG-4 Part 14 | `.mp4` | Y | Y | Y |
| Audio Video Interleave | `.avi` | Y | N | Y |
| Material Exchange Format | `.mxf` | Y | n/a | n/a |
| MPEG transport stream | `.ts` | Y | Y | N |
| 3GPP / Flash Video | `.3gp` / `.flv` | Y | n/a | n/a |
| WebM | `.webm` | n/a | n/a | Y |
| Advanced Systems Format | `.asf` `.wmv` | Y | Y | Y |
| QuickTime File Format | `.mov` | Y | Y | n/a |

#### Encoder Container Support
| Format | Extension | H.264/AVC | H.265/HEVC | AV1 |
| :--- | :--- | :---: | :---: | :---: |
| Matroska | `.mkv` | Y | Y | Y |
| MPEG-4 Part 14 | `.mp4` | Y | Y | Y |
| Audio Video Interleave | `.avi` | Y | Y | Y |
| Material Exchange Format | `.mxf` | Y | n/a | n/a |
| MPEG transport stream | `.ts` | Y | Y | Y |
| 3GPP / Flash Video | `.3gp` / `.flv` | Y | n/a | n/a |
| WebM | `.webm` | n/a | n/a | Y |
| Advanced Systems Format | `.asf` `.wmv` | Y | Y | Y |
| QuickTime File Format | `.mov` | Y | Y | n/a |

* [cite_start]**Y**: Hardware accelerated supported [cite: 33] | [cite_start]**n/a**: Not applicable in specification[cite: 34].
* [cite_start]*Note: Specific AMD generations are limited to specific driver versions; driver incompatibility can include hardware incompatibility[cite: 73].*

<details>
<summary>💡 Click to expand AMD Driver Version History</summary>

* **v1.5.2:** Adrenalin Edition (26.10.07.01)+. [cite_start]Updated FFmpeg to 8.0.1[cite: 36].
* **v1.5.0:** Adrenalin Edition 25.10.2 (25.20.21.01)+. [cite_start]Added 4:4:4/4:2:2 chroma subsampling for Video Converter[cite: 37, 38].
* **v1.4.36:** Adrenalin Edition 25.1.1 (24.30.31.03)+. [cite_start]Added B-frame support/picture management for AV1; high-quality presets for HEVC/AVC[cite: 39, 40].
* **v1.4.35:** Adrenalin Edition 24.9.1 (24.20.11.01)+. Multi-HW instance encoder mode; [cite_start]FFmpeg 7.0; split frame encoding[cite: 41, 42].
* **v1.4.34:** Adrenalin Edition 24.6.1 (24.10.21.01)+. [cite_start]Stable RADV drivers for AMF on Linux[cite: 43, 44].
* **v1.4.33:** Adrenalin Edition 24.1.1 (23.40.02)+. [cite_start]DX12 support for encoding/PreAnalysis; public Vulkan[cite: 45, 46].
* **v1.4.32:** Adrenalin Edition 23.12.1 (23.30.13.01)+. [cite_start]FRC component, VQEnhancer doc, FFmpeg 6.0[cite: 48, 49].
* **v1.4.30:** Adrenalin Edition 23.5.2 (23.10.01.45)+. AMF wrappers for software encoders; [cite_start]FFmpeg 5.1.2[cite: 50, 51, 52].
* **v1.4.29:** Adrenalin Edition 23.1.2 (22.40.01.34)+. [cite_start]Smart Access Video for AVC/HEVC/AV1[cite: 53].
* **v1.4.28:** Adrenalin Edition 22.12.1 (22.40.00.24)+. AV1 encoding support; [cite_start]12-bit AV1 decoding[cite: 55].
* **v1.4.26:** Adrenalin Edition 22.7.1 (22.20.15.01)+. [cite_start]PAQ, TAQ, and high motion quality boost[cite: 57, 58].
* **v1.4.24:** Adrenalin Edition 22.3.1 (21.50.11.03)+. AMD Direct Capture; [cite_start]Vulkan HEVC encoder on Navi[cite: 60, 61].
* **v1.4.23:** Adrenalin Edition 21.12.1 (21.40.11.03)+. [cite_start]Auto LTR encoder mode[cite: 62, 63].
* **v1.4.21:** Adrenalin Edition 21.10.1 (21.30.25.01)+. PSNR/SSIM scores; QVBR rate control; [cite_start]HDR for HEVC[cite: 64, 65].
* [cite_start]**v1.4.18:** Requires Vulkan SDK for some samples and Adrenalin 18.8.1+[cite: 67].
* [cite_start]**v1.4.4:** Requires `OCL_SDK_Light` and Crimson Edition 17.7.2+[cite: 69, 70].
</details>

---

### 3. NVIDIA NVENC Hardware Capabilities

#### H.265/HEVC Capabilities
| Hardware Features | 1st Gen Maxwell | 2nd Gen Maxwell | Pascal | Volta / TU117 | Ampere / TU | Ada | Jetson Thor | Blackwell |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Main profile (YUV 4:2:0)** | N | Y | Y | Y | Y | Y | Y | Y |
| **Lossless encoding** | N | N | Y | Y | Y | Y | Y | Y |
| **Main 10 profile (10-bit)** | N | N | Y | Y | Y | Y | Y | Y |
| **4:2:2 encoding** | N | N | N | N | N | N | N | Y |
| **4:4:4 encoding** | N | N | Y | Y | Y | Y | Y | Y |
| **8K encoding (8192x8192)** | N | N | Y | Y | Y | Y | Y | Y |
| **Weighted prediction** | N | N | Y | Y | Y | Y | Y | Y |
| **B Frame support** | N | N | N | N | Y | Y | Y | Y |
| **Multiple reference frames** | N | N | N | N | Y | Y | Y | Y |

#### H.264/AVC Capabilities
| Hardware Features | 1st Gen Maxwell | 2nd Gen Maxwell | Pascal | Volta / TU117 | Ampere / TU | Ada | Jetson Thor | Blackwell |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline main/high (YUV 420)**| Y | Y | Y | Y | Y | Y | Y | Y |
| **High 10 profile (10-bit)** | N | N | N | N | N | N | N | Y |
| **4:2:2 encoding** | N | N | N | N | N | N | N | Y |
| **4:4:4 encoding (CAVLC only)** | Y | Y | Y | Y | Y | Y | Y | Y |
| **Lossless encoding** | Y | Y | Y | Y | Y | Y | Y | Y |
| **Field encoding** | Y | Y | Y | Y | N | N | N | Y |
| **Weighted prediction** | N | N | Y | Y | Y | Y | Y | Y |
| **Multiple reference frames** | N | N | N | N | Y | Y | Y | Y |

* **Y**: Supported | [cite_start]**N**: Not supported[cite: 78, 82].
* [cite_start]*\*Supported in select Pascal generation GPUs[cite: 79, 83].*

---

## ❌ Troubleshooting Tips

* [cite_start]**Hardware-acceleration fails with 'Orig' format:** For HEVC, Intel is compatible with 8/10/12-bit formats, while NVENC and AMF support 8 and 10-bit[cite: 89]. [cite_start]If your file's format is outside this range, enforce a pixel format conversion, or use `libx265`/`libx264` to preserve it[cite: 91].
* **Encoding fails midway:** Usually an insufficient memory (RAM) issue. [cite_start]Offload your RAM and try again[cite: 92].
* **AMF 10-bit encoding fails:** Fails on AMD Adrenalin drivers below version 23.30. [cite_start]A driver update is required if the GPU supports it; encode in 8-bit otherwise[cite: 93].
* **Slow first launch:** Expected behavior due to extraction overhead. [cite_start]Use the `onedir` portable version for a faster launch[cite: 94].
