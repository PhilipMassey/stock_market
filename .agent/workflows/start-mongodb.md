---
description: Start the MongoDB database service in the background
---
This workflow starts the MongoDB service required for the stock_market application to run correctly.
The output will be redirected to the user's home directory log file.

// turbo
1. Start MongoDB:
```bash
nohup mongod --config /usr/local/etc/mongod.conf > /Users/philipmassey/mongod.log &
```
