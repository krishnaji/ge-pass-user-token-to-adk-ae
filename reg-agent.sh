# PLEASE UPDATE BELOW API CALLS FOR YOU APP ID AND PROJECT ID
# https://docs.cloud.google.com/gemini/enterprise/docs/register-and-manage-an-adk-agent

#GET ALL AUTH IDs
curl -X GET \
-H "Authorization: Bearer $(gcloud auth print-access-token)" \
-H "Content-Type: application/json" \
-H "X-Goog-User-Project: PROJECT-ID" \
"https://discoveryengine.googleapis.com/v1alpha/projects/PROJECT-ID/locations/global/authorizations"

#DELETE AUTH ID
curl -X DELETE \
-H "Authorization: Bearer $(gcloud auth print-access-token)" \
-H "Content-Type: application/json" \
-H "X-Goog-User-Project: PROJECT-ID" \
"https://discoveryengine.googleapis.com/v1alpha/projects/PROJECT-ID/locations/global/authorizations/AUTH-ID"


# CREATE AUTH_ID
# TO GET authorizationUri PLEASE USE auth_uri.py

curl -X POST \
   -H "Authorization: Bearer $(gcloud auth print-access-token)" \
   -H "Content-Type: application/json" \
   -H "X-Goog-User-Project: PROJECT-ID" \
   "https://global-discoveryengine.googleapis.com/v1alpha/projects/PROJECT-ID/locations/global/authorizations?authorizationId=AUTH-ID" \
   -d '{
      "name": "projects/PROJECT-ID/locations/global/authorizations/AUTH-ID",
      "serverSideOauth2": {
         "clientId": "",
         "clientSecret": "",
         "authorizationUri": "PASTE auth_uri.py. output here",
         "tokenUri": "https://oauth2.googleapis.com/token"
      }
   }'

# REGISTER AGENT
   curl -X POST \
      -H "Authorization: Bearer $(gcloud auth print-access-token)" \
      -H "Content-Type: application/json" \
      -H "X-Goog-User-Project: PROJECT-ID" \
      "https://global-discoveryengine.googleapis.com/v1alpha/projects/PROJECT-ID/locations/global/collections/default_collection/engines/GE-APP-ID/assistants/default_assistant/agents" \
      -d '{
         "displayName": "My Info",
         "description": "Gets current logged in user info",
         "icon": {
            "uri": ""
      },
      "adk_agent_definition": {
         "provisioned_reasoning_engine": {
            "reasoning_engine":
            "projects/PROJECT-NUMBER/locations/us-central1/reasoningEngines/REASONING-ENGINE-ID"
         }
      },
   "authorization_config": {


   "tool_authorizations": [
   "projects/PROJECT-NUMBER/locations/global/authorizations/AUTH-ID"
   ]
   }
   }'


# DELETE AGENT
curl -X DELETE \
-H "Authorization: Bearer $(gcloud auth print-access-token)" \
"https://us-discoveryengine.googleapis.com/v1alpha/projects/PROJECT-ID/locations/us/collections/default_collection/engines/GE-APP-ID/assistants/default_assistant/agents/AGENT-ID"