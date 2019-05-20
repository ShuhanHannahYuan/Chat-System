import tkinter as tk

window = tk.Tk()
window.title("Chat System")
window.geometry("900x600")

label = tk.Label(window, text = "Welcome to ICS Chat System", bg = "blue", font = ("Arial",18), width = 40, height = 2)

label.pack()

window.mainloop()