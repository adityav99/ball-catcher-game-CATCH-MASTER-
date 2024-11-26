import tkinter as tk
from tkinter import messagebox
import sqlite3
import random
import time
import os

# Define database and log file names
DB_NAME = 'details.db'
LOG_FILE = 'game_log.txt'

# Initialize database and tables
def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS scores (username TEXT, score INTEGER)")
    conn.commit()
    conn.close()

# Log session information
def log_session(username, level, score):
    with open(LOG_FILE, 'a') as log:
        log_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        log.write(f"Username: {username}, Level: {level}, Score: {score}, Login Time: {log_time}\n")

# Register a new user
def register():
    username = entry_username.get()
    password = entry_password.get()
    
    if username and password:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            messagebox.showerror("Error", "Username already exists!")
        else:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            messagebox.showinfo("Registration", "Registration successful!")
        conn.close()
    else:
        messagebox.showwarning("Input Error", "Please enter both username and password")

# Login existing user
def login():
    username = entry_username.get()
    password = entry_password.get()
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        messagebox.showinfo("Login", "Login successful!")
        log_session(username, "Login", 0)  # Log the login time
        open_game_window(username)
    else:
        messagebox.showerror("Error", "Invalid username or password")

# Ball-catching game
def open_game_window(username):
    game_window = tk.Toplevel(root)
    game_window.title("Ball Catching Game")
    
    # Game variables
    levels = {1: {"speed": 4, "level_name": "Easy"},
              2: {"speed": 8, "level_name": "Medium"},
              3: {"speed": 12, "level_name": "Hard"}}
    level = 1
    speed = levels[level]["speed"]
    ball_count = 0
    score = 0
    
    # Set up the canvas
    canvas = tk.Canvas(game_window, width=400, height=400, bg="lightblue")
    canvas.pack()
    
    # Create catcher (basket), score, and level display
    catcher = canvas.create_rectangle(170, 370, 230, 390, fill="darkorange")
    level_text = canvas.create_text(200, 20, text="Level: Easy", font=("Arial", 16, "bold"), fill="black")
    score_text = canvas.create_text(200, 50, text="Score: 0", font=("Arial", 14), fill="black")
    current_ball = None

    # Move catcher
    def move_left(event):
        if canvas.coords(catcher)[0] > 0:  # Prevent moving out of bounds
            canvas.move(catcher, -20, 0)

    def move_right(event):
        if canvas.coords(catcher)[2] < 400:  # Prevent moving out of bounds
            canvas.move(catcher, 20, 0)

    game_window.bind("<Left>", move_left)
    game_window.bind("<Right>", move_right)

    # Drop balls
    def drop_ball():
        nonlocal current_ball
        if current_ball is None:  # Only create a new ball if none exists
            x = random.randint(20, 380)
            ball_color = random.choice(["#FF6347", "#FFD700", "#00FA9A", "#1E90FF", "#FF69B4"])
            current_ball = canvas.create_oval(x, 10, x + 20, 30, fill=ball_color)
        game_window.after(1500, drop_ball)

    # Update game mechanics
    def update_game():
        nonlocal score, ball_count, level, speed, current_ball
        if current_ball:
            canvas.move(current_ball, 0, speed)
            ball_pos = canvas.coords(current_ball)
            catcher_pos = canvas.coords(catcher)

            # Check for collision with catcher
            if (catcher_pos[0] < ball_pos[0] < catcher_pos[2] and
                catcher_pos[1] < ball_pos[1] < catcher_pos[3]):
                canvas.delete(current_ball)
                current_ball = None
                score += 1
                ball_count += 1
                canvas.itemconfig(score_text, text=f"Score: {score}")
                
                # Increase level after every 5 balls
                if ball_count % 5 == 0:
                    level = min(level + 1, 3)  # Cap level at 3
                    speed = levels[level]["speed"]
                    canvas.itemconfig(level_text, text=f"Level: {levels[level]['level_name']}")

            # Remove ball if it hits the bottom
            elif ball_pos[3] >= 400:
                canvas.delete(current_ball)
                current_ball = None
                game_over(username, level, score)  # End game if a ball reaches the bottom
                return  # Stop the game loop on game over

        game_window.after(50, update_game)

    drop_ball()
    update_game()

# Game over and saving score
def game_over(username, level, score):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO scores (username, score) VALUES (?, ?)", (username, score))
    conn.commit()
    conn.close()
    
    # Log the game progress
    log_session(username, level, score)
    messagebox.showinfo("Game Over", f"Game Over! Your score: {score}")

# Main login/register interface
root = tk.Tk()
root.title("Ball Catching Game Login")
root.geometry("300x200")

tk.Label(root, text="Username").pack()
entry_username = tk.Entry(root)
entry_username.pack()

tk.Label(root, text="Password").pack()
entry_password = tk.Entry(root, show="*")
entry_password.pack()

tk.Button(root, text="Login", command=login).pack()
tk.Button(root, text="Register", command=register).pack()

# Initialize the database (if not already created)
setup_database()

# Start the main loop
root.mainloop()
