# Telegram Automation Tool (NiftyPool)

A powerful Telegram automation tool that allows you to manage multiple accounts and automate message sending to groups and channels.

## Features

- Multiple account management
- Auto-sending messages to groups and channels
- Export group lists
- Configurable message delays
- Comprehensive logging

## Installation Instructions

### For Termux (Android)

1. Set up storage access (important):
```bash
termux-setup-storage
```
2. Update Termux packages:
```bash
pkg update && pkg upgrade -y
```

3. Install required packages:
```bash
pkg install python git -y
```

4. Clone this repository:
```bash
git clone https://github.com/HarshDhaka69/Toxic.git
```

5. Navigate to the project directory:
```bash
cd Toxic
```

6. Install required Python packages:
```bash
pip install telethon asyncio colorama
```

7. Create necessary directories:
```bash
mkdir -p logs config exports
```

8. Run the script:
```bash
python NiftyPool.py
```

### For Windows/Linux/Mac

1. Make sure Python 3.6+ is installed
2. Clone this repository:
```bash
git clone https://github.com/HarshDhaka69/Toxic.git
```

3. Navigate to the project directory:
```bash
cd Toxic
```

4. Install required packages:
```bash
pip install telethon asyncio colorama
```

5. Create necessary directories:
```bash
mkdir -p logs config exports
```

6. Run the script:
```bash
python NiftyPool.py
```

## First-Time Setup

When running the script for the first time:

1. You'll need to register for Telegram API credentials:
   - Go to https://my.telegram.org/
   - Log in with your phone number
   - Go to "API Development Tools"
   - Create a new application (any name will do)
   - Note the "api_id" and "api_hash" values
   - Enter these values when the script prompts you

2. The script will create:
   - Session files in the current directory
   - Logs in the `logs` directory
   - Configuration files in the `config` directory

## Usage

1. **Login/Switch Account**: Manage multiple Telegram accounts
2. **Show Group List**: View all groups and channels you are a member of
3. **AutoSender**: Forward messages to multiple groups with customizable delays
4. **Export Groups**: Export your groups list to a CSV file
5. **Settings**: Configure tool behavior

## Support

For support, contact @ItsHarshX on Telegram. 