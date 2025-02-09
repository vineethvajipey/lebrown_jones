import tweepy
import requests
import json
import os
import time
import random
from datetime import datetime, timezone
from dotenv import load_dotenv
from nba_api.stats.endpoints import playercareerstats, teamgamelog, commonplayerinfo
from nba_api.stats.static import players, teams

def get_lebron_stats():
    try:
        # LeBron James player ID: 2544
        career = playercareerstats.PlayerCareerStats(player_id='2544')
        stats = career.get_dict()
        
        # Get the most recent season's stats
        latest_season = stats['resultSets'][0]['rowSet'][-1]
        return {
            'season': latest_season[1],
            'pts': latest_season[26],
            'ast': latest_season[21],
            'reb': latest_season[20]
        }
    except Exception as e:
        print(f"Error fetching LeBron's stats: {str(e)}")
        return None

def get_lakers_last_game():
    try:
        # Lakers team ID: 1610612747
        games = teamgamelog.TeamGameLog(team_id='1610612747')
        last_game = games.get_dict()['resultSets'][0]['rowSet'][0]
        
        return {
            'game_date': last_game[2],
            'matchup': last_game[3],
            'result': last_game[4],
            'pts': last_game[24],
            'opponent_pts': last_game[25]
        }
    except Exception as e:
        print(f"Error fetching Lakers' last game: {str(e)}")
        return None

def gen_tweet(tweet_number, tweet_history):
    # Randomly decide to include NBA stats (30% chance)
    include_stats = random.random() < 0.3
    
    if include_stats:
        # Randomly choose between LeBron stats and Lakers last game
        if random.random() < 0.5:
            stats = get_lebron_stats()
            if stats:
                prompt = f"""
                    prompt history: {" ".join(tweet_history)}
                    tweet number: {tweet_number}
                    
                    LeBron's stats for {stats['season']}:
                    Points per game: {stats['pts']}
                    Assists per game: {stats['ast']}
                    Rebounds per game: {stats['reb']}
                    
                    Generate an exciting tweet about LeBron's stats, expressing amazement at his performance.
                    Keep it between 10-15 words and include at least one statistic.
                """
            else:
                include_stats = False
        else:
            game = get_lakers_last_game()
            if game:
                prompt = f"""
                    prompt history: {" ".join(tweet_history)}
                    tweet number: {tweet_number}
                    
                    Lakers' last game:
                    {game['matchup']} ({game['result']})
                    Lakers scored: {game['pts']}
                    Opponent scored: {game['opponent_pts']}
                    
                    Generate an exciting tweet about this Lakers game, mentioning the score and result.
                    Keep it between 10-15 words.
                """
            else:
                include_stats = False
    
    if not include_stats:
        prompt = f"""
            prompt history: {" ".join(tweet_history)}
            tweet number: {tweet_number}

            generate a tweet that is 5 - 10 words, about something that is important to you. 
            Reflect and be honest. Be as crazy as you want.
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

def gen_reply(mention_text):
    # dobby api call for generating replies
    prompt = f"""
      someone mentioned me in this tweet: "{mention_text}"
      
      generate a friendly, witty response that is 5-15 words. Be creative and engaging, but stay respectful.
      Make sure the response is contextual to what they said.
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

def check_and_respond_to_mentions(client, last_checked_time):
    try:
        # Get my user ID
        my_id = client.get_me()[0].id
        
        # Get mentions since last check
        mentions = client.get_users_mentions(my_id, 
                                          since_id=last_checked_time,
                                          tweet_fields=['created_at', 'id'])
        
        if not mentions.data:
            return last_checked_time
            
        newest_id = last_checked_time
        
        # Process each mention
        for mention in mentions.data:
            try:
                # Like the mention
                try:
                    client.like(mention.id)
                    print(f"Liked tweet: {mention.id}")
                except Exception as e:
                    print(f"Error liking tweet {mention.id}: {str(e)}")

                # Generate and post reply
                reply_text = gen_reply(mention.text)
                client.create_tweet(
                    text=reply_text,
                    in_reply_to_tweet_id=mention.id
                )
                print(f"Replied to mention: {mention.text} with: {reply_text}")
                
                # Update newest_id if this mention is more recent
                if mention.id > newest_id:
                    newest_id = mention.id
                    
            except Exception as e:
                print(f"Error responding to mention {mention.id}: {str(e)}")
                continue
                
        return newest_id
        
    except Exception as e:
        print(f"Error checking mentions: {str(e)}")
        return last_checked_time

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

    # Initialize variables
    tweet_number = 1
    tweet_history = []
    last_tweet_time = time.time()
    last_mention_id = 1  # Start with 1 to get all mentions initially
    
    while True:
        try:
            current_time = time.time()
            
            # Check for mentions every 2 minutes
            last_mention_id = check_and_respond_to_mentions(client, last_mention_id)
            
            # Post scheduled tweet if an hour has passed
            if current_time - last_tweet_time >= 3600:  # 3600 seconds = 1 hour
                print(f"Generating tweet #{tweet_number}")
                tweet_content = gen_tweet(tweet_number, tweet_history)
                tweet = client.create_tweet(text=tweet_content)

                # Update history and counter
                tweet_history.append(tweet_content)
                if len(tweet_history) > 5:
                    tweet_history = tweet_history[-5:]
                tweet_number += 1
                
                last_tweet_time = current_time
                print(f"Tweet posted successfully! Next tweet in 1 hour.")
            
            # Sleep for 2 minutes before next check
            time.sleep(120)
            
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            print("Retrying in 5 minutes...")
            time.sleep(300)

if __name__ == "__main__":
    main()