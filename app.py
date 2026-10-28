from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
  return "Tsukuyomi C2 Server is Live and Working!"


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
