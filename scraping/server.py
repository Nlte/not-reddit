from flask import Flask, json, request, jsonify, render_template
from flask_cors import CORS, cross_origin
from scraper import Scraper

app = Flask(__name__)
CORS(app)

myScraper = Scraper()

@app.route("/")
def hello():
    return "Scraping service."

# curl -H "Content-Type: application/json" -X POST -d '{"website":"http://www.google.com"}' http://localhost:8080/scrape
@app.route('/scrape', methods = ['POST', 'OPTION'])
def scrapeAPI():
    # Get the parsed contents of the form data
    #if request.headers['Content-Type'] == 'application/json':
    json = request.json
    url = json["link"]
    text = myScraper.scrape_html(url)
    # Render template
    print(text)
    return text


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080)
