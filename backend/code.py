import time
import os
import pickle
from flask import Flask, jsonify, request, Response
import undetected_chromedriver as uc
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import uuid

app = Flask(__name__)

# Thread Pool Executor to handle multiple browser sessions
executor = ThreadPoolExecutor(max_workers=5)
session_lock = Lock()


# Function to create a new Chrome session
def create_chrome_session(profile_path):
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument(f"--user-data-dir={profile_path}")
    return uc.Chrome(options=options)


# Asynchronous wrapper to handle browser operations asynchronously
def async_browser_operation(fn, *args, **kwargs):
    return executor.submit(fn, *args, **kwargs)


@app.route("/gen_code", methods=["GET"])
def gen_code():
    def browser_task():
        try:
            session_key = str(uuid.uuid4())
            profile_path = f"./profile/{session_key}"
            driver = create_chrome_session(profile_path)
            driver.get(
                "https://account.samsung.com/accounts/v1/FMM2/signInGate?state=0k971pgy9078::hound-prd&redirect_uri=https:%2F%2Fsmartthingsfind.samsung.com%2Flogin.do&response_type=code&client_id=ntly6zvfpn&scope=iot.client&locale=en_US&acr_values=urn:samsungaccount:acr:basic&goBackURL=https:%2F%2Fsmartthingsfind.samsung.com%2Flogin"
            )
            time.sleep(1)
            driver.get("https://account.samsung.com/accounts/v1/FMM2/signInWithQrCode#")
            time.sleep(1)

            # Example placeholder, replace 'code' logic with correct code extraction if needed
            code = driver.execute_script("return code || null;")
            if not code:
                driver.quit()
                return jsonify({"error": "Code not found"}), 404
            print("http://localhost:5000/open/" + session_key)
            link = f"https://signin.samsung.com/key/{code}"
            html_button = f"<button style='width: 100%; height: 60px; font-size: 40px' onclick=\"window.location.href='{link}'\">\u0110ăng ký Beta</button>"
            print("Code:", code)
            with session_lock:
                os.makedirs(profile_path, exist_ok=True)
                with open(f"{profile_path}/cookies.pkl", "wb") as cookie_file:
                    pickle.dump(driver.get_cookies(), cookie_file)

            return (
                Response(html_button, mimetype="text/html"),
                200,
                {"session_key": session_key},
            )

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return async_browser_operation(browser_task).result()


@app.route("/open/<session_key>", methods=["GET"])
def open_with_session(session_key):
    def browser_task():
        profile_path = f"./profile/{session_key}"
        driver = create_chrome_session(profile_path)

        cookies_path = f"{profile_path}/cookies.pkl"
        if os.path.exists(cookies_path):
            with open(cookies_path, "rb") as cookie_file:
                cookies = pickle.load(cookie_file)
                driver.get(f"https://smartthingsfind.samsung.com/")
                for cookie in cookies:
                    driver.add_cookie(cookie)
                driver.refresh()
                time.sleep(100000)

    return async_browser_operation(browser_task).result()


if __name__ == "__main__":
    os.makedirs("./profile", exist_ok=True)
    app.run(host="0.0.0.0", port=5000, threaded=True)
