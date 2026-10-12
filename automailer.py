# Simple GUI script to automate sending internship applications.
# Includes anti-spam delays, config persistence, and a graceful abort feature.

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import threading
import time
import random
import os
import re
import json

CONFIG_FILE = "settings.json"

class AutoMailerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Automailer GUI")
        self.root.geometry("750x850")
        
        self.attachment_path = None
        self.cancel_flag = False
        
        self.templates = {
            "Generic (Dear Hiring Manager)": self.generate_body("Dear Hiring Manager,"),
            "Female (Dear Madam)": self.generate_body("Dear Madam,"),
            "Male (Dear Sir)": self.generate_body("Dear Sir,")
        }
        
        self.create_widgets()
        self.load_settings()

    def generate_body(self, greeting):
        return f"""{greeting}

Currently a student in [Your Degree/Year], I am seeking a summer internship from [Start Month] to [End Month] in the field of [Your Field].

Passionate about [Your Interests], I have developed solid practical skills through my academic and personal projects:

* Skill 1: [Detail or tool used].
* Skill 2: [Detail or tool used].
* Skill 3: [Detail or tool used].

Joining your team would allow me to bring my analytical skills and technical rigor to your projects. 

Please find attached my resume detailing my background and achievements. I am at your disposal for an interview to further discuss my motivation.

I look forward to hearing from you.

Best regards,

[Your Name]
[Your Phone]
[Your LinkedIn/GitHub]"""

    def create_widgets(self):
        # --- Credentials ---
        frame_creds = ttk.LabelFrame(self.root, text="SMTP Credentials (Gmail)")
        frame_creds.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame_creds, text="Email:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_email = ttk.Entry(frame_creds, width=40)
        self.entry_email.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_creds, text="App Password:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_pwd = ttk.Entry(frame_creds, width=40, show="*")
        self.entry_pwd.grid(row=1, column=1, padx=5, pady=5)

        # --- Message Setup ---
        frame_msg = ttk.LabelFrame(self.root, text="Email Setup")
        frame_msg.pack(fill="both", expand=True, padx=10, pady=5)

        ttk.Label(frame_msg, text="Subject:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_subject = ttk.Entry(frame_msg, width=60)
        self.entry_subject.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(frame_msg, text="Greeting type:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.combo_type = ttk.Combobox(frame_msg, values=list(self.templates.keys()), width=57, state="readonly")
        self.combo_type.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.combo_type.current(0)
        self.combo_type.bind("<<ComboboxSelected>>", self.update_template)

        ttk.Label(frame_msg, text="Body:").grid(row=2, column=0, padx=5, pady=5, sticky="ne")
        self.text_body = tk.Text(frame_msg, height=12, width=70)
        self.text_body.grid(row=2, column=1, padx=5, pady=5)
        self.update_template()

        # Attachment
        frame_file = ttk.Frame(frame_msg)
        frame_file.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        self.btn_attach = ttk.Button(frame_file, text="Attach CV (PDF)", command=self.attach_file)
        self.btn_attach.pack(side="left")
        self.lbl_file = ttk.Label(frame_file, text="No file selected", foreground="red")
        self.lbl_file.pack(side="left", padx=10)

        # --- Target list ---
        frame_dests = ttk.LabelFrame(self.root, text="Recipients (Paste raw text, script extracts emails)")
        frame_dests.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.text_dests = tk.Text(frame_dests, height=5, width=80)
        self.text_dests.pack(padx=5, pady=5, fill="both", expand=True)

        # --- Controls, Progress & Logs ---
        frame_ctrl = ttk.Frame(self.root)
        frame_ctrl.pack(fill="x", padx=10, pady=5)

        btn_frame = ttk.Frame(frame_ctrl)
        btn_frame.pack(pady=5)
        
        self.btn_send = ttk.Button(btn_frame, text="Start Sending", command=self.start_sending_thread)
        self.btn_send.pack(side="left", padx=5)

        self.btn_stop = ttk.Button(btn_frame, text="Stop / Abort", command=self.abort_process, state="disabled")
        self.btn_stop.pack(side="left", padx=5)

        self.progress = ttk.Progressbar(frame_ctrl, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=5)

        self.text_log = tk.Text(self.root, height=6, state="disabled", bg="#1e1e1e", fg="#00ff00", font=("Consolas", 9))
        self.text_log.pack(fill="x", padx=10, pady=5)

    def load_settings(self):
        """Loads saved email and subject from JSON config."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)
                    self.entry_email.insert(0, data.get("email", ""))
                    self.entry_subject.insert(0, data.get("subject", "Spontaneous Application: [Job Title]"))
            except Exception:
                pass

    def save_settings(self):
        """Saves current email and subject to JSON config."""
        data = {
            "email": self.entry_email.get().strip(),
            "subject": self.entry_subject.get().strip()
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f)

    def update_template(self, event=None):
        selection = self.combo_type.get()
        self.text_body.delete("1.0", tk.END)
        self.text_body.insert(tk.END, self.templates[selection])

    def attach_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if filepath:
            self.attachment_path = filepath
            self.lbl_file.config(text=f"Loaded: {os.path.basename(filepath)}", foreground="green")

    def log_message(self, msg):
        self.text_log.config(state="normal")
        self.text_log.insert("end", msg + "\n")
        self.text_log.see("end")
        self.text_log.config(state="disabled")

    def get_clean_emails(self):
        raw_text = self.text_dests.get("1.0", "end")
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', raw_text)
        return list(dict.fromkeys(emails))

    def abort_process(self):
        self.cancel_flag = True
        self.log_message("[!] Abort signal sent. Finishing current operation...")

    def start_sending_thread(self):
        if not self.entry_pwd.get():
            messagebox.showerror("Error", "App password is required.")
            return
        if not self.attachment_path:
            if not messagebox.askyesno("Warning", "No attachment selected. Continue?"):
                return
        
        emails = self.get_clean_emails()
        if not emails:
            messagebox.showerror("Error", "No valid emails found.")
            return

        self.save_settings()
        self.cancel_flag = False
        self.btn_send.config(state="disabled")
        self.btn_stop.config(state="normal")
        
        self.progress["maximum"] = len(emails)
        self.progress["value"] = 0
        
        self.log_message(f"--- Starting job: {len(emails)} emails ---")
        threading.Thread(target=self.send_emails, args=(emails,), daemon=True).start()

    def send_emails(self, emails):
        sender_email = self.entry_email.get().strip()
        sender_pwd = self.entry_pwd.get().replace(" ", "").strip()
        subject = self.entry_subject.get().strip()
        body = self.text_body.get("1.0", "end").strip()
        failed_list = []

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_pwd)
            self.log_message("[+] SMTP connection established.")

            for i, dest_email in enumerate(emails):
                if self.cancel_flag:
                    self.log_message("[-] Process aborted by user.")
                    break

                try:
                    msg = MIMEMultipart()
                    msg['From'] = sender_email
                    msg['To'] = dest_email
                    msg['Subject'] = subject
                    msg.attach(MIMEText(body, 'plain'))

                    if self.attachment_path:
                        with open(self.attachment_path, "rb") as f:
                            part = MIMEApplication(f.read(), Name=os.path.basename(self.attachment_path))
                        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(self.attachment_path)}"'
                        msg.attach(part)

                    server.send_message(msg)
                    self.log_message(f"[{i+1}/{len(emails)}] Sent to {dest_email}")

                except Exception as e:
                    self.log_message(f"[X] Failed to send to {dest_email} : {str(e)}")
                    failed_list.append(dest_email)

                self.progress["value"] = i + 1
                
                # Random sleep unless it's the last email or process is aborted
                if i < len(emails) - 1 and not self.cancel_flag:
                    delay = random.randint(15, 30)
                    self.log_message(f"    Sleeping {delay}s...")
                    time.sleep(delay)

            server.quit()
            
            if failed_list:
                with open("failed_emails.txt", "a") as f:
                    f.write("\n".join(failed_list) + "\n")
                self.log_message(f"[!] {len(failed_list)} failed. Saved to failed_emails.txt")
                
            self.log_message("--- Job finished ---")
            messagebox.showinfo("Done", "Email processing complete.")

        except smtplib.SMTPAuthenticationError:
            self.log_message("[X] Authentication failed. Check App Password.")
            messagebox.showerror("Auth Error", "Check your App Password.")
        except Exception as e:
            self.log_message(f"[X] Critical error: {str(e)}")
        
        finally:
            self.btn_send.config(state="normal")
            self.btn_stop.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoMailerApp(root)
    root.mainloop()