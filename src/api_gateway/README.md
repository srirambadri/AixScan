# API Gateway

ROS 2 package for the RVM scanner front end.

## What this does
1. `scan_listener` (ROS 2 node) listens for barcode/QR scanner input
   (scanners act like a keyboard, typing the code + Enter).
2. On each scan it does two things at once:
   - opens the default browser on the Flask form, passing the scanned
     code as `session_id`, and
   - calls the `latch_request` service (`std_srvs/srv/SetBool`) with
     `data: true` to ask for a latch.
3. `web_form` (Flask) shows a form asking for **Name** and **Email**.
4. On submit, the details are saved to a local SQLite DB (`rvm_users.db`)
   linked to that session_id, and a thank-you screen is shown.

The node that *serves* `latch_request` and drives the hardware lives
outside this package - `scan_listener` is only the client.

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
        ├── scan_listener.py      # service client + browser launcher
        ├── latch_server_stub.py  # test stand-in for the real latch node
        └── app.py                # Flask form
```

## Installation

Install the dependencies (`rclpy`, `std_srvs`, `python3-flask`):

```bash
cd ~/hardware_check
rosdep install --from-paths src --ignore-src -r -y
```

Then build and source the workspace:

```bash
colcon build --packages-select api_gateway
source install/setup.bash
```

## Run

```bash
# Terminal 1 - the web form
ros2 run api_gateway web_form

# Terminal 2 - the real latch node, or the stub while you build it
ros2 run api_gateway latch_server_stub

# Terminal 3 - the scan listener
ros2 run api_gateway scan_listener
```

Simulate a scan by typing any code (4+ characters) into terminal 3 and
pressing Enter - the browser opens and a latch request goes out.

Parameters, with defaults:

```bash
ros2 run api_gateway scan_listener --ros-args \
  -p base_url:=http://localhost:5000/ \
  -p service_name:=latch_request \
  -p min_code_length:=4 \
  -p service_timeout:=5.0 \
  -p debounce_sec:=1.0
```

Point `base_url` at the controller's IP if the kiosk browser runs on a
different device from the Flask process.

You can also call the service by hand to check the server side:

```bash
ros2 service call /latch_request std_srvs/srv/SetBool "{data: true}"
```

## Notes / next steps for production
- Replace `input()`-based scanning with your actual scanner SDK/serial
  interface if it doesn't emulate a keyboard.
- Put the kiosk browser in fullscreen/kiosk mode (e.g. Chromium
  `--kiosk --app=http://localhost:5000`) so it auto-returns after submit.
- `SetBool` carries no scan code, so the latch server can't tell which
  scan it is answering. If it needs to know, publish the code on a topic
  alongside the call or swap in a custom service definition.
- `rvm_users.db` is written next to the installed module, so it is wiped
  on a clean rebuild. Point `DB_PATH` somewhere persistent before any
  real use.
- Swap SQLite for your real backend (Postgres, API call to your cloud
  service, etc.) in `app.py`'s `/submit` route.
- Add a timeout to auto-close/reset the form if no one fills it in.
- Add CSRF protection (Flask-WTF) before exposing this beyond a local
  kiosk network.
