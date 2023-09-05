import random
import tkinter as tk
from tkinter import messagebox
import sys

num_digits = 4
num_guesses = 5

# variables
green = '#27e512'
yellow = '#e8ef0e'
gray = '#4c4c4c'
font = 'Verdana, 38'
numbers = []

class NumberWordleGame:
    def __init__(self, root, num_digits):
        self.root = root
        self.root.title("Factor 2")
        self.num_digits = num_digits
        self.secret_number = self.generate_random_number(self.num_digits)
        self.attempts = 0
        self.guesses = []

        self.label = tk.Label(root, text=f"Enter {self.num_digits} digit access code:", font=("Helvetica", 16), bg="white")
        self.label.pack(pady=10)

        self.entry = tk.Entry(root, font=("Helvetica", 14))
        self.entry.pack(pady=10)
        
        self.submit_button = tk.Button(root, text="Submit", command=self.check_guess, font=("Helvetica", 14), bg="green")
        self.submit_button.pack(pady=10)

        self.guess_frame = tk.Frame(root, bg="white")
        self.guess_frame.pack()


        self.guess_label = tk.Label(self.guess_frame, text="Grey = Digit incorrect", font=("Helvetica", 8), bg="grey")
        self.guess_label.pack()
        self.guess_label = tk.Label(self.guess_frame, text="Amber = Digit correct, wrong position", font=("Helvetica", 8), bg="orange")
        self.guess_label.pack()
        self.guess_label = tk.Label(self.guess_frame, text="Green = Digit and position correct", font=("Helvetica", 8), bg="green")
        self.guess_label.pack()
        self.guess_label = tk.Label(self.guess_frame, text="Feedback:", font=("Helvetica", 12), bg="white")
        self.guess_label.pack(pady=10)

    def generate_random_number(self, num_digits):
        return ''.join(random.sample('0123456789', num_digits))

    def compare_numbers(self, guess):
        feedback = []

        for i in range(self.num_digits):
            if guess[i] == self.secret_number[i]:
                feedback.append(('green', guess[i]))
            elif guess[i] in self.secret_number:
                feedback.append(('orange', guess[i]))
            else:
                feedback.append(('gray', guess[i]))

        return feedback

    def check_guess(self):
        user_guess = self.entry.get()

        if len(user_guess) != self.num_digits or not user_guess.isdigit():
            messagebox.showinfo("Invalid Input", f"Please enter a valid {self.num_digits}-digit number.")
            return

        feedback = self.compare_numbers(user_guess)
        self.guesses.append((user_guess, feedback))
        self.update_guess_display()

        if user_guess == self.secret_number:
            messagebox.showinfo("Succes", f"You have entered the correct number {user_guess}!\nIt took you {self.attempts + 1} attempts.")
            self.root.destroy()
            sys.exit(1)
        else:
            self.attempts += 1
            self.entry.delete(0, tk.END)
        if self.attempts == num_guesses:
            messagebox.showinfo("Failed!", f"You have reached the maximum of {num_guesses} attempts.")
            self.root.destroy()
            sys.exit(0)

    def update_guess_display(self):
        for guess, feedback in self.guesses:
            guess_feedback_frame = tk.Frame(self.guess_frame)
            guess_feedback_frame.pack()

        for color, digit in feedback:
            label = tk.Label(guess_feedback_frame, text=digit, width=3, height=1, relief='solid', bg=color)
            label.pack(side=tk.LEFT, padx=2)
            
                
if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg='white')
    game = NumberWordleGame(root, num_digits)
    root.mainloop()