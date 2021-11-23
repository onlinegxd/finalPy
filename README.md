# Specific Cryptocurrency News Scrapper and Summarizer with Authorization by Token

### Installation
Copy from source
```bash
git clone https://github.com/onlinegxd/finalPy
```

### Usage

```python
from flask import Flask, render_template, redirect, url_for, session
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from sqlalchemy import func
from requests import Session
from flask.helpers import make_response
from datetime import datetime, timedelta
import jwt
import json
# For article summary
import nltk
from newspaper import Article
# For news extract
import requests
```

### Examples

Login into page with specific Login and Password provided

It will redirect to the screen with cryptocurrencies articles search

Write any existing cryptocurrency name to see summarized articles and save them into DataBase

There're three database tables

First one contains information about Coin

Coin
| id | coin_name|
| -- | -------- |

if new Coin is provided add them to database, e.g.

| id | coin_name|
| -- | -------- |
|  1 |  Bitcoin |
|1027|  Ethereum|

Second contains information about articles

| article_id | article_text | coin_id |
| ---------- | ------------ | ------- |

if new Article is provided add them to database

*coin_id provided is taken from coinmarketcap.com

Third one contains registered users 

Already created accounts
| id | username | password | token |
| -- | -------- | -------- | ----- |
| 1  |  admin   |   123321 |       |
| 2  |  user    |  123123  |       |

Usage examples:

(/login) - Route containing login form
If provided Login and Password are correct redirects us to -> (/coin) page
![image](https://user-images.githubusercontent.com/80266425/143144740-f09c2f5f-a074-49c2-89c6-2de1e2d9d9cb.png)
![image](https://user-images.githubusercontent.com/80266425/143144756-b8a23f85-030d-48f6-a4ba-5abb2b48c3cc.png)

If provided user is not found outputs following text
![image](https://user-images.githubusercontent.com/80266425/143144795-06520031-8527-4004-b100-3b1e1458f723.png)

(/coin) - Route containing text-feild and button, by which you find the articles for provided coin
If provided coin name is correct, outputs available summarized article paragraphs by this coin
Then saves the summarized article info into database
![image](https://user-images.githubusercontent.com/80266425/143144908-903fa51a-fd20-4db9-87a4-49693f62c160.png)
![image](https://user-images.githubusercontent.com/80266425/143145034-6f91d332-affe-4382-bbe9-df1424821566.png)
If provided coin name is incorrect outputs following error code
![image](https://user-images.githubusercontent.com/80266425/143145105-d87353bf-1221-4ee8-8760-19fbd071f386.png)

If trying to access (/coin) page with incorrect token, outputs following error
![image](https://user-images.githubusercontent.com/80266425/143145181-ffde92ad-d95c-463b-8d26-4ff2a4a701af.png)
