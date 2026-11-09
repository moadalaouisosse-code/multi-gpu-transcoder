import customtkinter as ctk

class alertpopup(ctk.CTkToplevel):
    def __init__(self, app, icon_path=None, *args,**kwargs):
        super().__init__(app, *args, **kwargs)
        
        if icon_path:
            self.after(200, lambda: self.iconbitmap(icon_path))
        
        width=300
        height=150
        master_x=app.winfo_x()
        master_y=app.winfo_y()
        master_width=app.winfo_width()
        master_height=app.winfo_height()
        
        pos_x = master_x +(master_width//2) - (width//2)
        pos_y = master_y + (master_height//2) - (height//2)
        
        self.geometry(f"{width}x{height}+{pos_x}+{pos_y}")
        
        self.attributes('-topmost', True)
        self.label = ctk.CTkLabel(self, text = "", justify="center")
        self.label.pack(expand=True)
        
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.btn = ctk.CTkButton(self, text="OK", command=self.destroy)
        self.btn.pack(pady=(0,20))
 
    def alert(self, msg, color ="#fcebbb", title="Alert"):
        self.label.configure(text=msg, text_color=color)
        self.title(title)