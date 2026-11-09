import os
import subprocess
import psutil
import sys
import re
import json
import time
import datetime
import ctypes
from ctypes import Structure, c_float, c_uint, c_ubyte, c_char
from tqdm import tqdm
from colorama import Fore, Style, init
init(autoreset=True)



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
        'ffprobe', 
        '-v', 'error', 
        '-show_entries', 'format=duration',
        '-of', 'csv=p=0',
        filename
    ]
    
    result = subprocess.run(cmd, capture_output = True, text = True)
    stdout = result.stdout.strip()
    if stdout and stdout != 'N/A':
        return float(stdout)
    return 1
    
video_files = json.loads(sys.argv[1]) if len(sys.argv) > 1 else []

if video_files:
    for row in video_files:
        
        file = row['file']
        pxlfmt = row['pixel format'].lower()
        codec = row['codec'].lower()
        currentFree = psutil.disk_usage('/').free / 1024**3
        
        if currentFree < 1.0:
            print(f"{Fore.LIGHTRED_EX}{Style.BRIGHT}warning: not enough space habibi, you need 1GB at least")
            break
        
        outputName = "compressed_" + os.path.splitext(file)[0] + ".mp4"
        total_sec = get_duration(file)
        
        if codec == 'hevc_qsv':
            if pxlfmt == 'nv12':
                cmd = [
                    'ffmpeg',
                    '-init_hw_device', 'qsv=hw',
                    '-filter_hw_device', 'hw',
                    '-i', file,
                    '-vf', 'format=nv12,hwupload,vpp_qsv=format=nv12',
                    '-c:v', 'hevc_qsv',
                    '-preset', 'medium',
                    '-global_quality', '20',
                    '-fps_mode', 'passthrough',
                    '-color_range', '1',       
                    '-colorspace', 'bt709',      
                    '-color_primaries', 'bt709',
                    '-c:a', 'aac',
                    '-y', outputName
                ]

            elif pxlfmt in ['p010le' , 'p012le']:
                cmd = [
                    'ffmpeg',
                    '-init_hw_device', 'qsv=hw',
                    '-filter_hw_device', 'hw',
                    '-i', file,
                    '-vf', f'format={pxlfmt},hwupload,vpp_qsv=format={pxlfmt}',
                    '-c:v', 'hevc_qsv',
                    '-preset', 'medium',
                    '-global_quality', '20',
                    '-fps_mode', 'passthrough',
                    '-color_range', '1',
                    '-c:a', 'aac',
                    '-y', outputName
                ]

        elif codec == 'hevc_amf':
            if pxlfmt == 'nv12':
                cmd = [
                    'ffmpeg',
                    '-i', file,
                    '-vf', 'format=nv12,hwupload',
                    '-c:v', 'hevc_amf',
                    '-rc', 'cqp',
                    '-qp_i', '20',
                    '-qp_p', '20',
                    '-quality', 'balanced',
                    '-fps_mode', 'passthrough',
                    '-c:a', 'aac',
                    '-y', outputName
                ]
                
            elif pxlfmt in ['p010le', 'p012le']:
                cmd = [
                    'ffmpeg',
                    '-i', file,
                    '-vf', f'format={pxlfmt},hwupload',
                    '-c:v', 'hevc_amf',
                    '-rc', 'cqp',
                    '-qp_i', '20',
                    '-qp_p', '20',
                    '-quality', 'balanced',
                    '-fps_mode', 'passthrough',
                    '-c:a', 'aac',
                    '-y', outputName
                ]
                
        elif codec == 'hevc_nvenc':
            if pxlfmt == 'nv12':
                cmd = [
                    'ffmpeg',
                    '-i', file,
                    '-vf', 'format=nv12,hwupload_cuda',
                    '-c:v', 'hevc_nvenc',
                    '-preset', 'p4',
                    '-cq', '20',
                    '-fps_mode', 'passthrough',
                    '-c:a', 'aac',
                    '-y', outputName
                ]
            elif pxlfmt in ['p010le', 'p012le']:
                cmd = [
                    'ffmpeg',
                    '-i', file,
                    '-vf', f'format={pxlfmt},hwupload_cuda',
                    '-c:v', 'hevc_nvenc',
                    '-preset', 'p4',
                    '-cq', '20',
                    '-fps_mode', 'passthrough',
                    '-c:a', 'aac',
                    '-y', outputName
                ]
        
        else:
            print(f"{Fore.LIGHTRED_EX}Unknown codec {codec}, skipping...")
            continue
        
        print(f"Processing: {Fore.CYAN}{Style.BRIGHT}{file} {Fore.RESET}...")
        
        try:   
            processing = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            ps_process = psutil.Process(processing.pid)
        except FileNotFoundError:
            print("FATAL: The 'ffmpeg' executable was not found. Please install or add it to PATH.")
            exit()
        except PermissionError:
            print("FATAL: Python doesn't have permission to run ffmpeg.exe (check Antivirus).")
            exit()
        except Exception as e:
            print(f"SYSTEM ERROR: Something went wrong starting the process: {e}")
            continue
        
        pbar = tqdm(total=100, unit='%', colour='#ffe4d9', bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}% [{elapsed}]')
        last_pct = 0
        for line in processing.stdout:
            temp = get_cpu_temp()
            
            if temp is not None and temp > 85:
                ps_process.suspend()
                pbar.write(f"{Fore.LIGHTRED_EX}{Style.BRIGHT}Computer is too hot, pausing the encoding for a while... ({Fore.RESET}{temp}°C{Fore.LIGHTRED_EX}{Style.BRIGHT})")
                while temp > 50:
                    time.sleep(5)
                    temp = get_cpu_temp()
                pbar.write(f"{Fore.CYAN}{Style.BRIGHT}Computer has cooled down, resuming the encoding now... ({Fore.RESET}{temp}°C{Fore.CYAN}{Style.BRIGHT})")
                ps_process.resume()

            match = re.search(r"time=(\d+):(\d+):(\d+\.\d+)", line)
            if match:
                h, m, s = map(float, match.groups())
                current_sec = (h * 3600) + (m * 60) + s
                pct = min(int((current_sec / total_sec) * 100), 100)
                pbar.update(pct - last_pct)
                last_pct = pct
            
        processing.wait()
        
        if processing.returncode == 0 and os.path.exists(outputName):
            pbar.n = 100
            pbar.refresh()
            pbar.close()
            print(f"{Fore.CYAN}{Style.BRIGHT}{outputName} {Fore.RESET}is successfully compressed habibi, please check your folder! <3")
            sys.stdout.write('\a')
        else:
            pbar.close()
            print(f"{Fore.LIGHTRED_EX}{Style.BRIGHT}an error has occured, file encoding has failed!")
            if os.path.exists(outputName):
                os.remove(outputName)