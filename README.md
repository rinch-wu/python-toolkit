# Python Toolkit (`python-toolkit`)

A production-ready Python utility suite featuring advanced decorator patterns, concurrent task dispatchers, browser fingerprint spoofing, dynamic proxy pools, and automation helpers.

---

## 🌟 Highlights

### 1. Advanced Decorator Suite (`decorator.py`)
- **StateStore & Concurrency Safety**: Thread-safe progress tracking and metrics store (`StateStore`) with lock synchronization and summary reporting.
- **Declarative Guard (`call_when`)**: Conditional execution decorator ensuring functions only execute when all predicate functions return `True`.
- **Fault-Tolerant Execution (`except_`)**: Automatic exception catching, stack trace logging, and error count thresholding.
- **Dynamic Task Dispatcher (`map_`)**: Seamless unified dispatching supporting both multi-threaded tasks and `asyncio` awaitables (`asyncio.gather`).
- **Thread Naming & Progress (`threadname_`, `tqdm_update`, `time_`)**: Automatic index-aligned thread renaming, progress bar updating, and runtime profiling.
- **Method-Level Mutex (`lock_`)**: Minimalist threading lock decorator for critical sections.

### 2. Fingerprint-Resistant Networking (`requests.py`)
- **TLS / JA3 Browser Impersonation**: Built on top of `curl_cffi` to evade advanced WAF and anti-bot systems.
- **Dynamic Proxy Rotation**: Integrated with SOCKS5 / HTTP proxy pools with automatic failover and exponential backoff retry.
- **Lifecycle Interceptor Hooks**: Extensible `request_before` and `request_after` pipeline for dynamic headers, cookies, and session rotation.

### 3. Automation & System Utilities
- **Browser Automation (`chrome.py`, `selenium_.py`)**: Headless Chrome orchestration with anti-detection evasions.
- **Proxy Management (`proxy/`)**: Scrapers, validators, and health-checking pools.
- **Process & Resource Lifecycle (`auto_exit.py`, `kill_process.py`)**: Safe shutdown hooks and cleanup handlers.

---

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/rinch-wu/python-toolkit.git
cd python-toolkit
pip install -r requirements.txt
```

### Decorator Examples

```python
from decorator import call_when, lock_, except_, StateStore

# 1. Declarative Condition Guard
is_ready = lambda: True

@call_when(is_ready)
def sensitive_task():
    print("Task executed safely under guard.")

# 2. Thread-Safe Execution with StateStore
state = StateStore(total=100)

@except_(state_store=state)
@lock_
def process_data(item):
    # Safe thread execution
    pass
```

### Fingerprinted Request Example

```python
from requests import Requests

client = Requests(address="session_1", use_proxies=False)
response = client.get("https://httpbin.org/headers")
print(response.json())
```

---

## 📄 License
MIT License
