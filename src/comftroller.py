##################################################
###
### comftroller.py
### module to interact with a running comfyui server
###
##################################################

import time
import json
import urllib.request
import requests
import threading
import websockets
import asyncio
import base64

# local modules: 
import utils 

##################################################
###
### VARIABLES
###
##################################################

# HOSTNAME and PORT where ComfyUI is running
HOSTPORTNAME = "127.0.0.1:8188"

# The path where ComfyUI stores generated output
GENERATION_OUTPUT_PATH = "/comfyui/output"

# Time to wait between API check attempts in milliseconds
API_AVAILABLE_INTERVAL_MS = 100

# Maximum number of API check attempts
# should be available within 1 second!
API_AVAILABLE_MAX_RETRIES = 99

# Time to wait between poll attempts in milliseconds
HISTORY_POLLING_INTERVAL_MS = 100

# Maximum number of poll attempts
HISTORY_POLLING_MAX_RETRIES = 9

# base url for api and websocket
API_URL = f"http://{HOSTPORTNAME}"
WS_URL = f"ws://{HOSTPORTNAME}/ws"

# when set to true, allows for a LOT more events being sent to
# the runpod worker for being polled. you might not want to
# have so much information and only need general processing 
# information, in which case you can set this to False <3
# Additionl events when True: 
# executing, executed, execution_start, execution_cached
# NOTE: any "images" property referenced in these outputs is
# unobtainable, as it only exists temporarily in the worker
USE_CLIENT_ID = True

##################################################
###
### FUNCTIONS
###
##################################################

# some random client id for current session, so we can 
# get extra data on the nodes that are executing etc. 
# DONT CHANGE THIS, ITS USED INTERNALLY BY WS :)
SESSION_CLIENT_ID = None 


def check_server(url=None, retries=99, delay=1000):
    """
    Check if a server is reachable via HTTP GET request

    Args:
    - url (str): The URL to check
    - retries (int, optional): The number of times to attempt connecting to the server. Default is 50
    - delay (int, optional): The time in milliseconds to wait between retries. Default is 500

    Returns:
    bool: True if the server is reachable within the given number of retries, otherwise False
    """
    for i in range(retries):
        try:
            response = requests.get(url)
            # If the response status code is 200, the server is up and running
            if response.status_code == 200:
                utils.log(f"API: reachable!")
                return True
        except requests.RequestException as e:
            utils.log(f"API: unreachable.. retrying in {delay}ms")
            # If an exception occurs, the server may not be ready
            pass

        # Wait for the specified delay before retrying
        time.sleep(delay/1000)

    utils.log(f"Failed to connect to server at {url} after {retries} attempts.")
    return False


def queue_workflow(workflow):
    """
    Queue a workflow to be processed by ComfyUI

    Args:
        workflow (dict): A dictionary containing the workflow to be processed

    Returns:
        dict: The JSON response from ComfyUI after processing the prompt
    """

    # "prompt": worlkflow
    # "client_id": SESSION_CLIENT_ID
    # "number": 1
    # "front": True
    # "extra_data": {
    #     "???": "???"
    # }
    opts = {"prompt": workflow}

    if USE_CLIENT_ID: 
        utils.log(f"queing workflow for session: {SESSION_CLIENT_ID}")
        opts["client_id"] = SESSION_CLIENT_ID

    else: 
        utils.log(f"queing workflow")

    data = json.dumps(opts).encode("utf-8")
    utils.log(f"queing data {data}")
    req = urllib.request.Request(f"{API_URL}/prompt", data=data)
    return json.loads(urllib.request.urlopen(req).read())


def get_history(prompt_id):
    """
    Retrieve the history of a given prompt using its ID

    Args:
        prompt_id (str): The ID of the prompt whose history is to be retrieved

    Returns:
        dict: The history of the prompt, containing all the processing steps and results
    """
    with urllib.request.urlopen(f"{API_URL}/history/{prompt_id}") as response:
        return json.loads(response.read())


def upload_image(filename, image_data, image_type="image/png", subfolder="", overwrite="true"):
    url = f"{API_URL}/upload/image"
    files = {'image': (filename, image_data, image_type)}
    data = {
        'subfolder': subfolder,
        'overwrite': overwrite,
        'type': "input",
    }
    try:
        response = requests.post(url, files=files, data=data)
        response.raise_for_status()  # Raise an exception for HTTP errors (e.g., 4xx, 5xx)
        response_data = response.json()
        print("Image uploaded successfully:", response_data)
    except requests.exceptions.RequestException as e:
        print("Error while uploading image:", e)


async def comfy_websock_listener(ondata=utils.log):
    global SESSION_CLIENT_ID
    utils.log("WS: connecting...")
    async with websockets.connect(WS_URL) as websocket:
        utils.log("WS: connected!")
        listening = True
        
        try:
            while listening:
                message = await websocket.recv()

                ## the utils.log(message) below will output base64 data
                # utils.log("WS: message!")
                # utils.log(message)

                if isinstance(message, bytes):
                    # Handle binary data (similar to ArrayBuffer)
                    data_view = memoryview(message)
                    event_type = int.from_bytes(data_view[0:4], byteorder='big')
                    buffer = data_view[4:]
                    
                    if event_type == 1:
                        # Handle binary data with specific event type
                        image_type = int.from_bytes(data_view[4:8], byteorder='big')
                        image_data = buffer
                    
                        if image_type == 1:
                            image_mime = "image/jpeg"
                        elif image_type == 2:
                            image_mime = "image/png"
                        else:
                            image_mime = "image/png"

                        # Create a Blob-like object from bytes
                        image_blob = bytes(buffer)

                        # utils.log(f"preview received in {image_mime} format")
                        # !todo?: Emit or process image_blob as needed

                    else:
                        # Handle other binary data as needed
                        pass
                else:
                    # Handle non-binary (e.g., JSON) data

                    # Add error handling for JSON decoding
                    try:
                        event_dict = json.loads(message)
                    except json.JSONDecodeError as e:
                        utils.log(f"JSON decoding error: {e}")
                        pass # Skip this message and continue listening

                    event_type = event_dict.get('type')
                    event_data = event_dict.get('data', {})

                    # trigger utils.log or runpod.serverless.process_update and send the event_dict. 
                    # This is how we send event data out to runpod for polling via the worker/status endpoint
                    ondata(json.dumps(event_dict))

                    if event_type == 'status':
                        sid = event_data.get('sid')
                        status = event_data.get('status', {})
                        exec_info = status.get('exec_info', {})
                        queue = exec_info.get('queue_remaining', {})
                        # queue WILL be 0 when initially connecting, as we havent sent the 
                        # workflow yet, which is triggered ms after we set the session id 
                        if sid is None and queue == 0:
                            utils.log("execution_complete")
                            SESSION_CLIENT_ID = None
                            listening = False
                        # set the sessionid, to be used when triggering the workflow
                        # things are done this way to give access to many more ws events
                        elif sid is not None and SESSION_CLIENT_ID is None:
                            SESSION_CLIENT_ID = event_data.get('sid')
                            utils.log(f"obtained session id: {SESSION_CLIENT_ID}")
                        
                    elif event_type == 'error' or event_type == 'close':
                        SESSION_CLIENT_ID = None
                        listening = False

        except websockets.exceptions.ConnectionClosedError as e:
            utils.log(f"WebSocket connection closed: {e}")
        except Exception as e:
            utils.log(f"An unexpected error occurred: {e}")


def run_comfy_websock_listener(ondata=utils.log):
    asyncio.run(comfy_websock_listener(ondata))


def run(workflow, files=[], ondata=utils.log):
    # Make sure that the ComfyUI API is available
    check_server(API_URL, API_AVAILABLE_MAX_RETRIES, API_AVAILABLE_INTERVAL_MS)

    thread = threading.Thread(target=lambda: run_comfy_websock_listener(ondata))
    thread.start()

    retries = 0
    while SESSION_CLIENT_ID is None and retries < 10:
        wait_ms = 10 # small wait for ws connect event to fire?
        time.sleep(wait_ms / 1000)
        retries += 1

    utils.log(f"session id after {retries} retries: {SESSION_CLIENT_ID}")

    for id, file in enumerate(files):
        image_data = base64.b64decode(file)
        upload_image(f"upload-{id}.png", image_data, "uploads")

    try:
        queued = queue_workflow(workflow)
        comfy_job_id = queued["prompt_id"]
        utils.log(f"JOB: {comfy_job_id} queued!")
    except Exception as e:
        return utils.error(f"Error queuing workflow: {str(e)}")
    
    thread.join() # Wait for the thread to finish

    retries = 0
    try:
        while retries < HISTORY_POLLING_MAX_RETRIES:
            history = get_history(comfy_job_id)

            # Exit the loop if we have found the history
            if comfy_job_id in history and history[comfy_job_id].get("outputs"):
                break
            else:
                # Wait before trying again
                time.sleep(HISTORY_POLLING_INTERVAL_MS / 1000)
                retries += 1
        else:
            return utils.error(f"Max retries reached while waiting for image generation")
    except Exception as e:
        return utils.error(f"Error waiting for image generation: {str(e)}")    

    return history[comfy_job_id].get("outputs")

