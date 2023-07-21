#!/usr/bin/python3
import tkinter as tk

def clicked():
    n = 0
    txt = "Welcome to our bank vault. You mission is to test our security systm and attempt to open our bank vault."
    showChar(n, txt)

def showChar(n, txt):
    n += 1
    label.config(text = txt[:n])
    if n < len(txt):
        root.after(100, lambda: showChar(n, txt))

root = tk.Tk()
label = tk.Label(root, text = "")
label.pack()
button = tk.Button(root, text = "Start", command = clicked)
button.pack()
root.mainloop()
