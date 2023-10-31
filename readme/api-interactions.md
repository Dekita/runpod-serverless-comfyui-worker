## Interacting with your endpoint API
* In the [User Settings](https://www.runpod.io/console/serverless/user/settings) click on `API Keys` and then on the `API Key` button
* Save the generated key somewhere, as you will not be able to see it again when you navigate away from the page
* Use cURL or any other tool to access the API using the API key and your Endpoint-ID:
  * Replace `<api_key>` with your key
  * Replace `<endpoint_id>` with the ID of the endpoint, you find that when you click on your endpoint, it's part of the URLs shown at the bottom of the first box

You can now create a new job for your serverless worker on runpod either syncronously, or async. 
Use the /run or /runsync endpoint respectively. 
The difference being that /run will return immediately and requires an additional api call to obtain job status upon completion. 

### Request Format
The API expects JSON input in the following format:
- input
  - tobase64: (Boolean) - will attempt to return base64 for generated images. Should only be used for testing
  - workflow: {JSON} - the workflow obtained by clicking `Save (API Format)` in comfy ui
```
{
    "input": {
        "tobase64": false,
        "workflow": {}
    }
}
```

#### Example Requests:
With cURL
```bash
curl -X POST \
-H "Authorization: Bearer <api_key>" \
-H "Content-Type: application/json" \
--data @examples/test_input.json \
https://api.runpod.ai/v2/<endpoint_id>/runsync
```

With [runpod.js](https://github.com/dekita/runpod.js)
```js
// import runpod.js and workflow json
import RunPod from 'dekita-runpod-js';
import WORKFLOW from './examples/test_input.json';

// result will contain "id" so it can later be polled
// this is also true when using `.run` for async job
// this example runs syncronously though, so wont return
// until the job is complete. use async for long running jobs.
const result = await RunPod.serverless.runsync("ENDPOINT_ID", {
    // webhook: "https://URL.TO.YOUR.WEBHOOK"
    // policy: {executiontimeout: 5000},
    input: {
        tobase64: false,
        workflow: WORKFLOW, 
    },
});

console.log(result)
```

#### Example request response:
Response
```json
{
    "delayTime": 2188,
    "executionTime": 2297,
    "id": "sync-c0cd1eb2-068f-4ecf-a99a-55770fc77391-e1",
    "output":{
        "error": "only exists if error was thrown, contains message ofc",
        "files": ["https://bucket.s3.region.amazonaws.com/generations/sync-c0cd1eb2-068f-4ecf-a99a-55770fc77391-e1/c67ad621.png"],
        "datas": {
            "nodeid": {
                "nodeoutput1": "ouput-value-I",
                "nodeoutput2": "ouput-value-II"
            }
        }
    },
    "status": "COMPLETED"
}
```

#### Health status
With cURL
```bash
curl -H "Authorization: Bearer <api_key>" https://api.runpod.ai/v2/<endpoint_id>/health
```

With [runpod.js](https://github.com/dekita/runpod.js)
```js
import RunPod from 'dekita-runpod-js';
console.log(await RunPod.serverless.health("ENDPOINT_ID"))
```

#### Async example
With [runpod.js](https://github.com/dekita/runpod.js)
```js
// import runpod.js and workflow json
import RunPod from 'dekita-runpod-js';
import WORKFLOW from './examples/test_input.json';
// helper function to wait some amount of ms
const wait = async(milliseconds = 1000) => {
    return new Promise((r) => setTimeout(r, milliseconds));
}
// run the initial job asyncronously
const result = await RunPod.serverless.run("ENDPOINT_ID", {
    // webhook: "https://URL.TO.YOUR.WEBHOOK"
    // policy: {executiontimeout: 5000},
    input: {
        tobase64: false,
        workflow: WORKFLOW, 
    },
});
// keep trying to get the result until completed
let retry_counter = 0; 
while (result.status === 'IN_QUEUE') {
    await wait(5000); // wait some time. why here? why not! 
    if (++retry_counter > 9) break; // stop looping after x attempts
    console.log(`calling api for latest status update:`)
    result = await RunPod.serverless.status(runpod_endpoint, result.id);
    console.log(result) // will contain latest progress data pushed by worker
}
// just log the final result data <3
console.log(`final status update:`)
console.log(result) // will contain final job output data
```

## IMPORTANT NOTES
If you are generating very large files, batch files, videos, etc. you should NOT return base64 as there is a payload limit on runpod requests. See [runpod-serverless-controls-and-limitations](https://docs.runpod.io/docs/controls-limitations) for more information on payload limits.

At the time of writing this payload limits are 10MB for /run, and 20MB for /runsync. 
