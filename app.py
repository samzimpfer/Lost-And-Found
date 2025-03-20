from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response
import matplotlib.pyplot as plt
import numpy as np
import os
import sqlite3 as sql

app = Flask(__name__)

# returns true if any user is currently logged in
def check_logged_in():
    database = sql.connect("database.db", isolation_level=None)
    cur = database.cursor()
    entries = cur.execute(f"SELECT * FROM users WHERE logged_in = 1").fetchall()

    return len(entries) > 0

# generates a plot of the number of lost items in each category and saves it as a .png to the static folder
def generate_plot():
    database = sql.connect("database.db", isolation_level=None)
    database.row_factory = sql.Row
    cur = database.cursor()

    category_data = cur.execute(f"SELECT categories.category, count(categories.category) as 'count' FROM categories INNER JOIN items ON items.category = categories.category WHERE items.lost_found = 'Lost' GROUP BY categories.category").fetchall()

    xvals = []
    yvals = []
    for cd in category_data:
        xvals.append(cd['category'])
        yvals.append(cd['count'])

    plt.bar(xvals, yvals, color=(37/255.0, 79/255.0, 123/255.0, 1))
    plt.title("Number of lost items per category")
    plt.xlabel("Categories")
    plt.ylabel("Number of items")
    plt.xticks(rotation=60)
    plt.xticks(fontsize=8)
    plt.tight_layout()

    plt.savefig(os.path.join('static', 'plot.png'))

@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if check_logged_in(): # jump to home if any user is logged in already
        return redirect(url_for("home"))
    else:
        if request.method == "POST":
            database = sql.connect("database.db", isolation_level=None)
            cur = database.cursor()

            username = request.form.get("username", None)
            password = request.form.get("password", None)

            # search database for username inputted
            entries = cur.execute(f"SELECT * FROM users WHERE username = '{username}'").fetchall()
            
            if len(entries) < 1: # display error if username not found
                database.close()
                return render_template("login.html", password_error_display="none")
            
            else: # verify passowrd if username found
                entries = cur.execute(f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'").fetchall()

                if len(entries) < 1: # display error for incorrect password
                    database.close()
                    return render_template("login.html", username_error_display="none")
                
                else: # successful login
                    print("Login successfull")
                    cur.execute(f"UPDATE users SET logged_in = 1 WHERE username = '{username}'")
                    database.close()
                    return redirect(url_for("home"))
        
        return render_template("login.html", username_error_display="none", password_error_display="none")
            
@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    if request.method == "POST":
        username = request.form.get("username", None)
        password = request.form.get("password", None)
        phone = request.form.get("phone", None)
        address = request.form.get("address", None)

        # search database for username inputted
        database = sql.connect("database.db", isolation_level=None)
        cur = database.cursor()
        entries = cur.execute(f"SELECT * FROM users WHERE username = '{username}'").fetchall()
        
        if len(entries) > 0: # display error if username already in database
            database.close()
            return render_template("create_account.html")
        else:
            # add user
            cur.execute(f"INSERT INTO users (username, password, phone, address, logged_in) VALUES ('{username}', '{password}', '{phone}', '{address}', 0)")
            database.close()

            # back to login
            return redirect(url_for("login"))

    return render_template("create_account.html", username_error_display="none")

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/find_item", methods=["GET", "POST"])
def find_item():
    database = sql.connect("database.db", isolation_level=None)
    database.row_factory = sql.Row
    cur = database.cursor()

    # load categories to be displayed in html
    entires = cur.execute("SELECT category FROM categories ORDER BY category").fetchall()
    categories = [c['category'] for c in entires]

    # load items to be displayed in html
    filter_string = "WHERE lost_found = 'Found'"
    if request.method == "POST": # filter items
        # build sql string to filter items by
        category = request.form.get("category")
        keyword = request.form.get("keyword")
        start_date = request.form.get("start-date")
        end_date = request.form.get("end-date")

        if category != "":
            filter_string += f" AND category = '{category}'"
        if keyword != "":
            filter_string += f" AND description LIKE '%{keyword}%'"
        if start_date != "":
            filter_string += f" AND date_logged >= '{start_date}'"
        if end_date != "":
            filter_string += f" AND date_logged <= '{end_date}'"

    info = cur.execute(f"SELECT * FROM items INNER JOIN users ON users.user_id = items.reporter_id {filter_string} ORDER BY date_logged DESC").fetchall()
    database.close()

    return render_template("find_item.html", categories=categories, info=info)

@app.route("/report_found", methods=["GET", "POST"])
def report_found():
    database = sql.connect("database.db", isolation_level=None)
    database.row_factory = sql.Row
    cur = database.cursor()

    # load categories to be displayed in html
    entires = cur.execute("SELECT category FROM categories ORDER BY category").fetchall()
    categories = [c['category'] for c in entires]

    # load items to be displayed in html
    filter_string = "WHERE lost_found = 'Lost'"
    if request.method == "POST": # filter items
        # build sql string to filter items by
        category = request.form.get("category")
        keyword = request.form.get("keyword")
        start_date = request.form.get("start-date")
        end_date = request.form.get("end-date")

        if category != "":
            filter_string += f"AND category = '{category}'"
        if keyword != "":
            filter_string += f"AND description LIKE '%{keyword}%'"
        if start_date != "":
            filter_string += f"AND date_logged >= '{start_date}'"
        if end_date != "":
            filter_string += f"AND date_logged <= '{end_date}'"

    info = cur.execute(f"SELECT * FROM items INNER JOIN users ON users.user_id = items.reporter_id {filter_string} ORDER BY date_logged DESC").fetchall()
    database.close()

    return render_template("report_found.html", categories=categories, info=info)

@app.route("/report_new_lost", methods=["GET", "POST"])
def report_lost():
    database = sql.connect("database.db", isolation_level=None)
    database.row_factory = sql.Row
    cur = database.cursor()

    # load categories to be displayed in html
    entires = cur.execute("SELECT category FROM categories ORDER BY category").fetchall()
    categories = [c['category'] for c in entires]

    if request.method == "POST": # item reported
        # get id of current user
        user_id = cur.execute("SELECT user_id FROM users WHERE logged_in = 1").fetchall()[0]['user_id']

        description = request.form.get("description")
        category = request.form.get("category")
        date = request.form.get("date")

        # update categories
        if category == "other":
            category = request.form.get("other-category", None)
            if category not in categories:
                cur.execute(f"INSERT INTO categories (category, user_defined) VALUES ('{category}', 1)")

        # insert new item
        cur.execute(f"INSERT INTO items (description, category, date_logged, lost_found, reporter_id) VALUES ('{description}', '{category}', '{date}', 'Lost', {user_id})")
        database.close()

        return redirect(url_for('home'))
    
    database.close()
    return render_template("report_new_lost.html", categories=categories)

@app.route("/report_new_found", methods=["GET", "POST"])
def report_new_found():
    database = sql.connect("database.db", isolation_level=None)
    database.row_factory = sql.Row
    cur = database.cursor()

    # load categories to be displayed in html
    entires = cur.execute("SELECT category FROM categories ORDER BY category").fetchall()
    categories = [c['category'] for c in entires]

    if request.method == "POST": # item reported
        # get id of current user
        user_id = cur.execute("SELECT user_id FROM users WHERE logged_in = 1").fetchall()[0]['user_id']

        description = request.form.get("description", None)
        category = request.form.get("category", None)
        date = request.form.get("date", None)

        # update categories
        if category == "other":
            category = request.form.get("other-category", None)
            if category not in categories:
                cur.execute(f"INSERT INTO categories (category, user_defined) VALUES ('{category}', 1)")

        # insert new item
        cur.execute(f"INSERT INTO items (description, category, date_logged, lost_found, reporter_id) VALUES ('{description}', '{category}', '{date}', 'Found', {user_id})")
        database.close()

        return redirect(url_for("home"))

    database.close()
    return render_template("report_new_found.html", categories=categories)

@app.route("/claim", methods=["GET", "POST"])
def claim():
    if request.method == "POST": # item claimed from either find_item or report_found_item
        item_id = request.form.get("item-id-placeholder")

        database = sql.connect("database.db", isolation_level=None)
        database.row_factory = sql.Row
        cur = database.cursor()

        # get info on item to be displayed in html
        item = cur.execute(f"SELECT * FROM items WHERE item_id = {item_id}").fetchall()[0]
        reporter_username = cur.execute(f"SELECT username FROM users INNER JOIN items ON users.user_id = items.reporter_id WHERE item_id = {item_id}").fetchall()[0]['username']

        # get current user_id and file their claim
        user_id = cur.execute("SELECT user_id FROM users WHERE logged_in = 1").fetchall()[0]['user_id']
        print(user_id)
        cur.execute(f"INSERT INTO claims (user_id, item_id) VALUES ({user_id}, {item_id})")
        database.close()

        return render_template("claim.html", item=item, reporter_username=reporter_username)
    
    return render_template("claim.html")

@app.route("/profile", methods=["GET", "POST"])
def profile():
    database = sql.connect("database.db", isolation_level=None)
    database.row_factory = sql.Row
    cur = database.cursor()

    user_info = cur.execute("SELECT * FROM users WHERE logged_in = 1").fetchall()[0]

    if request.method == "POST": # handle item deletions
        item_id = request.form.get("item-id-placeholder")
        cur.execute(f"DELETE FROM claims WHERE item_id = {item_id}")
        cur.execute(f"DELETE FROM items WHERE item_id = {item_id}")

    # load items belonging to current user to be displayed in html
    lost_items = cur.execute(f"SELECT * FROM items INNER JOIN users ON users.user_id = items.reporter_id WHERE lost_found = 'Lost' AND reporter_id = {user_info['user_id']} ORDER BY date_logged DESC").fetchall()

    found_items = cur.execute(f"SELECT * FROM items INNER JOIN users ON users.user_id = items.reporter_id WHERE lost_found = 'Found' AND reporter_id = {user_info['user_id']} ORDER BY date_logged DESC").fetchall()

    claimed_items = cur.execute(f"SELECT lost_found, users.username AS 'other_user', description, reporter_id FROM items INNER JOIN claims on items.item_id = claims.item_id INNER JOIN users ON claims.user_id = users.user_id AND reporter_id = {user_info['user_id']}").fetchall()

    database.close()

    return render_template("profile.html", info=user_info, lost_items=lost_items, found_items=found_items, claimed_items=claimed_items)

@app.route("/edit_user", methods=["GET", "POST"])
def edit_info():
    database = sql.connect("database.db", isolation_level=None)
    database.row_factory = sql.Row
    cur = database.cursor()

    user_info = cur.execute("SELECT * FROM users WHERE logged_in = 1").fetchall()[0]

    if request.method == "POST": # handle changes submitted
        username = request.form.get("username", None)
        phone = request.form.get("phone", None)
        address = request.form.get("address", None)

        if username != user_info['username']:
            entries = cur.execute(f"SELECT * FROM users WHERE username = '{username}'").fetchall()
            
            if len(entries) > 0: # display error if username already in database
                database.close()
                return render_template("edit_user.html", info=user_info)
            
        # update info
        cur.execute(f"UPDATE users SET username = '{username}', phone = '{phone}', address = '{address}' WHERE user_id = {user_info['user_id']}")
        database.close()

        # back to profile
        return redirect(url_for("profile"))

    database.close()
    return render_template("edit_user.html", info=user_info, username_error_display="none")

@app.route("/edit_item", methods=["GET", "POST"])
def edit_item():
    database = sql.connect("database.db", isolation_level=None)
    database.row_factory = sql.Row
    cur = database.cursor()

    # load categories to be displayed in html
    entires = cur.execute("SELECT category FROM categories ORDER BY category").fetchall()
    categories = [c['category'] for c in entires]

    if request.method == "POST": # load item to be displayed
        item_id = request.form.get("item-id-placeholder")
        item = cur.execute(f"SELECT * FROM items WHERE item_id = {item_id}").fetchall()[0]
        database.close()

        return render_template("edit_item.html", categories=categories, item=item)

    database.close()
    return render_template("edit_item.html", categories=categories)

@app.route("/update_item", methods=["GET", "POST"])
def update_item():
    database = sql.connect("database.db", isolation_level=None)
    database.row_factory = sql.Row
    cur = database.cursor()

    # load categories to be displayed in html
    entires = cur.execute("SELECT category FROM categories ORDER BY category").fetchall()
    categories = [c['category'] for c in entires]

    if request.method == "POST": # handle changes submitted
        item_id = request.form.get("item-id-placeholder", None)
        description = request.form.get("description", None)
        category = request.form.get("category", None)
        date = request.form.get("date", None)

        # update categories
        if category == "other":
            category = request.form.get("other-category", None)
            if category not in categories:
                cur.execute(f"INSERT INTO categories (category, user_defined) VALUES ('{category}', 1)")

        # update item
        cur.execute(f"UPDATE items SET description = '{description}', category = '{category}', date_logged = '{date}' WHERE item_id = {item_id}")

    database.close()
    
    return redirect(url_for("profile"))

@app.route("/insights")
def insights():
    database = sql.connect("database.db", isolation_level=None)
    database.row_factory = sql.Row
    cur = database.cursor()

    info = cur.execute(f"SELECT users.username, count(users.user_id) as 'num_items' FROM users INNER JOIN claims ON users.user_id = claims.user_id INNER JOIN items on items.item_id = claims.item_id WHERE lost_found = 'Lost' GROUP BY users.user_id ORDER BY num_items DESC")

    return render_template("insights.html", info=info)

@app.route("/logout")
def logout():
    database = sql.connect("database.db", isolation_level=None)
    cur = database.cursor()
    entries = cur.execute(f"UPDATE users SET logged_in = 0 WHERE logged_in = 1")
    database.close()

    return render_template("login.html", username_error_display="none", password_error_display="none")

if __name__ == "__main__":
    generate_plot()
    app.run(debug=True)

    # test
