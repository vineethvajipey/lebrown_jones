# CDP Agentkit Twitter LangChain Extension Examples - Chatbot Python

This example demonstrates an agent setup as a terminal style chatbot with access to Twitter (X) API actions.

## Ask the chatbot to engage in the Twitter (X) ecosystem!
- "What are my account details?"
- "Please post a message for me to Twitter"
- "Please get my mentions"
- "Please post responses to my mentions"

## Requirements
- Python 3.10+
- Poetry for package management and tooling
  - [Poetry Installation Instructions](https://python-poetry.org/docs/#installation)
- [OpenAI API Key](https://platform.openai.com/docs/quickstart#create-and-export-an-api-key)
- [Twitter (X) API Key's](https://developer.x.com/en/portal/dashboard)

### Twitter Application Setup
1. Visit the Twitter (X) [Developer Portal](https://developer.x.com/en/portal/dashboard)
2. Navigate to your project
3. Navigate to your application
4. Edit "User authentication settings"
5. Set "App permissions" to "Read and write and Direct message"
6. Set "Type of App" to "Web App, Automated app or Bot"
7. Set "App info" urls
8. Save
9. Navigate to "Keys and tokens"
10. Regenerate all keys and tokens

### Checking Python Version

```bash
python --version
poetry --version
```

## Run the Chatbot

### Env
Ensure the following vars are set in .env-local:
- "OPENAI_API_KEY"
- "TWITTER_ACCESS_TOKEN"
- "TWITTER_ACCESS_TOKEN_SECRET"
- "TWITTER_API_KEY"
- "TWITTER_API_SECRET"
- "TWITTER_BEARER_TOKEN"

Rename .env-local to .env

```bash
make run
```
