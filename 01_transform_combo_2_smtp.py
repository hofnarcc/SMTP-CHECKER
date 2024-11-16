import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime

def get_smtp_details(email):
    smtp_configs = {
        "gmail.com": ("smtp.gmail.com", 587),
        "mailgun.org": ("smtp.mailgun.org", 587),
        "office365.com": ("smtp.office365.com", 587),
        "sendgrid.net": ("smtp.sendgrid.net", 587),
    }
    
    domain = email.split('@')[1] if '@' in email else None  # Extract domain from email
    return smtp_configs.get(domain, None)  # Return corresponding SMTP config or None

def transform_accounts(input_file, output_file, option, progress_bar):
    total_lines = sum(1 for line in open(input_file))
    processed_lines = 0

    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            line = line.strip()
            if not line:
                continue

            try:
                if option == 1:
                    # Option 1: username:password input
                    username, password = line.split(':')
                    # Generate SMTP addresses for all services
                    for smtp_service, (host, port) in {
                        "Gmail": ("gmail.com", "smtp.gmail.com", 587),
                        "Mailgun": ("mailgun.org", "smtp.mailgun.org", 587),
                        "Office365": ("office365.com", "smtp.office365.com", 587),
                        "SendGrid": ("sendgrid.net", "smtp.sendgrid.net", 587),
                    }.items():
                        email_address = f"{username}@{host}"  # Create email from username
                        outfile.write(f"{port}|{host}|{email_address}|{password}\n")  # Write to output file

                elif option == 2:
                    # Option 2: email:password input
                    email, password = line.split(':')
                    
                    smtp_details = get_smtp_details(email)
                    if smtp_details:
                        host, port = smtp_details
                        outfile.write(f"{port}|{host}|{email}|{password}\n")  # Write to output file
                    else:
                        print(f"Warning: No SMTP configuration found for email '{email}'. Skipping...")

            except ValueError:
                print(f"Skipping invalid line: {line}")
                continue

            processed_lines += 1
            progress_bar['value'] = (processed_lines / total_lines) * 100
            root.update_idletasks()  # Update the GUI

def start_transformation():
    input_file = input_path.get()
    option = option_var.get()
    
    if not os.path.exists(input_file):
        messagebox.showerror("Error", "The specified input file does not exist.")
        return
    
    # Create output directory based on current date and time
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(os.getcwd(), f"transformed_accounts_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, "transformed_accounts.txt")
    
    # Start transformation
    progress_bar['value'] = 0
    transform_accounts(input_file, output_file, option, progress_bar)
    
    messagebox.showinfo("Success", f"Transformation complete. Output saved to: {output_file}")

# GUI setup
root = tk.Tk()
root.title("COMBO 2 SMTP [TRANSFORMER]")

# Input file selection
tk.Label(root, text="Select Input File:").grid(row=0, column=0, padx=10, pady=10)
input_path = tk.StringVar()
input_entry = tk.Entry(root, textvariable=input_path, width=40)
input_entry.grid(row=0, column=1, padx=10, pady=10)
tk.Button(root, text="Browse", command=lambda: input_path.set(filedialog.askopenfilename())).grid(row=0, column=2, padx=10, pady=10)

# Option selection
option_var = tk.IntVar(value=1)
tk.Label(root, text="Choose an option:").grid(row=1, column=0, padx=10, pady=10)
tk.Radiobutton(root, text="Option 1 (username:password)", variable=option_var, value=1).grid(row=1, column=1, padx=10, pady=10)
tk.Radiobutton(root, text="Option 2 (email:password)", variable=option_var, value=2).grid(row=1, column=2, padx=10, pady=10)

# Progress bar
progress_bar = ttk.Progressbar(root, orient='horizontal', length=300, mode='determinate')
progress_bar.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

# Start button
tk.Button(root, text="Start Transformation", command=start_transformation).grid(row=3, column=0, columnspan=3, pady=20)

root.mainloop()
