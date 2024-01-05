
# LOGIN PAGE
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


# REGISTER PAGE
@app.route("/register", method=["GET", "POST"])
def register():
    # Forget any user_id
    session.clear()

    # GET method
    if request.method == "GET":
        return render_template("register.html")

    # POST method
    else:
        # store value in parameter and and give error respond
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not username or not password or not confirmation:
            return apology("invalid username and/or password", 400)

        if password != confirmation:
            return apology("password mismatch fails", 400)

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
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = username_new

        return redirect("/")

# BUY PAGE
@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    # GET method
    if request.method == "GET":
        return render_template("buy.html")

    # POST method
    else:
        # Request parameter from buy.html
        shares = request.form.get("shares")
        if not shares:
            flash("Shares must be positive integer")
            return redirect("/buy")

        # handles fractional, negative, and non-numeric shares
        try:
            shares = int(shares)
        except ValueError:
            flash("Shares must be positive integer")
            return redirect("/buy")
        if shares <= 0:
            flash("Shares must be greater than 0")
            return redirect("/buy")

        # using lookup() to return Dict of data -> return name, price, symbol
        try:
            stock_info = lookup("BTC")
        except ValueError:
            flash("Invalid input for shares.")
            return redirect("/buy")
        
        # Check if stock_info found or not
        if stock_info is None:
            flash("Invalid Symbol")
            return redirect("/buy")

        # Total cost
        buy_cost = int(shares) * stock_info["price"]
        # Query users database to find their cash
        user_cash = db.execute(
            "SELECT cash FROM users WHERE id = ?", session["user_id"]
        )
        # Compare buy_cost to actual user cash
        if buy_cost > user_cash[0]["cash"]:
            return apology("Cash less than buy volume")

        # Updata total cash for their user in users table
        update_cash = float(user_cash[0]["cash"]) - float(buy_cost)
        db.execute(
            "UPDATE users SET cash = ? WHERE id = ?", update_cash, session["user_id"]
        )

        # Record transaction data into transactions table
        try:
            db.execute(
                "INSERT INTO transactions_db (user_id, price, symbol, shares, transaction_type, timestamp, total_cash) VALUES (?, ?, ?, ?, ?, ?, ?)",
                session["user_id"],
                stock_info["price"],
                stock_info["symbol"],
                shares,
                "BUY",
                datetime.now(),
                update_cash,
            )
        except Exception as e:
            print("SQL Error:", str(e))
            return apology("Error recording transaction")

        # flash Bought seccussful
        flash("Bought successfully!")

        return redirect("/")

# SELL PAGE
@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    # Identify who login from session["user_id"] = rows[0]["id"]
    user_id = session["user_id"]

    # GET method
    if request.method == "GET":
        # Get symbol data from transactions_db
        symbol_list_db = db.execute(
            "SELECT DISTINCT(symbol) FROM transactions_db WHERE user_id = ?", user_id
        )
        # Extract to list
        symbol_list = []
        for symbol_row in symbol_list_db:
            symbol_list.append(symbol_row["symbol"])
        return render_template("sell.html", symbol_list_db=symbol_list)

    else:
        # Request parameter from sell.html
        symbol = request.form.get("symbol")
        sell_shares = request.form.get("shares")
        if not symbol or not sell_shares:
            return apology("Missing Symbol and/or Shares")

        # handles fractional, negative, and non-numeric shares
        try:
            sell_shares = int(sell_shares)
        except ValueError:
            return apology("shares must be a positive integer", 400)
        if sell_shares <= 0:
            return apology("Shares must be greater than 0")

        # using lookup() to return Dict of data -> return name, price, symbol
        stock_info = {}

        try:
            stock_info = lookup(symbol)
        except ValueError:
            return apology("shares must be a positive integer", 400)

        if stock_info is None:
            return apology("Invalid Symbol")

        # Total cost
        sell_cost = sell_shares * float(stock_info["price"])
        # Query list of buy from database
        buy_db = db.execute(
            "SELECT SUM(price) AS total_buy_prices, SUM(shares) AS total_buy_shares FROM transactions_db WHERE user_id = ? AND transaction_type = 'BUY' AND symbol = ?",
            user_id,
            symbol,
        )

        # Compare sell shares volume to buy shares volume
        if sell_shares > buy_db[0]["total_buy_shares"]:
            return apology("Sell shares more than Buy shares")

        # Query users database to find their cash
        user_cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        # Updata total cash for their user in users table
        update_cash = user_cash[0]["cash"] + sell_cost
        # Update cost in users table
        db.execute("UPDATE users SET cash = ? WHERE id = ?", update_cash, user_id)

        # Record transaction data into transactions table
        try:
            db.execute(
                "INSERT INTO transactions_db (user_id, price, symbol, shares, transaction_type, timestamp, total_cash) VALUES (?, ?, ?, ?, ?, ?, ?)",
                user_id,
                stock_info["price"],
                stock_info["symbol"],
                sell_shares,
                "SELL",
                datetime.now(),
                update_cash,
            )
        except Exception as e:
            print("SQL Error:", str(e))
            return apology("Transaction failed. Please try again.", 500)

        # flash Bought seccussful
        flash("SOLD SUCCESS!")

        return redirect("/")



<script src="../static/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.0.2/dist/chart.min.js"></script>
    <script src="../static/js/jquery-3.5.1.js"></script>
    <script src="../static/js/jquery.dataTables.min.js"></script>
    <script src="../static/js/dataTables.bootstrap5.min.js"></script>