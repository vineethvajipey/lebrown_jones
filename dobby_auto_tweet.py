import tweepy
import requests
import json
import os
import time
from dotenv import load_dotenv

def gen_tweet(tweet_number, tweet_history):
    # dobby api call
    prompt = f"""
      prompt history: {" ".join(tweet_history)}
      tweet number: {tweet_number}

      generate a tweet that is 5 - 10 words, about something that is important to you. Reflect and be honest. Be as crazy as you want.
    """

    url = "https://api.fireworks.ai/inference/v1/chat/completions"
    payload = {
      "model": "accounts/sentientfoundation/models/dobby-mini-unhinged-llama-3-1-8b",
      "max_tokens": 16384,
      "top_p": 1,
      "top_k": 40,
      "presence_penalty": 0,
      "frequency_penalty": 0,
      "temperature": 0.6,
      "messages": [
        {
          "role": "user",
          "content": prompt
        }
      ]
    }
    headers = {
      "Accept": "application/json",
      "Content-Type": "application/json",
      "Authorization": "fw_3ZY2YhjaY1dqAJ3vc5ksouJG"
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    print(response.text)

    out = response.json()['choices'][0]['message']['content']
    
    return out

def main():
    
    load_dotenv()

    ## twitter api setup

    consumer_key = os.getenv('TWITTER_API_KEY')
    consumer_secret = os.getenv('TWITTER_API_SECRET')
    access_token = os.getenv('TWITTER_ACCESS_TOKEN')
    access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
    client_id = os.getenv('TWITTER_CLIENT_ID')
    client_secret = os.getenv('TWITTER_CLIENT_SECRET')

    # print("consumer_key: ", consumer_key, "\n",
    #       "consumer_secret: ", consumer_secret, "\n",
    #       "access_token: ", access_token, "\n", 
    #       "access_token_secret: ", access_token_secret, "\n",
    #       "bearer_token: ", bearer_token, "\n",
    #       "client_id: ", client_id, "\n",
    #       "client_secret: ", client_secret, "\n")

    auth = tweepy.OAuth1UserHandler(
        consumer_key, consumer_secret, access_token, access_token_secret
    )

    client = tweepy.Client(
        bearer_token=bearer_token,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )

    # tweet loop

    tweet_number = 1
    tweet_history = []
    
    while True:
        try:
            print(f"Generating tweet #{tweet_number}")
            tweet_content = gen_tweet(tweet_number, tweet_history)
            tweet = client.create_tweet(text=tweet_content)

            # Update history and counter
            tweet_history.append(tweet_content)
            # Keep only last 5 tweets in history to avoid prompt getting too long
            if len(tweet_history) > 5:
                tweet_history = tweet_history[-5:]
            tweet_number += 1
            
            print(f"Tweet posted successfully! Waiting for 1 hour...")
            time.sleep(3600)  # Sleep for 1 hour (3600 seconds)
            
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            print("Retrying in 5 minutes...")
            time.sleep(300)  # Wait 5 minutes before retrying if there's an error

if __name__ == "__main__":
    main()