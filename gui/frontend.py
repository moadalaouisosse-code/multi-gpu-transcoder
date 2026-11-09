from backend import detect_encoders, get_video_files, get_metadata, get_duration, get_cpu_temp, get_images, encode
import taskbar_class
from popups_class import alertpopup
import customtkinter as ctk
import os
import re
import sys
import threading
import time
import datetime
from tkinter import filedialog
import ctypes

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))
    
icon_path = os.path.join(base_path, 'icon.ico')



video_files, free_space = get_video_files()
results = detect_encoders()
file = None
saveas = None
suggested_name = ""
root = "Compressed video"
abort_flag = False
pause_flag = False
ps_process = None
processing = None
current_quality_value = 20
total_sec = None
data = []
temp_current_value = 85
color_transfer = ""
original_pxl = ""

#translation for known brands
brand_names = {
    'isom': 'MP4',
    'mp42': 'MP4',
    'avc1': 'MP4',
    'qt  ': 'MOV (QuickTime)',
    'M4V ': 'M4V (iTunes)',
    'matroska': 'MKV',
    'webm': 'WebM',
    'msnv': 'MP4 (Sony)',
    'f4v ': 'F4V (Flash)',
}

#pixel format dictionary
format_info = {
    'yuv420p':    "8-bit · Standard SDR · Most compatible",
    'yuv420p10le':"10-bit · HDR capable · Wider color range",
    'yuv420p12le':"12-bit · High precision HDR · Cinema grade",
    'yuv422p':    "8-bit · Broadcast standard · No vertical subsampling",
    'yuv422p10le':"10-bit · Broadcast HDR · Professional editing",
    'yuv444p':    "8-bit · Full chroma · No subsampling loss",
    'yuv444p10le':"10-bit · Full chroma HDR · Maximum quality",
    'nv12':       "8-bit · GPU optimized · Hardware accelerated",
    'p010le':     "10-bit · GPU optimized · Hardware accelerated HDR",
    'yuvj420p':   "8-bit · Full range SDR · Legacy JPEG standard",
    'yuvj422p':   "8-bit · Full range broadcast · Legacy JPEG standard",
    'yuvj444p':   "8-bit · Full range chroma · Legacy JPEG standard",
    'yuv422p12le':"12-bit · Ultra-high precision · Professional broadcast",
    'yuv444p12le':"12-bit · Full chroma cinema · Maximum master quality",
    'nv16':       "8-bit · Hardware accelerated · 4:2:2 subsampling",
    'nv21':       "8-bit · Hardware accelerated · VU interleaved",
    'nv20le':     "10-bit · Hardware accelerated · 4:2:2 packed",
    'p012le':     "12-bit · GPU optimized · Hardware accelerated HDR",
    'gray':       "8-bit · Pure monochrome · No color data",
    'gray10le':   "10-bit · High-depth monochrome · Smooth gradients",
    'gray12le':   "12-bit · Cinema monochrome · Maximum shading detail",
    'gbrp':       "8-bit · Planar RGB · No chroma subsampling",
    'gbrp10le':   "10-bit · Planar RGB HDR · Graphics & grading master",
    'gbrp12le':   "12-bit · Planar RGB cinema · Ultimate color precision",
    'bgra':       "8-bit · Packed RGB with Alpha · UI & screen capture",
    'x2rgb10le':  "10-bit · Packed RGB · High-depth UI & desktop",
    'yuva420p':   "8-bit · Video with Alpha · Transparent overlays",
    'yuva420p10le':"10-bit · HDR Video with Alpha · Vis eff. mastering",
    'yuyv422':    "8-bit · Packed YUYV · Standard capture & webcam",
    'y210le':     "10-bit · Packed YUYV · High-depth capture",
    'vuyx':       "8-bit · Packed VUYX · Hardware capture standard",
    'xv30le':     "10-bit · Packed YUV 4:4:4 · Ultra-low latency HDR",
    'qsv':        "Hardware specific · Intel QuickSync native surface"
}

#resolution map
resolution_map = {
                'Orig': 'Orig',
                '4k': '2160',
                '2k': '1440',
                '1080p': '1080',
                '720p': '720'
                }

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Encoder")
app.geometry("1000x675")
app.resizable(False, False)
app.iconbitmap(icon_path)
app.update()

  
hwnd = ctypes.windll.user32.GetParent(app.winfo_id()) or app.winfo_id()
taskbar = taskbar_class.get_taskbar()
    


#file frame, equivalent of div in html / priority is based on the code order
folder_select_frame = ctk.CTkFrame(app, height=30)
folder_select_frame.pack(side="bottom", fill="x", pady=(0, 10), padx=10, expand=False)


file_frame = ctk.CTkFrame(app, width=600)
file_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

ctk.CTkLabel(file_frame, text = f"You have {free_space:.2f} GB of free space.", text_color="#888888", font=("Arial", 13)).pack(padx=5, pady=5)


def window_is_visible():
    return app.state() != 'iconic' and app.focus_displayof() is not None
 
 
def recursive_callback():
    
    if not window_is_visible():
        app.after(0, lambda: taskbar.SetProgressValue(hwnd, 100, 100)) 
        app.after(2000, recursive_callback)
    else:
        app.after(0, lambda: taskbar.SetProgressValue(hwnd, 0, 100)) 


def select_file():
    global file
    file_selector = filedialog.askopenfilename(
                    initialdir=r"C:/",
                    title="Open your file",
                    filetypes=[("All Video Files", "*.mp4 *.mov *.avi *.mkv *.wmv *.flv *.webm")]
                    )
    if file_selector:
        file = file_selector
        

info_frame = ctk.CTkFrame(file_frame, height=410, fg_color="#4f4b42")
info_frame.pack_propagate(False)
info_frame.pack(fill="both", padx=10, pady=5)

ctk.CTkLabel(info_frame, text="FILE INFO", font=("Arial", 16, "bold")).pack(padx=20, pady=(20,30))

data_container = ctk.CTkFrame(info_frame, fg_color="transparent")
data_container.pack(fill="both", expand=True, padx=15)

info_labels = {}

def create_info_row(parent, row, label_text):
    
    #left column
    lbl = ctk.CTkLabel(parent, text=label_text, font=("Arial", 12, "bold"), text_color="#aaaaaa", anchor="w")
    lbl.grid(row=row, column=0, sticky="w", pady=5)
    
    #right column
    val_color = "white"
    val_txt = ("Arial", 12)
    if label_text in ["File:", "Pxl Format:"]: 
        val_color = "#A5D6A7"
        val_txt = ("Arial", 12, "bold")
    
    val = ctk.CTkLabel(parent, text="---", font=val_txt, text_color=val_color, anchor="w", 
        wraplength=155, justify="left")
    val.grid(row=row, column=1, sticky="w", padx=(10,0), pady=5)
    
    return val

        
info_labels['file'] = create_info_row(data_container, 0, "File:")
info_labels['res'] = create_info_row(data_container, 1, "Resolution:")
info_labels['codec'] = create_info_row(data_container, 2, "Codec:")
info_labels['fmt'] = create_info_row(data_container, 3, "Pxl Format:")
info_labels['bit'] = create_info_row(data_container, 4, "Bitrate:")
info_labels['brand'] = create_info_row(data_container, 5, "Brand:")
info_labels['dur'] = create_info_row(data_container, 6, "Duration:")


def get_file_info():
    global file, info_labels, brand_names, data, color_transfer, original_pxl
        
    if file:
        data = get_metadata(file)
    
        if data['streams']:
            
            try:
                raw_bitrate = data['streams'][0].get('bit_rate') or data.get('format', {}).get('bit_rate', 0)
                bitrate = int(raw_bitrate) // 1000
                bitrate_display = f"{bitrate}kbps." if bitrate > 0 else "N/A"
                raw_duration = data['streams'][0].get('duration') or data.get('format', {}).get('duration', 0)
                duration = str(datetime.timedelta(seconds= int(float(raw_duration)))) if raw_duration else "N/A"
                pix_fmt = data['streams'][0].get('pix_fmt', 'unknown')
                width = data['streams'][0].get('width', 'N/A')
                height = data['streams'][0].get('height', 'N/A')
                codec = data['streams'][0].get('codec_long_name', 'unknown')
                major_brand = data.get('format', {}).get('tags', {}).get('major_brand', 'N/A')
                
                #fetching data for the backend
                color_transfer = data['streams'][0].get('color_transfer', 'unknown')
                original_pxl = data['streams'][0].get('pix_fmt', 'unknown')

                if major_brand in brand_names:
                    brand_name = f"{major_brand} / {brand_names[major_brand]}"
                else:
                    brand_name = major_brand
                
                info_labels['file'].configure(text=os.path.basename(file))
                info_labels['res'].configure(text=f"{width} x {height}")
                info_labels['codec'].configure(text=codec)
                info_labels['fmt'].configure(text=pix_fmt)
                info_labels['bit'].configure(text=bitrate_display)
                info_labels['brand'].configure(text=brand_name)
                info_labels['dur'].configure(text=duration)
                
            except (KeyError, IndexError, ValueError) as e:
                print(f"Error reading metada: {e}")
 
 
image_frame = ctk.CTkFrame(app, width=380, height=250)
image_frame.place(x=305.5, y=10)
image_label = ctk.CTkLabel(image_frame, text="Select your video.", text_color="#888888", font=("Arial", 11), justify='center', fg_color="transparent", width=370, height=240)
image_label.pack(padx=5, pady=5)


def get_temp_value(temp_new_value):
    global temp_current_value
    
    temp_new_value = int(temp_picker.get())
    if temp_current_value != temp_new_value:
        temp_current_value = temp_new_value
        temp_picker_label.configure(text=f'{temp_current_value} °C')        


temp_guard_frame = ctk.CTkFrame(app, height=60, width=250, fg_color='transparent')
temp_guard_frame.place(x=366, y=269)

temp_guard_label = ctk.CTkLabel(temp_guard_frame, text='Temperature throttling:', text_color="#888888", font=("Arial", 13))
temp_guard_label.pack(padx=10, pady=(10,0), side='left')

temp_guard_selector = ctk.CTkSegmentedButton(temp_guard_frame, values=["Enable", "Disable"])
temp_guard_selector.set("Disable")
temp_guard_selector.pack(padx=(0,10), pady=(10,0), side="right")

temp_slider_container=ctk.CTkFrame(app, width=400, height=40, fg_color='transparent')
temp_slider_container.place(x=372, y=310)

temp_picker = ctk.CTkSlider(temp_slider_container, from_=60, to=90, progress_color="#5d5444", button_color="#8c816d", button_hover_color="#1f6aa5", command=get_temp_value)
temp_picker.set(85)
temp_picker.pack(side='left', pady=5)

temp_picker_label = ctk.CTkLabel(temp_slider_container, text=f'{int(temp_picker.get())} °C', text_color='#FF5252', font=("Arial", 13))
temp_picker_label.pack(side='right', padx=(5,0))


                
def display_image():
    global file, total_sec
    
    if file:
        total_sec = get_duration(file)
        timestamp = total_sec*0.5
        pil_image = get_images(file, timestamp)
    
        if pil_image:
            screenshot = ctk.CTkImage(light_image=pil_image, size=(pil_image.width, pil_image.height))
            app.after(0, lambda: image_label.configure(image=screenshot, text=""))
        
    
def select_button_command():
    select_file()
    
    get_file_info()
    app.update_idletasks()
    
    global data
    
    if data and data['streams']:
        pxl = data['streams'][0].get('pix_fmt', "N/A")
        pxl_info = format_info.get(pxl, f"{pxl} · Unknown format")
        app.after(0, lambda: pxl_info_label.configure(text=pxl_info))
    
    threading.Thread(target=display_image, daemon=True).start()

                    
ctk.CTkButton(file_frame, text="Select video", command=select_button_command).pack(padx=10, pady=(25,0))

pxl_info_label = ctk.CTkLabel(file_frame, text="Select your video.", 
                font=("Arial", 11), text_color="#888888", wraplength=250, justify="center")
pxl_info_label.pack(pady=(30, 0))

folder_label = ctk.CTkLabel(folder_select_frame, text=suggested_name)
folder_label.pack(side="left", padx=(10,0))


def save_as():
    global saveas, file, suggested_name, root

    if file:
        suggested_name = os.path.basename(file)
        root, ext = os.path.splitext(suggested_name)
    
    directory_selector=filedialog.asksaveasfilename(
                       initialdir=r"C:/",
                        title="Save your file",
                        initialfile= root,
                        defaultextension=".mp4",
                        filetypes=[("All Video Files", "*.mp4 *.mov *.avi *.mkv *.wmv *.flv *.webm")]
                       )
    if directory_selector:
        saveas = directory_selector
        folder_label.configure(text=saveas)
        

save_as_button = ctk.CTkButton(folder_select_frame, text="Select folder", command=save_as)
save_as_button.pack(side="right")
    
right_panel = ctk.CTkFrame(app, width=300)
right_panel.pack(side="right", fill="both", expand=False, padx=10, pady=10)


def allowed_pxl_formats(selected_codec):
    selected_codec = encoder.get() or None
    format_check = any(x in selected_codec for x in ['H.264_QSV', 'H.264_AMF', 'AVC-AMF Hybrid', 'AVC-QSV Hybrid', 'H.264_NVENC', 'AVC-NVENC Hybrid', 'AVC/H.264'])
    
    if format_check:
        app.after(0, lambda: pxl_selector.set('8 bit'))
        app.after(0, lambda: pxl_selector.configure(state="disabled"))
        
    elif any(x in selected_codec for x in ['HEVC_AMF', 'HEVC_NVENC']):
        app.after(0, lambda: pxl_selector.set('Orig'))
        app.after(0, lambda: pxl_selector.configure(state="disabled"))
        
    else:
        app.after(0, lambda: pxl_selector.configure(state="normal"))
        
        
    if any(x in selected_codec for x in ['HEVC_AMF', 'H.264_AMF']):
        app.after(0, lambda: resolution_selector.set('Orig'))
        app.after(0, lambda: resolution_selector.configure(state="disabled"))
    else:
        app.after(0, lambda: resolution_selector.configure(state="normal"))
        
    

ctk.CTkLabel(right_panel, text="DETECTED ENCODERS", font=("Arial", 16, "bold")).pack(padx=10, pady=(10,10))    

if results == 'No HW support.':
    noencoder = ctk.CTkLabel(right_panel, text=results, anchor='w', width=270, text_color='#FF5252')
    noencoder.pack(padx=10, pady=(0,5))
else:
    encoder = ctk.CTkOptionMenu(right_panel, values=results, hover=True, anchor='w', width=270, command=allowed_pxl_formats)
    encoder.pack(padx=10, pady=(0,5))

ctk.CTkLabel(right_panel, text="Quality (lower is better):").pack(pady=(0,0))
slider_container = ctk.CTkFrame(right_panel, fg_color="transparent")
slider_container.pack(padx=10, pady=(0,10))


def get_value(new_quality_value):
    global current_quality_value
    
    new_quality_value = int(quality_selector.get()) 
    if new_quality_value != current_quality_value:
        current_quality_value = new_quality_value
        quality_label.configure(text=current_quality_value)

        
quality_selector = ctk.CTkSlider(slider_container, from_=1, to=51, progress_color="#5d5444", button_color="#8c816d", button_hover_color="#1f6aa5", command=get_value)
quality_selector.set(20)
quality_selector.pack(side="left")

quality_label = ctk.CTkLabel(slider_container, text=int(quality_selector.get()), text_color="#d3d0c9")
quality_label.pack(side="right", padx=(5,0), pady=(0,5))

pxl_row = ctk.CTkFrame(right_panel, fg_color="transparent")
pxl_row.pack(fill="x", padx=35, pady=(0,10))
ctk.CTkLabel(pxl_row, text="Pixel Format:", text_color="#888888", font=("Arial", 13)).pack(side="left")
pxl_selector = ctk.CTkSegmentedButton(pxl_row, values=["Orig", "8 bit", "10 bit"])

if isinstance(results, list) and results and any(x in results[0] for x in ['HEVC_AMF', 'HEVC_NVENC']):
    app.after(0, lambda: pxl_selector.set("Orig"))
    app.after(0, lambda: pxl_selector.configure(state="disabled"))
    
elif isinstance(results, list) and results and any(x in results[0] for x in ['H.264_QSV', 'AVC-QSV Hybrid', 'H.264_AMF', 'AVC-AMF Hybrid', 'H.264_NVENC', 'AVC-NVENC Hybrid', 'AVC/H.264']):
    app.after(0, lambda: pxl_selector.set("8 bit"))
    app.after(0, lambda: pxl_selector.configure(state="disabled"))
    
else:
    app.after(0, lambda: pxl_selector.set("Orig"))
    
pxl_selector.pack(side="right")

res_row = ctk.CTkFrame(right_panel, fg_color="transparent")
res_row.pack(fill="x", padx=35, pady=(0,10))
ctk.CTkLabel(res_row, text="Res:", text_color="#888888", font=("Arial", 13)).pack(side="left")
resolution_selector = ctk.CTkSegmentedButton(res_row, values=["Orig", "4K", "2K", "1080p", "720p"])
resolution_selector.set("Orig")

if isinstance(results, list) and results and any(x in results[0] for x in ['HEVC_AMF', 'H.264_AMF']):
    app.after(0, lambda: resolution_selector.set("Orig"))
    app.after(0, lambda: resolution_selector.configure(state="disabled"))
    
resolution_selector.pack(side="right")

fps_row = ctk.CTkFrame(right_panel, fg_color="transparent")
fps_row.pack(fill="x", padx=35, pady=(0,10))
ctk.CTkLabel(fps_row, text="FPS:", text_color="#888888", font=("Arial", 13)).pack(side="left")
fps_selector = ctk.CTkSegmentedButton(fps_row, values=["Orig", "60", "30", "24"])
fps_selector.set("Orig")
fps_selector.pack(side="right")

encoding_notification = ctk.CTkScrollableFrame(right_panel, label_font=("Arial", 12))
encoding_notification.pack(pady=(0,10))

progress_container = ctk.CTkFrame(right_panel, fg_color="transparent")
progress_container.pack(padx=10, pady=(0,10))
progress_bar = ctk.CTkProgressBar(
                    progress_container, height=10, 
                    progress_color=("#FFF9C4", "#F9E79F"), 
                    orientation='horizontal'
                    )
progress_bar.set(0)
progress_bar.pack(side="left", fill="x", expand="true", padx=(0,10))
progress_label = ctk.CTkLabel(progress_container, text="0%", font=("Arial", 12))
progress_label.pack(side="right")

log_frame = ctk.CTkFrame(app, height=280, width=380)
log_frame.pack_propagate(False)
log_frame.pack(side="bottom", pady=(0,10))
log_title = ctk.CTkLabel(log_frame, text="Progress log:", font=("Arial", 12, "bold"), justify="left")
log_title.pack()
log_panel = ctk.CTkTextbox(log_frame, font=("Arial", 12), text_color="#fcebbb")
log_panel.pack(fill="both", expand=True, padx=10, pady=(5, 10))


def start_encode():
    global file, saveas, ps_process, processing, current_quality_value, color_transfer, original_pxl

    if file is None and saveas:
        popup = alertpopup(app, icon_path=icon_path)
        popup.alert("Select a file!")
        return
        
    if saveas is None and file:
        popup = alertpopup(app, icon_path=icon_path)
        popup.alert("Select a folder to save the file!")
        return
        
    if saveas is None and file is None:
        popup = alertpopup(app, icon_path=icon_path)
        popup.alert("Select a file and a folder to save the file!")
        return
        
    selected_pxl = pxl_selector.get()
    selected_resolution = resolution_map[resolution_selector.get()]
    selected_fps = fps_selector.get()
    
    pxl_map = {
        'Orig': 'Orig',
        '8 bit': 'nv12',
        '10 bit': 'p010le',
        '12 bit': 'p012le'
    }
    
    pxlfmt = pxl_map[selected_pxl]
    encoding_choice = encoder.get()
    
    processing, ps_process = encode(file, encoding_choice, pxlfmt, saveas, current_quality_value, selected_resolution, selected_fps, color_transfer, original_pxl)
 #   print(current_quality_value)
    
    if processing is None:
        popup = alertpopup(app, icon_path=icon_path)
        popup.alert("Encoding failed, try again or choose another codec!", "#FF5722")
        return
        
    #threading to avoid window freezing while compressing
    thread = threading.Thread(target=watch_progress, args=(processing, ps_process, file))
    thread.start()

  
def pause_resume():
    global pause_flag, ps_process
    
    def update_notification(msg, color):
        def add_label():
            notif_label = ctk.CTkLabel(encoding_notification, text=msg, text_color=color, anchor="w", wraplength=200)
            notif_label.pack(padx=2, pady=3)
            encoding_notification.update_idletasks()
            encoding_notification._parent_canvas.yview_moveto(1.0)
        app.after(0, add_label)
    
    if not pause_flag and ps_process:
        pause_flag = True
        if ps_process.status() != "stopped":
            ps_process.suspend()
 #       print(ps_process.status(), pause_flag)
        app.after(0, lambda: progress_bar.configure(progress_color="#B19CD9")) 
        app.after(0, lambda: log_panel.configure(text_color="#B19CD9")) 
        app.after(0, lambda: progress_label.configure(text_color="#B19CD9")) 
        app.after(0, lambda: pause_resume_button.configure(text_color="#B19CD9"))
        update_notification("Processing paused...", "#B19CD9")
        app.after(0, lambda: taskbar.SetProgressState(hwnd, 0x8)) #tasbar progress color
    elif pause_flag and ps_process:
        pause_flag = False
        ps_process.resume()
 #       print(pause_flag)
 #       print(ps_process.status())
        app.after(0, lambda: progress_bar.configure(progress_color=("#FFF9C4", "#F9E79F"))) 
        app.after(0, lambda: log_panel.configure(text_color="#fcebbb"))
        app.after(0, lambda: progress_label.configure(text_color="#fcebbb"))
        app.after(0, lambda: pause_resume_button.configure(text_color="#fca397"))
        update_notification("Processing is resuming...", "#00E5FF")
        app.after(0, lambda: taskbar.SetProgressState(hwnd, 2)) #tasbar progress color 

    else:
        pass

  
def abort_encoding():
    global abort_flag, ps_process
    abort_flag=True
    if ps_process:
        ps_process.resume()
 #      print(ps_process.status())

    
def watch_progress(processing, ps_process, file):
    global abort_flag, total_sec, pause_flag, saveas
    
    abort_flag=False
    pause_flag = False
    file_name= os.path.basename(file)
    throttling = temp_guard_selector.get() or 'Enable'
    
    temp_top_guard = int(temp_picker.get())
    temp_bottom_guard = (temp_top_guard * 75) / 100 # 75% of the picked temp
    if temp_bottom_guard and temp_bottom_guard < 50:
        temp_bottom_guard = 50
   # print(f'temp is {temp_top_guard} {temp_bottom_guard}')
    
    app.after(0, log_panel.delete, "0.0", "end")
    
    def update_notification(msg, color="#fcebbb"):
        def add_label():
            notif_label = ctk.CTkLabel(encoding_notification, text=msg, text_color=color, anchor="w", wraplength=200)
            notif_label.pack(padx=2,pady=3)
            encoding_notification.update_idletasks() #calculate the new size
            encoding_notification._parent_canvas.yview_moveto(1.0) #move towards the end (Y axis)
            
        app.after(0, add_label)
        
    update_notification(f"------------------------\nEncoding \"{file_name}\"...", "#A5D6A7")
    
    def update_log(log):
        app.after(0, lambda: [log_panel.insert("end", log), log_panel.see("end")])
        
    app.after(0, lambda: encode_button.configure(state="disabled"))
    app.after(0, lambda: temp_guard_selector.configure(state="disabled"))
    app.after(0, lambda: fps_selector.configure(state="disabled"))
    app.after(0, lambda: pxl_selector.configure(state="disabled"))
    app.after(0, lambda: resolution_selector.configure(state="disabled"))
    app.after(0, lambda: encoder.configure(state="disabled"))
    app.after(0, lambda: pause_resume_button.configure(state="normal"))
    app.after(0, lambda: abort_button.configure(state="normal"))
    
    app.after(0, lambda: progress_bar.configure(progress_color=("#FFF9C4", "#F9E79F"))) 
    app.after(0, lambda: log_panel.configure(text_color="#fcebbb"))
    app.after(0, lambda: progress_label.configure(text_color="#fcebbb"))
    app.after(0, lambda: pause_resume_button.configure(text_color="#fca397"))
    
    app.after(0, lambda: taskbar.SetProgressState(hwnd, 2))
    app.after(0, lambda: taskbar.SetProgressValue(hwnd, 0, 100))
    
    while True:
        
        if abort_flag:
            processing.terminate()
            processing.wait()
            update_notification(f"⚠ {file_name}'s encoding is aborted...", "#FF5252")
            app.after(0, lambda: encode_button.configure(state="normal"))
            app.after(0, lambda: temp_guard_selector.configure(state="normal"))
            app.after(0, lambda: pause_resume_button.configure(state="disabled"))
            app.after(0, lambda: abort_button.configure(state="disabled"))
            app.after(0, lambda: encoder.configure(state="normal"))
            app.after(0, lambda: fps_selector.configure(state="normal"))
        
            if any(x in encoder.get() for x in['H.264_QSV', 'H.264_AMF', 'AMD AVC-AMF', 'Intel AVC-QSV', 'AVC/H.264', 'H.264_NVENC', 'AVC-NVENC Hybrid']):
                app.after(0, lambda: pxl_selector.set('8 bit'))
                app.after(0, lambda: pxl_selector.configure(state="disabled"))
                app.after(0, lambda: resolution_selector.configure(state="normal"))
            elif any(x in encoder.get() for x in ['HEVC_AMF', 'HEVC_NVENC']):
                app.after(0, lambda: pxl_selector.set('Orig'))
                app.after(0, lambda: pxl_selector.configure(state="disabled"))
            elif any(x in encoder.get() for x in ['HEVC_AMF', 'H.264_AMF']):
                app.after(0, lambda: resolution_selector.set('Orig'))
                app.after(0, lambda: resolution_selector.configure(state="disabled"))
            else:
                app.after(0, lambda: pxl_selector.configure(state="normal"))
                app.after(0, lambda: resolution_selector.configure(state="normal"))
            
            app.after(0, lambda: progress_bar.configure(progress_color="#FF5252"))
            app.after(0, lambda: log_panel.configure(text_color="#FF5252"))
            app.after(0, lambda: progress_label.configure(text_color="#FF5252"))
            app.after(0, lambda: taskbar.SetProgressState(hwnd, 0x4))
            app.after(2000, lambda: taskbar.SetProgressValue(hwnd, 0, 100))
            if saveas and os.path.exists(saveas):
                os.remove(saveas)
            break
            
        line = processing.stdout.readline()
        if not line and processing.poll() is not None:
            break
        
        if line:
            
            temp = int(get_cpu_temp() or 0)
            if throttling == 'Disable':
                temp = 0
            
            if temp > temp_top_guard and not pause_flag:
                update_notification(f"⚠️ Too hot! pausing... ({temp}°C)","#FF5722")
                app.after(0, lambda: taskbar.SetProgressState(hwnd, 0x8))
                ps_process.suspend()
                
                
                while pause_flag or temp > temp_bottom_guard:
                    if abort_flag:
                        break
                    if pause_flag:
 #                       print("breaking")
                        break
                    time.sleep(1)
                    temp = int(get_cpu_temp() or 0)
                if not abort_flag and not pause_flag and temp < (int(temp_bottom_guard) + 1) :
                    ps_process.resume()
                    update_notification(f"❄️ Resuming... ({temp}°C)","#81D4FA")
                    app.after(0, lambda: taskbar.SetProgressState(hwnd, 2))
                
            match = re.search(r'time=(\d+):(\d+):(\d+.\d+)', line)
            
            if match:
                h, m, s = map(float, match.groups())
                current_sec = (h*3600) + (m*60) + s
                pct = min((current_sec/total_sec)*100, 100)
                app.after(0, progress_bar.set, pct/100)
                app.after(0, lambda: taskbar.SetProgressValue(hwnd, int(pct), 100))
                app.after(0, lambda p=pct: progress_label.configure(text=f"{p:.0f}%"))
                update_log(f"{line}...\n\n")
                
                
    processing.wait()
    if processing.returncode == 0 and not abort_flag:
        app.after(0, lambda: progress_label.configure(text="100%"))
        app.after(0, progress_bar.set, 1)
        update_notification(f"\"{file_name}\" encoding completed...", "#2ECC71")
        app.after(0, lambda: encode_button.configure(state="normal"))
        app.after(0, lambda: temp_guard_selector.configure(state="normal"))
        app.after(0, lambda: encoder.configure(state="normal"))
        app.after(0, lambda: pause_resume_button.configure(state="disabled"))
        app.after(0, lambda: abort_button.configure(state="disabled"))
        app.after(0, lambda: fps_selector.configure(state="normal"))
        
        if any(x in encoder.get() for x in['H.264_QSV', 'H.264_AMF', 'AMD AVC-AMF', 'Intel AVC-QSV', 'H.264_NVENC', 'AVC-NVENC Hybrid', 'AVC/H.264']):
            app.after(0, lambda: pxl_selector.set('8 bit'))
            app.after(0, lambda: pxl_selector.configure(state="disabled"))
            app.after(0, lambda: resolution_selector.configure(state="normal"))
        elif any(x in encoder.get() for x in ['HEVC_AMF', 'HEVC_NVENC']):
            app.after(0, lambda: pxl_selector.set('Orig'))
            app.after(0, lambda: pxl_selector.configure(state="disabled"))
        elif any(x in encoder.get() for x in ['HEVC_AMF', 'H.264_AMF']):
            app.after(0, lambda: resolution_selector.set('Orig'))
            app.after(0, lambda: resolution_selector.configure(state="disabled"))
        else:
            app.after(0, lambda: pxl_selector.configure(state="normal"))
            app.after(0, lambda: resolution_selector.configure(state="normal"))
        
        app.after(0, lambda:taskbar.SetProgressValue(hwnd, 100, 100))
        app.after(2000, lambda:taskbar.SetProgressValue(hwnd, 0, 100))
        app.after(0, lambda: folder_label.configure(text=""))
        saveas = None
        try:
            sys.stdout.write('\a')
        except Exception as e:
            print(e)
        
    elif processing.returncode != 0 and not abort_flag:
        update_notification(f"Encoding \"{file_name}\"  failed...", "#FF5252")
        app.after(0, lambda: progress_bar.configure(progress_color="#FF5252"))
        app.after(0, lambda: log_panel.configure(text_color="#FF5252"))
        app.after(0, lambda: progress_label.configure(text_color="#FF5252"))
        app.after(0, lambda: encode_button.configure(state="normal"))
        app.after(0, lambda: temp_guard_selector.configure(state="normal"))
        app.after(0, lambda: pause_resume_button.configure(state="disabled"))
        app.after(0, lambda: abort_button.configure(state="disabled"))
        app.after(0, lambda: encoder.configure(state="normal"))
        app.after(0, lambda: fps_selector.configure(state="normal"))
        
        if any(x in encoder.get() for x in['H.264_QSV', 'H.264_AMF', 'AMD AVC-AMF', 'Intel AVC-QSV','H.264_NVENC', 'AVC-NVENC Hybrid', 'AVC/H.264']):
            app.after(0, lambda: pxl_selector.set('8 bit'))
            app.after(0, lambda: pxl_selector.configure(state="disabled"))
            app.after(0, lambda: resolution_selector.configure(state="normal"))
        elif any(x in encoder.get() for x in ['HEVC_AMF', 'HEVC_NVENC']):
            app.after(0, lambda: pxl_selector.set('Orig'))
            app.after(0, lambda: pxl_selector.configure(state="disabled"))
        elif any(x in encoder.get() for x in ['HEVC_AMF', 'H.264_AMF']):
            app.after(0, lambda: resolution_selector.set('Orig'))
            app.after(0, lambda: resolution_selector.configure(state="disabled"))
        else:
            app.after(0, lambda: pxl_selector.configure(state="normal"))
            app.after(0, lambda: resolution_selector.configure(state="normal"))
        
        app.after(0, lambda: taskbar.SetProgressState(hwnd, 0x4))
        if saveas and os.path.exists(saveas):
            os.remove(saveas)
        recursive_callback()
        if 'AMD AMF Hybrid' in encoder.get():
            popup = alertpopup(app, icon_path=icon_path)
            popup.alert(f"""Try to use 8 bit or choose another codec. 
Encoding failed!""", "#FF5722")
            return
        else:
            popup = alertpopup(app, icon_path=icon_path)
            popup.alert("Encoding failed, try again or choose another codec!", "#FF5722")
            return
            
        
def on_closing():
    global ps_process, abort_flag, processing
    
    if ps_process:
        try:
            ps_process.resume()
            ps_process.kill()
        except Exception as e:
            print(f"cleanup failure: {e}")
    
    if processing:
        processing.wait()
    app.destroy()
    os._exit(0)
        
    
encode_button = ctk.CTkButton(right_panel, text= "ENCODE", text_color="#dcfcd7", command=start_encode)
encode_button.pack(fill="x", expand=False, padx=5, pady=(0, 10))

controls_container = ctk.CTkFrame(right_panel, fg_color="transparent")
controls_container.pack(pady=(5,10))

pause_resume_button = ctk.CTkButton(controls_container, text= "Pause/Resume", text_color="#ffdba6", command=pause_resume, state="disabled")
pause_resume_button.pack(side="left",padx=(5,2))

abort_button = ctk.CTkButton(controls_container, text= "Abort", text_color="#fca397", command=abort_encoding, state="disabled")
abort_button.pack(side="right",padx=(1,5))

app.protocol("WM_DELETE_WINDOW", on_closing)

app.mainloop()