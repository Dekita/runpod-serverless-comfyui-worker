"""
This module contains functionality for interacting with comfyui.
"""


import json
import urllib.request
# import urllib.parse
import time
# import os
import requests
# import base64

import threading
import websockets
import asyncio

# from array import array

import utils 

# import nudenet lib: (nudity detection)
# see: https://github.com/notAI-tech/NudeNet/tree/v3
# from nudenet import NudeDetector

# HOSTNAME and PORT where ComfyUI is running
HOSTPORTNAME = "127.0.0.1:8188"

# The path where ComfyUI stores generated output
GENERATION_OUTPUT_PATH = "/comfyui/output"

# Time to wait between API check attempts in milliseconds
API_AVAILABLE_INTERVAL_MS = 1000

# Maximum number of API check attempts
# should be available within 1 second!
API_AVAILABLE_MAX_RETRIES = 9

# Time to wait between poll attempts in milliseconds
HISTORY_POLLING_INTERVAL_MS = 100

# Maximum number of poll attempts
HISTORY_POLLING_MAX_RETRIES = 9

# base url for api and websocket
API_URL = f"http://{HOSTPORTNAME}"
WS_URL = f"ws://{HOSTPORTNAME}/ws"


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
    data = json.dumps({"prompt": workflow}).encode("utf-8")
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


async def comfy_websock_listener(ondata=utils.log):
    utils.log("WS: connecting...")
    async with websockets.connect(WS_URL) as websocket:
        utils.log("WS: connected!")
        listening = True
        
        try:
            while listening:
                message = await websocket.recv()

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

                        # Emit or process image_blob as needed
                        # log(f"preview received in {image_mime} format")
                    else:
                        # Handle other binary data as needed
                        pass
                else:
                    # Handle non-binary (e.g., JSON) data

                    # Add error handling for JSON decoding
                    try:
                        event_data = json.loads(message)
                    except json.JSONDecodeError as e:
                        utils.log(f"JSON decoding error: {e}")
                        pass
                        # continue  # Skip this message and continue listening
                    
                    event_type = event_data.get('type')
                    # utils.log or runpod.serverless.process_update
                    ondata(json.dumps(event_data))

                    if event_type == 'status' and event_data.get('data', {}).get('status', {}).get('exec_info', {}).get('queue_remaining', {}) == 0:
                        utils.log("execution_complete")
                        listening = False

                    elif event_type == 'error' or event_type == 'close':
                        listening = False

        except websockets.exceptions.ConnectionClosedError as e:
            utils.log(f"WebSocket connection closed: {e}")
        except Exception as e:
            utils.log(f"An unexpected error occurred: {e}")


def run_comfy_websock_listener(ondata=utils.log):
    asyncio.run(comfy_websock_listener(ondata))
    # asyncio.get_event_loop().run_until_complete(comfy_websock_listener(job))

    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # loop.run_until_complete(comfy_websock_listener(job))


def run(workflow, ondata=utils.log):
    # Make sure that the ComfyUI API is available
    check_server(API_URL, API_AVAILABLE_MAX_RETRIES, API_AVAILABLE_INTERVAL_MS)

    thread = threading.Thread(target=lambda: run_comfy_websock_listener(ondata))
    thread.start()

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

