import ttkbootstrap as ttk
import CustomWidgets as cw

root = ttk.Window()
root.geometry("300x300")
root.title("ScrolledFrame")
root.config(padx=10, pady=10)

sf = cw.ScrolledFrame(root, positionYBar="right", positionXBar="Top")
sf_frame = sf.getScrollableFrame()

for i in range(100):
    ttk.Label(sf_frame, text=f"Label {i}").pack()

sf.pack(fill="both", expand=True)

root.mainloop()

