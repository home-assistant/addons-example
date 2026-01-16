from flask import Flask, jsonify
import subprocess

app = Flask(__name__)

@app.route("/refresh", methods=["POST"])
def refresh():
    result = subprocess.run(
        ["python3", "/app/main.py", "--once"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        return jsonify({"status": "ok"}), 200
    else:
        return jsonify({
            "status": "error",
            "stderr": result.stderr
        }), 500
