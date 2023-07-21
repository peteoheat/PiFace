#!/usr/bin/python3
import tkinter as tk

def clicked():
    n = 0
    txt = "Welcome to our bank vault. You mission is to test our security systm and attempt to open our bank vault."
    showChar(n, txt)

def showChar(n, txt):
    n += 1
    lbl.config(text = txt[:n])
    if n < len(txt):
        #window.after(150, lambda: showChar(n, txt))
        window.after(150, showChar, n, txt)

window = tk.Tk()
window.title('Break the Bank')
window.geometry("300x200+10+20")
lbl=tk.Label(window, text="", fg = 'red', font=("Helvetica", 16))
btn=tk.Button(window, text="Click to start", fg='blue', bg='red', command = clicked)
lbl.pack()
btn.pack()
window.mainloop()
