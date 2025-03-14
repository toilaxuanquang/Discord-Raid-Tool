import requests
import random
import time
import threading
import json
import colorama
import websocket
from colorama import Fore, Style
import os
import sys

colorama.init(autoreset=True)

def purple_gradient(text, center=False):
    lines = text.splitlines()
    terminal_width = os.get_terminal_size().columns if hasattr(os, 'get_terminal_size') else 80
    for line in lines:
        if center:
            padding = (terminal_width - len(line)) // 2
            line = " " * padding + line + " " * (terminal_width - len(line) - padding)
        for i, char in enumerate(line):
            r = int(147 + (108 * (i / len(line))))
            g = int(112 * (1 - i / len(line)))
            b = int(219 - (50 * (i / len(line))))
            color = f"\033[38;2;{r};{g};{b}m{char}"
            print(color, end="")
        print("\033[0m")

def loading_animation():
    terminal_width = os.get_terminal_size().columns if hasattr(os, 'get_terminal_size') else 80
    base_text = "[/] Loading"
    frames = [
        f"{base_text}.  ",
        f"{base_text}.. ",
        f"{base_text}...",
        f"{base_text}.. ",
        f"{base_text}.  ",
        f"[\\] Loading.. ",
        f"[-] Loading.. ",
        f"[|] Loading.. ",
    ]
    colors = [
        (147, 112, 219), (155, 100, 210), (163, 88, 201), (171, 76, 192),
        (179, 64, 183), (187, 52, 174), (195, 40, 165), (203, 28, 156),
        (211, 16, 147), (219, 4, 138), (211, 16, 147), (203, 28, 156),
        (195, 40, 165), (187, 52, 174), (179, 64, 183), (171, 76, 192),
        (163, 88, 201), (155, 100, 210), (147, 112, 219)
    ]
    for _ in range(3):
        for frame, (r, g, b) in zip(frames, colors):
            padding = (terminal_width - len(frame)) // 2
            centered_frame = " " * padding + frame
            sys.stdout.write(f"\r\033[38;2;{r};{g};{b}m{centered_frame}\033[0m")
            sys.stdout.flush()
            time.sleep(0.1)
    sys.stdout.write(f"\r{' ' * terminal_width}\r")
    sys.stdout.flush()

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

class DiscordBot:
    def __init__(self, token_file, spam_interval=1):
        self.token_file = token_file
        self.spam_interval = spam_interval
        self.spam_duration = None
        self.spam_messages = [
            "**XUAN QUANG ON TOP**\n discord.gg/etx",
            "**HIDDEN GỬI LỜI CHÀO TỚI CÁC BÉ YÊU**\n discord.gg/etx",
            "**FROM HIDDEN WITH LOVE**\n discord.gg/etx"
        ]
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.2210.91",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Android 14; Mobile; rv:121.0) Gecko/121.0 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
            "Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Android 13; Mobile; rv:119.0) Gecko/119.0 Firefox/119.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 OPR/101.0.0.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.51",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
        ]
        self.active_threads = []
        self.running = True
        self.voice_connections = {}
        self.rate_limit_delays = {}
        self.tokens = self.get_tokens()
        self.bot_profiles = {}
        self.guild_members = []

    def check_token(self, token):
        url = "https://discord.com/api/v9/users/@me"
        headers = {
            'Authorization': token,
            'User-Agent': random.choice(self.user_agents),
            'Content-Type': 'application/json'
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                user_data = response.json()
                username = user_data.get('username', 'Unknown')
                purple_gradient(f"[DEBUG] Valid token: {token[:25]}... | Username: {username}", center=True)
                return True, username
            else:
                purple_gradient(f"[DEBUG] Invalid token: {token[:25]}...", center=True)
                return False, None
        except requests.RequestException as e:
            purple_gradient(f"[DEBUG] Error checking token: {token[:25]}... {e}", center=True)
            return False, None

    def check_all_tokens(self):
        clear_terminal()
        purple_gradient("[DEBUG] Token check started...", center=True)
        tokens = []
        try:
            with open(self.token_file, "r") as f:
                tokens = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            purple_gradient(f"[DEBUG] File {self.token_file} not found!", center=True)
            return []

        if not tokens:
            purple_gradient("[DEBUG] Token file is empty!", center=True)
            return []

        valid_tokens = []
        for token in tokens:
            is_valid, username = self.check_token(token)
            if is_valid:
                valid_tokens.append(token)
            time.sleep(0.5)

        purple_gradient(f"[DEBUG] Check completed. Valid tokens: {len(valid_tokens)}", center=True)
        input(f"{Fore.MAGENTA}➤ Press Enter to continue...{Style.RESET_ALL}")
        return valid_tokens

    def get_tokens(self):
        try:
            with open(self.token_file, "r") as f:
                tokens = [line.strip() for line in f if line.strip()]
                if not tokens:
                    purple_gradient("[DEBUG] Token file is empty!", center=True)
                    return []
                purple_gradient(f"[DEBUG] Loaded tokens: {len(tokens)}", center=True)
                return tokens
        except FileNotFoundError:
            purple_gradient(f"[DEBUG] File {self.token_file} not found!", center=True)
            return []

    def remove_token(self, token):
        if token in self.tokens:
            self.tokens.remove(token)
            purple_gradient(f"[DEBUG] Token {token[:25]}... has been removed from the session", center=True)

    def get_channel_users(self, token, channel_id):
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
        headers = {
            'Authorization': token,
            'User-Agent': random.choice(self.user_agents),
            'Content-Type': 'application/json'
        }
        user_ids = set()
        last_message_id = None
        total_messages = 0
        limit = 100

        while total_messages < 800:
            params = {'limit': limit}
            if last_message_id:
                params['before'] = last_message_id
            try:
                response = requests.get(url, headers=headers, params=params, timeout=10)
                if response.status_code == 200:
                    time.sleep(1)
                    messages = response.json()
                    if not messages:
                        break
                    for msg in messages:
                        if 'author' in msg:
                            user_ids.add(msg['author']['id'])
                    last_message_id = messages[-1]['id']
                    total_messages += len(messages)
                else:
                    purple_gradient(f"[DEBUG] Error {response.status_code} when fetching messages: {token[:25]}...", center=True)
                    break
            except requests.RequestException as e:
                purple_gradient(f"[DEBUG] Network error when fetching messages: {token[:25]}... {e}", center=True)
                break

        return [f"<@{user_id}>" for user_id in user_ids]

    def change_nickname(self, token, guild_id, new_nickname):
        url = f"https://discord.com/api/v9/guilds/{guild_id}/members/@me"
        headers = {
            'Authorization': token,
            'User-Agent': random.choice(self.user_agents),
            'Content-Type': 'application/json'
        }
        data = {"nick": new_nickname}
        try:
            response = requests.patch(url, headers=headers, json=data, timeout=10)
            if response.status_code == 200:
                purple_gradient(f"[DEBUG] Changed nickname to '{new_nickname}' for {token[:25]}...", center=True)
            elif response.status_code == 429:
                retry_after = response.json().get('retry_after', 5)
                purple_gradient(f"[DEBUG] Rate limited: waiting {retry_after:.2f} seconds for {token[:25]}...", center=True)
                time.sleep(retry_after)
            else:
                purple_gradient(f"[DEBUG] Error {response.status_code} when changing nickname: {token[:25]}...", center=True)
        except requests.RequestException as e:
            purple_gradient(f"[DEBUG] Network error when changing nickname: {token[:25]}... {e}", center=True)

    def set_online_status(self, token, status_text=None, activity_type="playing"):
        ws_url = "wss://gateway.discord.gg/?v=9&encoding=json"
        ws = websocket.WebSocket()
        try:
            ws.connect(ws_url)
            presence = {
                "status": "online",
                "afk": False
            }
            if status_text:
                activity_types = {
                    "playing": 0,
                    "streaming": 1,
                    "listening": 2,
                    "watching": 3,
                    "custom": 4,
                    "competing": 5
                }
                presence["activities"] = [{
                    "name": status_text,
                    "type": activity_types.get(activity_type, 0)
                }]
            identify_payload = {
                "op": 2,
                "d": {
                    "token": token,
                    "properties": {"$os": "windows", "$browser": "chrome", "$device": "pc"},
                    "presence": presence,
                    "compress": False,
                    "large_threshold": 250
                }
            }
            ws.send(json.dumps(identify_payload))
            response = json.loads(ws.recv())
            if response.get("op") == 10:
                heartbeat_interval = response["d"]["heartbeat_interval"] / 1000
                ws.send(json.dumps({"op": 1, "d": None}))
                purple_gradient(f"[DEBUG] Set status 'online' with '{activity_type} {status_text or ''}' for {token[:25]}...", center=True)
                threading.Thread(target=self.keep_online, args=(ws, heartbeat_interval, token)).start()
            else:
                raise Exception("Invalid WebSocket response")
        except Exception as e:
            purple_gradient(f"[DEBUG] Error setting status: {token[:25]}... {e}", center=True)

    def set_custom_presence(self, token, status="online", status_text=None, activity_type="playing"):
        ws_url = "wss://gateway.discord.gg/?v=9&encoding=json"
        ws = websocket.WebSocket()
        try:
            ws.connect(ws_url)
            valid_statuses = ["online", "dnd", "idle", "invisible"]
            presence = {
                "status": status if status in valid_statuses else "online",
                "afk": False
            }
            if status_text:
                activity_types = {
                    "playing": 0,
                    "streaming": 1,
                    "listening": 2,
                    "watching": 3,
                    "custom": 4,
                    "competing": 5
                }
                presence["activities"] = [{
                    "name": status_text,
                    "type": activity_types.get(activity_type, 0)
                }]
            identify_payload = {
                "op": 2,
                "d": {
                    "token": token,
                    "properties": {"$os": "windows", "$browser": "chrome", "$device": "pc"},
                    "presence": presence,
                    "compress": False,
                    "large_threshold": 250
                }
            }
            ws.send(json.dumps(identify_payload))
            response = json.loads(ws.recv())
            if response.get("op") == 10:
                heartbeat_interval = response["d"]["heartbeat_interval"] / 1000
                ws.send(json.dumps({"op": 1, "d": None}))
                status_display = status if not status_text else f"{status} ({activity_type} {status_text})"
                purple_gradient(f"[DEBUG] Set status '{status_display}' for {token[:25]}...", center=True)
                threading.Thread(target=self.keep_online, args=(ws, heartbeat_interval, token)).start()
            else:
                raise Exception("Invalid WebSocket response")
        except Exception as e:
            purple_gradient(f"[DEBUG] Error setting custom status: {token[:25]}... {e}", center=True)

    def keep_online(self, ws, heartbeat_interval, token):
        while self.running and token in self.tokens:
            try:
                ws.send(json.dumps({"op": 1, "d": None}))
                time.sleep(heartbeat_interval)
            except Exception:
                purple_gradient(f"[DEBUG] Error maintaining status: {token[:25]}...", center=True)
                break
        ws.close()

    def update_profile(self, token, pronoun=None, bio=None):
        url = "https://discord.com/api/v9/users/@me/profile"
        headers = {
            'Authorization': token,
            'User-Agent': random.choice(self.user_agents),
            'Content-Type': 'application/json'
        }
        data = {}
        if pronoun:
            data["pronouns"] = pronoun
        if bio:
            data["bio"] = bio
        try:
            response = requests.patch(url, headers=headers, json=data, timeout=10)
            if response.status_code == 200:
                purple_gradient(f"[DEBUG] Updated profile for {token[:25]}... Pronoun: {pronoun}, Bio: {bio}", center=True)
                self.bot_profiles[token] = {"pronoun": pronoun, "bio": bio}
            elif response.status_code == 429:
                retry_after = response.json().get('retry_after', 5)
                purple_gradient(f"[DEBUG] Rate limited: waiting {retry_after:.2f} seconds for {token[:25]}...", center=True)
                time.sleep(retry_after)
            else:
                purple_gradient(f"[DEBUG] Error {response.status_code} when updating profile: {token[:25]}...", center=True)
        except requests.RequestException as e:
            purple_gradient(f"[DEBUG] Network error when updating profile: {token[:25]}... {e}", center=True)

    def send_message(self, token, channel_id):
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
        headers = {
            'Authorization': token,
            'User-Agent': random.choice(self.user_agents),
            'Content-Type': 'application/json'
        }

        proxies = {
            "http": "http://axdokkpn-rotate:etdeptrai@p.webshare.io:80",
            "https": "http://axdokkpn-rotate:etdeptrai@p.webshare.io:80"
        }
        start_time = time.time()
        
        while self.running and token in self.tokens:
            if self.spam_duration and (time.time() - start_time) >= self.spam_duration:
                purple_gradient(f"[DEBUG] Spam time has expired for {token[:25]}...", center=True)
                break
                
            message_content = random.choice(self.spam_messages)
            
            if self.guild_members:
                mention = random.choice(self.guild_members)
                message_content = f"{mention} {message_content}"
            else:
                purple_gradient("[DEBUG] No members to mention!", center=True)
            
            nonce = str(random.randint(100000000000000000, 999999999999999999))
            data = {"content": message_content, "nonce": nonce, "tts": False}
            try:
                if token in self.rate_limit_delays:
                    delay = self.rate_limit_delays[token]
                    if time.time() < delay:
                        time.sleep(delay - time.time())

                response = requests.post(url, headers=headers, json=data, proxies=proxies, timeout=10)
                if response.status_code == 200:
                    purple_gradient(f"[DEBUG] Sent message: {token[:25]}...", center=True)
                elif response.status_code == 429:
                    retry_after = response.json().get('retry_after', 5)
                    purple_gradient(f"[DEBUG] Rate limited: waiting {retry_after:.2f} seconds for {token[:25]}...", center=True)
                    self.rate_limit_delays[token] = time.time() + retry_after
                    continue
                elif response.status_code == 401:
                    purple_gradient(f"[DEBUG] Invalid token: {token[:25]}...", center=True)
                    self.remove_token(token)
                    break
                else:
                    purple_gradient(f"[DEBUG] Error {response.status_code}: {token[:25]}...", center=True)
            except requests.RequestException as e:
                purple_gradient(f"[DEBUG] Network error: {token[:25]}... {e}", center=True)
                time.sleep(5)
                continue
            time.sleep(self.spam_interval)

    def unmute(self, guild_id, channel_id):
        for token, ws in list(self.voice_connections.items()):
            try:
                unmute_payload = {
                    "op": 4,
                    "d": {"guild_id": guild_id, "channel_id": channel_id, "self_mute": False, "self_deaf": False}
                }
                ws.send(json.dumps(unmute_payload))
                purple_gradient(f"[DEBUG] Token {token[:25]}... has been unmuted", center=True)
            except Exception as e:
                purple_gradient(f"[DEBUG] Error unmuting: {token[:25]}... {e}", center=True)

    def mute(self, guild_id, channel_id):
        for token, ws in list(self.voice_connections.items()):
            try:
                mute_payload = {
                    "op": 4,
                    "d": {"guild_id": guild_id, "channel_id": channel_id, "self_mute": True, "self_deaf": True}
                }
                ws.send(json.dumps(mute_payload))
                purple_gradient(f"[DEBUG] Token {token[:25]}... has been muted", center=True)
            except Exception as e:
                purple_gradient(f"[DEBUG] Error muting: {token[:25]}... {e}", center=True)

    def join_voice(self, token, guild_id, channel_id):
        ws_url = "wss://gateway.discord.gg/?v=9&encoding=json"
        ws = websocket.WebSocket()
        try:
            ws.connect(ws_url)
            identify_payload = {
                "op": 2,
                "d": {
                    "token": token,
                    "properties": {"$os": "windows", "$browser": "chrome", "$device": "pc"},
                    "compress": False,
                    "large_threshold": 250
                }
            }
            ws.send(json.dumps(identify_payload))
            response = json.loads(ws.recv())
            if response.get("op") == 10:
                heartbeat_interval = response["d"]["heartbeat_interval"] / 1000
                ws.send(json.dumps({"op": 1, "d": None}))
                voice_state_payload = {
                    "op": 4,
                    "d": {"guild_id": guild_id, "channel_id": channel_id, "self_mute": True, "self_deaf": True}
                }
                ws.send(json.dumps(voice_state_payload))
                purple_gradient(f"[DEBUG] Connected to channel {channel_id}: {token[:25]}...", center=True)
                self.voice_connections[token] = ws

                while self.running and token in self.tokens:
                    time.sleep(heartbeat_interval)
                    ws.send(json.dumps({"op": 1, "d": None}))
            else:
                raise Exception("Invalid WebSocket response")
        except Exception as e:
            purple_gradient(f"[DEBUG] WebSocket error: {token[:25]}... socket closed.", center=True)
            self.remove_token(token)
        finally:
            if token in self.voice_connections:
                try:
                    ws.close()
                except:
                    pass
                del self.voice_connections[token]

    def join_group_call(self, token, channel_id):
        ws_url = "wss://gateway.discord.gg/?v=9&encoding=json"
        ws = websocket.WebSocket()
        try:
            ws.connect(ws_url)
            identify_payload = {
                "op": 2,
                "d": {
                    "token": token,
                    "properties": {"$os": "windows", "$browser": "chrome", "$device": "pc"},
                    "compress": False,
                    "large_threshold": 250
                }
            }
            ws.send(json.dumps(identify_payload))
            response = json.loads(ws.recv())
            if response.get("op") == 10:
                heartbeat_interval = response["d"]["heartbeat_interval"] / 1000
            else:
                purple_gradient(f"[DEBUG] WebSocket error: {token[:25]}...", center=True)
                ws.close()
                return

            ws.send(json.dumps({"op": 1, "d": None}))
            voice_state_payload = {
                "op": 4,
                "d": {"guild_id": None, "channel_id": channel_id, "self_mute": True, "self_deaf": True}
            }
            ws.send(json.dumps(voice_state_payload))
            purple_gradient(f"[DEBUG] Connected to call {channel_id}: {token[:25]}...", center=True)
            self.voice_connections[token] = ws

            while self.running and token in self.tokens:
                time.sleep(heartbeat_interval)
                ws.send(json.dumps({"op": 1, "d": None}))
        except Exception as e:
            purple_gradient(f"[DEBUG] WebSocket error: {token[:25]}... {e}", center=True)
            self.remove_token(token)
        finally:
            if token in self.voice_connections and not self.running:
                del self.voice_connections[token]
            ws.close()

    def mass_group_call_join(self, channel_id):
        self.tokens = self.get_tokens()
        if not self.tokens:
            return
        self.running = True
        self.active_threads = []
        for token in self.tokens:
            thread = threading.Thread(target=self.join_group_call, args=(token, channel_id))
            self.active_threads.append(thread)
            thread.start()
            time.sleep(random.uniform(0.5, 1.5))

    def disconnect_voice(self):
        for token, ws in list(self.voice_connections.items()):
            voice_state_payload = {
                "op": 4,
                "d": {"guild_id": None, "channel_id": None, "self_mute": True, "self_deaf": True}
            }
            try:
                ws.send(json.dumps(voice_state_payload))
                ws.close()
                purple_gradient(f"[DEBUG] Disconnected: {token[:25]}...", center=True)
            except Exception as e:
                purple_gradient(f"[DEBUG] Error disconnecting: {token[:25]}... {e}", center=True)
            finally:
                if token in self.voice_connections:
                    del self.voice_connections[token]

    def run_spam(self, channel_id):
        self.tokens = self.get_tokens()
        if not self.tokens:
            return
        self.guild_members = self.get_channel_users(self.tokens[0], channel_id)
        if not self.guild_members:
            purple_gradient("[DEBUG] Could not retrieve user list from channel!", center=True)
            return
        self.running = True
        self.active_threads = []
        for token in self.tokens:
            thread = threading.Thread(target=self.send_message, args=(token, channel_id))
            self.active_threads.append(thread)
            thread.start()

    def run_voice(self, guild_id, channel_id):
        self.tokens = self.get_tokens()
        if not self.tokens:
            return
        self.running = True
        self.active_threads = []
        for token in self.tokens:
            thread = threading.Thread(target=self.join_voice, args=(token, guild_id, channel_id))
            self.active_threads.append(thread)
            thread.start()
            time.sleep(random.uniform(0.5, 1.5))

    def stop(self):
        self.running = False
        self.disconnect_voice()
        for thread in self.active_threads:
            thread.join()
        purple_gradient("[DEBUG] Program stopped", center=True)

    def join_server(self, token, invite_code):
        url = f"https://discord.com/api/v9/invites/{invite_code}"
        headers = {
            'Authorization': token,
            'User-Agent': random.choice(self.user_agents),
            'Content-Type': 'application/json'
        }
        data = {}
        proxies = {
            "http": "http://axdokkpn-rotate:etdeptrai@p.webshare.io:80",
            "https": "http://axdokkpn-rotate:etdeptrai@p.webshare.io:80"
        }
        try:
            response = requests.post(url, headers=headers, json=data, proxies=proxies, timeout=10)
            if response.status_code == 200:
                purple_gradient(f"[DEBUG] Joined server with invite code {invite_code} using token {token[:25]}...", center=True)
            elif response.status_code == 429:
                retry_after = response.json().get('retry_after', 5)
                purple_gradient(f"[DEBUG] Rate limited: waiting {retry_after:.2f} seconds for {token[:25]}...", center=True)
                time.sleep(retry_after)
                self.join_server(token, invite_code)
            elif response.status_code in [403, 400]:
                try:
                    error_data = response.json()
                    if 'captcha_key' in error_data:
                        purple_gradient(f"[DEBUG] Captcha required for token {token[:25]}... Skipping.", center=True)
                    else:
                        purple_gradient(f"[DEBUG] Error {response.status_code}: {error_data.get('message', 'Unknown error')} for token {token[:25]}...", center=True)
                except ValueError:
                    purple_gradient(f"[DEBUG] Error {response.status_code}: Unable to parse response for token {token[:25]}...", center=True)
            elif response.status_code == 401:
                purple_gradient(f"[DEBUG] Invalid token: {token[:25]}...", center=True)
                self.remove_token(token)
            else:
                purple_gradient(f"[DEBUG] Error {response.status_code} when joining server: {token[:25]}...", center=True)
        except requests.RequestException as e:
            purple_gradient(f"[DEBUG] Network error when joining server: {token[:25]}... {e}", center=True)

def print_header():
    clear_terminal()
    loading_animation()
    purple_gradient("""

    """)

def print_menu():
    clear_terminal()
    purple_gradient("""
                              _____ _   _  ___  _   _ 
                             | ____| \ | |/ _ \| | | |
                             |  _| |  \| | | | | | | |
                             | |___| |\  | |_| | |_| |
                             |_____|_| \_|\___/ \___/ 
                    
               ╔════════════════════════════════════════════════════╗
               ║          Discord Spammer & Voice Joiner            ║
               ║        Developed by Xuan Quang | Version Beta      ║
               ╚════════════════════════════════════════════════════╝
                    
                    ╔═════╦════════════════════════════════════╗
                    ║  №  ║             Options                ║
                    ╠═════╬════════════════════════════════════╣
                    ║  1  ║ Spammer                            ║
                    ║  2  ║ Join voice                         ║
                    ║  3  ║ Disconnect voice                   ║
                    ║  4  ║ Stop & Exit                        ║
                    ║  5  ║ Check Token                        ║
                    ║  6  ║ Delete terminal (clear)            ║
                    ║  7  ║ Change nickname                    ║
                    ║  8  ║ Set status 'online'                ║
                    ║  9  ║ Change pronouns                    ║
                    ║ 10  ║ Set custom status                  ║
                    ║ 11  ║ Join server                        ║
                    ╚═════╩════════════════════════════════════╝
    """)

def main():
    token_file = "tokens.txt"
    bot = DiscordBot(token_file)
    print_header()

    while True:
        print_menu()
        choice = input(f"{Fore.MAGENTA}➤ Enter choice (1-11) or 'clear': {Style.RESET_ALL}")

        if choice == "1":
            clear_terminal()
            channel_id = input(f"{Fore.MAGENTA}➤ Text channel ID: {Style.RESET_ALL}")
            spam_interval = float(input(f"{Fore.MAGENTA}➤ Interval (seconds): {Style.RESET_ALL}"))
            spam_time = input(f"{Fore.MAGENTA}➤ Spam duration (seconds) or Enter for infinite: {Style.RESET_ALL}")
            bot.spam_interval = spam_interval
            bot.spam_duration = float(spam_time) if spam_time else None
            bot.run_spam(channel_id)
            purple_gradient("[DEBUG] Spammer started. Type 'stop' to stop", center=True)
            if input().lower() == "stop":
                bot.stop()
                print_menu()

        elif choice == "2":
            clear_terminal()
            guild_id = input(f"{Fore.MAGENTA}➤ Server ID: {Style.RESET_ALL}")
            voice_channel_id = input(f"{Fore.MAGENTA}➤ Voice channel ID: {Style.RESET_ALL}")
            bot.run_voice(guild_id, voice_channel_id)
            purple_gradient("[DEBUG] Voice joiner started. Commands: 'unmute', 'mute', 'stop'", center=True)
            while True:
                command = input().lower()
                if command == "unmute":
                    bot.unmute(guild_id, voice_channel_id)
                elif command == "mute":
                    bot.mute(guild_id, voice_channel_id)
                elif command == "stop":
                    bot.stop()
                    break
                else:
                    purple_gradient("[DEBUG] Invalid command! Available: unmute, mute, stop", center=True)

        elif choice == "3":
            bot.disconnect_voice()
            print_menu()

        elif choice == "4":
            bot.stop()
            break

        elif choice == "5":
            bot.tokens = bot.check_all_tokens()

        elif choice == "6" or choice.lower() == "clear":
            clear_terminal()

        elif choice == "7":
            clear_terminal()
            guild_id = input(f"{Fore.MAGENTA}➤ Server ID: {Style.RESET_ALL}")
            new_nickname = input(f"{Fore.MAGENTA}➤ New nickname: {Style.RESET_ALL}")
            for token in bot.tokens:
                bot.change_nickname(token, guild_id, new_nickname)
            input(f"{Fore.MAGENTA}➤ Press Enter to return...{Style.RESET_ALL}")

        elif choice == "8":
            clear_terminal()
            for token in bot.tokens:
                bot.set_online_status(token)
            purple_gradient("[DEBUG] Setting status 'online'...", center=True)
            input(f"{Fore.MAGENTA}➤ Press Enter to return...{Style.RESET_ALL}")

        elif choice == "9":
            clear_terminal()
            pronoun = input(f"{Fore.MAGENTA}➤ New pronoun (Enter to skip): {Style.RESET_ALL}")
            bio = input(f"{Fore.MAGENTA}➤ New bio (Enter to skip): {Style.RESET_ALL}")
            for token in bot.tokens:
                bot.update_profile(token, pronoun if pronoun else None, bio if bio else None)
            input(f"{Fore.MAGENTA}➤ Press Enter to return...{Style.RESET_ALL}")

        elif choice == "10":
            clear_terminal()
            status_text = input(f"{Fore.MAGENTA}➤ Status text (e.g., 'Minecraft'): {Style.RESET_ALL}")
            activity_type = input(f"{Fore.MAGENTA}➤ Activity type (playing, streaming, listening, watching, custom, competing) [default 'playing']: {Style.RESET_ALL}").lower()
            if not activity_type:
                activity_type = "playing"
            for token in bot.tokens:
                bot.set_online_status(token, status_text, activity_type)
            purple_gradient(f"[DEBUG] Setting custom status 'online ({activity_type} {status_text})'...", center=True)
            input(f"{Fore.MAGENTA}➤ Press Enter to return...{Style.RESET_ALL}")

        elif choice == "11":
            clear_terminal()
            invite_code = input(f"{Fore.MAGENTA}➤ Invite code: {Style.RESET_ALL}")
            for token in bot.tokens:
                bot.join_server(token, invite_code)
                time.sleep(1)
            input(f"{Fore.MAGENTA}➤ Press Enter to return...{Style.RESET_ALL}")

        else:
            purple_gradient("[DEBUG] Invalid choice! Enter a number from 1 to 11 or 'clear'", center=True)
            time.sleep(2)

if __name__ == "__main__":
    main()