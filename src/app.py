from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars

####################
#### Flask Setup ###
####################

app = Flask(__name__)

####################
#### Mongo Setup ###
####################

app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_app"
mongo = PyMongo(app)

####################
#### App Routes ####
####################

@app.route("/")
def echo():
    scraped_data = mongo.db.scraped_data.find_one()
    return render_template("index.html", scraped_data=scraped_data)

@app.route("/scrape")
def scraper():
    scraped_data = mongo.db.scraped_data
    data = scrape_mars.scrape()
    scraped_data.update({}, data, upsert=True)
    return redirect("/", code=302)

if __name__ == "__main__":
    app.run(debug=True)