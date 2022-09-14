# A file containing old/deprecated functionality. Can be entirely ignored, simply left for reference and will likely be removed soon.

import tweepy
import config
import sys

def user_input():
    ''' Re-name this function to 'main' if you wish to extract follower count of a file with usernames '''

    from os.path import exists
    client = tweepy.Client(bearer_token=config.BEARER_TOKEN)

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

'''
def alt_main():
    # This function is not used (for now), but left here just for reference
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
        # printTweetInfo(tweets.data);
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
        # printUserInfo(users.data);

    return 0;
    '''