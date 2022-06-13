import tweepy
import config

client = tweepy.Client(bearer_token=config.BEARER_TOKEN);

def printUserInfo(userData):
    print('-'*72);
    print('| {:20} | {:20} | id'.format('name', 'username'));
    print('-'*72);
    for user in userData:
        print('| {:20.17} | {:20} | {:<32}'.format(user.name, user.username, user.id));

def main():
    usr_choice, tw_id = None, None;

    while (1):
        usr_choice  = input("\nTwitter Tool Options:\n1. Get retweeters\n2. Get likers\n> ");
        tw_id       = input("Tweet ID: ");

        if (not tw_id.isdecimal() or not usr_choice.isdecimal()):
            print("\nError: all inputs must be decimal");
        elif (usr_choice != '1' and usr_choice != '2'):
            print("\nError: must pick option '1' or '2'");
        else:
            break;
            
    users = client.get_retweeters(id=tw_id) if usr_choice == '1' else client.get_liking_users(id=tw_id);
    if (users.data is None):
        print("\nError: invalid tweet ID... exiting...");
        return -1;

    printUserInfo(users.data);
    return 0;

if __name__ == "__main__":
    main();