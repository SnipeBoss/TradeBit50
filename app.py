"""
Simulation Cryptocurrency Exchange using Binance API
"""
import os
# Import Flask library
from flask import Flask, render_template, request, flash, redirect, jsonify, session
from flask_session import Session
import datetime
# Import SQL from CS50 library
from cs50 import SQL
# Import Hash function
from werkzeug.security import check_password_hash, generate_password_hash
# Import Python_Binance src : https://python-binance.readthedocs.io/en/latest/
from binance.client import Client


# Import external file with API key and API Secret from Binance
import config_key
# Import external file with Helpers function
from get_data_binance import login_required, get_realtime_btc, usd
# sources for datetime : https://www.freecodecamp.org/news/python-datetime-now-how-to-get-todays-date-and-time/
from datetime import datetime

# Create Flask application object
app = Flask(__name__)

# Custom filter -> It configures Jinja with a custom “filter,” usd, a function that will make it easier to format values as US dollars (USD).
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies) ->  store sessions on the local filesystem (i.e., disk) as opposed to storing them inside of (digitally signed) cookies
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# The testnet parameter will also be used by any websocket streams when the client is passed to the BinanceSocketManager.
client = Client(config_key.api_key, config_key.api_secret)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")



# Callback function
@app.after_request
def after_request(response):
    """
    after_request callback function -> execute after req has been processed, allows to modify the response before it send back to cilent.
    the propose is to ensure that the responses sent it to the client are not cached by the browser
    """
    """Ensure responses aren't cached"""
    # indicates that the response should not be cached (no-cache), should not be stored by any caching mechanism (no-store), and must be revalidated by the server before being served again (must-revalidate)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    # sets the expiration date of the response to a past date (0), effectively signaling to the browser that the response has already expired and should not be used.
    response.headers["Expires"] = 0
    #  Pragma header is included for compatibility with older HTTP/1.0 clients and specifies that caching should be avoided
    response.headers["Pragma"] = "no-cache"
    return response


# REGISTER PAGE
@app.route("/register", methods=["GET", "POST"])
def register():
    # Forget any user_id
    session.clear()

    # GET method
    if request.method == "GET":
        return render_template("register.html")

    # POST method
    else:
        # store value in parameter and give error respond if their any invalid input
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not username or not password or not confirmation:
            flash("Please input gmail and/or password")
            return redirect("/register")

        if password != confirmation:
            flash("Sorry password is not the same as confirmation")
            return redirect("/register")

        # hashing password
        password_hash = generate_password_hash(password)

        # store it to users table database
        try:
            username_new = db.execute(
                "INSERT INTO users (username, hash) VALUES(?, ?)",
                username,
                password_hash,
            )
        except:
            flash("Invalid username and/or password")
            return redirect("/register")

        # Remember which user has logged in
        session["user_id"] = username_new

        return redirect("/")
    
    
# LOGIN PAGE
@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()

    # POST method
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Please input gmail and/or password")
            return redirect("/login")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Please input gmail and/or password")
            return redirect("/login")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            flash("Invalid gmail and/or password")
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # GET method
    else:
        return render_template("login.html")


# LOG OUT stage
@app.route("/logout")
def logout():
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/login")


# CHART PAGE
@app.route("/")
@login_required
def index():
    # show user name
    user = db.execute(
            "SELECT username FROM users WHERE id = ?", session["user_id"]
        )
    user = user[0]["username"]
    
    # show realtime price in user cards
    bitcoin_price = get_realtime_btc()
    
    # All Data from transactions_binance_db table
    transactions_binance_db = db.execute("SELECT * FROM transactions_binance_db WHERE user_id = ?", session["user_id"])

    # Total user coins
    user_coins = db.execute("SELECT COALESCE(SUM(CASE WHEN transaction_type = 'BUY' THEN coins WHEN transaction_type = 'SELL' THEN -coins ELSE 0 END), 0) AS total_coins FROM transactions_binance_db WHERE user_id = ?;", session["user_id"])
    user_coins = user_coins[0]["total_coins"]
    
    # Actual cash
    users_db = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
    cash = users_db[0]["cash"]
    
    return render_template("chart.html", 
                           user=user, 
                           bitcoin_price=bitcoin_price,
                           user_coins = user_coins,
                           cash = cash,
                           transactions_binance_db=transactions_binance_db)


# BUY PAGE
@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
     # GET method
    if request.method == "GET":
        user = db.execute(
            "SELECT username FROM users WHERE id = ?", session["user_id"]
        )
        user = user[0]["username"]
        return render_template("buy.html", user=user)

    # POST method
    else:
        # Request parameter from buy.html
        coin = request.form.get("coin")
        if not coin:
            flash("Please input coin you want to buy")
            return redirect("/")

        # handles fractional, negative, and non-numeric coin
        try:
            coin = float(coin)
        except ValueError:
            flash("ERROR : coin is not numerical")
            return redirect("/")
        if coin <= 0:
            flash("Coin must be greater than 0")
            return redirect("/")

        # Using get_realtime_btc() that provide realtime bitcoin price
        try:
            bitcoin_realtime = get_realtime_btc()
        except ValueError:
            flash("ERROR : Cant connect to BTCUSDT price from Binance API")
            return redirect("/")
        # Check if bitcoin_realtime except or not
        if bitcoin_realtime is None:
            flash("ERROR : Cant connect to BTCUSDT price from Binance API")
            return redirect("/")
        
        # Convert to float
        bitcoin_realtime = float(bitcoin_realtime)

        # Total cost
        buy_cost = float(coin) * bitcoin_realtime
        
        # Query users database to find their cash
        user_cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        
        # Compare buy_cost to actual user cash
        if buy_cost > float(user_cash[0]["cash"]):
            flash("Cash is not enough to buy")
            return redirect("/")

        # Updata total cash for their user in users table
        update_cash = float(user_cash[0]["cash"]) - float(buy_cost)
        db.execute("UPDATE users SET cash = ? WHERE id = ?", update_cash, session["user_id"])

        # Record transaction data into transactions binance table
        try:
            db.execute(
                "INSERT INTO transactions_binance_db (user_id, price, coins, transaction_type, timestamp, total_cash) VALUES (?, ?, ?, ?, ?, ?)",
                session["user_id"],
                bitcoin_realtime,
                coin,
                "BUY",
                datetime.now(),
                update_cash,
            )
        except Exception as e:
            print("SQL Error:", str(e))
            flash("ERROR : Cannot insert to database")
            return redirect("/")

        # flash Bought seccussful
        flash("Bought successfully!")

        return redirect("/")


# SELL PAGE
@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    # Identify who login
    user_id = session["user_id"]

    # GET method
    if request.method == "GET":
        user = db.execute(
            "SELECT username FROM users WHERE id = ?", session["user_id"]
        )
        user = user[0]["username"]
        return render_template("sell.html", user=user)

    # POST method
    else:
        # Request parameter from sell.html
        coin = request.form.get("coin")
        if not coin:
            flash("Please input coin to sell")
            return redirect("/")

        # Handles fractional, negative, and non-numeric coins
        try:
            coin = float(coin)
        except ValueError:
            flash("ERROR: coin must be numerical")
            return redirect("/")
        if coin <= 0:
            flash("Coin must greater than 0")
            return redirect("/")

        # Using get_realtime_btc() that provide realtime bitcoin price 
        try:
            bitcoin_realtime = get_realtime_btc()
        except ValueError:
            flash("ERROR : Cant connected to BTCUSDT price from Binance API")
            return redirect("/")

        if bitcoin_realtime is None:
            flash("ERROR : Cant connected to BTCUSDT price from Binance API")
            return redirect("/")
        
        # Convert bitcoin_realtime to float
        bitcoin_realtime = float(bitcoin_realtime)

        # Total sell cost
        sell_cost = float(coin) * bitcoin_realtime
        
        # Confirm that sell coins less than buy coins
        buy_db = db.execute("SELECT SUM(coins) AS total_buy_coins FROM transactions_binance_db WHERE user_id = ? AND transaction_type = 'BUY'",user_id)

        if coin >= buy_db[0]["total_buy_coins"]:
            flash("Sell coin must be less than your own coin")
            return redirect("/")

        # Query users database to find their cash
        user_cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        
        # Updata total cash for their user in users table
        update_cash = user_cash[0]["cash"] + float(sell_cost)
        
        # Update cost in users table
        db.execute("UPDATE users SET cash = ? WHERE id = ?", update_cash, user_id)

        # Record transaction data into transactions table
        try:
            db.execute(
                "INSERT INTO transactions_binance_db (user_id, price, coins, transaction_type, timestamp, total_cash) VALUES (?, ?, ?, ?, ?, ?)",
                user_id,
                sell_cost,
                coin,
                "SELL",
                datetime.now(),
                update_cash,
            )
        except Exception as e:
            print("SQL Error:", str(e))
            flash("ERROR : Cant insert to database")
            return redirect("/")

        # flash Bought seccussful
        flash("SOLD SUCCESS!")

        return redirect("/")


# ADD CASH PAGE
@app.route("/addcash", methods=["GET", "POST"])
@login_required
def AddCash():
    # Identify who login from session["user_id"] = rows[0]["id"]
    user_id = session["user_id"]

    # GET method
    if request.method == "GET":
        user = db.execute(
            "SELECT username FROM users WHERE id = ?", session["user_id"]
        )
        user = user[0]["username"]
        return render_template("addcash.html", user=user)

    # POST method
    else:
        # Request parameter from addcash.html
        add_cash = request.form.get("add_cash")
        if not add_cash:
            flash("Please input coin to make transaction")
            return redirect("/")

        # Handles fractional, negative, and non-numeric
        try:
            add_cash = float(add_cash)
        except ValueError:
            flash("Cash must be numerical")
            return redirect("/")

        if add_cash <= 0:
            flash("Cash must be greater than 0")
            return redirect("/")

        # Query users database to find their cash
        user_cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        
        # Updata total cash for their user in users table
        update_cash = float(user_cash[0]["cash"]) + add_cash
        
        # Update cash in users table
        db.execute("UPDATE users SET cash = ? WHERE id = ?", update_cash, user_id)

        # Record transaction data into transactions table
        try:
            db.execute(
                "INSERT INTO transactions_binance_db (user_id, timestamp, total_cash) VALUES (?, ?, ?)",
                user_id,
                datetime.now(),
                update_cash,
            )
        except Exception as e:
            print("SQL Error:", str(e))
            flash("ERROR: Cant insert to database")
            return redirect("/")

        # flash Bought seccussful
        flash("ADD CASH SUCCESS!")

        return redirect("/")


# Optional : Visulize Candle Stick Data format
@app.route("/history")
def history():
    candlesticks = client.get_historical_klines("BTCUSDT", 
                                                Client.KLINE_INTERVAL_5MINUTE, 
                                                "1 day ago UTC")
    # Create a list to show the data
    processed_candlesticks = []
    for data in candlesticks:
        """
        get_historical_klines return in json form. FOR EXAMPLE IN JSON FORM :
        { time: '2018-10-19', open: 180.34, high: 180.99, low: 178.57, close: 179.85 }
        """
        candlestick = {
            "time": data[0],
            "open": data[1], 
            "high": data[2], 
            "low": data[3], 
            "close": data[4] 
            }
        
        processed_candlesticks.append(candlestick)
    
    # Return in JSON format
    """
    EXAMPLE FOR RETURN FORMAT:
    [{"close":"43671.08000000","high":"43671.08000000","low":"43636.39000000","open":"43659.63000000","time":1703444400000},
    """
    return jsonify(processed_candlesticks)


# Handles Error
if __name__ == "__main__":
    app.run(debug=True)