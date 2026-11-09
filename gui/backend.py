import os
import io
import subprocess
import psutil
import json
import ctypes
from PIL import Image
from ctypes import Structure, c_float, c_uint, c_ubyte, c_char
import sys

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

ffmpeg_path = os.path.join(base_path, 'ffmpeg.exe')
ffprobe_path = os.path.join(base_path, 'ffprobe.exe')
# Fall back to ffmpeg/ffprobe on PATH if the binaries aren't bundled next to the script
if not os.path.exists(ffmpeg_path):
    ffmpeg_path = 'ffmpeg'
if not os.path.exists(ffprobe_path):
    ffprobe_path = 'ffprobe'

CREATE_NO_WINDOW = 0x08000000

encoders = ['hevc_qsv', 'hevc_amf', 'hevc_nvenc', 'h264_qsv', 'h264_amf', 'h264_nvenc', 'libx264', 'libx265']
supported = []
encoding_choice = ""
long_name = {
'hevc_qsv':'Intel Quick Sync Video (HEVC_QSV)',
'hybrid_hevc_qsv':'Intel QSV Hybrid (CPU-In/GPU-Out)',
'h264_qsv':'Intel Quick Sync Video (H.264_QSV)',
'hybrid_h264_qsv':'Intel AVC-QSV Hybrid (CPU-In/GPU-Out)',

'hevc_amf':'AMD Adv. Media Frmwrk (HEVC_AMF)',
'hybrid_hevc_amf':'AMD AMF Hybrid (CPU-In/GPU-Out)',
'h264_amf':'AMD Adv. Media Frmwrk (H.264_AMF)',
'hybrid_h264_amf':'AMD AVC-AMF Hybrid (CPU-In/Out)',


'hevc_nvenc':'NVIDIA Video Encoder (HEVC_NVENC)',
'hybrid_hevc_nvenc':'NV NVENC Hybrid (CPU-In/GPU-Out)',
'h264_nvenc':'NV Video Enc. (H.264_NVENC)',
'hybrid_h264_nvenc':'NV AVC-NVENC Hybrid (CPU-In/Out)',

'libx264': 'Software Legacy (AVC/H.264)',
'libx265': 'Software High Efficiency (HEVC/H.265)'
}
no_support = "No HW support."


def detect_encoders():

    for encoder in encoders:

        cmd = [ffmpeg_path, '-hide_banner', '-f', 'lavfi', '-i', 'nullsrc', '-c:v', encoder, '-frames:v', '1', '-f', 'null', '-']
        try:
            processing = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=CREATE_NO_WINDOW)
        except FileNotFoundError:
            print("FATAL: The 'ffmpeg' executable was not found. Please install or add it to PATH.")
            exit()
        except PermissionError:
            print("FATAL: Python doesn't have permission to run ffmpeg.exe (check Antivirus).")
            exit()
        except Exception as e:
            print(f"SYSTEM ERROR: Something went wrong starting the process: {e}")
            exit()

        if processing.returncode == 0:
            if encoder == 'hevc_qsv':
                supported.append(long_name[encoder])
                supported.append(long_name['hybrid_hevc_qsv'])
            elif encoder == 'hevc_amf':
                supported.append(long_name[encoder])
                supported.append(long_name['hybrid_hevc_amf'])
            elif encoder == 'hevc_nvenc':
                supported.append(long_name[encoder])
                supported.append(long_name['hybrid_hevc_nvenc'])
                
            elif encoder == 'h264_qsv':
                supported.append(long_name[encoder])
                supported.append(long_name['hybrid_h264_qsv'])
            elif encoder == 'h264_amf':
                supported.append(long_name[encoder])
                supported.append(long_name['hybrid_h264_amf'])
            elif encoder == 'h264_nvenc':
                supported.append(long_name[encoder])
                supported.append(long_name['hybrid_h264_nvenc'])
                
            else:
                supported.append(long_name[encoder])

    if not supported:
        supported.append(no_support)
        return supported
        
    else:
        return supported
        

class CoreTempSharedDataEx(Structure):
    _pack_ = 4
    _fields_ = [
        ("uiLoad",          c_uint * 256),
        ("uiTjMax",         c_uint * 128),
        ("uiCoreCnt",       c_uint),
        ("uiCPUCnt",        c_uint),
        ("fTemp",           c_float * 256),
        ("fVID",            c_float),
        ("fCPUSpeed",       c_float),
        ("fFSBSpeed",       c_float),
        ("fMultiplier",     c_float),
        ("sCPUName",        c_char * 100),
        ("ucFahrenheit",    c_ubyte),
        ("ucDeltaToTjMax",  c_ubyte),
        ("ucTdpSupported",  c_ubyte),
        ("ucPowerSupported",c_ubyte),
        ("uiStructVersion", c_uint),
        ("uiTdp",           c_uint * 128),
        ("fPower",          c_float * 128),
        ("fMultipliers",    c_float * 256),
    ]

def get_cpu_temp():
    kernel = ctypes.windll.kernel32
    kernel.MapViewOfFile.restype = ctypes.c_void_p
    kernel.UnmapViewOfFile.argtypes = [ctypes.c_void_p]
    
    mapping = kernel.OpenFileMappingW(0x0004, False, "CoreTempMappingObjectEx")
    if not mapping:
        return None
    view = kernel.MapViewOfFile(mapping, 0x0004, 0, 0, ctypes.sizeof(CoreTempSharedDataEx))
    if not view:
        kernel.CloseHandle(mapping)
        return None
    data = CoreTempSharedDataEx.from_address(view)
    temps = [data.fTemp[i] for i in range(data.uiCoreCnt)]
    if data.ucFahrenheit:
        temps = [(t - 32) * 5 / 9 for t in temps]
    kernel.UnmapViewOfFile(view)
    kernel.CloseHandle(mapping)
    return max(temps) if temps else None

def get_duration(filename):
    cmd = [
        ffprobe_path, 
        '-v', 'error', 
        '-show_entries', 'format=duration',
        '-of', 'csv=p=0',
        filename
    ]
    
    result = subprocess.run(cmd, capture_output = True, text = True, creationflags=CREATE_NO_WINDOW)
    stdout = result.stdout.strip()
    if stdout and stdout != 'N/A':
        return float(stdout)
    return 1

def get_video_files():
    videoFiles = [f for f in os.listdir('.') if f.endswith(('.mp4', '.mkv', '.avi', '.webm', '.wmv', '.mov', '.ts', '.bin')) and not f.startswith('compressed_')]
    disk = psutil.disk_usage('/')
    free_gb = disk.free / 1024**3
    return videoFiles, free_gb

def get_metadata(file):
        
    cmd = [
        ffprobe_path, 
        '-v', 'error',
        '-select_streams', 'v:0', 
        '-show_entries', 'format=duration,bit_rate:format_tags=major_brand:stream=codec_long_name,pix_fmt,width,height,duration,bit_rate,color_transfer', 
        '-of', 'json', 
        file
    ]
    run = subprocess.run(cmd, capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)
    
    try:
        data = json.loads(run.stdout)
    except json.JSONDecodeError:
        data = {'streams': []}        
    return data
    
def get_images(file, timestamp):
    
    raw_bytes = None
    process = None
    cmd = [
        ffmpeg_path, 
        '-ss',  str(timestamp),
        '-i', file,
        '-vf', 'scale=400:204:force_original_aspect_ratio=decrease',
        '-frames:v', '1',
        '-q:v', '2',
        '-f', 'image2pipe',
        '-vcodec', 'mjpeg', 'pipe:1'
    ]
    
    try:
        process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, creationflags=CREATE_NO_WINDOW)
        raw_bytes = process.stdout
        
        if not raw_bytes:
            print(f"ffmpeg ran the process but returned 0 bytes")
            return None

        pil_image = Image.open(io.BytesIO(raw_bytes))
        return pil_image
            
    except Exception as e:
        if process is None:
            print(f"Error processing the image fetching command")
        else:
            print(f"Error fetching or converting image: {e}")
        return None
        
def encode (file, encoding_choice, pxlfmt, outputName, quality, resolution, fps, color_transfer, original_pxl):
    
    if 'HEVC_QSV' in encoding_choice:
        qsv_vf = ''
        
        if pxlfmt != 'Orig':
            qsv_vf = f'vpp_qsv=format={pxlfmt}'
            
        if resolution != 'Orig':
            if qsv_vf:
                qsv_vf += ','
            qsv_vf += f'scale_qsv=w=-1:h={resolution}'
            
        if fps != 'Orig':
            if qsv_vf:
                qsv_vf += ','
            qsv_vf += f'vpp_qsv=framerate={fps}'

        cmd = [
            ffmpeg_path, 
            '-hwaccel', 'qsv',
            '-hwaccel_output_format', 'qsv',
            '-i', file,            
            '-c:v', 'hevc_qsv',
            '-preset', 'medium',     
            '-global_quality', f'{quality}',            
            '-color_range', 'tv',       
            '-c:a', 'copy',
            '-y', outputName
        ]
        
        if qsv_vf:
            cmd.insert(7, '-vf')
            cmd.insert(8, qsv_vf)
        
        if fps == 'Orig':
            idx = 15 if qsv_vf else 13
            cmd.insert(idx, '-fps_mode')
            cmd.insert(idx+1, 'passthrough')
            
    elif 'Intel QSV Hybrid' in encoding_choice:
        vf_qsv_hybrid = ''
        
        if pxlfmt != 'Orig':
            vf_qsv_hybrid = f'format={pxlfmt},hwupload,vpp_qsv=format={pxlfmt}'
            
        if resolution != 'Orig':
            if vf_qsv_hybrid:
                vf_qsv_hybrid += ','
            vf_qsv_hybrid += f'scale_qsv=w=-1:h={resolution}'
            
        if fps != 'Orig':
            if vf_qsv_hybrid:
                vf_qsv_hybrid += ','
            vf_qsv_hybrid += f'vpp_qsv=framerate={fps}'

        cmd = [
            ffmpeg_path,
            '-init_hw_device', 'qsv=hw',
            '-filter_hw_device', 'hw',
            '-i', file,
            '-c:v', 'hevc_qsv',
            '-preset', 'medium',
            '-global_quality', f'{quality}',
            '-fps_mode', 'passthrough' if fps == 'Orig' else 'cfr',
            '-color_range', '1',       
            '-c:a', 'aac',
            '-y', outputName
        ]
        
        if vf_qsv_hybrid:
            cmd.insert(7, '-vf')
            cmd.insert(8, vf_qsv_hybrid)
        
        if pxlfmt == 'nv12':
            idx = 19 if vf_qsv_hybrid else 17
            cmd.insert(idx, '-colorspace')
            cmd.insert(idx+1, 'bt709')
            cmd.insert(idx+2, '-color_primaries')
            cmd.insert(idx+3, 'bt709')
    
    elif 'H.264_QSV' in encoding_choice:

        h264_qsv_vf = f'vpp_qsv=format={pxlfmt}'
        if resolution != 'Orig':
            h264_qsv_vf += f',scale_qsv=w=-1:h={resolution}'
        if fps != 'Orig':
            h264_qsv_vf += f',vpp_qsv=framerate={fps}'

        cmd = [
            ffmpeg_path,
            '-hwaccel', 'qsv',
            '-hwaccel_output_format', 'qsv',
            '-i', file,
            '-vf', h264_qsv_vf,
            '-c:v', 'h264_qsv',
            '-preset', 'medium',
            '-global_quality', f'{quality}',
            '-color_range', 'tv',
            '-c:a', 'copy',
            '-y', outputName
        ]

        if fps == 'Orig':
            cmd.insert(15, '-fps_mode')
            cmd.insert(16, 'passthrough')
            
    elif 'AVC-QSV Hybrid' in encoding_choice:

        vf_h264_qsv_hybrid = f'format={pxlfmt},hwupload,vpp_qsv=format={pxlfmt}'
        if resolution != 'Orig':
            vf_h264_qsv_hybrid += f',scale_qsv=w=-1:h={resolution}'
        if fps != 'Orig':
            vf_h264_qsv_hybrid += f',vpp_qsv=framerate={fps}'

        cmd = [
            ffmpeg_path,
            '-init_hw_device', 'qsv=hw',
            '-filter_hw_device', 'hw',
            '-i', file,
            '-vf', vf_h264_qsv_hybrid,
            '-c:v', 'h264_qsv',
            '-preset', 'medium',
            '-global_quality', f'{quality}',
            '-fps_mode', 'passthrough' if fps == 'Orig' else 'cfr',
            '-color_range', '1',
            '-c:a', 'aac',
            '-y', outputName
        ]

        if pxlfmt == 'nv12':
            cmd.insert(19, '-colorspace')
            cmd.insert(20, 'bt709')
            cmd.insert(21, '-color_primaries')
            cmd.insert(22, 'bt709')
        
    elif 'HEVC_AMF' in encoding_choice:
        
        is_10bit = original_pxl in ('yuv420p10le', 'yuv420p10be','yuv422p10le', 
        'yuv422p10be', 'yuv444p10le', 'yuv444p10be','p010le', 'p010be', 'p210le', 
        'p210be', 'p410le', 'p410be','y210le', 'y210be','y410le', 'y410be','v210',
        'yuva420p10le', 'yuva420p10be','yuva422p10le', 'yuva422p10be','yuva444p10le',
        'yuva444p10be')
        
        is_8bit = original_pxl in ('yuv420p', 'yuv422p', 'yuv444p','nv12', 'nv21',
        'yuyv422', 'uyvy422', 'yuv411p', 'yuv410p','yuvj420p', 'yuvj422p', 'yuvj444p',
        'yuva420p', 'yuva422p', 'yuva444p','gray', 'monow', 'monob')
        
        if is_10bit:
            pxl = 'p010le'
        elif is_8bit:
            pxl = 'nv12'
        else:
            return None, None
            
        cmd = [
            ffmpeg_path,
            '-hwaccel', 'd3d11va',
            '-hwaccel_output_format', pxl,
            '-i', file,
            '-c:v', 'hevc_amf',
            '-rc', 'cqp',
            '-qp_i', f'{quality}',
            '-qp_p', f'{quality}',
            '-quality', 'balanced',
            '-c:a', 'copy',
            '-y', outputName
        ]
        
        if fps == 'Orig':
            cmd.insert(17, '-fps_mode')
            cmd.insert(18, 'passthrough')
        else:
            cmd.insert(17, '-r')
            cmd.insert(18, str(fps))
            
            
    elif 'AMD AMF Hybrid' in encoding_choice:
        vf_amf_hybrid = ''
        
        is_10bit = original_pxl in ('yuv420p10le', 'yuv420p10be','yuv422p10le', 
        'yuv422p10be', 'yuv444p10le', 'yuv444p10be','p010le', 'p010be', 'p210le', 
        'p210be', 'p410le', 'p410be','y210le', 'y210be','y410le', 'y410be','v210',
        'yuva420p10le', 'yuva420p10be','yuva422p10le', 'yuva422p10be','yuva444p10le',
        'yuva444p10be')
        
        is_8bit = original_pxl in ('yuv420p', 'yuv422p', 'yuv444p','nv12', 'nv21',
        'yuyv422', 'uyvy422', 'yuv411p', 'yuv410p','yuvj420p', 'yuvj422p', 'yuvj444p',
        'yuva420p', 'yuva422p', 'yuva444p','gray', 'monow', 'monob')
        
        if resolution != 'Orig':
            vf_amf_hybrid = f'scale=-1:{resolution}'
        
        if pxlfmt != 'Orig':
            if pxlfmt == 'nv12':
                if vf_amf_hybrid:
                    vf_amf_hybrid += ','
                if color_transfer in ('smpte2084', 'arib-std-b67'):
                    vf_amf_hybrid += f'zscale=t=linear:npl=100,tonemap=reinhard:desat=0,zscale=p=bt709:t=bt709:m=bt709:r=tv,format=nv12,hwupload=derive_device=d3d11va'
                else:
                    vf_amf_hybrid += f'format=nv12,hwupload=derive_device=d3d11va'
                    
            elif pxlfmt == 'p010le':
                if vf_amf_hybrid:
                    vf_amf_hybrid += ','
                if color_transfer not in ('smpte2084', 'arib-std-b67'):
                    vf_amf_hybrid += f'zscale=p=bt2020:t=smpte2084:m=bt2020nc,format=p010le,hwupload=derive_device=d3d11va'
                else:
                    vf_amf_hybrid += f'format=p010le,hwupload=derive_device=d3d11va'
                    
        else:
            if vf_amf_hybrid:
                vf_amf_hybrid += ','
            if is_8bit:
                vf_amf_hybrid += f'format=nv12,hwupload=derive_device=d3d11va'
            elif is_10bit:
                vf_amf_hybrid += f'format=p010le,hwupload=derive_device=d3d11va'
            else:
                return None, None

        cmd = [
            ffmpeg_path,
            '-init_hw_device', 'd3d11va=dx',
            '-i', file,
            '-vf', vf_amf_hybrid,
            '-c:v', 'hevc_amf',
            '-rc', 'cqp',
            '-qp_i', f'{quality}',
            '-qp_p', f'{quality}',
            '-quality', 'balanced',
            '-fps_mode' if fps == 'Orig' else '-r', 'passthrough' if fps == 'Orig' else str(fps),
            '-c:a', 'aac',
            '-y', outputName
        ]
        
    
    elif 'H.264_AMF' in encoding_choice:

        cmd = [
            ffmpeg_path,
            '-hwaccel', 'd3d11va',
            '-hwaccel_output_format', 'nv12',
            '-i', file,
            '-c:v', 'h264_amf',
            '-rc', 'cqp',
            '-qp_i', f'{quality}',
            '-qp_p', f'{quality}',
            '-quality', 'balanced',
            '-c:a', 'copy',
            '-y', outputName
        ]

        if fps == 'Orig':
            cmd.insert(13, '-fps_mode')
            cmd.insert(14, 'passthrough')
        else:
            cmd.insert(13, '-r')
            cmd.insert(14, str(fps))
            
    elif 'AVC-AMF Hybrid' in encoding_choice:
        vf_amf_avc_hybrid = ''
        
        if resolution != 'Orig':
            vf_amf_avc_hybrid = f'scale=-1:{resolution}'

        if vf_amf_avc_hybrid:
            vf_amf_avc_hybrid += ','
            
        if color_transfer in ('smpte2084', 'arib-std-b67'):
            vf_amf_avc_hybrid += f'zscale=t=linear:npl=100,tonemap=reinhard:desat=0,zscale=p=bt709:t=bt709:m=bt709:r=tv,format=nv12,hwupload=derive_device=d3d11va'
        else:
            vf_amf_avc_hybrid += f'format=nv12,hwupload=derive_device=d3d11va'

        cmd = [
            ffmpeg_path,
            '-init_hw_device', 'd3d11va=dx',
            '-i', file,
            '-vf', vf_amf_avc_hybrid,
            '-c:v', 'h264_amf',
            '-rc', 'cqp',
            '-qp_i', f'{quality}',
            '-qp_p', f'{quality}',
            '-quality', 'balanced',
            '-fps_mode' if fps == 'Orig' else '-r', 'passthrough' if fps == 'Orig' else str(fps),
            '-c:a', 'aac',
            '-y', outputName
        ]
    
    elif 'HEVC_NVENC' in encoding_choice:
        vf_hevc_nvenc = ""
        
        is_8bit = original_pxl in ('yuv420p', 'yuv422p', 'yuv444p','nv12', 'nv21',
        'yuyv422', 'uyvy422', 'yuv411p', 'yuv410p','yuvj420p', 'yuvj422p', 'yuvj444p',
        'yuva420p', 'yuva422p', 'yuva444p','gray', 'monow', 'monob')
        
        if resolution != 'Orig':
            vf_hevc_nvenc = f"scale_cuda=-1:{resolution}"

        cmd = [
            ffmpeg_path,
            '-hwaccel', 'cuda',
            '-hwaccel_output_format', 'cuda',
            '-i', file,
            '-c:v', 'hevc_nvenc',
            '-preset', 'p4',
            '-cq', f'{quality}',
            '-c:a', 'copy',
            '-y', outputName
        ]
        
        if resolution != 'Orig':
            cmd.insert(7, '-vf')
            cmd.insert(8, vf_hevc_nvenc)
        
        if fps == 'Orig':
            idx = 15 if resolution != 'Orig' else 13
            cmd.insert(idx, '-fps_mode')
            cmd.insert(idx+1, 'passthrough')
        else:
            idx = 15 if resolution != 'Orig' else 13
            cmd.insert(idx, '-r')
            cmd.insert(idx+1, str(fps))
            
        if is_8bit:
            idx = 17 if resolution != 'Orig' else 15
            cmd.insert(idx, '-color_range')
            cmd.insert(idx+1, '1')
            cmd.insert(idx+2, '-colorspace')
            cmd.insert(idx+3, 'bt709')
            cmd.insert(idx+4, '-color_primaries')
            cmd.insert(idx+5, 'bt709')
                        
    elif 'NV NVENC Hybrid' in encoding_choice:
        vf_nvenc_hybrid = ""
        
        if resolution != 'Orig':
            vf_nvenc_hybrid = f'scale=-1:{resolution}'
            
        if pxlfmt != 'Orig':
            if vf_nvenc_hybrid:
                vf_nvenc_hybrid += ","
            vf_nvenc_hybrid += f'format={pxlfmt},hwupload_cuda'
        else:
            if vf_nvenc_hybrid:
                vf_nvenc_hybrid += ","
            vf_nvenc_hybrid += f'format={original_pxl},hwupload_cuda'

        if fps != 'Orig':
            vf_nvenc_hybrid += f',fps={fps}'

        cmd = [
            ffmpeg_path,
            '-i', file,
            '-vf', vf_nvenc_hybrid,
            '-c:v', 'hevc_nvenc',
            '-preset', 'p4',
            '-cq', f'{quality}',
            '-fps_mode', 'passthrough' if fps == 'Orig' else 'cfr',
            '-c:a', 'aac',
            '-y', outputName
        ]
        
        if pxlfmt == 'nv12':
            cmd.insert(9, '-colorspace')
            cmd.insert(10, 'bt709')
            cmd.insert(11, '-color_primaries')
            cmd.insert(12, 'bt709')
            cmd.insert(13, '-color_range')
            cmd.insert(14, '1')
            
    elif 'H.264_NVENC' in encoding_choice:
        vf_avc_nvenc = ""
        
        if resolution != 'Orig':
            vf_avc_nvenc = f"scale_cuda=-1:{resolution}"

        cmd = [
            ffmpeg_path,
            '-hwaccel', 'cuda',
            '-hwaccel_output_format', 'cuda',
            '-i', file,
            '-c:v', 'h264_nvenc',
            '-preset', 'p4',
            '-cq', f'{quality}',
            '-color_range', '1',
            '-colorspace', 'bt709',
            '-color_primaries', 'bt709',
            '-c:a', 'copy',
            '-y', outputName
        ]
        
        if resolution != 'Orig':
            cmd.insert(7, '-vf')
            cmd.insert(8, vf_avc_nvenc)
        
        if fps == 'Orig':
            idx = 15 if resolution != 'Orig' else 13
            cmd.insert(idx, '-fps_mode')
            cmd.insert(idx+1, 'passthrough')
        else:
            idx = 15 if resolution != 'Orig' else 13
            cmd.insert(idx, '-r')
            cmd.insert(idx+1, str(fps))
            
    elif 'AVC-NVENC Hybrid' in encoding_choice:

        vf_h264_nvenc_hybrid = f'format=nv12,hwupload_cuda'
        if resolution != 'Orig':
            vf_h264_nvenc_hybrid = f'scale=-1:{resolution},format=nv12,hwupload_cuda'
        if fps != 'Orig':
            vf_h264_nvenc_hybrid += f',fps={fps}'

        cmd = [
            ffmpeg_path,
            '-i', file,
            '-vf', vf_h264_nvenc_hybrid,
            '-c:v', 'h264_nvenc',
            '-preset', 'p4',
            '-color_range', '1',
            '-colorspace', 'bt709',
            '-color_primaries', 'bt709',
            '-cq', f'{quality}',
            '-fps_mode', 'passthrough' if fps == 'Orig' else 'cfr',
            '-c:a', 'aac',
            '-y', outputName
        ]
            
    elif 'AVC/H.264' in encoding_choice or 'HEVC/H.265' in encoding_choice:
        legacy_vf = ''
        pxl_lib_map= {
                    'Orig':'Orig',
                    'nv12':'nv12',
                    'p010le':'yuv420p10le',
                    'p012le':'yuv420p12le'
                    }
        
        if pxlfmt != 'Orig':
            legacy_vf = f'format={pxl_lib_map[pxlfmt]}'
            
        if resolution != 'Orig':
            if legacy_vf:
                legacy_vf += ','
            legacy_vf += f'scale=-1:{resolution}'
            
        if fps != 'Orig':
            if legacy_vf:
                legacy_vf += ','
            legacy_vf += f'fps={fps}'

        codec = 'libx264' if 'AVC/H.264' in encoding_choice else 'libx265'
        
        cmd = [
            ffmpeg_path,
            '-i', file,
            '-c:v', codec,
            '-preset', 'medium',
            '-crf', f'{quality}',
            '-fps_mode', 'passthrough' if fps == 'Orig' else 'cfr',
            '-c:a', 'aac',
            '-y', outputName
        ]
        
        if legacy_vf:
            cmd.insert(3, '-vf')
            cmd.insert(4, legacy_vf)
        
        if pxlfmt == 'nv12':
            idx = 9 if legacy_vf else 7
            cmd.insert(idx, '-colorspace')
            cmd.insert(idx+1, 'bt709')
            cmd.insert(idx+2, '-color_primaries')
            cmd.insert(idx+3, 'bt709')
            cmd.insert(idx+4, '-color_range')
            cmd.insert(idx+5, '1')

    try:
        processing = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=CREATE_NO_WINDOW)
        ps_process = psutil.Process(processing.pid)
    except FileNotFoundError:
        print("Unable to encode the file...")
        exit()
    return processing, ps_process