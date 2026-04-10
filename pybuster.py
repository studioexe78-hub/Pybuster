#!/usr/bin/env python3
import requests
import threading
import queue
import argparse
import sys
import time

# ألوان لتنسيق المخرجات في تيرمكس
G = '\033[92m'  # أخضر
Y = '\033[93m'  # أصفر
R = '\033[91m'  # أحمر
W = '\033[0m'   # أبيض
B = '\033[94m'  # أزرق

def get_args():
    parser = argparse.ArgumentParser(description=f"{B}PyBuster v1.0 - Simple & Fast Directory Scanner{W}")
    parser.add_argument("-u", "--url", dest="target_url", help="Target URL (e.g. http://example.com)", required=True)
    parser.add_argument("-w", "--wordlist", dest="wordlist", help="Path to wordlist file", required=True)
    parser.add_argument("-t", "--threads", dest="threads", help="Number of threads (default: 20)", type=int, default=20)
    parser.add_argument("-e", "--ext", dest="extensions", help="Extensions to check (e.g. php,html,txt)", default="")
    return parser.parse_args()

args = get_args()
word_queue = queue.Queue()

def request_thread():
    while not word_queue.empty():
        word = word_queue.get()
        
        # تنظيف الكلمة وإضافة لواحق الملفات إذا وُجدت
        suffixes = [""] 
        if args.extensions:
            suffixes += [f".{ext.strip()}" for ext in args.extensions.split(",")]

        for suffix in suffixes:
            path = f"{word}{suffix}"
            url = f"{args.target_url.rstrip('/')}/{path}"
            
            try:
                # محاولة الاتصال بالموقع
                response = requests.get(url, timeout=5, allow_redirects=False)
                
                # فحص حالة الصفحة
                if response.status_code == 200:
                    print(f"{G}[+] Found: /{path} (Status: 200){W}")
                elif response.status_code in [301, 302]:
                    print(f"{Y}[!] Redirect: /{path} (Status: {response.status_code}){W}")
                elif response.status_code == 403:
                    print(f"{R}[*] Forbidden: /{path} (Status: 403){W}")
                    
            except requests.exceptions.RequestException:
                pass # تجاهل أخطاء الاتصال البسيطة
        
        word_queue.task_done()

def main():
    # بانر ترحيبي
    print(f"{B}="*40)
    print(f"{G}   PyBuster - Web Directory Scanner")
    print(f"{B}="*40 + f"{W}")
    print(f"[*] Target:   {args.target_url}")
    print(f"[*] Wordlist: {args.wordlist}")
    print(f"[*] Threads:  {args.threads}")
    if args.extensions:
        print(f"[*] Extensions: {args.extensions}")
    print(f"{B}-"*40 + f"{W}")

    # تحميل الكلمات
    try:
        with open(args.wordlist, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                word = line.strip()
                if word and not word.startswith("#"):
                    word_queue.put(word)
    except FileNotFoundError:
        print(f"{R}[-] Error: Wordlist file not found!{W}")
        return

    total_words = word_queue.qsize()
    print(f"[*] Loaded {total_words} words. Starting scan...\n")

    # تشغيل الـ Threads
    start_time = time.time()
    for i in range(args.threads):
        t = threading.Thread(target=request_thread)
        t.daemon = True
        t.start()

    try:
        word_queue.join()
    except KeyboardInterrupt:
        print(f"\n{R}[!] Stopping scan...{W}")
        sys.exit()

    end_time = time.time()
    print(f"\n{B}="*40)
    print(f"[*] Scan finished in {round(end_time - start_time, 2)} seconds.")
    print(f"{B}="*40 + f"{W}")

if __name__ == "__main__":
    main()
