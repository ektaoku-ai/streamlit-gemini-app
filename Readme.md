# How to run the project

This project requires an API key to connect to Gemini. The secret is stored under ```.streamlit/secrets.toml``` file.

Format for the secret is 

```
GEMINI_API_KEY = <YOUR_API_KEY>
```

## How to get the API key
1. Go to https://aistudio.google.com/api-keys
1. Click on 'Create API key' to create a new key for the project.
1. After the API key is created, copy the key and put it under 'secrets.toml file

## Running the project

From command line run
```
streamlit run <fileName>.py
```
You should see a new browser window open up.