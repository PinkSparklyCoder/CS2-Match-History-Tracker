import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
import os
import tkinter.simpledialog as simpledialog

# File to store match data
CSV_FILE = "cs2_match_data.csv"

# Function to determine Win/Loss with Overtime consideration
def determine_result(t_rounds, ct_rounds, overtime=False, overtime_winner=None):
    total_rounds = t_rounds + ct_rounds
    if overtime:
        if overtime_winner == "T":
            return "Overtime Win (T)"
        elif overtime_winner == "CT":
            return "Overtime Win (CT)"
        else:
            return "Overtime Loss"
    elif total_rounds >= 24:  # Explicit check for overtime match condition
        return "Overtime Win" if t_rounds + ct_rounds > 24 else "Overtime Loss"
    elif total_rounds > 12:  # Normal match condition
        return "Win"
    else:
        return "Loss"

# Function to handle overtime winner selection
def ask_overtime_winner():
    winner = simpledialog.askstring("Overtime Winner", "Who won in overtime? (T or CT)").strip()
    if winner not in ["T", "CT"]:
        messagebox.showerror("Input Error", "Please select a valid overtime winner (T or CT).")
        return None
    return winner

# Function to save match data
def save_match():
    map_name = map_var.get()
    
    try:
        t_rounds = int(t_var.get())
        ct_rounds = int(ct_var.get())
    except ValueError:
        messagebox.showerror("Input Error", "Rounds must be valid integers!")
        return
    
    overtime = overtime_var.get()
    
    if not map_name or t_rounds < 0 or ct_rounds < 0:
        messagebox.showerror("Input Error", "Please enter valid match data!")
        return
    
    if overtime:  # If overtime is checked, ask who won
        overtime_winner = ask_overtime_winner()
        if not overtime_winner:
            return  # If no valid winner was selected, do not proceed
    else:
        overtime_winner = None
    
    result = determine_result(t_rounds, ct_rounds, overtime, overtime_winner)
    
    # Defining match data
    match_data = {"Map": map_name, "T Rounds": t_rounds, "CT Rounds": ct_rounds, "Result": result}
    
    # Save to CSV
    df = pd.DataFrame([match_data])  # Creating DataFrame from match data
    if not os.path.exists(CSV_FILE):
        df.to_csv(CSV_FILE, index=False)  # If file doesn't exist, create new one
    else:
        df.to_csv(CSV_FILE, mode="a", header=False, index=False)  # Append to file if it exists
    
    messagebox.showinfo("Success", "Match saved successfully!")
    reset_fields()

# Function to reset input fields
def reset_fields():
    map_var.set("")   # Clear the map selection (combobox)
    t_var.delete(0, tk.END)  # Clear the T rounds entry
    ct_var.delete(0, tk.END)  # Clear the CT rounds entry
    overtime_var.set(False)  # Uncheck the overtime checkbox

# GUI setup
root = tk.Tk()
root.title("CS2 Premier Match Tracker")
root.geometry("500x437")  # 25% bigger than the original 400x350

# Map selection
tk.Label(root, text="Map:").pack()
map_var = ttk.Combobox(root, values=["Mirage", "Inferno", "Nuke", "Dust 2", "Vertigo", "Ancient", "Anubis"])
map_var.pack()

# T rounds input
tk.Label(root, text="T Rounds Won:").pack()
t_var = tk.Entry(root)
t_var.pack()

# CT rounds input
tk.Label(root, text="CT Rounds Won:").pack()
ct_var = tk.Entry(root)
ct_var.pack()

# Overtime checkbox
overtime_var = tk.BooleanVar()
overtime_check = tk.Checkbutton(root, text="Overtime", variable=overtime_var)
overtime_check.pack()

# Save button
save_button = tk.Button(root, text="Save Match", command=save_match)
save_button.pack()

# View match history
def show_history():
    if not os.path.exists(CSV_FILE):
        messagebox.showinfo("No Data", "No match data found!")
        return

    df = pd.read_csv(CSV_FILE)
    if df.empty:  # Check if DataFrame is empty
        messagebox.showinfo("No Data", "No match history available!")
        return

    history_window = tk.Toplevel(root)
    history_window.title("Match History")
    history_window.geometry("500x437")  # 25% bigger

    tree = ttk.Treeview(history_window, columns=list(df.columns), show="headings")
    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    for _, row in df.iterrows():
        tree.insert("", "end", values=list(row))

    tree.pack(expand=True, fill="both")

# Add history button
history_button = tk.Button(root, text="View Match History", command=show_history)
history_button.pack()

# Add chart button
def show_chart():
    if not os.path.exists(CSV_FILE):
        messagebox.showinfo("No Data", "No match data found!")
        return
    
    df = pd.read_csv(CSV_FILE)
    
    if df.empty or "Result" not in df.columns:  # Check if DataFrame is empty or missing "Result" column
        messagebox.showinfo("No Data", "No data available for plotting!")
        return
    
    win_counts = df[df["Result"].str.contains("Win")]["Map"].value_counts()
    
    if win_counts.empty:  # Check if win_counts is empty
        messagebox.showinfo("No Wins", "No wins available to display!")
        return
    
    plt.figure(figsize=(10, 6))  # Make the chart 25% bigger
    win_counts.plot(kind="bar", color="green")
    plt.title("Wins per Map")
    plt.xlabel("Map")
    plt.ylabel("Number of Wins")
    plt.xticks(rotation=45)
    plt.show()

# Add Chart button
chart_button = tk.Button(root, text="Show Wins Chart", command=show_chart)
chart_button.pack()

# Add Match filtering
def show_filtered_history(filter_type="All"):
    if not os.path.exists(CSV_FILE):
        messagebox.showinfo("No Data", "No match data found!")
        return

    df = pd.read_csv(CSV_FILE)

    if filter_type == "wins":
        df = df[df["Result"].str.contains("Win")]
    elif filter_type == "Overtime":
        df = df[df["Result"].str.contains("Overtime")]

    history_window = tk.Toplevel(root)
    history_window.title(f"Match History - {filter_type}")
    history_window.geometry("500x437")  # 25% bigger

    tree = ttk.Treeview(history_window, columns=list(df.columns), show="headings")
    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    for _, row in df.iterrows():
        tree.insert("", "end", values=list(row))

    tree.pack(expand=True, fill="both")

# Filtering button
tk.Button(root, text="Show All Matches", command=lambda: show_filtered_history("All")).pack()
tk.Button(root, text="Show Only Wins", command=lambda: show_filtered_history("wins")).pack()
tk.Button(root, text="Show Only Overtime Matches", command=lambda: show_filtered_history("Overtime")).pack()

root.mainloop()
