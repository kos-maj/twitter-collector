import tweepy
import config
import sys
from os.path import exists

'''
TO DO: Add functionality for use case 2 (get tweets from users within a set time range)

-> tweepy client 'search_all_tweets(query, end_time, start_time, ...)' endpoint is only available
to those who have been approved for the Academic Research product track.

-> For now cannot implement this since only have basic developer track

'''

client = tweepy.Client(bearer_token=config.BEARER_TOKEN);

def printUserInfo(userData):
    print('-'*72);
    print('| {:20} | {:20} | id'.format('name', 'username'));
    print('-'*72);
    for user in userData:
        print('| {:20.17} | {:20} | {:<32}'.format(user.name, user.username, user.id));

def printTweetInfo(tweetData):
    for tweet in tweetData:
        print('-'*72);
        print(f'id:\t{tweet.id}\ntext:\t{tweet.text}');
        print('-'*72);

def main():
    # Error handling
    if(len(sys.argv) != 2):
        print('Error: must provide a file of usernames as input.');
        return -1;

    path = './' + sys.argv[1];
    if(exists(path)):
        usernames = [];
        
        # Read all usernames from file
        with open(path) as fin:
            while(1):
                line = fin.readline();
                if not line:
                    break;
                else:
                    usernames.append(line.rstrip());

        # Get public metrics of each user
        user_data = client.get_users(usernames=usernames, user_fields='public_metrics');

        # Output each user's up-to-date follower count
        path = './followers.txt';
        with open(path, 'w') as fout:
            for user in user_data.data:
               fout.write(f'{user.username}:{user.public_metrics["followers_count"]}\n') 

        print('[+] Finished. Program exiting...'); 
    else:
        print('Error: input file does not exist.');
        return -1;

    return 0;

def alt_main():
    usr_choice = None;

    while (1):
        usr_choice  = input("\nTwitter Tool Options:\n1. Get retweeters\n2. Get likers\n3. Date range\n> ");

        if (not usr_choice.isdecimal() or usr_choice not in ['1','2','3']):
            print("\nError: must pick option '1', '2', or '3'");
        else:
            break;

    # Pull tweets from a user within a given time frame
    if (usr_choice == '3'): 
        usr_id = input("Username/ID: ");

        print("format: 'MM/DD/YYYY'");
        start = input("start date: ").split(sep='/');
        end   = input("end date: ").split(sep='/');
        
        # Convert to integers for datetime
        start = [int(i) for i in start];
        end   = [int(i) for i in end];

        query = f'from:{usr_id}';

        # Make request to API
        from datetime import datetime
        tweets = client.search_recent_tweets(
            query = query,
            start_time = datetime(year=start[2], month=start[0], day=start[1]),
            end_time = datetime(year=end[2], month=end[0], day=end[1])
        );

        # Error handling
        if (tweets.data is None):
            print("\nError: invalid author ID or username... exiting...");
            return -1;
        
        # Print retrieved tweets
        printTweetInfo(tweets.data);
    else:
        tw_id = None;
        while(1):
            tw_id = input("Tweet ID: ");

            if(tw_id.isdecimal()):
                break;
            else:
                print("Error: Tweet ID must be decimal...");

        # Get retweeters / likers (depending on user input)
        users = client.get_retweeters(id=tw_id) if usr_choice == '1' else client.get_liking_users(id=tw_id);
        if (users.data is None):
            print("\nError: invalid tweet ID... exiting...");
            return -1;

        # Print retrieved users 
        printUserInfo(users.data);

    return 0;

if __name__ == "__main__":
    main();