import os
import sys
import asyncio
import random
from typing import List, Tuple
import aiohttp
from aiohttp_socks import ProxyConnector
from colorama import init, Fore, Style

init(autoreset=True)

BORDER_WIDTH = 80

API_BASE_URL = "https://api.statement.mezo.org/api/v1"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "vi,en-US;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Content-Type": "application/json",
    "Origin": "https://statement.mezo.org",
    "Referer": "https://statement.mezo.org/",
    "Sec-Ch-Ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
}

CONFIG = {
    "DELAY_BETWEEN_ACCOUNTS": 3,
    "RETRY_ATTEMPTS": 3,
    "RETRY_DELAY": 5,
    "THREADS": 5,
    "BYPASS_SSL": True,
    "TIMEOUT": 30,
}

# Mezo Social Tasks
TASKS = [
    {"id": "696f19856e4943dd780e3738", "name": "Share Mezo Statement on X", "endpoint": "claim-share-statement", "points": 500},
    {"id": "696f19856e4943dd780e3735", "name": "Follow Mezo on X", "endpoint": "claim-follow", "points": 200},
    {"id": "696f19866e4943dd780e373b", "name": "Join Discord", "endpoint": "claim-social", "points": 100, "platform": "discord"},
    {"id": "696f19866e4943dd780e373e", "name": "Join Telegram", "endpoint": "claim-social", "points": 100, "platform": "telegram"},
    {"id": "696f19876e4943dd780e3741", "name": "Enter Email", "endpoint": "submit-email", "points": 100, "needs_email": True},
]

LANG = {
    'vi': {
        'title': 'MEZO STATEMENT - NHIỆM VỤ MXH',
        'processing_accounts': '⚙ ĐANG XỬ LÝ {count} TÀI KHOẢN',
        'getting_dashboard': 'Đang lấy thông tin tài khoản...',
        'dashboard_success': 'Đã lấy thông tin thành công!',
        'completing_task': 'Đang hoàn thành nhiệm vụ',
        'task_success': 'Nhiệm vụ đã hoàn thành!',
        'success': '✅ Hoàn thành nhiệm vụ cho tài khoản {username}',
        'points_earned': 'Điểm',
        'total_points': 'Tổng điểm',
        'failure': '❌ Thất bại: {error}',
        'pausing': 'Tạm dừng',
        'seconds': 'giây',
        'completed': '✅ HOÀN THÀNH: {successful}/{total} TÀI KHOẢN THÀNH CÔNG',
        'error': 'Lỗi',
        'token_not_found': '❌ Không tìm thấy tệp token.txt',
        'token_empty': '❌ Không tìm thấy token hợp lệ',
        'token_error': '❌ Không thể đọc token.txt',
        'email_not_found': '❌ Không tìm thấy tệp email.txt',
        'invalid_token': 'không hợp lệ, đã bỏ qua',
        'warning_line': 'Cảnh báo: Dòng',
        'found_proxies': 'Tìm thấy {count} proxy trong proxies.txt',
        'found_tokens': 'Thông tin: Tìm thấy {count} token',
        'found_emails': 'Thông tin: Tìm thấy {count} email',
        'no_proxies': 'Không tìm thấy proxy trong proxies.txt',
        'using_proxy': '🔄 Sử dụng Proxy - [{proxy}] với IP công khai - [{public_ip}]',
        'no_proxy': 'Không có proxy',
        'unknown': 'Không xác định',
        'invalid_proxy': '⚠ Proxy không hợp lệ: {proxy}',
        'ip_check_failed': '⚠ Không thể kiểm tra IP: {error}',
        'social_tasks_header': 'NHIỆM VỤ MẠNG XÃ HỘI',
        'tasks_to_complete': 'Nhiệm vụ hoàn thành',
        'checking_status': 'Đang kiểm tra trạng thái nhiệm vụ...',
        'status_checked': 'Đã kiểm tra trạng thái!',
        'already_completed': 'Đã hoàn thành trước đó',
        'username': 'Tên người dùng',
        'followers': 'Người theo dõi',
        'account_info': 'Thông tin tài khoản',
    },
    'en': {
        'title': 'MEZO STATEMENT - SOCIAL TASKS',
        'processing_accounts': '⚙ PROCESSING {count} ACCOUNTS',
        'getting_dashboard': 'Getting account info...',
        'dashboard_success': 'Got account info successfully!',
        'completing_task': 'Completing task',
        'task_success': 'Task completed!',
        'success': '✅ Tasks completed for account {username}',
        'points_earned': 'Points',
        'total_points': 'Total Points',
        'failure': '❌ Failed: {error}',
        'pausing': 'Pausing',
        'seconds': 'seconds',
        'completed': '✅ COMPLETED: {successful}/{total} ACCOUNTS SUCCESSFUL',
        'error': 'Error',
        'token_not_found': '❌ token.txt file not found',
        'token_empty': '❌ No valid tokens found',
        'token_error': '❌ Failed to read token.txt',
        'email_not_found': '❌ email.txt file not found',
        'invalid_token': 'is invalid, skipped',
        'warning_line': 'Warning: Line',
        'found_proxies': 'Found {count} proxies in proxies.txt',
        'found_tokens': 'Info: Found {count} tokens',
        'found_emails': 'Info: Found {count} emails',
        'no_proxies': 'No proxies found in proxies.txt',
        'using_proxy': '🔄 Using Proxy - [{proxy}] with Public IP - [{public_ip}]',
        'no_proxy': 'No proxy',
        'unknown': 'Unknown',
        'invalid_proxy': '⚠ Invalid proxy: {proxy}',
        'ip_check_failed': '⚠ Failed to check IP: {error}',
        'social_tasks_header': 'SOCIAL TASKS',
        'tasks_to_complete': 'Tasks completed',
        'checking_status': 'Checking task status...',
        'status_checked': 'Status checked!',
        'already_completed': 'Already completed',
        'username': 'Username',
        'followers': 'Followers',
        'account_info': 'Account Info',
    }
}

def print_border(text: str, color=Fore.CYAN, width=BORDER_WIDTH, language: str = 'en'):
    text = text.strip()
    if len(text) > width - 4:
        text = text[:width - 7] + "..."
    padded_text = f" {text} ".center(width - 2)
    print(f"{color}┌{'─' * (width - 2)}┐{Style.RESET_ALL}")
    print(f"{color}│{padded_text}│{Style.RESET_ALL}")
    print(f"{color}└{'─' * (width - 2)}┘{Style.RESET_ALL}")

def print_separator(color=Fore.MAGENTA, language: str = 'en'):
    print(f"{color}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")

def print_message(message: str, color=Fore.YELLOW, language: str = 'en'):
    print(f"{color}  {message}{Style.RESET_ALL}")

def print_accounts_summary(count: int, language: str = 'en'):
    print_border(
        LANG[language]['processing_accounts'].format(count=count),
        Fore.MAGENTA, language=language
    )
    print()

def load_tokens(file_path: str = "token.txt", language: str = 'en') -> List[Tuple[int, str]]:
    try:
        if not os.path.exists(file_path):
            print(f"{Fore.RED}  ✖ {LANG[language]['token_not_found']}{Style.RESET_ALL}")
            with open(file_path, 'w') as f:
                f.write("# Add Bearer tokens here, one per line\n# Example: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...\n")
            sys.exit(1)
        
        valid_tokens = []
        with open(file_path, 'r') as f:
            for i, line in enumerate(f, 1):
                token = line.strip()
                if token and not token.startswith('#'):
                    valid_tokens.append((i, token))
        
        if not valid_tokens:
            print(f"{Fore.RED}  ✖ {LANG[language]['token_empty']}{Style.RESET_ALL}")
            sys.exit(1)
        
        return valid_tokens
    except Exception as e:
        print(f"{Fore.RED}  ✖ {LANG[language]['token_error']}: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

def load_emails(file_path: str = "email.txt", language: str = 'en') -> List[str]:
    try:
        if not os.path.exists(file_path):
            print(f"{Fore.YELLOW}  ⚠ {LANG[language]['email_not_found']}{Style.RESET_ALL}")
            with open(file_path, 'w') as f:
                f.write("# Add emails here, one per line\n# Example: your@email.com\n")
            return []
        
        emails = []
        with open(file_path, 'r') as f:
            for line in f:
                email = line.strip()
                if email and not email.startswith('#'):
                    emails.append(email)
        
        return emails
    except Exception as e:
        print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {str(e)}{Style.RESET_ALL}")
        return []

def load_proxies(file_path: str = "proxies.txt", language: str = 'en') -> List[str]:
    try:
        if not os.path.exists(file_path):
            print(f"{Fore.YELLOW}  ⚠ {LANG[language]['no_proxies']}. Using no proxy.{Style.RESET_ALL}")
            with open(file_path, 'w') as f:
                f.write("# Add proxies here, one per line\n# Example: socks5://user:pass@host:port\n")
            return []
        
        proxies = []
        with open(file_path, 'r') as f:
            for line in f:
                proxy = line.strip()
                if proxy and not line.startswith('#'):
                    proxies.append(proxy)
        
        if not proxies:
            print(f"{Fore.YELLOW}  ⚠ {LANG[language]['no_proxies']}. Using no proxy.{Style.RESET_ALL}")
            return []
        
        print(f"{Fore.YELLOW}  ℹ {LANG[language]['found_proxies'].format(count=len(proxies))}{Style.RESET_ALL}")
        return proxies
    except Exception as e:
        print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {str(e)}{Style.RESET_ALL}")
        return []

async def get_proxy_ip(proxy: str = None, language: str = 'en') -> str:
    IP_CHECK_URL = "https://api.ipify.org?format=json"
    try:
        if proxy:
            connector = ProxyConnector.from_url(proxy)
            async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(IP_CHECK_URL) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('ip', LANG[language]['unknown'])
                    return LANG[language]['unknown']
        else:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(IP_CHECK_URL) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('ip', LANG[language]['unknown'])
                    return LANG[language]['unknown']
    except Exception as e:
        print(f"{Fore.YELLOW}  ⚠ {LANG[language]['ip_check_failed'].format(error=str(e))}{Style.RESET_ALL}")
        return LANG[language]['unknown']

async def mezo_social_tasks(token: str, index: int, email: str = None, proxy: str = None, language: str = 'en') -> bool:
    print_border(f"Mezo Social Tasks - Account {index}", Fore.YELLOW, language=language)

    public_ip = await get_proxy_ip(proxy, language)
    proxy_display = proxy if proxy else LANG[language]['no_proxy']
    print(f"{Fore.CYAN}🔄 {LANG[language]['using_proxy'].format(proxy=proxy_display, public_ip=public_ip)}{Style.RESET_ALL}")

    for attempt in range(CONFIG['RETRY_ATTEMPTS']):
        try:
            connector = ProxyConnector.from_url(proxy) if proxy else None
            async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=CONFIG['TIMEOUT'])) as session:
                print(f"{Fore.CYAN}  > {LANG[language]['getting_dashboard']}{Style.RESET_ALL}")
                
                headers = HEADERS.copy()
                headers['Authorization'] = f"Bearer {token}"
                
                async with session.get(
                    f"{API_BASE_URL}/user/dashboard",
                    headers=headers,
                    ssl=not CONFIG['BYPASS_SSL']
                ) as response:
                    if response.status != 200:
                        print(f"{Fore.RED}  ✖ Get dashboard failed: HTTP {response.status}{Style.RESET_ALL}")
                        if attempt < CONFIG['RETRY_ATTEMPTS'] - 1:
                            await asyncio.sleep(CONFIG['RETRY_DELAY'])
                            continue
                        return False
                    
                    dashboard_data = await response.json()
                    user_data = dashboard_data.get('data', {})
                    username = user_data.get('username', 'Unknown')
                    total_points = user_data.get('nTotalPoints', 0)
                    followers = user_data.get('followers', 0)
                    
                    print(f"{Fore.GREEN}  ✓ {LANG[language]['dashboard_success']}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}  - {LANG[language]['username']}: {username}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}  - {LANG[language]['total_points']}: {total_points}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}  - {LANG[language]['followers']}: {followers}{Style.RESET_ALL}")
                    print()
                
                print(f"{Fore.CYAN}  > {LANG[language]['checking_status']}{Style.RESET_ALL}")
                completed_task_ids = set()
                
                try:
                    async with session.get(
                        f"{API_BASE_URL}/twitter/quests/completed?status=verified",
                        headers=headers,
                        ssl=not CONFIG['BYPASS_SSL']
                    ) as response:
                        if response.status == 200:
                            completed_data = await response.json()
                            for completion in completed_data.get('data', {}).get('completions', []):
                                task_id = completion.get('oQuestId', {}).get('_id')
                                if task_id:
                                    completed_task_ids.add(task_id)
                            print(f"{Fore.GREEN}  ✓ {LANG[language]['status_checked']}{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.YELLOW}  ⚠ Check status error: {str(e)}{Style.RESET_ALL}")
                
                print()
                print(f"{Fore.CYAN}┌─ {LANG[language]['social_tasks_header']} ─────────────────────────────────────────────{Style.RESET_ALL}")
                
                completed_tasks = []
                total_points_earned = 0
                
                for task in TASKS:
                    task_id = task['id']
                    task_name = task['name']
                    task_points = task['points']
                    
                    # Check if already completed
                    if task_id in completed_task_ids:
                        print(f"{Fore.GREEN}│ ✓ {task_name}: {LANG[language]['already_completed']} (+{task_points} {LANG[language]['points_earned']}){Style.RESET_ALL}")
                        continue
                    
                    print(f"{Fore.CYAN}│ > {LANG[language]['completing_task']}: {task_name}...{Style.RESET_ALL}")
                    
                    try:
                        # Handle email task differently
                        if task.get('needs_email'):
                            if not email:
                                print(f"{Fore.YELLOW}│ ⚠ {task_name}: No email provided{Style.RESET_ALL}")
                                continue
                            
                            payload = {
                                "questId": task_id,
                                "email": email
                            }
                            
                            async with session.post(
                                f"{API_BASE_URL}/user/quest/submit-email",
                                json=payload,
                                headers=headers,
                                ssl=not CONFIG['BYPASS_SSL']
                            ) as response:
                                if response.status == 200:
                                    print(f"{Fore.GREEN}│ ✓ {task_name}: {LANG[language]['task_success']} (+{task_points} {LANG[language]['points_earned']}){Style.RESET_ALL}")
                                    completed_tasks.append(task_name)
                                    total_points_earned += task_points
                                else:
                                    response_text = await response.text()
                                    print(f"{Fore.YELLOW}│ ⚠ {task_name}: HTTP {response.status}{Style.RESET_ALL}")
                        else:
                            endpoint = task['endpoint']
                            async with session.post(
                                f"{API_BASE_URL}/twitter/quest/{endpoint}/{task_id}",
                                headers=headers,
                                ssl=not CONFIG['BYPASS_SSL']
                            ) as response:
                                if response.status == 200:
                                    print(f"{Fore.GREEN}│ ✓ {task_name}: {LANG[language]['task_success']} (+{task_points} {LANG[language]['points_earned']}){Style.RESET_ALL}")
                                    completed_tasks.append(task_name)
                                    total_points_earned += task_points
                                else:
                                    response_text = await response.text()
                                    print(f"{Fore.YELLOW}│ ⚠ {task_name}: HTTP {response.status}{Style.RESET_ALL}")
                    except Exception as e:
                        print(f"{Fore.YELLOW}│ ⚠ {task_name}: {str(e)}{Style.RESET_ALL}")
                
                print(f"{Fore.CYAN}└──────────────────────────────────────────────────────────────{Style.RESET_ALL}")
                print()
                
                if completed_tasks:
                    print(f"{Fore.GREEN}  ✅ {LANG[language]['success'].format(username=username)}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}  - {LANG[language]['tasks_to_complete']}: {', '.join(completed_tasks)}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}  - {LANG[language]['points_earned']}: +{total_points_earned}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}  ℹ No new tasks completed{Style.RESET_ALL}")
                
                print()
                return True

        except Exception as e:
            if attempt < CONFIG['RETRY_ATTEMPTS'] - 1:
                delay = CONFIG['RETRY_DELAY']
                print(f"{Fore.RED}  ✖ {LANG[language]['failure'].format(error=str(e))}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}  ℹ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}{Style.RESET_ALL}")
                await asyncio.sleep(delay)
                continue
            print(f"{Fore.RED}  ✖ {LANG[language]['failure'].format(error=str(e))}{Style.RESET_ALL}")
            return False
    return False

async def run_social(language: str = 'vi'):
    print()
    print_border(LANG[language]['title'], Fore.CYAN, language=language)
    print()

    proxies = load_proxies(language=language)
    print()

    tokens = load_tokens(language=language)
    print(f"{Fore.YELLOW}  ℹ {LANG[language]['found_tokens'].format(count=len(tokens))}{Style.RESET_ALL}")
    
    emails = load_emails(language=language)
    if emails:
        print(f"{Fore.YELLOW}  ℹ {LANG[language]['found_emails'].format(count=len(emails))}{Style.RESET_ALL}")
    print()

    if not tokens:
        return

    print_separator(language=language)
    random.shuffle(tokens)
    print_accounts_summary(len(tokens), language)

    total_interactions = 0
    successful_interactions = 0

    async def process_account(index, line_num, token):
        nonlocal successful_interactions, total_interactions
        proxy = proxies[index % len(proxies)] if proxies else None
        email = emails[index % len(emails)] if emails else None
        
        async with semaphore:
            success = await mezo_social_tasks(token, line_num, email, proxy, language)
            total_interactions += 1
            if success:
                successful_interactions += 1
            if index < len(tokens) - 1:
                print_message(f"{LANG[language]['pausing']} {CONFIG['DELAY_BETWEEN_ACCOUNTS']:.2f} {LANG[language]['seconds']}", Fore.YELLOW, language)
                await asyncio.sleep(CONFIG['DELAY_BETWEEN_ACCOUNTS'])

    semaphore = asyncio.Semaphore(CONFIG['THREADS'])
    tasks = [process_account(i, line_num, token) for i, (line_num, token) in enumerate(tokens)]
    await asyncio.gather(*tasks, return_exceptions=True)

    print()
    print_border(
        LANG[language]['completed'].format(successful=successful_interactions, total=total_interactions),
        Fore.GREEN, language=language
    )
    print()

if __name__ == "__main__":
    asyncio.run(run_social('vi'))
