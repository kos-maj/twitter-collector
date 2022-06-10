import tweepy
import config

client = tweepy.Client(bearer_token=config.BEARER_TOKEN);

# response = client.search_recent_tweets(query=query, max_results=25, expansions=['author_id']);
# users = {user['id']: user for user in response.includes['users']}
# for user in users.values():
    # print(f'id: {user.id}\nname: {user.name}\nusername: {user.username}\n\n');


# Get users which like a given tweet
tweet_id = "1535283632922845184"
users = client.get_liking_users(id=tweet_id);

# users = client.get_retweeters(id=tweet_id);       # For retweeters

for user in users.data:
    print(user.username + ' | ' + user.name);
print(f'total count: {users.meta["result_count"]}');
