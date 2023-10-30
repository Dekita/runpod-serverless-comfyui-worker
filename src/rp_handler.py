"""
The main serverless worker module for runpod
"""

# system lib imports
import json
import os

# required lib imports
import runpod

# src imports
import comftroller
import uploader
import utils 

# additional outputs logging. helpful for testing 
LOG_JOB_OUTPUTS = True

def handler(job):
    """
    The main function that handles a job of generating an image.

    This function validates the input, sends a prompt to ComfyUI for processing,
    polls ComfyUI for result, and retrieves generated images.

    Args:
        job (dict): A dictionary containing job details and input parameters.

    Returns:
        dict: A dictionary containing either an error message or a success status with generated images.
    """
    job_input = job["input"]
    job_output = {}

    # Validate inputs
    if job_input is None:
        return utils.error(f"no 'input' property found on job data")

    if job_input.get("workflow") is None:
        return utils.error(f"no 'workflow' property found on job data")
    
    workflow = job_input.get("workflow")

    # if workflow is a string then try convert to json
    if isinstance(workflow, str):
        try:
            workflow = json.loads(workflow)
        except json.JSONDecodeError:
            return utils.error(f"Invalid JSON format in 'workflow' data")
        
    # ensure workflow is valid JSON:
    if not isinstance(workflow, dict):
        return utils.error(f"'workflow' must be a JSON object or JSON-encoded string")
    
    # set callback for when comftroller processes incomming data
    # update_progress = lambda data: runpod.serverless.progress_update(job, data)
    update_progress = utils.log

    # outputs is equal to the completed comfyui job id history object
    outputs = comftroller.run(workflow, ondata=update_progress)
    if LOG_JOB_OUTPUTS:
        utils.log("---- RAW OUTPUTS ----")
        utils.log(outputs)
        utils.log("")

    # if 'run' had an error, then stop job and return error as result
    if outputs.get('error'):
        return outputs.get('error')

    # Fetching generated images
    output_files = [] # array of output filepath/urls
    output_datas = {} # dict of nont image output node datas as {"nodeid":{"outputdata":...}}

    # uglry nesterd lewpz: el boo!
    for node_id, node_output in outputs.items():
        # add output data to output_datas if not images or gifs data
        if not any(key in node_output for key in ["images", "gifs"]):
            output_datas[node_id] = outputs[node_id]
        # scan job outputs for images/gifs (videos)
        for key in ["images","gifs"]:
            if key in node_output:
                for data in node_output[key]:
                    if data.get("type") == 'output':
                        base = comftroller.GENERATION_OUTPUT_PATH
                        path = data["subfolder"] + data["filename"]
                        output_files.append(f"{base}/{path}")

    # if you dont know what this does... you shouldnt be here.
    utils.log(f"#files generated: {len(output_files)}")
    if LOG_JOB_OUTPUTS:
        utils.log("---- OUTPUT DATAS ----")
        utils.log(output_datas)
        utils.log("")

    # return an error if for some reason the files cant be found. 
    # should never happen... but just in case <3
    for outfile in output_files:
        if not os.path.exists(outfile):
            return utils.error(f"couldn't locate output file: {outfile} #sadface")

    # log progress update to runpod so it knows we might take a moment to upload to aws
    update_progress({"saving-image-data": True})

    # attempt to upload the generated files to aws, 
    # send_to_aws returns (True, [file urls, ...]) or (False, [file paths, ...])
    aws_uploaded, bucket_urls = uploader.send_to_aws(output_files, 'generations')

    # define return object 
    job_output["files"] = bucket_urls
    job_output["datas"] = output_datas

    # convert generated image to base64 if not uploaded to aws and able
    # !NOTE: RUNPOD HAS PAYLOAD LIMITS!! CANNOT RETURN BASE64 FOR MULTIPLE LARGE FILES!!!
    if not aws_uploaded and utils.job_prop_to_bool(job_input, "tobase64"):
        for index, local_file in enumerate(bucket_urls):
            job_output["files"][index] = utils.base64_encode(local_file)

    return job_output


# Start the handler
runpod.serverless.start({"handler": handler})
