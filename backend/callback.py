from flask import Flask, request

app = Flask(__name__)


@app.route("/callback_url", methods=["POST", "GET"])
def callback():
    args = request.args.to_dict()
    form = request.form.to_dict()
    json_data = request.get_json(silent=True)

    print("Callback received:")
    print("Args:", args)
    print("Form:", form)
    print("JSON:", json_data)

    return "OK", 200


if __name__ == "__main__":
    app.run(debug=True)
