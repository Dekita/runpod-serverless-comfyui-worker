"""
This module contains utility functions for file handling.
"""


# required imports for utility functions:
import base64

# # import nudenet lib: (nudity detection)
# # see: https://github.com/notAI-tech/NudeNet/tree/v3
# from nudenet import NudeDetector

# def detect_nudity(img_file):
#     """
#     Returns:
#     list: of detected nudity for img_file if able
#     """
#     log(f"scanning nudity for {img_file}")
#     return NudeDetector().detect(img_file) 


def log(string):
    """
    Logs string to console with basic system prefix
    
    Args:
    - string (str): The string to log
    """
    print(f"[runpod-worker-comfy] {string}")




def job_prop_to_bool(job_input, propname):
    """
    Returns boolean based on variable value.
    Allows for checking string booleans, eg: "true"

    Args:
    - job_input (dict): A dictionary containing job input parameters.
    
    Returns: 
    bool: True if job_input dict has propname that seems bool-ish
    """
    value = job_input.get(propname)
    if value is None: return False
    if isinstance(value, bool): return value
    true_strings = ['true', 't', 'yes', 'y', 'ok', '1']
    if isinstance(value, str): return value.lower().strip() in true_strings
    return False




def error(error_message):
    """
    Logs error message and then returns basic dict with "error" prop using message

    Args:
    - error_message (string): A string containing the error emssage to show
    
    Returns: 
    dict: containing error property with error message
    """    
    log(error_message) # log message then return error value
    return {"error": error_message}




def base64_encode(img_file):
    """
    Returns base64 encoded image.
    """
    log(f"scanning base64 for {img_file}")
    with open(img_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
        return encoded_string.decode("utf-8")
    
