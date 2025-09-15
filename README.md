# Youtube-Checker

A Python script that automatically checks YouTube updates and sends email notifications. The script can be run manually or scheduled using GitHub Actions.

---

## Features

- Monitors YouTube for updates.
- Supports tracking **multiple YouTube channels** at the same time.
- Sends email notifications when new content is detected.
- Runs automatically on a schedule using GitHub Actions.
- Securely handles credentials using GitHub Secrets.

---

## Getting Started

### Prerequisites

- Python 3.10+ installed.
- GitHub account for Actions automation.
- Gmail account with an **App Password** for sending emails securely.

### Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/Youtube-Checker.git
cd Youtube-Checker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up GitHub Secrets:
- EMAIL_ADDRESS → your Gmail address.
- EMAIL_APP_PASSWORD → your Gmail App Password (recommended over your main password).

### Configuring Multiple Channels

You can track multiple YouTube channels by adding their channel IDs in the channels list in main.py:
```python
# main.py
channels = [
    "UC_x5XG1OV2P6uZZ5FSM9Ttw",  # Example Channel 1
    "UC29ju8bIPH5as8OGnQzwJyA",  # Example Channel 2
    # Add more channel IDs here
]
```

- The script will check all listed channels and send an email whenever new content is detected.
- To find a channel ID:
  1. Go to the channel’s page on YouTube.
  2. Look at the URL: https://www.youtube.com/channel/CHANNEL_ID
  3. Copy the CHANNEL_ID into the list.

### How It Works (Visual)
```Text
+-------------------+       +-------------------+
| YouTube Channel 1 |       | YouTube Channel 2 |
+-------------------+       +-------------------+
           |                         |
           | New video detected      | New video detected
           v                         v
+----------------------------------------------+
| Script checks all channels periodically     |
+----------------------------------------------+
           |
           v
+-------------------+
| Send Email Alert  |
+-------------------+
```

### Example Table of Multiple Channels
| Channel Name         | Channel ID                | Last Checked | New Video Alert |
| -------------------- | ------------------------- | ------------ | --------------- |
| Google Developers    | UC\_x5XG1OV2P6uZZ5FSM9Ttw | 2025-09-11   | Yes/No          |
| Traversy Media       | UC29ju8bIPH5as8OGnQzwJyA  | 2025-09-11   | Yes/No          |
| Add more channels... | Your channel IDs          | Timestamp    | Yes/No          |

### Usage

### Run locally:
```bash
python main.py
```

### Run via GitHub Actions:
- The workflow is scheduled in `.github/workflows/email_check.yml` to run automatically every 30 minutes.
- You can also manually trigger the workflow from the **Actions** tab.

### Workflow Example
```yaml
name: Run Youtube-Checker

on:
  schedule:
    - cron: "*/30 * * * *" # runs every 30 minutes
  workflow_dispatch:       # allows manual run

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.10"
      - run: pip install -r requirements.txt
      - run: python main.py
        env:
          EMAIL_ADDRESS: ${{ secrets.EMAIL_ADDRESS }}
          EMAIL_APP_PASSWORD: ${{ secrets.EMAIL_APP_PASSWORD }}
```

### Security Notes
- Never hardcode your email or password in the script.
- Always use GitHub Secrets for credentials.
- Gmail App Passwords are recommended for automation.

### License
MIT License © Jiggy Palconit
