from flask import Flask, render_template, request, url_for, flash, redirect, jsonify
from api_reader import APIReader, Verifier
from execute_api import run_inference
import openai
from flask_cors import CORS, cross_origin


def chat(message):
    response = openai.ChatCompletion.create(model="gpt-4", messages=message)
    return response.choices[0].message.content.strip()


app = Flask(__name__)

CORS(app, origins="*")


messages = []

sys_role = "You are an expert in Applescript, and can parse information and implement in steps what the user asks."
message = [{"role": "system", "content": sys_role}]


@app.route("/")
def index():
    return render_template("index.html", messages=messages)


@cross_origin()
@app.route("/create/", methods=["GET", "POST", "OPTIONS"])
def create():
    if request.method == "POST":
        title = request.get_json()["title"]

        print(title)
        if not title:
            flash("Title is required!")
        else:
            return run_inference(title)
            # message.append({"role": "assistant", "content": response})
            # ans = response.split("```")[1][len("applescript"):]
    #             if title.startswith("API"):
    #                 ans = run_inference(title)
    #                 return ans
    # 3            title_prompt = (
    #                 "Write AppleScript code that does the following tasks:" + title
    #             )
    #             print(ans)
    #             print("============================================================")

    #             messages.append({"title": title, "content": ans.split("\n")})
    #             return redirect(url_for("index"))

    return render_template("create.html")


if __name__ == "__main__":
    app.run(debug=True)
