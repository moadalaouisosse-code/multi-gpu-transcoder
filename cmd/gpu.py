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


encoders = ['hevc_qsv', 'hevc_amf', 'hevc_nvenc']
supported = []
encoding_choice = ""
long_name = {
'hevc_qsv':'Intel Quick Sync Video (HEVC_QSV)',
'hevc_amf':'AMD Advanced Media Framework (HEVC_AMF)',
'hevc_nvenc':'NVIDIA Video Encoder (HEVC_NVENC)'
}


for encoder in encoders:

    cmd = ['ffmpeg', '-hide_banner', '-f', 'lavfi', '-i', 'nullsrc', '-c:v', encoder, '-frames:v', '1', '-f', 'null', '-']
    try:
        processing = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
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
        supported.append(long_name[encoder])


if not supported:
    print("No HW support.")
    exit()
    
elif len(supported) == 1:
    print(f"""
    Your supported encoder:
    {Fore.CYAN}{Style.BRIGHT}{supported[0]}""")
    encoding_choice = re.search(r'\((.*?)\)', supported[0]).group(1)
    
else:
    print("""
    Your supported encoders, pick your :""")
    choices = {chr(97 + i): item for i, item in enumerate(supported)}
    
    for key, val in choices.items():
        print(f"""
    {key}- {Fore.CYAN}{Style.BRIGHT}{val}{Fore.RESET}
    """)
    
    input_key = input("\nChoice:").strip().lower()

    if input_key in choices:
        encoding_choice = re.search(r'\((.*?)\)', choices[input_key]).group(1)
    else:
        encoding_choice = re.search(r'\((.*?)\)', supported[0]).group(1)
        
if encoding_choice == 'HEVC_QSV':
        cmd = ['ffmpeg', '-init_hw_device', 'qsv=hw', '-hide_banner']
        
elif encoding_choice == 'HEVC_AMF':
    cmd = ['ffmpeg', '-init_hw_device', 'amf=hw','-hide_banner']
    
elif encoding_choice == 'HEVC_NVENC':
    cmd = ['ffmpeg', '-init_hw_device', 'cuda=hw','-hide_banner']
    
try:
    hw_processing = subprocess.run(cmd, capture_output=True, text=True)
    print(f"\n{Fore.LIGHTYELLOW_EX}{hw_processing.stderr}")
except Exception as e:
    print(f"\n{Fore.LIGHTRED_EX}{Style.BRIGHT}Chip name is unknown...")
        


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

videoFiles = [f for f in os.listdir('.') if f.endswith(('.mp4', '.mkv', '.avi', '.webm', '.wmv', '.mov', '.ts', '.bin')) and not f.startswith('compressed_')]
disk = psutil.disk_usage('/')
free_gb = disk.free / 1024**3

failed = []
        
print(f"\nthere are {Fore.CYAN}{len(videoFiles)} {Fore.RESET}video file(s) and there is {Fore.CYAN}{free_gb:.2f} {Fore.RESET}free gb")

for file in videoFiles:
    currentFree = psutil.disk_usage('/').free / 1024**3
    
    if currentFree < 1.0:
        print(f"{Fore.LIGHTRED_EX}{Style.BRIGHT}warning: not enough space habibi, you need 1GB at least")
        break

    outputName = "compressed_" + os.path.splitext(file)[0] + ".mp4"
    total_sec = get_duration(file)
    
    cmd = [
        'ffprobe', 
        '-v', 'error',
        '-select_streams', 'v:0', 
        '-show_entries', 'format_tags=major_brand:stream=codec_long_name,pix_fmt,width,height,duration,bit_rate', 
        '-of', 'json', 
        file
    ]
    
    run = subprocess.run(cmd, capture_output=True, text=True)
    try:
        data = json.loads(run.stdout)
    except json.JSONDecodeError:
        print(f"Could not parse metadata for {Fore.LIGHTRED_EX}{file}{Fore.RESET}, continuing anyway...")
        data = {'streams': []}
    
    if data['streams']:
        
        try:
            bitrate = int(data['streams'][0].get('bit_rate', 0)) // 1000
            bitrate_display = f"{bitrate}kbps." if bitrate > 0 else "N/A"
            duration = str(datetime.timedelta(seconds= int(float(data['streams'][0].get('duration', 0)))))
            pix_fmt = data['streams'][0].get('pix_fmt', 'unknown')
            width = data['streams'][0].get('width', 'N/A')
            height = data['streams'][0].get('height', 'N/A')
            codec = data['streams'][0].get('codec_long_name', 'unknown')
            major_brand = data.get('format', {}).get('tags', {}).get('major_brand', 'Unknown')    
        
            print(f"""
        Current file: {Fore.CYAN}{Style.BRIGHT}{file} {Fore.RESET}
        Resolution: {width} x {height}.
        Codec: {codec}.
        Pixel Format: {Fore.CYAN}{Style.BRIGHT}{pix_fmt}{Fore.RESET}.  
        Bitrate: {bitrate_display}.
        Major Brand: {major_brand}.
        Duration: {duration}.
            """)
        except (KeyError, IndexError, ValueError):
            print(f"Could not read stream info for {Fore.LIGHTRED_EX}{file}{Fore.RESET}, continuing anyway...")
    
    pixel_choice = input(f"""
Choose the pixel format:

{Fore.CYAN}a){Fore.RESET} 8 bits. (default)
{Fore.CYAN}b){Fore.RESET} 10 bits.
{Fore.CYAN}c){Fore.RESET} 12 bits.
{Fore.CYAN}d){Fore.RESET} Skip.
{Fore.LIGHTRED_EX}e){Fore.RESET} Exit.  
Your choice: """).strip().lower()

    pxlfmt='nv12'
    if pixel_choice=='a':
        pxlfmt='nv12'
    if pixel_choice=='b':
        pxlfmt='p010le'
    if pixel_choice=='c':
        pxlfmt='p012le'
    if pixel_choice=='d':
        continue
    if pixel_choice=='e':
        exit()
    if pixel_choice not in ('a','b','c','d','e'):
        print("Invalid input. Defaulting to 8 bits...")

    if encoding_choice == 'HEVC_QSV':
        cmd = [
            'ffmpeg', 
            '-hwaccel', 'qsv',
            '-hwaccel_output_format', 'qsv',
            '-i', file,
            '-vf', f'vpp_qsv=format={pxlfmt}',
            '-c:v', 'hevc_qsv',
            '-preset', 'medium',     
            '-global_quality', '20',            
            '-fps_mode', 'passthrough',
            '-color_range', 'tv',       
            '-c:a', 'copy',
            '-y', outputName
        ]
    elif encoding_choice == 'HEVC_AMF':
        cmd = [
            'ffmpeg',   
            '-hwaccel', 'd3d11va',
            '-hwaccel_output_format', 'd3d11',
            '-i', file,
            '-vf', f'format={pxlfmt},hwupload',
            '-c:v', 'hevc_amf',
            '-rc', 'cqp',
            '-qp_i', '20',
            '-qp_p', '20',
            '-quality', 'balanced',                 
            '-fps_mode', 'passthrough',
            '-c:a', 'copy',
            '-y', outputName
        ]
    elif encoding_choice == 'HEVC_NVENC':
        cmd = [
            'ffmpeg',
            '-hwaccel', 'cuda',
            '-hwaccel_output_format', 'cuda',
            '-i', file,
            '-vf', f'scale_cuda=format={pxlfmt}',
            '-c:v', 'hevc_nvenc',
            '-preset', 'p4',
            '-cq', '20',
            '-fps_mode', 'passthrough',
            '-c:a', 'copy',
            '-y', outputName
        ]
    
    print(f"\nProcessing: {Fore.CYAN}{Style.BRIGHT}{file} {Fore.RESET}...\n")
    
    try:
        processing = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        ps_process = psutil.Process(processing.pid)
    except FileNotFoundError:
        print(f"{Fore.LIGHTRED_EX}{Style.BRIGHT}Unable to encode the file...")
        failed.append({'file': file, 'pixel format': pxlfmt})
        continue
    
    pbar = tqdm(total=100, unit='%', colour='#ffe4d9', bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}% [{elapsed}]')
    last_pct = 0
    
    if processing:
        for line in processing.stdout:
            temp = get_cpu_temp()
            
            if temp is not None and temp > 65:
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
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{outputName} {Fore.RESET}is successfully compressed habibi, please check your folder! <3")
        sys.stdout.write('\a')
    else:
        pbar.close()
        print(f"\n{Fore.LIGHTRED_EX}{Style.BRIGHT}an error has occured, file encoding has failed!")
        failed.append({'file' : file, 'pixel format' : pxlfmt, 'codec' : encoding_choice})
        if os.path.exists(outputName):
            os.remove(outputName)
       
if failed:
    forward_choice = input(f"""
Would you like to encode the failed with the alternative encoder?
{Fore.CYAN}{Style.BRIGHT}Y{Fore.RESET} / {Fore.LIGHTRED_EX}{Style.BRIGHT}N{Fore.RESET}
Your choice (Default: N): """).strip().lower()

    if forward_choice=='y':
        try:
            subprocess.run(['python', 'cpuGpu.py', json.dumps(failed)])
        except FileNotFoundError:
            print(f"{Fore.LIGHTRED_EX}{Style.BRIGHT} Failing forwarding towards the alternative encoder...")
    else:
        print(f"you can always encode the failed files using {Fore.CYAN}{Style.BRIGHT}manualcpuQsv{Fore.RESET} at anytime. have a nice day!")