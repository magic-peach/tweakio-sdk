# 🚀 Tweakio-SDK

> **The Production-Grade, Multi-Platform Communication Automation Framework**  
> _Built on Playwright, Camoufox & BrowserForge for maximum reliability and undetectability._

[![PyPI version](https://badge.fury.io/py/tweakio-SDK.svg)](https://pypi.org/project/tweakio-SDK/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## 🎯 Vision

Tweakio-SDK isn't just a WhatsApp bot—it's a **multi-platform communication automation framework** designed with production-grade architecture patterns.

**Current**: WhatsApp Web automation (v0.1.4)  
**Future**: Telegram, Instagram, Discord, and custom platforms—all sharing the same Core.

Whether you're building intelligent chatbots, automated alert systems, or multi-account management tools, Tweakio provides the **platform-agnostic foundation** you need.

---

## ✨ Features

*   **🌐 Multi-Platform Ready**: Modular architecture with platform-specific implementations (`src/WhatsApp/`, future: `src/Telegram/`, `src/Instagram/`)
*   **🛡️ Anti-Detection First**: Built on **Playwright + Camoufox** to mimic real browser fingerprints
*   **🔄 Multi-Account Support**: Manage multiple accounts with isolated browser contexts
*   **🧩 Plugin Architecture**: Add features without touching the Core (Interface-based design)
*   **🤖 Human-Like Behavior**: Natural typing speeds, mouse movements, and intelligent pauses
*   **📦 Rich Metadata**: Type-safe `Chat` and `Message` dataclasses
*   **⚡ Async-First Design**: Non-blocking SQLite writes with background queue workers
*   **⚖️ Intelligent Rate Limiting**: Configurable window-based throttling to prevent bans
*   **📡 Dynamic Selectors**: Adaptive element detection that survives UI changes

---

## 📦 Installation

```bash
pip install tweakio-SDK
```

_Note: Requires Python 3.8+_

_Currently we are supporting Whatsapp Web but in future we will add more support to different platforms_
---

## ⚡ Quick Start

Here is a complete, working example using the latest **Fetcher** API:

```python
import asyncio
from tweakio_whatsapp import BrowserManager, WhatsappLogin, MessageProcessor, ChatLoader


async def main():
    # 1️⃣ Initialize Browser with Anti-Detect capabilities
    browser_manager = BrowserManager(headless=False)
    page = await browser_manager.getPage()

    # 2️⃣ Perform Login (Scan QR Code if needed)
    wp_login = WhatsappLogin(page=page)
    await wp_login.login()

    # 3️⃣ Start Message Processor & Chat Loader
    processor = MessageProcessor(page=page)
    chat_loader = ChatLoader(page=page)

    print("🚀 Fetching chats...")

    # 4️⃣ Iterate through chats and process messages
    # Fetcher returns a Chat object (metadata) and the chat name
    async for chat, name in chat_loader.Fetcher(MaxChat=5):
        print(f"📂 Checking Chat: {name}")

        messages = await processor.MessageFetcher(chat=chat)
        for msg in messages:
            print(f"   📩 Message: {msg.text} (ID: {msg.data_id})")


if __name__ == "__main__":
    asyncio.run(main())
```

> **💡 Pro Tip:** Check `test/play.py` in the repository for more advanced examples!

---

## 🛠️ Modules Overview

| Module | Description |
| :--- | :--- |
| **BrowserManager** | Handles browser creation, fingerprinting, and proxy management. |
| **WhastappLogin** | Manages QR scanning, session saving, and login verification. |
| **MessageProcessor** | Fetches, traces, and filters messages with built-in rate limiting. |
| **Storage** | Async queue-powered SQLite wrapper for efficient persistence. |
| **ChatLoader** | Handles chat fetching and unread status via the `Fetcher` API. |

---

## 🤝 Contributing

We welcome contributions! If you have ideas for new features or bug fixes:

1.  Fork the repo 🍴
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request 🚀

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 🛠️ Performance & Safety Note

Tweakio-SDK v0.1.2+ uses an **Async SQL Writer**. This means database operations never block your main automation loop, ensuring maximum responsiveness even during heavy message bursts.

---

## 🗺️ Roadmap

### v0.2.0 - Multi-Platform Foundation (Q2 2026)
- [ ] **Telegram Integration**: Full support for Telegram automation via `src/Telegram/`
- [ ] **Repository Pattern**: Database-agnostic storage layer (SQLite, PostgreSQL, Redis)
- [ ] **CI/CD Pipeline**: Automated testing and deployment workflows

### v0.3.0 - Multi-Account & Production Tools (Q3 2026)
- [ ] **Multi-Account Manager**: Single instance handling N accounts with context isolation
- [ ] **Instagram Support**: Add `src/Instagram/` implementation
- [ ] **Testing Suite**: Comprehensive pytest coverage for all modules
- [ ] **Docker Support**: Containerized deployment for production environments

### v0.4.0 - Enterprise Features (Q4 2026)
- [ ] **Custom Platform SDK**: Framework for adding proprietary platforms (Arrattai, etc.)
- [ ] **Webhook System**: Event-driven architecture for integrations
- [ ] **Admin Dashboard**: Web UI for monitoring and managing multiple bots

---

_Made with passion by the Tweakio Team_

