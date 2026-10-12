# Internship Automailer

I wrote this quick Python UI to help me apply to companies for my summer internship without having to send emails one by one or manually copy-paste hundreds of addresses. 

You just dump a raw list of emails into the text box, and the script handles the rest. It extracts valid emails, removes duplicates, attaches your CV, and sends them out. It incorporates a random delay (15-30s) between each email so Gmail doesn't flag the account as a spam bot.

## Features
- **Regex Extraction**: Paste raw text; it will find the emails and drop duplicates.
- **Config Persistence**: Automatically saves your email and subject line to `settings.json` so you don't have to retype them.
- **Graceful Abort & Progress Bar**: Added a Stop button to safely halt the loop without crashing the app, plus a visual progress bar.
- **Error Logging**: If an email bounces or fails, it gets appended to a `failed_emails.txt` file automatically.
- **Dynamic Templates**: Easily switch the email greeting between *Dear Madam*, *Dear Sir*, or *Dear Hiring Manager*.
- **No external dependencies**: Uses only standard Python libraries (`tkinter`, `smtplib`, `re`, `threading`, `json`).

## Setup

1. Clone the repo:
   ```bash
   git clone [https://github.com/achrafnassereddine/automailer.git](https://github.com/achrafnassereddine//automailer.git)
   cd automailer
