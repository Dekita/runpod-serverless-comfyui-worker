
from runpod.serverless.utils import rp_upload
import uuid
import os

# local modules: 
import utils 

def all_strings_start_with(strings, x='x'):
    # Use a generator expression to check if all strings start with 'x'
    return all(s.startswith(x) for s in strings)


def send_to_aws(output_files, bucket_folder='comfyui', bucket_creds = None):
    utils.log("attempting aws file upload...")

    if bucket_creds != None and not isinstance(bucket_creds, dict):
        utils.log(f"'bucket_creds' must be a JSON object")
        return (False, output_files)

    boto_client, transfer_config = rp_upload.get_boto_client(bucket_creds)
    if boto_client is None:
        utils.log("no aws credentials set in env, skipping aws upload!")
    else:
        bucket_urls = []
        for filepath in output_files:
            filename = str(uuid.uuid4())[:8]
            _, extension = os.path.splitext(filepath)
            aws_filepath = filename + extension
            utils.log(f"uploading: {aws_filepath}")
            bucket_urls.append(rp_upload.upload_file_to_bucket(
                file_name = aws_filepath, # amazon filepath to copy to
                file_location = filepath, # local filepath to copy from
                bucket_name = bucket_folder, # aws bucket folder to put things in
                bucket_creds = bucket_creds, # override aws credentials per request - if given
            ))
            
        # not uploaded so return regular filepaths
        if not all_strings_start_with(bucket_urls, 'local_upload/'):
            # return array of uploaded item's as: [presigned_url, presigned_url, ...]  
            utils.log("aws upload success! returning presigned urls")
            return (True, bucket_urls)

    # not uploaded so return regular filepaths
    utils.log("not uploaded to aws, returning local urls")
    return (False, output_files)
