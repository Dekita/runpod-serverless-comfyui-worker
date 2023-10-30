
from runpod.serverless.utils import rp_upload
import utils 
import uuid
import os


def all_strings_start_with(strings, x='x'):
    # Use a generator expression to check if all strings start with 'x'
    return all(s.startswith(x) for s in strings)


def send_to_aws(output_files, bucket_folder='comfyui'):
    utils.log("attempting aws file upload...")

    boto_client, transfer_config = rp_upload.get_boto_client()
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
            ))
            # not uploaded so return regular filepaths
            if not all_strings_start_with(bucket_urls, 'local_upload/'):
                # return array of uploaded item's as: [presigned_url, presigned_url, ...]  
                utils.log("aws upload success! returning presigned urls")
                return (True, bucket_urls)

    # not uploaded so return regular filepaths
    utils.log("not uploaded to aws, returning local urls")
    return (False, output_files)
