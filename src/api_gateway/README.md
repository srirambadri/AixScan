# API Gateway

ROS 2 package for the RVM scanner front end.

## What this does
1. `scan_listener` listens for barcode/QR scanner input.
2. When a scan is detected, it opens the default browser to the Flask app,
   passing the scanned code as `session_id`.
3. `web_form` (Flask) serves the form asking for **Name** and **Email**, and
   publishes `true` on `/scan_event` the moment that page is served.
4. On submit, the details are saved to a local SQLite DB (`rvm_users.db`)
   linked to that session_id, and a thank-you screen is shown.

The ROS side is a `std_msgs/Bool` published when the form opens.

```bash
src/
└── api_gateway/
    ├── package.xml
    ├── setup.py
    ├── setup.cfg
    ├── resource/
    │   └── api_gateway
    ├── templates/
    │   ├── index.html
    │   └── thank_you.html
    └── api_gateway/
        ├── __init__.py
        ├── scan_listener.py   # watches the scanner, opens the browser
        └── app.py             # Flask form + /scan_event publisher
```

## Download
```bash
git clone -b hardware_check --single-branch https://github.com/srirambadri/AixScan.git
```

## Installation

Install the dependencies (`rclpy`, `std_msgs`, `python3-flask`):

```bash
cd ~/AixScan
rosdep install --from-paths src --ignore-src -r -y
```

Then build and source the workspace:

```bash
colcon build --packages-select api_gateway
source install/setup.bash
```

## Run

#### Terminal 1
```bash
ros2 run api_gateway web_form
```

#### Terminal 2
```bash
ros2 topic echo /scan_event
```

#### Terminal 3
```bash
ros2 run api_gateway scan_listener
```

Simulate a scan by typing any code (4+ characters) into terminal 3 and
pressing Enter. The browser opens the form and `data: true` appears in
terminal 2.

Opening the page by hand does the same thing, which is the quickest way to
test the topic on its own:

```bash
curl "http://localhost:5000/?session_id=TEST1234"
```

## Editing the HTML

`index.html` and `thank_you.html` can be replaced wholesale as long as they
keep what `app.py` expects:

| Template | Needs |
|---|---|
| `index.html` | A form posting to `/submit` with fields `name`, `email` and hidden `session_id`. Renders `{{ session_id }}` and optional `{{ error }}`. |
| `thank_you.html` | Renders optional `{{ name }}`. |

Route names, function names and field names are unchanged from the original
scripts, so no Python needs touching when the HTML is swapped.

## Notes / next steps for production
- Replace `input()`-based scanning with your actual scanner SDK/serial
  interface if it doesn't emulate a keyboard.
- Put the kiosk browser in fullscreen/kiosk mode (e.g. Chromium
  `--kiosk --app=http://localhost:5000`) so it auto-returns after submit.
- `/scan_event` fires on every page load, including a browser refresh. If
  the subscriber must act once per physical scan, de-duplicate on the
  subscriber side or publish the `session_id` instead of a bare bool.
- `rvm_users.db` is written next to the installed module, so it is wiped on
  a clean rebuild. Point `DB_PATH` somewhere persistent before any real use.
- Swap SQLite for your real backend (Postgres, API call to your cloud
  service, etc.) in `app.py`'s `/submit` route.
- Add a timeout to auto-close/reset the form if no one fills it in.
- Add CSRF protection (Flask-WTF) before exposing this beyond a local
  kiosk network.
