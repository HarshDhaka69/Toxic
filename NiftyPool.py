from telethon import TelegramClient, functions, types
import asyncio
import os
import logging
import time
import platform
import json
import getpass
from datetime import datetime
from colorama import Fore, Style, Back, init

# Set up logging
log_directory = "logs"
os.makedirs(log_directory, exist_ok=True)
log_filename = os.path.join(log_directory, f"niftypool_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("NiftyPool")

# Initialize colorama with autoreset
init(autoreset=True)

# Constants
CONFIG_DIR = "config"
CREDENTIALS_FILE = os.path.join(CONFIG_DIR, "credentials.json")
DELAY_BETWEEN_MESSAGES = 5  # Default delay between messages

# Terminal utilities
def clear_screen():
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def print_header():
    clear_screen()
    print(f"{Fore.CYAN}{Style.BRIGHT}╔══════════════════════════════════════════════════════════════╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{Style.BRIGHT}║{Back.BLUE}                   TELEGRAM AUTOMATION TOOL                    {Back.RESET}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{Style.BRIGHT}╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}               Contact Owner : @ItsHarshX (Telegram)               {Style.RESET_ALL}")
    print()

def print_footer():
    print()
    print(f"{Fore.CYAN}{Style.BRIGHT}════════════════════════════════════════════════════════════════{Style.RESET_ALL}")
    print()

def print_menu_item(number, text, selected=False):
    if selected:
        print(f"{Fore.BLACK}{Back.CYAN} {number} {Back.RESET} {Fore.CYAN}{Style.BRIGHT}{text}{Style.RESET_ALL}")
    else:
        print(f"{Fore.CYAN} {number} {Fore.WHITE}{text}{Style.RESET_ALL}")

def print_info(text):
    print(f"{Fore.BLUE}ℹ {text}{Style.RESET_ALL}")

def print_success(text):
    print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")

def print_warning(text):
    print(f"{Fore.YELLOW}⚠ {text}{Style.RESET_ALL}")

def print_error(text):
    print(f"{Fore.RED}✗ {text}{Style.RESET_ALL}")

def print_loading(text):
    print(f"{Fore.MAGENTA}⟳ {text}...{Style.RESET_ALL}")

def loading_animation(text, seconds=2):
    animation = "|/-\\"
    for i in range(seconds * 10):
        time.sleep(0.1)
        print(f"\r{Fore.MAGENTA}⟳ {text}... {animation[i % len(animation)]}", end="")
    print()

# Credentials management
def ensure_config_dir():
    """Ensure config directory exists"""
    os.makedirs(CONFIG_DIR, exist_ok=True)

def save_credentials(session_name, api_id, api_hash):
    """Save API credentials to config file"""
    ensure_config_dir()
    
    credentials = {}
    if os.path.exists(CREDENTIALS_FILE):
        try:
            with open(CREDENTIALS_FILE, 'r') as f:
                credentials = json.load(f)
        except:
            credentials = {}
    
    credentials[session_name] = {
        "api_id": api_id,
        "api_hash": api_hash,
        "last_used": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    try:
        with open(CREDENTIALS_FILE, 'w') as f:
            json.dump(credentials, f)
        return True
    except Exception as e:
        logger.error(f"Failed to save credentials: {str(e)}", exc_info=True)
        return False

def get_credentials(session_name):
    """Get saved API credentials for a session"""
    if not os.path.exists(CREDENTIALS_FILE):
        return None
        
    try:
        with open(CREDENTIALS_FILE, 'r') as f:
            credentials = json.load(f)
            
        if session_name in credentials:
            return credentials[session_name]
        return None
    except Exception as e:
        logger.error(f"Failed to read credentials: {str(e)}", exc_info=True)
        return None

async def get_chat_info(client):
    chat_info = []
    try:
        print_loading("Fetching chats")
        async for dialog in client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                chat_info.append({
                    "id": dialog.id,
                    "name": dialog.name,
                    "type": "channel" if dialog.is_channel else "group"
                })
        print_success(f"Retrieved {len(chat_info)} chats")
        logger.info(f"Successfully retrieved {len(chat_info)} chats")
    except Exception as e:
        print_error(f"Error retrieving chat info: {str(e)}")
        logger.error(f"Error retrieving chat info: {str(e)}", exc_info=True)
    return chat_info

async def send_last_message_to_groups(client, time_delay, num_times, chat_ids):
    for i in range(num_times):
        print()
        print_info(f"Send round {i+1}/{num_times}")
        try:
            messages = await client.get_messages('me', limit=1)
            if messages and len(messages) > 0:
                last_message = messages[0]
                print_info(f"Found message (ID: {last_message.id}) to forward")
                logger.info(f"Found last message (ID: {last_message.id}) to forward")
                
                total = len(chat_ids)
                successful = 0
                failed = 0
                failed_chats = []
                
                print_info(f"Sending to {total} groups:")
                print(f"{Fore.CYAN}┌{'─' * 60}┐{Style.RESET_ALL}")
                
                for idx, chat_id in enumerate(chat_ids):
                    progress = int((idx / total) * 50)
                    print(f"\r{Fore.CYAN}│{Fore.GREEN}{'█' * progress}{Fore.WHITE}{'░' * (50 - progress)}{Fore.CYAN}│ {idx}/{total} {(idx/total)*100:.1f}%", end="")
                    
                    try:
                        await client.forward_messages(chat_id, last_message)
                        successful += 1
                        logger.info(f"Message successfully sent to chat_id {chat_id}")
                    except Exception as e:
                        failed += 1
                        failed_chats.append((chat_id, str(e)))
                        error_msg = f"Failed to send to {chat_id}: {str(e)}"
                        logger.error(error_msg)
                    
                    # Added 5-second delay between messages to avoid rate limiting
                    await asyncio.sleep(DELAY_BETWEEN_MESSAGES)
                
                print(f"\r{Fore.CYAN}│{Fore.GREEN}{'█' * 50}{Fore.CYAN}│ {total}/{total} 100.0%{' ' * 10}")
                print(f"{Fore.CYAN}└{'─' * 60}┘{Style.RESET_ALL}")
                
                print_success(f"Completed: {successful} successful, {failed} failed")
                
                # Show failed chats if any
                if failed > 0:
                    print_warning("Failed chats:")
                    for chat_id, error in failed_chats[:5]:  # Show only first 5 failures
                        print(f"{Fore.RED}  • Chat ID {chat_id}: {error}")
                    if len(failed_chats) > 5:
                        print(f"{Fore.RED}  • ... and {len(failed_chats) - 5} more (check logs for details)")
            else:
                print_warning("No messages found to forward")
                logger.warning("No messages found to forward")
        except Exception as e:
            print_error(f"Error in auto-sending: {str(e)}")
            logger.error(f"Error in auto-sending loop: {str(e)}", exc_info=True)
            
        if i < num_times - 1:  # Don't show countdown after the last iteration
            print_info(f"Waiting {time_delay} seconds until next round")
            
            # Countdown timer
            for remaining in range(time_delay, 0, -1):
                mins, secs = divmod(remaining, 60)
                print(f"\r{Fore.BLUE}ℹ Next round in: {mins:02d}:{secs:02d}", end="")
                await asyncio.sleep(1)
            print()
            
        logger.info(f"Completed send round {i+1}/{num_times}")

async def login_account():
    logger.info("Starting new account login process")
    try:
        print_header()
        print(f"{Fore.YELLOW}{Style.BRIGHT}╔═══ ACCOUNT LOGIN ═══╗{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}╚{'═' * 21}╝{Style.RESET_ALL}")
        print()
        
        session_name = input(f"{Fore.WHITE}Enter session name {Fore.CYAN}(default: my_account){Fore.WHITE}: {Style.BRIGHT}") or "my_account"
        
        # Check if we already have credentials for this session
        credentials = get_credentials(session_name)
        if credentials:
            print_info(f"Found saved credentials for {session_name}")
            use_saved = input(f"{Fore.WHITE}Use saved credentials? {Fore.CYAN}(Y/n){Fore.WHITE}: {Style.BRIGHT}").lower() != 'n'
            
            if use_saved:
                api_id = credentials["api_id"]
                api_hash = credentials["api_hash"]
            else:
                api_id = int(input(f"{Fore.WHITE}Enter api id: {Style.BRIGHT}"))
                api_hash = input(f"{Fore.WHITE}Enter api hash: {Style.BRIGHT}")
        else:
            api_id = int(input(f"{Fore.WHITE}Enter api id: {Style.BRIGHT}"))
            api_hash = input(f"{Fore.WHITE}Enter api hash: {Style.BRIGHT}")
        
        print()
        print_loading("Connecting to Telegram")
        
        # Check if session file exists before trying to login
        session_exists = os.path.exists(f"{session_name}.session")
        
        client = TelegramClient(session_name, api_id, api_hash)
        await client.start()
        
        if await client.is_user_authorized():
            me = await client.get_me()
            success_msg = f"Successfully logged in as {me.first_name} (@{me.username})"
            print_success(success_msg)
            logger.info(success_msg)
            
            # Save credentials if this is a new session or we used new credentials
            if not session_exists or not credentials or not use_saved:
                save_credentials(session_name, api_id, api_hash)
                print_info("Credentials saved for future use")
        else:
            print_error("Failed to login: User not authorized")
            logger.error("Failed to login: User not authorized")
            await client.disconnect()
            input(f"\n{Fore.WHITE}Press Enter to continue...")
            return None
            
        input(f"\n{Fore.WHITE}Press Enter to continue...")
        return client
    except Exception as e:
        print_error(f"Login error: {str(e)}")
        logger.error(f"Login error: {str(e)}", exc_info=True)
        input(f"\n{Fore.WHITE}Press Enter to continue...")
        return None

async def list_sessions():
    try:
        sessions = []
        for file in os.listdir():
            if file.endswith('.session'):
                sessions.append(file.replace('.session', ''))
        logger.info(f"Found {len(sessions)} session files")
        return sessions
    except Exception as e:
        print_error(f"Error listing sessions: {str(e)}")
        logger.error(f"Error listing sessions: {str(e)}", exc_info=True)
        return []

async def switch_account():
    logger.info("Starting account switch process")
    try:
        print_header()
        print(f"{Fore.YELLOW}{Style.BRIGHT}╔═══ SWITCH ACCOUNT ═══╗{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}╚{'═' * 23}╝{Style.RESET_ALL}")
        print()
        
        sessions = await list_sessions()
        
        if not sessions:
            print_warning("No saved sessions found. Please create a new account.")
            logger.info("No saved sessions found, redirecting to new login")
            input(f"\n{Fore.WHITE}Press Enter to continue...")
            return await login_account()
        
        print_info("Available sessions:")
        for i, session in enumerate(sessions, 1):
            # Show additional info if credentials exist
            creds = get_credentials(session)
            last_used = f" (Last used: {creds['last_used']})" if creds and 'last_used' in creds else ""
            print(f"{Fore.CYAN} {i} {Fore.WHITE}{session}{Fore.YELLOW}{last_used}")
        
        print(f"\n{Fore.CYAN} {len(sessions) + 1} {Fore.WHITE}Create new account")
        print()
        
        try:
            choice = int(input(f"{Fore.WHITE}Select an account: {Style.BRIGHT}"))
            
            if choice == len(sessions) + 1:
                logger.info("User chose to create new account")
                return await login_account()
            
            if 1 <= choice <= len(sessions):
                session_name = sessions[choice - 1]
                logger.info(f"Selected session: {session_name}")
                
                # Check if we have saved credentials
                credentials = get_credentials(session_name)
                if credentials:
                    print_info(f"Found saved credentials for {session_name}")
                    use_saved = input(f"{Fore.WHITE}Use saved credentials? {Fore.CYAN}(Y/n){Fore.WHITE}: {Style.BRIGHT}").lower() != 'n'
                    
                    if use_saved:
                        api_id = credentials["api_id"]
                        api_hash = credentials["api_hash"]
                    else:
                        api_id = int(input(f"{Fore.WHITE}Enter api id: {Style.BRIGHT}"))
                        api_hash = input(f"{Fore.WHITE}Enter api hash: {Style.BRIGHT}")
                else:
                    api_id = int(input(f"{Fore.WHITE}Enter api id: {Style.BRIGHT}"))
                    api_hash = input(f"{Fore.WHITE}Enter api hash: {Style.BRIGHT}")
                
                print()
                print_loading("Connecting to Telegram")
                
                # Validate session file exists
                if not os.path.exists(f"{session_name}.session"):
                    print_error(f"Session file for {session_name} not found")
                    logger.error(f"Session file not found: {session_name}.session")
                    input(f"\n{Fore.WHITE}Press Enter to continue...")
                    return None
                
                client = TelegramClient(session_name, api_id, api_hash)
                await client.start()
                
                if await client.is_user_authorized():
                    me = await client.get_me()
                    success_msg = f"Successfully switched to {me.first_name} (@{me.username})"
                    print_success(success_msg)
                    logger.info(success_msg)
                    
                    # Update last used time
                    if credentials:
                        credentials["last_used"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        save_credentials(session_name, api_id, api_hash)
                    else:
                        save_credentials(session_name, api_id, api_hash)
                        print_info("Credentials saved for future use")
                else:
                    print_error("Failed to authenticate with saved session")
                    logger.error(f"Failed to authenticate with session: {session_name}")
                    await client.disconnect()
                    input(f"\n{Fore.WHITE}Press Enter to continue...")
                    return await login_account()
                    
                input(f"\n{Fore.WHITE}Press Enter to continue...")
                return client
            
            print_error("Invalid choice")
            logger.warning(f"Invalid choice: {choice}")
            input(f"\n{Fore.WHITE}Press Enter to continue...")
            return None
        except ValueError:
            print_error("Invalid input. Please enter a number.")
            input(f"\n{Fore.WHITE}Press Enter to continue...")
            return None
    except Exception as e:
        print_error(f"Error during account switch: {str(e)}")
        logger.error(f"Error during account switch: {str(e)}", exc_info=True)
        input(f"\n{Fore.WHITE}Press Enter to continue...")
        return None

async def settings_menu(client):
    """Settings menu for configuring tool behavior"""
    global DELAY_BETWEEN_MESSAGES
    
    selected_option = 1
    
    while True:
        print_header()
        print(f"{Fore.YELLOW}{Style.BRIGHT}╔═══ SETTINGS ═══╗{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}╚{'═' * 17}╝{Style.RESET_ALL}")
        print()
        
        print_menu_item(1, f"Message delay: {DELAY_BETWEEN_MESSAGES} seconds", selected_option == 1)
        print_menu_item(2, "Save settings", selected_option == 2)
        print_menu_item(3, "Back to main menu", selected_option == 3)
        
        print_footer()
        
        try:
            choice = int(input(f"{Fore.WHITE}Enter your choice: {Style.BRIGHT}"))
            selected_option = choice
            
            if choice == 1:
                try:
                    new_delay = int(input(f"{Fore.WHITE}Enter new delay in seconds (5-30 recommended): {Style.BRIGHT}"))
                    if new_delay < 1:
                        print_warning("Delay must be at least 1 second")
                        if new_delay < 3:
                            print_warning("Warning: Very short delays may trigger Telegram's anti-spam measures")
                    else:
                        DELAY_BETWEEN_MESSAGES = new_delay
                        print_success(f"Message delay set to {DELAY_BETWEEN_MESSAGES} seconds")
                except ValueError:
                    print_error("Invalid input. Please enter a number.")
            elif choice == 2:
                # Save settings to a config file
                try:
                    ensure_config_dir()
                    settings = {
                        "delay_between_messages": DELAY_BETWEEN_MESSAGES,
                        "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    with open(os.path.join(CONFIG_DIR, "settings.json"), 'w') as f:
                        json.dump(settings, f)
                    
                    print_success("Settings saved successfully")
                except Exception as e:
                    print_error(f"Failed to save settings: {str(e)}")
                    logger.error(f"Failed to save settings: {str(e)}", exc_info=True)
            elif choice == 3:
                return
            else:
                print_error("Invalid choice")
        except ValueError:
            print_error("Invalid input. Please enter a number.")
        
        input(f"\n{Fore.WHITE}Press Enter to continue...")

def load_settings():
    """Load settings from config file"""
    global DELAY_BETWEEN_MESSAGES
    
    settings_file = os.path.join(CONFIG_DIR, "settings.json")
    if os.path.exists(settings_file):
        try:
            with open(settings_file, 'r') as f:
                settings = json.load(f)
                
            if "delay_between_messages" in settings:
                DELAY_BETWEEN_MESSAGES = settings["delay_between_messages"]
                logger.info(f"Loaded message delay setting: {DELAY_BETWEEN_MESSAGES} seconds")
        except Exception as e:
            logger.error(f"Failed to load settings: {str(e)}", exc_info=True)

async def export_groups(client):
    """Export groups to a CSV file"""
    try:
        print_header()
        print(f"{Fore.YELLOW}{Style.BRIGHT}╔═══ EXPORT GROUPS ═══╗{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}╚{'═' * 22}╝{Style.RESET_ALL}")
        print()
        
        print_loading("Fetching groups and channels")
        chat_info = await get_chat_info(client)
        
        if not chat_info:
            print_warning("No groups or channels found to export")
            input(f"\n{Fore.WHITE}Press Enter to continue...")
            return
        
        # Ensure exports directory exists
        export_dir = "exports"
        os.makedirs(export_dir, exist_ok=True)
        
        export_file = os.path.join(export_dir, f"groups_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        
        # Write to CSV
        with open(export_file, 'w', encoding='utf-8') as f:
            f.write("ID,Name,Type\n")  # CSV header
            for chat in chat_info:
                # Escape double quotes in name
                name = chat['name'].replace('"', '""')
                f.write(f"{chat['id']},\"{name}\",{chat['type']}\n")
        
        print_success(f"Successfully exported {len(chat_info)} groups/channels to:")
        print_info(f"{export_file}")
        logger.info(f"Exported {len(chat_info)} groups to {export_file}")
        
    except Exception as e:
        print_error(f"Error exporting groups: {str(e)}")
        logger.error(f"Error exporting groups: {str(e)}", exc_info=True)
    
    input(f"\n{Fore.WHITE}Press Enter to continue...")

async def main():
    logger.info("Application started")
    
    # Load settings
    ensure_config_dir()
    load_settings()
    
    client = None
    selected_option = 1
    
    while True:
        try:
            # Main menu
            print_header()
            
            if client:
                me = await client.get_me()
                print(f"{Fore.GREEN}● Logged in as: {Style.BRIGHT}{me.first_name} (@{me.username}){Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}● Not logged in{Style.RESET_ALL}")
            
            print()
            print_menu_item(1, "Login/Switch Account", selected_option == 1)
            print_menu_item(2, "Show Group List", selected_option == 2)
            print_menu_item(3, "AutoSender", selected_option == 3)
            print_menu_item(4, "Export Groups", selected_option == 4)
            print_menu_item(5, "Settings", selected_option == 5)
            print_menu_item(6, "Exit", selected_option == 6)
            
            print_footer()
            
            try:
                choice = int(input(f"{Fore.WHITE}Enter your choice: {Style.BRIGHT}"))
                selected_option = choice  # Store last selection
                logger.info(f"User selected menu option: {choice}")
                
                if choice == 1:
                    # Handle login/switch account
                    if client:
                        logger.info("Disconnecting current client before switching")
                        await client.disconnect()
                        client = None
                    
                    print_header()
                    sessions = await list_sessions()
                    
                    if sessions:
                        print(f"{Fore.YELLOW}{Style.BRIGHT}╔═══ ACCOUNT LOGIN ═══╗{Style.RESET_ALL}")
                        print(f"{Fore.YELLOW}╚{'═' * 21}╝{Style.RESET_ALL}")
                        print()
                        
                        print_info("Available sessions:")
                        for i, session in enumerate(sessions, 1):
                            # Show additional info if credentials exist
                            creds = get_credentials(session)
                            last_used = f" (Last used: {creds['last_used']})" if creds and 'last_used' in creds else ""
                            print(f"{Fore.CYAN} {i} {Fore.WHITE}{session}{Fore.YELLOW}{last_used}")
                        
                        print(f"\n{Fore.CYAN} {len(sessions) + 1} {Fore.WHITE}Create new account")
                        print()
                        
                        login_choice = input(f"{Fore.WHITE}Select an account or create new {Fore.CYAN}(default: Create new){Fore.WHITE}: {Style.BRIGHT}")
                        
                        if not login_choice or login_choice.strip() == "":
                            logger.info("User selected default: new account")
                            client = await login_account()
                        else:
                            try:
                                if int(login_choice) == len(sessions) + 1:
                                    logger.info("User selected: new account")
                                    client = await login_account()
                                else:
                                    index = int(login_choice) - 1
                                    if 0 <= index < len(sessions):
                                        session_name = sessions[index]
                                        logger.info(f"User selected session: {session_name}")
                                        
                                        # Check if we have saved credentials
                                        credentials = get_credentials(session_name)
                                        if credentials:
                                            print_info(f"Found saved credentials for {session_name}")
                                            use_saved = input(f"{Fore.WHITE}Use saved credentials? {Fore.CYAN}(Y/n){Fore.WHITE}: {Style.BRIGHT}").lower() != 'n'
                                            
                                            if use_saved:
                                                api_id = credentials["api_id"]
                                                api_hash = credentials["api_hash"]
                                            else:
                                                api_id = int(input(f"{Fore.WHITE}Enter api id: {Style.BRIGHT}"))
                                                api_hash = input(f"{Fore.WHITE}Enter api hash: {Style.BRIGHT}")
                                        else:
                                            api_id = int(input(f"{Fore.WHITE}Enter api id: {Style.BRIGHT}"))
                                            api_hash = input(f"{Fore.WHITE}Enter api hash: {Style.BRIGHT}")
                                        
                                        print()
                                        print_loading("Connecting to Telegram")
                                        
                                        client = TelegramClient(session_name, api_id, api_hash)
                                        await client.start()
                                        
                                        if await client.is_user_authorized():
                                            me = await client.get_me()
                                            success_msg = f"Successfully logged in as {me.first_name} (@{me.username})"
                                            print_success(success_msg)
                                            logger.info(success_msg)
                                            
                                            # Update last used time
                                            if credentials:
                                                credentials["last_used"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                                save_credentials(session_name, api_id, api_hash)
                                            else:
                                                save_credentials(session_name, api_id, api_hash)
                                                print_info("Credentials saved for future use")
                                        else:
                                            print_error("Failed to authenticate with saved session")
                                            logger.error(f"Failed to authenticate with session: {session_name}")
                                            await client.disconnect()
                                            client = await login_account()
                                    else:
                                        print_error("Invalid choice")
                                        logger.warning(f"Invalid session index: {index}")
                                        client = await login_account()
                            except ValueError:
                                print_error("Invalid input")
                                logger.error("Invalid input for login choice")
                                client = await login_account()
                    else:
                        logger.info("No sessions found, creating new account")
                        client = await login_account()
                    
                    if client is None:
                        logger.warning("Login failed or was canceled")
                        print_error("Failed to login")
                        input(f"\n{Fore.WHITE}Press Enter to continue...")
                
                elif choice == 2:
                    # Show Group List
                    if not client:
                        logger.warning("Attempted to show groups without login")
                        print_error("Please login first!")
                        input(f"\n{Fore.WHITE}Press Enter to continue...")
                        continue
                    
                    print_header()
                    print(f"{Fore.YELLOW}{Style.BRIGHT}╔═══ GROUP LIST ═══╗{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}╚{'═' * 18}╝{Style.RESET_ALL}")
                    print()
                        
                    logger.info("Retrieving chat list")
                    chat_info = await get_chat_info(client)
                    
                    if chat_info:
                        print(f"{Fore.CYAN}┌{'─' * 70}┐{Style.RESET_ALL}")
                        print(f"{Fore.CYAN}│ {Fore.YELLOW}{'ID':12} {Fore.GREEN}{'Type':10} {Fore.WHITE}{'Name':45} {Fore.CYAN}│{Style.RESET_ALL}")
                        print(f"{Fore.CYAN}├{'─' * 70}┤{Style.RESET_ALL}")
                        
                        for chat in chat_info:
                            # Truncate name if too long
                            name = chat['name']
                            if len(name) > 44:
                                name = name[:41] + "..."
                            
                            chat_type = chat['type']
                            type_color = Fore.GREEN if chat_type == "group" else Fore.MAGENTA
                            
                            print(f"{Fore.CYAN}│ {Fore.YELLOW}{chat['id']:12} {type_color}{chat_type:10} {Fore.WHITE}{name:45} {Fore.CYAN}│{Style.RESET_ALL}")
                        
                        print(f"{Fore.CYAN}└{'─' * 70}┘{Style.RESET_ALL}")
                    else:
                        print_warning("No groups or channels found")
                    
                    logger.info(f"Displayed {len(chat_info)} chats")
                    input(f"\n{Fore.WHITE}Press Enter to continue...")
                
                elif choice == 3:
                    # AutoSender
                    if not client:
                        logger.warning("Attempted to use AutoSender without login")
                        print_error("Please login first!")
                        input(f"\n{Fore.WHITE}Press Enter to continue...")
                        continue
                    
                    print_header()
                    print(f"{Fore.YELLOW}{Style.BRIGHT}╔═══ AUTO SENDER ═══╗{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}╚{'═' * 19}╝{Style.RESET_ALL}")
                    print()
                        
                    logger.info("Starting AutoSender")
                    print_info("Retrieving chat list...")
                    chat_info = await get_chat_info(client)
                    
                    if not chat_info:
                        print_error("No groups or channels found to send messages to")
                        input(f"\n{Fore.WHITE}Press Enter to continue...")
                        continue
                    
                    # Filter options
                    print_info("Select groups to send to:")
                    print(f"{Fore.CYAN} 1 {Fore.WHITE}All groups and channels ({len(chat_info)} total)")
                    print(f"{Fore.CYAN} 2 {Fore.WHITE}Only groups")
                    print(f"{Fore.CYAN} 3 {Fore.WHITE}Only channels")
                    print(f"{Fore.CYAN} 4 {Fore.WHITE}Custom selection")
                    print()
                    
                    filter_choice = int(input(f"{Fore.WHITE}Enter your choice {Fore.CYAN}(default: 1){Fore.WHITE}: {Style.BRIGHT}") or "1")
                    
                    if filter_choice == 2:
                        chat_ids = [chat["id"] for chat in chat_info if chat["type"] == "group"]
                        print_info(f"Selected {len(chat_ids)} groups")
                    elif filter_choice == 3:
                        chat_ids = [chat["id"] for chat in chat_info if chat["type"] == "channel"]
                        print_info(f"Selected {len(chat_ids)} channels")
                    elif filter_choice == 4:
                        # Custom selection logic
                        print_info("Enter chat IDs to include (comma separated):")
                        ids_input = input(f"{Fore.WHITE}IDs: {Style.BRIGHT}")
                        try:
                            # Parse comma-separated IDs
                            custom_ids = [int(x.strip()) for x in ids_input.split(',') if x.strip()]
                            # Filter to only those that exist in our chat_info
                            valid_ids = [chat["id"] for chat in chat_info]
                            chat_ids = [id for id in custom_ids if id in valid_ids]
                            print_info(f"Selected {len(chat_ids)} valid chats")
                        except ValueError:
                            print_error("Invalid input. Using all chats instead.")
                            chat_ids = [chat["id"] for chat in chat_info]
                    else:  # Default to all
                        chat_ids = [chat["id"] for chat in chat_info]
                    
                    if not chat_ids:
                        print_error("No chats selected to send messages to")
                        input(f"\n{Fore.WHITE}Press Enter to continue...")
                        continue
                    
                    print_info(f"Will send to {len(chat_ids)} chats")
                    
                    try:
                        numtime = int(input(f"{Fore.WHITE}How many times to send the message: {Style.BRIGHT}"))
                        timee = int(input(f"{Fore.WHITE}Time delay between sending rounds (seconds): {Style.BRIGHT}"))
                        
                        if numtime <= 0 or timee < 0:
                            print_error("Invalid values. Number of times must be positive and delay must be non-negative.")
                            input(f"\n{Fore.WHITE}Press Enter to continue...")
                            continue
                            
                        # Confirm current message delay
                        global DELAY_BETWEEN_MESSAGES
                        print_info(f"Current delay between messages: {DELAY_BETWEEN_MESSAGES} seconds")
                        change_delay = input(f"{Fore.WHITE}Change message delay? {Fore.CYAN}(y/N){Fore.WHITE}: {Style.BRIGHT}").lower() == 'y'
                        
                        if change_delay:
                            try:
                                new_delay = int(input(f"{Fore.WHITE}Enter new delay in seconds (5-30 recommended): {Style.BRIGHT}"))
                                if new_delay < 1:
                                    print_error("Delay must be at least 1 second")
                                    if new_delay < 3:
                                        print_warning("Warning: Very short delays may trigger Telegram's anti-spam measures")
                                else:
                                    DELAY_BETWEEN_MESSAGES = new_delay
                                    print_success(f"Message delay set to {DELAY_BETWEEN_MESSAGES} seconds")
                            except ValueError:
                                print_error("Invalid input. Keeping current delay.")
                        
                        logger.info(f"AutoSender configured: {numtime} times with {timee}s delay to {len(chat_ids)} chats")
                        
                        print()
                        print_info("Checking for last message...")
                        messages = await client.get_messages('me', limit=1)
                        if not messages or len(messages) == 0:
                            print_error("No message found to forward. Please send a message to Saved Messages first.")
                            input(f"\n{Fore.WHITE}Press Enter to continue...")
                            continue
                            
                        # Preview the message
                        last_msg = messages[0]
                        preview_text = last_msg.text
                        if not preview_text and last_msg.media:
                            preview_text = "[Media message]"
                        elif not preview_text:
                            preview_text = "[Empty message]"
                            
                        if len(preview_text) > 30:
                            preview_text = preview_text[:27] + "..."
                            
                        print_success(f"Found message to forward: '{preview_text}'")
                        print()
                        
                        # Final confirmation
                        print_warning(f"Ready to send message {numtime} times to {len(chat_ids)} chats")
                        print_warning(f"Delay between chats: {DELAY_BETWEEN_MESSAGES}s, Delay between rounds: {timee}s")
                        confirm = input(f"{Fore.WHITE}Proceed? {Fore.CYAN}(Y/n){Fore.WHITE}: {Style.BRIGHT}").lower() != 'n'
                        
                        if not confirm:
                            print_info("Operation cancelled")
                            input(f"\n{Fore.WHITE}Press Enter to continue...")
                            continue
                        
                        print_info("Starting auto-sending process:")
                        
                        await send_last_message_to_groups(client, timee, numtime, chat_ids)
                        print_success("Auto-sending completed")
                    except ValueError:
                        print_error("Invalid input. Please enter numbers only.")
                    
                    input(f"\n{Fore.WHITE}Press Enter to continue...")
                
                elif choice == 4:
                    # Export Groups
                    if not client:
                        logger.warning("Attempted to export groups without login")
                        print_error("Please login first!")
                        input(f"\n{Fore.WHITE}Press Enter to continue...")
                        continue
                    
                    await export_groups(client)
                
                elif choice == 5:
                    # Settings
                    await settings_menu(client)
                
                elif choice == 6:
                    # Exit
                    if client:
                        logger.info("Disconnecting client before exit")
                        await client.disconnect()
                    logger.info("Application exit requested")
                    
                    print_header()
                    print(f"{Fore.YELLOW}{Style.BRIGHT}╔═══ GOODBYE ═══╗{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}╚{'═' * 15}╝{Style.RESET_ALL}")
                    print()
                    
                    print_success("Thank you for using Telegram Automation Tool")
                    print_info("Exiting application...")
                    await asyncio.sleep(1)
                    break
                
                else:
                    logger.warning(f"Invalid menu choice: {choice}")
                    print_error("Invalid choice. Please select a number between 1-6.")
                    input(f"\n{Fore.WHITE}Press Enter to continue...")
            
            except ValueError:
                logger.error("Invalid input for menu choice")
                print_error("Invalid input. Please enter a number.")
                input(f"\n{Fore.WHITE}Press Enter to continue...")
        except Exception as e:
            logger.critical(f"Unhandled exception in main loop: {str(e)}", exc_info=True)
            print_error(f"An unexpected error occurred: {str(e)}")
            print_warning("The error has been logged. Please check the logs for details.")
            input(f"\n{Fore.WHITE}Press Enter to continue...")
            # Continue running despite errors

if __name__ == "__main__":
    try:
        # Initial welcome screen
        print_header()
        print(f"{Fore.YELLOW}{Style.BRIGHT}╔═══ WELCOME ═══╗{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}╚{'═' * 15}╝{Style.RESET_ALL}")
        print()
        print_info("Telegram Automation Tool v1.1")
        print_info(f"Logs will be saved to: {log_filename}")
        print_info(f"For support, contact @ItsHarshX on Telegram")
        print()
        print_info("Press Enter to start...")
        input()
        
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application terminated by user (KeyboardInterrupt)")
        print()
        print_warning("Application terminated by user.")
    except Exception as e:
        logger.critical(f"Fatal error: {str(e)}", exc_info=True)
        print_error(f"A fatal error occurred: {str(e)}")
        print_warning(f"Check the log file for details: {log_filename}")