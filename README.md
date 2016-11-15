# SlowLoris in Python

An implementation of SlowLoris in Python 3 with multithreading. SlowLoris is a DDoS method that affects a number of webservers that use threaded processes and set a limit on the number of threads/processes that can be automatically spawned in order to keep from exhausting the memory on the server.

This includes but is not necessarily limited to the following:

- Apache 1.x
- Apache 2.x
- dhttpd
- WebSense "block pages" (unconfirmed)
- Trapeze Wireless Web Portal (unconfirmed)
- Verizon's MI424-WR FIOS Cable modem (unconfirmed)
- Verizon's Motorola Set-top box (port 8082 and requires auth - unconfirmed)
- BeeWare WAF (unconfirmed)
- Deny All WAF (patched)

[More information on Wikipedia](https://en.wikipedia.org/wiki/Slowloris_(computer_security))
---
## Installation
Simply run `setup.py install`
---
## Usage

>usage: slowloris [-h] [--sock_count SOCK_COUNT]
>                 [--thread_count THREAD_COUNT] [--port PORT]
>                 host