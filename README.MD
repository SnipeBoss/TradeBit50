# TradeBit50 - Simulated Bitcoin Trading Platform
#### Video Demo:  https://youtu.be/b9yccGeCkqQ?si=0a0g4fnnX3p_A0oB


## Description:

## What will your software do? What features will it have?
This project is a simulated BTCUSDT exchange platform website. It provides BTCUSDT prices from the Binance API, visualizes candlestick charts using TradingView GitHub documentation, and incorporates a dashboard from the Chart.js library. Users can visualize database transactions and see real-time BTCUSDT prices. The platform allows users to add cash and buy or sell Bitcoin at the real-time price. Additionally, a login and register system is included for personalized dashboards. To enhance visualization, a 5-minute interval for candlestick charts is provided.


## Propose
TradeBit50 is a simulated Bitcoin cryptocurrency trading platform designed for users with little to no trading experience. It enables risk-free trading using virtual funds. Real-time Bitcoin price and candlestick chart data are sourced from the Binance API, providing users with the ability to visualize the dynamic Bitcoin graph in real-time. Inspired by platforms like Binance and TradingView, this project aims to encourage individuals hesitant or fearful of trading to gain hands-on experience in a safe and supportive environment.


## What new skills will you need to acquire? What topics will you need to research?
To execute this project, the following skills and research areas are required:

1. Setting up a Flask environment on a local desktop.
[src : https://geekpython.in/run-flask-app-from-the-command-line-in-windows]

2. Understanding and using the Binance API, including creating API keys.
[src API Binance documentation : https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md ]
[src python-binance library : https://python-binance.readthedocs.io/en/latest/]

3. Creating candlestick charts using TradingView's lightweight chart documentation.
Developing an admin dashboard.
[src binance-tutorials : https://github.com/hackingthemarkets/binance-tutorials]
[src https://github.com/frontendfunn/bootstrap-5-admin-dashboard-template]


## How will it be executed?
After unzipping this project, a list of folders will be provided, including templates, static, app.py, get_data_binance.py, config_key.py, finance.db, README.md, env, and flask_session. To use this project, create a Binance API and include it in config_key.py.
[src Create Binance API : https://www.binance.com/en/support/faq/how-to-create-api-keys-on-binance-360002502072]


## Tools
Frontend: HTML, CSS, JS (including jQuery, DOM), Bootstrap, Chart.js
Backend: Flask
Database: SQLite
API: Binance API
Others: TradingView GitHub lightweight chart documentation


## How does this project work?
### Database:
- finance.db provides:
transactions_binance_db: Transaction information (id, user_id, coins, price, transaction_type, total_cash, timestamp), used to store transactions from users.
users: User information (id, username, hash, cash), used to identify users.

### Frontend:
- template folder:
register.html (Bootstrap):
Allows users to input their email, password, and confirm_password. The password is hashed before being stored in the users table in finance.db.

login.html (Bootstrap):
Checks whether the provided credentials are in the users table.

chart.html (Bootstrap + Chart.js) @login_required:
Provides a dashboard to visualize real-time BTCUSDT prices and user cash/coins. Uses chart.js to create candlestick charts with a 5-minute time interval from the Binance API and utilizes get_data_binance.py to visualize real-time BTCUSDT prices.

buy.html, sell.html, addcash.html (Bootstrap + Chart.js) @login_required:
Enables buying, selling, and adding cash transactions with updates to the users table and transactions_binance_db.

- static folder:
css:
style.css, bootstrap.min.css, dataTables.bootstrap5.min.css:
CSS files from the admin dashboard GitHub template.
buy_style.css:
Bootstrap framework styles for buy.html, sell.html, addcash.html.

js:
bootstrap.bundle.min.js, dataTables.bootstrap5.min.js, jquery-3.5.1.js, jquery.dataTables.min.js:
JS files from the admin dashboard GitHub template.
script.js, chart.js:
Provide candlestick charts from TradingView documentation with a 5-minute time interval.
picture:
Stores pictures used in the project.

### Backend:
app.py:
Provides routes to HTML pages used with config_key.py and get_data_binance.py.

config_key.py:
Provides API key and secret (Must be input before using the website).

get_data_binance.py:
Provides helper functions including login_required(), get_realtime_binance(), and usd().


## What might you consider to be a good outcome for your project? A better outcome? The best outcome?
A good outcome would be gaining a practical understanding of using APIs in real-world projects and creating effective chart visualizations for websites. A better outcome would involve deeper insights into Flask development. The best outcome would be acquiring comprehensive knowledge of API utilization, web development, and the creation of interactive dashboards. Special thanks to Harvard University for providing an exceptional course experience.
