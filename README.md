# multi-gpu-transcoder

A hardware-accelerated transcoder for Intel QSV, AMD AMF, and NVIDIA NVENC, and hybrid encoders for maximum compatibility and efficiency.

---

## 📋 Requirements & Quick Start
* **OS:** Windows 7 or above.
* **Hardware:** Intel, AMD, or NVIDIA GPU.
* **SmartScreen Warning:** Expected for unsigned software. Click *More info* -> *Run anyway*.
* **Temperature Throttling:** For battery preservation over performance, install [Core Temp](https://www.alcpu.com/CoreTemp) and ensure it's running in the background. If it isn't running, throttling is silently disabled. Note that all modern chips have native integrated throttling systems.

---

## 🛠️ App Glossary

### Encoders
* **QSV/AMF/NVENC Transcoders:** Use a full GPU decode/encode path. Fastest encoders.
* **QSV/AMF/NVENC Hybrid Transcoders:** Use a CPU decode/GPU encode path. Bypasses all/most GPU limitations. Very fast encoders.
* **libx264/libx265 Transcoders:** Use a full CPU decode/encode path. Slowest, most compatible encoders.

### Codecs & Pixel Formats
* **HEVC/H.265:** Slower, but offers better compression and quality preservation.
* **AVC/H.264:** Fastest, acceptable compression, compatible with legacy hardware.
* **Pixel Formats:** `Orig` (Same as source, including 12-bit+ and 5-bit-), `8 bit` (SDR Limited Range), and `10 bit` (HDR).
* **Quality:** Controls the bitrate (and file size). A higher value reduces the bitrate.

---

## 📊 Hardware & Driver Support Matrix

### 1. Intel Quick Sync Video (QSV) Support
| Platform Name | Graphics Generation | Adds Support For... |
| :--- | :--- | :--- |
| Ironlake / Sandy Bridge | gen5 / gen6 | MPEG-2, H.264 decode. VC-1 decode; H.264 encode. |
| Ivy Bridge / Bay Trail / Haswell | gen7 / gen7 / gen7.5 | JPEG decode; MPEG-2 encode. |
| Broadwell / Braswell | gen8 / gen8 | VP8 decode. H.265 decode; JPEG, VP8 encode. |
| Skylake | gen9 | H.265 encode. |
| Apollo Lake | gen9 | VP9, H.265 Main10 decode. |
| Kaby Lake / Coffee Lake | gen9.5 / gen9.5 | VP9 profile 2 decode; VP9, H.265 Main10 encode. |
| Gemini Lake / Cannon Lake / Ice Lake | gen10 / gen11 | H.265 8-bit 422/444 decode/encode; VP9 8/10-bit 444 decode/encode. |
| Tiger Lake / Rocket Lake | gen12 / gen12 | AV1 8/10-bit; H.265 12-bit decode; VP9 12-bit decode. |
| DG1 / SG1 / Alder Lake / Raptor Lake | gen12 | VP8 encode removed. |
| DG2 | gen12 | AV1 encode. |

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

* **Y**: Hardware accelerated supported | **n/a**: Not applicable in specification.
* *Note: Specific AMD generations are limited to specific driver versions; driver incompatibility can include hardware incompatibility.*

<details>
<summary>💡 Click to expand AMD Driver Version History</summary>

* **v1.5.2:** Adrenalin Edition (26.10.07.01)+. Updated FFmpeg to 8.0.1.
* **v1.5.0:** Adrenalin Edition 25.10.2 (25.20.21.01)+. Added 4:4:4/4:2:2 chroma subsampling for Video Converter.
* **v1.4.36:** Adrenalin Edition 25.1.1 (24.30.31.03)+. Added B-frame support/picture management for AV1; high-quality presets for HEVC/AVC.
* **v1.4.35:** Adrenalin Edition 24.9.1 (24.20.11.01)+. Multi-HW instance encoder mode; FFmpeg 7.0; split frame encoding.
* **v1.4.34:** Adrenalin Edition 24.6.1 (24.10.21.01)+. Stable RADV drivers for AMF on Linux.
* **v1.4.33:** Adrenalin Edition 24.1.1 (23.40.02)+. DX12 support for encoding/PreAnalysis; public Vulkan.
* **v1.4.32:** Adrenalin Edition 23.12.1 (23.30.13.01)+. FRC component, VQEnhancer doc, FFmpeg 6.0.
* **v1.4.30:** Adrenalin Edition 23.5.2 (23.10.01.45)+. AMF wrappers for software encoders; FFmpeg 5.1.2.
* **v1.4.29:** Adrenalin Edition 23.1.2 (22.40.01.34)+. Smart Access Video for AVC/HEVC/AV1.
* **v1.4.28:** Adrenalin Edition 22.12.1 (22.40.00.24)+. AV1 encoding support; 12-bit AV1 decoding.
* **v1.4.26:** Adrenalin Edition 22.7.1 (22.20.15.01)+. PAQ, TAQ, and high motion quality boost.
* **v1.4.24:** Adrenalin Edition 22.3.1 (21.50.11.03)+. AMD Direct Capture; Vulkan HEVC encoder on Navi.
* **v1.4.23:** Adrenalin Edition 21.12.1 (21.40.11.03)+. Auto LTR encoder mode.
* **v1.4.21:** Adrenalin Edition 21.10.1 (21.30.25.01)+. PSNR/SSIM scores; QVBR rate control; HDR for HEVC.
* **v1.4.18:** Requires Vulkan SDK for some samples and Adrenalin 18.8.1+.
* **v1.4.4:** Requires `OCL_SDK_Light` and Crimson Edition 17.7.2+.
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

* **Y**: Supported | **N**: Not supported.
* *\*Supported in select Pascal generation GPUs.*

---

## ❌ Troubleshooting Tips

* **Hardware-acceleration fails with 'Orig' format:** For HEVC, Intel is compatible with 8/10/12-bit formats, while NVENC and AMF support 8 and 10-bit. If your file's format is outside this range, enforce a pixel format conversion, or use `libx265`/`libx264` to preserve it.
* **Encoding fails midway:** Usually an insufficient memory (RAM) issue. Offload your RAM and try again.
* **AMF 10-bit encoding fails:** Fails on AMD Adrenalin drivers below version 23.30. A driver update is required if the GPU supports it; encode in 8-bit otherwise.
* **Slow first launch:** Expected behavior due to extraction overhead. Use the `onedir` portable version for a faster launch.
