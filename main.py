import requests
import time
import os
import random
import urllib
import string
import sys

BASE_URL = "https://discord.com/api/v9"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def title(title):
    if sys.platform.startswith('win'):
        os.system(f'title {title}')
    else:
        print(f"\33]0;{title}\a", end='', flush=True)

title("VOIDNET")

def get_headers(token):
    return {
        "Authorization": token,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

def get_user_id(token):
    r = requests.get(f"{BASE_URL}/users/@me", headers=get_headers(token))
    if r.status_code == 200:
        return r.json()["id"]
    else:
        print(f"failed to get user id: {r.status_code} {r.text}")
        return None

def list_servers(token):
    r = requests.get(f"{BASE_URL}/users/@me/guilds", headers=get_headers(token))
    if r.status_code == 200:
        return r.json()
    else:
        print(f"failed to get servers: {r.status_code} {r.text}")
        return []

def list_channels(token, server_id):
    r = requests.get(f"{BASE_URL}/guilds/{server_id}/channels", headers=get_headers(token))
    if r.status_code == 200:
        channels = r.json()
        return [c for c in channels if c['type'] == 0]
    else:
        print(f"failed to get channels: {r.status_code} {r.text}")
        return []

def send_message(token, channel_id, message):
    data = {"content": message}
    r = requests.post(f"{BASE_URL}/channels/{channel_id}/messages", headers=get_headers(token), json=data)
    if r.status_code in (200, 201):
        print("message sent.")
    else:
        print(f"failed to send message: {r.status_code} {r.text}")

def get_channel_messages(token, channel_id):
    r = requests.get(f"{BASE_URL}/channels/{channel_id}/messages?limit=50", headers=get_headers(token))
    if r.status_code == 200:
        return r.json()
    else:
        print(f"failed to get messages: {r.status_code} {r.text}")
        return []

def leave_all_servers(token):
    servers = list_servers(token)
    if not servers:
        print("no servers to leave")
        input("press enter...")
        return
    for srv in servers:
        r = requests.delete(f"{BASE_URL}/users/@me/guilds/{srv['id']}", headers=get_headers(token))
        if r.status_code == 204:
            print(f"left server {srv['name']}")
        else:
            print(f"failed to leave server {srv['name']}: {r.status_code} {r.text}")
        time.sleep(1)
    print("done leaving all servers")
    input("press enter...")

def change_server_nickname(token, server_id, new_nick):
    user_id = get_user_id(token)
    if not user_id:
        print("cant get user id, aborting nickname change")
        return
    r = requests.get(f"{BASE_URL}/guilds/{server_id}/members/{user_id}", headers=get_headers(token))
    if r.status_code == 200:
        current_nick = r.json().get("nick") or "(none)"
    else:
        current_nick = "(unknown)"
    print(f"current nickname: {current_nick}")
    data = {"nick": new_nick}
    r = requests.patch(f"{BASE_URL}/guilds/{server_id}/members/@me", headers=get_headers(token), json=data)
    if r.status_code == 200:
        print("nickname changed")
    elif r.status_code == 403:
        print("failed: missing permissions. make sure your token has rights to change nickname in that server.")
    else:
        print(f"failed to change nickname: {r.status_code} {r.text}")
    time.sleep(1)

def update_status_message(token, new_status):
    data = {
        "custom_status": {
            "text": new_status
        }
    }
    r = requests.patch(f"{BASE_URL}/users/@me/settings", headers=get_headers(token), json=data)
    if r.status_code == 200:
        print("status message updated")
    else:
        print(f"failed to update status message: {r.status_code} {r.text}")

def update_status_mode(token, mode):
    if mode not in ["online", "idle", "dnd", "invisible"]:
        print("invalid status mode")
        return
    data = {"status": mode}
    r = requests.patch(f"{BASE_URL}/users/@me/settings", headers=get_headers(token), json=data)
    if r.status_code == 200:
        print(f"status mode set to {mode}")
    else:
        print(f"failed to update status mode: {r.status_code} {r.text}")

def list_friends(token):
    r = requests.get(f"{BASE_URL}/users/@me/relationships", headers=get_headers(token))
    if r.status_code == 200:
        friends = r.json()
        print(f"total friends: {len(friends)}\n")
        for i, f in enumerate(friends, start=1):
            user = f["user"]
            print(f"{i}. {user['username']} (id: {user['id']})")
    else:
        print(f"failed to get friends: {r.status_code} {r.text}")
    input("press enter...")

def unfriend_user_by_id(token, user_id):
    r = requests.delete(f"{BASE_URL}/users/@me/relationships/{user_id}", headers=get_headers(token))
    if r.status_code == 204:
        print(f"successfully unfriended user id {user_id}")
    else:
        print(f"failed to unfriend user {user_id}: {r.status_code} {r.text}")
    input("press enter...")

def dm_user(token):
    user_id = input("enter user id to dm: ").strip()
    if not user_id.isdigit():
        print("invalid user id")
        input("press enter...")
        return
    data = {"recipient_id": user_id}
    r = requests.post(f"{BASE_URL}/users/@me/channels", headers=get_headers(token), json=data)
    if r.status_code not in (200, 201):
        print(f"failed to create dm channel: {r.status_code} {r.text}")
        input("press enter...")
        return
    channel_id = r.json()["id"]
    while True:
        clear_screen()
        messages = get_channel_messages(token, channel_id)
        for msg in reversed(messages):
            author = msg['author']['username']
            content = msg['content']
            print(f"{author}: {content}")
        print("\nenter your message (type 0 to exit to main menu):")
        msg = input("> ").strip()
        if msg == "0":
            break
        send_message(token, channel_id, msg)
        time.sleep(0.5)

def channel_menu(token, server_id):
    while True:
        clear_screen()
        channels = list_channels(token, server_id)
        if not channels:
            print("no text channels found")
            input("press enter...")
            return
        print("channels:")
        for i, ch in enumerate(channels, 1):
            print(f"{i}. {ch['name']} (id: {ch['id']})")
        print("0. back to main menu")
        choice = input("pick channel: ").strip()
        if choice == "0":
            break
        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(channels):
            print("invalid choice")
            input("press enter...")
            continue
        channel_id = channels[int(choice)-1]['id']
        while True:
            clear_screen()
            messages = get_channel_messages(token, channel_id)
            for msg in reversed(messages):
                author = msg['author']['username']
                content = msg['content']
                print(f"{author}: {content}")
            print("\nenter message (0 to return to main menu):")
            msg = input("> ").strip()
            if msg == "0":
                return
            send_message(token, channel_id, msg)
            time.sleep(0.5)

def delete_server_by_id(token):
    server_id = input("enter server id to delete: ").strip()
    if not server_id:
        print("server id required")
        time.sleep(1)
        return
    headers = get_headers(token)
    r = requests.get(f"{BASE_URL}/guilds/{server_id}", headers=headers)
    if r.status_code != 200:
        print(f"failed to get server info, error {r.status_code}")
        print(r.text)
        time.sleep(2)
        return
    server = r.json()
    server_name = server.get("name", "(unknown)")
    r2 = requests.delete(f"{BASE_URL}/guilds/{server_id}", headers=headers, json={"code": server_name})
    if r2.status_code == 204:
        print(f"successfully deleted server '{server_name}'")
    else:
        print(f"failed to delete server: {r2.status_code} {r2.text}")
    time.sleep(2)

def get_account_info(token):
    r = requests.get(f"{BASE_URL}/users/@me", headers=get_headers(token))
    if r.status_code == 200:
        data = r.json()
        print("account info:\n")
        print(f"username: {data['username']}#{data['discriminator']}")
        print(f"id: {data['id']}")
        print(f"email: {data.get('email')}")
        print(f"phone: {data.get('phone')}")
        print(f"verified: {data.get('verified')}")
        print(f"mfa_enabled: {data.get('mfa_enabled')}")
    else:
        print(f"failed to get account info: {r.status_code} {r.text}")
    input("press enter...")

def mass_server_nuke(token):
    servers = list_servers(token)
    if not servers:
        print("no servers to nuke")
        input("press enter...")
        return
    print(f"fucking nuking {len(servers)} servers...")
    for srv in servers:
        r_del = requests.delete(f"{BASE_URL}/guilds/{srv['id']}", headers=get_headers(token))
        if r_del.status_code == 204:
            print(f"deleted server: {srv['name']}")
        else:
            print(f"failed to delete {srv['name']}: {r_del.status_code} {r_del.text}")
        time.sleep(1)
    print("mass server nuke complete. RIP servers.")
    input("press enter...")

def remove_all_friends(token):
    r = requests.get(f"{BASE_URL}/users/@me/relationships", headers=get_headers(token))
    if r.status_code != 200:
        print(f"failed to get friends: {r.status_code} {r.text}")
        input("press enter...")
        return
    friends = r.json()
    if not friends:
        print("no friends to remove")
        input("press enter...")
        return
    print(f"removing {len(friends)} friends...")
    for f in friends:
        user_id = f["id"]
        r_del = requests.delete(f"{BASE_URL}/users/@me/relationships/{user_id}", headers=get_headers(token))
        if r_del.status_code == 204:
            print(f"removed friend id {user_id}")
        else:
            print(f"failed to remove friend {user_id}: {r_del.status_code} {r_del.text}")
        time.sleep(1)
    print("all friends removed. enjoy the lonely life.")
    input("press enter...")

def download_all_dms(token):
    r = requests.get(f"{BASE_URL}/users/@me/channels", headers=get_headers(token))
    if r.status_code != 200:
        print(f"failed to get dm channels: {r.status_code} {r.text}")
        input("press enter...")
        return
    channels = r.json()
    if not channels:
        print("no dm channels found")
        input("press enter...")
        return

    filename = "all_dms.txt"
    with open(filename, "w", encoding="utf-8") as f:
        for ch in channels:
            recipients = ch.get("recipients", [])
            if len(recipients) == 1:
                user = recipients[0]
                username = user.get("username", "unknown")
                user_id = user.get("id", "unknown")
                header = f"=== DM with {username} ({user_id}) ===\n"
            else:
                header = f"=== DM with channel id {ch['id']} ===\n"
            f.write(header)

            after = None
            while True:
                url = f"{BASE_URL}/channels/{ch['id']}/messages?limit=100"
                if after:
                    url += f"&before={after}"
                r_msgs = requests.get(url, headers=get_headers(token))
                if r_msgs.status_code != 200:
                    print(f"failed to get messages for channel {ch['id']}: {r_msgs.status_code} {r_msgs.text}")
                    break
                msgs = r_msgs.json()
                if not msgs:
                    break
                msgs.reverse()
                for msg in msgs:
                    author = msg['author']['username']
                    content = msg['content'].replace('\n', ' ')
                    f.write(f"{author}: {content}\n")
                after = msgs[0]['id']
                if len(msgs) < 100:
                    break
            f.write("\n\n")
    print(f"all dms saved to {filename}")
    input("press enter...")

def mass_rename_nicknames(token):
    servers = list_servers(token)
    if not servers:
        print("no servers found")
        input("press enter...")
        return
    new_nick = input("enter new nickname to set on all servers: ").strip()
    if not new_nick:
        print("nickname required")
        input("press enter...")
        return
    print(f"changing nickname to '{new_nick}' on {len(servers)} servers...")
    for srv in servers:
        data = {"nick": new_nick}
        r = requests.patch(f"{BASE_URL}/guilds/{srv['id']}/members/@me", headers=get_headers(token), json=data)
        if r.status_code == 200:
            print(f"changed nickname in {srv['name']}")
        elif r.status_code == 403:
            print(f"no permission to change nickname in {srv['name']}")
        else:
            print(f"failed to change nickname in {srv['name']}: {r.status_code} {r.text}")
        time.sleep(1)
    print("mass rename complete.")
    input("press enter...")

def random_name(length=25):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def create_channel(name, token, guild_id):
    headers = {
        "Authorization": token,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Content-Type": "application/json"
    }
    url = f"https://discord.com/api/v9/guilds/{guild_id}/channels"
    payload = {"name": name, "type": 0}
    r = requests.post(url, headers=headers, json=payload)
    if r.status_code == 201:
        print(f"Created channel: {name}")
    else:
        print(f"Failed to create channel {name}: {r.status_code} {r.text}")

def spam_channels(token, guild_id, amount=50):
    print("[*] Starting channel spam...")
    for _ in range(amount):
        name = random_name()
        create_channel(name, token, guild_id)
        time.sleep(0.1)

def get_friends(token):
    headers = {
        "Authorization": token,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    friends_res = requests.get("https://discord.com/api/v9/users/@me/relationships", headers=headers)
    if friends_res.status_code != 200:
        print("failed to get friends list:", friends_res.text)
        return []
    friends = friends_res.json()
    return [f['user']['id'] for f in friends if f['type'] == 1]

def dm_all_friends(token, friend_id, message):
    headers = {
        "Authorization": token,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    dm_res = requests.post("https://discord.com/api/v9/users/@me/channels", headers=headers, json={"recipient_id": friend_id})
    if dm_res.status_code != 200:
        print(f"failed to create dm with {friend_id}: {dm_res.text}")
        return False
    dm_channel_id = dm_res.json()['id']
    msg_res = requests.post(f"https://discord.com/api/v9/channels/{dm_channel_id}/messages", headers=headers, json={"content": message})
    if msg_res.status_code in (200, 201):
        print(f"sent to {friend_id}")
        return True
    else:
        print(f"failed to send to {friend_id}: {msg_res.text}")
        return False

def spam_friends(token, message, delay=0.5):
    friend_ids = get_friends(token)
    print(f"found {len(friend_ids)} friends. sending messages...")
    for fid in friend_ids:
        dm_all_friends(token, fid, message)
        time.sleep(delay)
    print("done.")

def get_messages(token, channel_id, limit=100):
    headers = {
        "Authorization": token,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Content-Type": "application/json"
    }
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages?limit={limit}"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r.json()
    else:
        print(f"Failed to fetch messages: {r.status_code} {r.text}")
        return []

def react_to_messages(token, channel_id):
    headers = {
        "Authorization": token,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Content-Type": "application/json"
    }

    emojis = input("enter emojis (separate with ', '): ").strip().split(", ")
    messages = get_messages(token, channel_id, limit=100)

    if not messages:
        print("no messages found")
        return

    for msg in messages:
        msg_id = msg['id']
        for emoji_char in emojis:
            emoji_encoded = urllib.parse.quote(emoji_char)
            url = f"https://discord.com/api/v10/channels/{channel_id}/messages/{msg_id}/reactions/{emoji_encoded}/@me"

            success = False
            while not success:
                r = requests.put(url, headers=headers)
                if r.status_code == 204:
                    print(f"reacted with {emoji_char} to msg {msg_id}")
                    success = True
                elif r.status_code == 429:
                    retry_after = r.json().get("retry_after", 1)
                    print(f"rate limited on {emoji_char} for msg {msg_id}, retrying in {retry_after}s")
                    time.sleep(retry_after)
                else:
                    print(f"failed to react {emoji_char} to msg {msg_id}: {r.status_code} {r.text}")
                    time.sleep(1)

def get_channels(token, guild_id):
    headers = {
        "Authorization": token,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Content-Type": "application/json"
    }
    url = f"https://discord.com/api/v9/guilds/{guild_id}/channels"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r.json()
    else:
        print(f"Failed to get channels: {r.status_code}")
        return []

def delete_channel(token, channel_id):
    headers = {
        "Authorization": token,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Content-Type": "application/json"
    }
    url = f"https://discord.com/api/v9/channels/{channel_id}"
    r = requests.delete(url, headers=headers)
    if r.status_code == 204:
        print(f"Deleted channel {channel_id}")
    else:
        print(f"Failed to delete channel {channel_id}: {r.status_code}")

def get_roles(token, guild_id):
    headers = {
        "Authorization": token,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Content-Type": "application/json"
    }
    url = f"https://discord.com/api/v9/guilds/{guild_id}/roles"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r.json()
    else:
        print(f"Failed to get roles: {r.status_code}")
        return []

def delete_role(token, guild_id, role_id):
    headers = {
        "Authorization": token,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Content-Type": "application/json"
    }
    url = f"https://discord.com/api/v9/guilds/{guild_id}/roles/{role_id}"
    r = requests.delete(url, headers=headers)
    if r.status_code == 204:
        print(f"deleted role {role_id}")
    else:
        print(f"failed to delete role {role_id}: {r.status_code}")

def get_members(token, guild_id):
    headers = {
        "Authorization": token,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Content-Type": "application/json"
    }
    url = f"https://discord.com/api/v9/guilds/{guild_id}/members?limit=1000"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r.json()
    else:
        print(f"failed to get members: {r.status_code}")
        return []

def get_own_id(token):
    headers = {
        "Authorization": token,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Content-Type": "application/json"
    }
    url = "https://discord.com/api/v9/users/@me"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r.json()['id']
    else:
        return None

def nuke(token, guild_id):
    print("[*] starting server detonation...")

    channels = get_channels(token, guild_id)
    for ch in channels:
        delete_channel(token, ch['id'])
        time.sleep(1)

    roles = get_roles(token, guild_id)
    for role in roles:
        if role['name'] == "@everyone":
            continue
        delete_role(token, guild_id, role['id'])
        time.sleep(1)

    members = get_members(token, guild_id)
    own_id = get_own_id(token)
    for member in members:
        if member['user']['id'] == own_id:
            continue
        time.sleep(1)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main_menu(token):
    while True:
        clear_screen()
        LIGHT_PURPLE = "\033[38;5;219m"
        LIGHT_CYAN = "\033[96m"
        LIGHT_RED = "\033[91m"
        RESET = "\033[0m"
        BOLD = "\033[1m"

        header = f"""
{LIGHT_PURPLE}{BOLD}
 ██▒   █▓ ▒█████   ██▓▓█████▄  ███▄    █ ▓█████▄▄▄█████▓
▓██░   █▒▒██▒  ██▒▓██▒▒██▀ ██▌ ██ ▀█   █ ▓█   ▀▓  ██▒ ▓▒
 ▓██  █▒░▒██░  ██▒▒██▒░██   █▌▓██  ▀█ ██▒▒███  ▒ ▓██░ ▒░
  ▒██ █░░▒██   ██░░██░░▓█▄   ▌▓██▒  ▐▌██▒▒▓█  ▄░ ▓██▓ ░ 
   ▒▀█░  ░ ████▓▒░░██░░▒████▓ ▒██░   ▓██░░▒████▒ ▒██▒ ░ 
   ░ ▐░  ░ ▒░▒░▒░ ░▓   ▒▒▓  ▒ ░ ▒░   ▒ ▒ ░░ ▒░ ░ ▒ ░░   
   ░ ░░    ░ ▒ ▒░  ▒ ░ ░ ▒  ▒ ░ ░░   ░ ▒░ ░ ░  ░   ░    
     ░░  ░ ░ ░ ▒   ▒ ░ ░ ░  ░    ░   ░ ░    ░    ░      
      ░      ░ ░   ░     ░             ░    ░  ░        
     ░                 ░      
         ░ ░                {LIGHT_PURPLE}
{RESET}
"""

        print(header)

        menu_layout = f"""
{LIGHT_CYAN}{BOLD}[ account & servers ]{RESET}
   {LIGHT_CYAN}01{RESET}  list servers
   {LIGHT_CYAN}02{RESET}  dm user by id
   {LIGHT_RED}03{RESET}  leave all servers
   {LIGHT_CYAN}04{RESET}  change server nickname
   {LIGHT_CYAN}05{RESET}  edit status message
   {LIGHT_CYAN}06{RESET}  edit status mode
   {LIGHT_CYAN}07{RESET}  view account info (email + phone)

{LIGHT_CYAN}{BOLD}[ friends ]{RESET}
   {LIGHT_CYAN}08{RESET}  list all friends
   {LIGHT_CYAN}09{RESET}  unfriend user by id
   {LIGHT_RED}10{RESET}  remove all friends
   {LIGHT_RED}11{RESET}  dm all friends custom message

{LIGHT_CYAN}{BOLD}[ nukes & chaos ]{RESET}
   {LIGHT_RED}12{RESET}  delete server by id (no 2fa)
   {LIGHT_RED}13{RESET}  mass server nuke
   {LIGHT_RED}14{RESET}  mass rename nicknames on all servers
   {LIGHT_RED}15{RESET}  spam channels
   {LIGHT_RED}16{RESET}  react to messages with emojis
   {LIGHT_RED}17{RESET}  mass delete channels & roles

{LIGHT_CYAN}{BOLD}[ misc ]{RESET}
   {LIGHT_CYAN}18{RESET}  download all dms
   {LIGHT_RED}00{RESET}  exit
"""

        print(menu_layout)
        print()
        choice = input(f"{BOLD}{LIGHT_PURPLE}>>> choose wisely: {RESET}").strip()

        if choice == "1":
            servers = list_servers(token)
            if not servers:
                print("no servers found")
                input("press enter...")
                continue
            while True:
                clear_screen()
                print("servers:")
                for i, srv in enumerate(servers, 1):
                    print(f"{i}. {srv['name']} (id: {srv['id']})")
                print("0. back to main menu")
                sel = input("pick server: ").strip()
                if sel == "0":
                    break
                if not sel.isdigit() or int(sel) < 1 or int(sel) > len(servers):
                    print("invalid choice")
                    input("press enter...")
                    continue
                server_id = servers[int(sel)-1]['id']
                channel_menu(token, server_id)

        elif choice == "2":
            dm_user(token)

        elif choice == "3":
            leave_all_servers(token)

        elif choice == "4":
            servers = list_servers(token)
            if not servers:
                print("no servers found")
                input("press enter...")
                continue
            while True:
                clear_screen()
                print("servers:")
                for i, srv in enumerate(servers, 1):
                    print(f"{i}. {srv['name']} (id: {srv['id']})")
                print("0. back")
                sel = input("pick server: ").strip()
                if sel == "0":
                    break
                if not sel.isdigit() or int(sel) < 1 or int(sel) > len(servers):
                    print("invalid choice")
                    input("press enter...")
                    continue
                server_id = servers[int(sel)-1]['id']
                new_nick = input("enter new nickname: ").strip()
                if not new_nick:
                    print("nickname required")
                    input("press enter...")
                    continue
                change_server_nickname(token, server_id, new_nick)
                input("press enter to continue...")

        elif choice == "5":
            new_status = input("enter new custom status message: ")
            update_status_message(token, new_status)
            input("press enter...")

        elif choice == "6":
            print("status modes: online, idle, dnd, invisible")
            mode = input("enter status mode: ").strip()
            update_status_mode(token, mode)
            input("press enter...")

        elif choice == "7":
            get_account_info(token)

        elif choice == "8":
            list_friends(token)

        elif choice == "9":
            user_id = input("enter user id to unfriend: ").strip()
            unfriend_user_by_id(token, user_id)

        elif choice == "10":
            remove_all_friends(token)

        elif choice == "11":
            message = input("enter message to send to all friends: ")
            spam_friends(token, message)
            input("done. press enter...")

        elif choice == "12":
            delete_server_by_id(token)

        elif choice == "13":
            mass_server_nuke(token)

        elif choice == "14":
            mass_rename_nicknames(token)

        elif choice == "15":
            guild_id = input("enter guild id: ").strip()
            amount = input("how many channels to create (default 50): ").strip()
            amount = int(amount) if amount.isdigit() else 50
            spam_channels(token, guild_id, amount)
            input("done. press enter...")

        elif choice == "16":
            channel_id = input("enter channel id to react in: ").strip()
            react_to_messages(token, channel_id)
            input("done. press enter...")

        elif choice == "17":
            guild_id = input("enter guild id: ").strip()
            nuke(token, guild_id)
            input("done. press enter...")

        elif choice == "18":
            download_all_dms(token)

        elif choice == "0":
            break

        else:
            print("invalid option")
            input("press enter...")

if __name__ == "__main__":
    token = input("enter your discord token: ").strip()
    main_menu(token)