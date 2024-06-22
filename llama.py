
from clarifai.client.workflow import Workflow

# Your PAT (Personal Access Token) can be found in the Account's Security section

# Initialize the workflow_url
workflow_url = "https://clarifai.com/dhdtx1j3kzt4/genai/workflows/workflow-814c8b"
text_classfication_workflow = Workflow(
    url= workflow_url , pat="20d41d0a457747768593f8089a4c24db"
)
result = text_classfication_workflow.predict_by_bytes(b"I hate you", input_type="text")
print(result.results[0].outputs[0].data)

from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2
import streamlit as st

# Your PAT (Personal Access Token) can be found in the portal under Authentification
PAT = st.secrets.PAT
# Specify the correct user_id/app_id pairings
# Since you're making inferences outside your app's scope
USER_ID = st.secrets.USER_ID
APP_ID = st.secrets.APP_ID
# Change these to whatever model and text URL you want to use
WORKFLOW_ID = 'genai'

############################################################################
# YOU DO NOT NEED TO CHANGE ANYTHING BELOW THIS LINE TO RUN THIS EXAMPLE
############################################################################

def get_response(prompt):
    channel = ClarifaiChannel.get_grpc_channel()
    stub = service_pb2_grpc.V2Stub(channel)

    metadata = (('authorization', 'Key ' + PAT),)

    userDataObject = resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID)

    response = ""  # save response from the model

    post_workflow_results_response = stub.PostWorkflowResults(
        service_pb2.PostWorkflowResultsRequest(
            user_app_id=userDataObject,  
            workflow_id=WORKFLOW_ID,
            inputs=[
                resources_pb2.Input(
                    data=resources_pb2.Data(
                        text=resources_pb2.Text(
                            raw=prompt
                        )
                    )
                )
            ]
        ),
        metadata=metadata
    )

    if post_workflow_results_response.status.code != status_code_pb2.SUCCESS:
        print(post_workflow_results_response.status)

        return response

    # We'll get one WorkflowResult for each input we used above. Because of one input, we have here one WorkflowResult
    results = post_workflow_results_response.results[0]

    # Each model we have in the workflow will produce one output.
    for output in results.outputs:
        model = output.model

        print("Predicted concepts for the model `%s`" % model.id)
        for concept in output.data.concepts:
            print("	%s %.2f" % (concept.name, concept.value))

        response += output.data.text.raw + "\n"

    # Uncomment this line to print the full Response JSON
    # print(results)
    print(response)