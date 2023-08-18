import praw
from dotenv import load_dotenv
import os
import questionary
import promptlayer
load_dotenv()
promptlayer.api_key = os.getenv("PROMPTLAYER_API_KEY")
openai = promptlayer.openai


class RedditBot:
    def __init__(self):
        load_dotenv()  # Load environment variables from .env file
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent='your_user_agent',
            username=os.getenv('REDDIT_USERNAME'),
            password=os.getenv('REDDIT_PASSWORD')
        )
        openai.api_key = os.getenv('OPENAI_API_KEY')

    def connect_to_reddit(self):
        # Connect to Reddit API using provided credentials
        questionary.print("Logging in to Reddit...")
        self.reddit.read_only = False
        questionary.print("Logged in successfully!")

    def grab_subreddit(self, subreddit_name):
        subreddit = self.reddit.subreddit(subreddit_name)
        return subreddit

    def grab_post(self, subreddit):
        questionary.print("Grabbing a post from the subreddit...")
        for post in subreddit.new(limit=1):
            return post
        
    def get_post_and_comments(self, post_url):
        """Retrieve the post and comments from the url"""
        questionary.print("Retrieving post with url {}...\n".format(post_url))
        post = self.reddit.submission(url=post_url)
        print(post.comments)
        questionary.print("Post with url {} retrieved...\n".format(post_url))
        return post

    def grab_comments(self, post):
        """Retrieves the comments from the post"""        
        post.comments.replace_more(limit=0)
        print(post.comments.list())
        questionary.print("Comments from post retrieved...\n")
        return post.comments.list()
    
    def generate_comment(self, subreddit, post, comment, post_title, post_author, comment_author, subreddit_description, subreddit_summary):
        try:
            questionary.print("Generating AI comment...\n")
            template_dict = promptlayer.prompts.get("r_MindfulnessAudienceTemplate")
            system_prompt = template_dict['template']
            

            # Replace the variables in the prompt with the comment body
            formatted_system_prompt = system_prompt.format(
                comment=comment,
                subreddit_description=subreddit_description,
                subreddit_summary=subreddit_summary,
                post_text=post,
                subreddit=subreddit,
                post_title=post_title,
                post_author=post_author,
                comment_author=comment_author
            )

            # Generate the comment using OpenAI
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-16k",
                temperature=0.76,
                max_tokens=750,
                messages=[
                    {"role": "system", "content": formatted_system_prompt},
                    {"role": "user", "content": "You start typing your reply..."}
                ],
            )
            response_comment = completion.choices[0]["message"]["content"]
            questionary.print("AI comment generated...\n")
            return response_comment
        except Exception as e:
            print("Error:", e)
            # Return a default comment if an error occurs
            return "I'm sorry, I couldn't generate a suitable comment at the moment."
        
    # replies to the comment it created an ai response
    def reply_to_comment(self, comment, ai_response):
        try:
            questionary.print("Replying to comment...\n")
            # upvote the comment
            comment.upvote()
            # reply to the comment
            reply_obj = comment.reply(ai_response)
            reply_link = reply_obj.permalink
            questionary.print("Successfully replied to comment: https://www.reddit.com{}...\n".format(reply_link))            
            return reply_obj
        except Exception as e:
            questionary.print("Error:", e)

    

    # make a comment on the post it created an ai response
    def make_comment(self, post, ai_response):
        """Make a comment on the post"""
        questionary.print("Making a comment on the post...\n")
        comment_obj = post.reply(ai_response)
        comment_link = comment_obj.permalink
        questionary.print("Successfully made a comment: https://www.reddit.com{} ...\n".format(comment_link))
        return comment_obj
    


def main():
    
    # Prompt user for subreddit name, subreddit description, and subreddit summary
    subreddit_name = questionary.text("Enter the subreddit name: ").ask()
    subreddit_description = questionary.text("Enter the subreddit description: ").ask()
    subreddit_summary = questionary.text("Enter the subreddit summary: ").ask()

    # ask for the path to the text file that has a list of reddit posts urls
    path = questionary.text("Enter the path to the text file with the list of reddit posts urls: ").ask()

    # open the text file and read the urls into a list
    with open(path) as f:
        urls = f.readlines()
    urls = [url.strip() for url in urls]


    questionary.print("Gaining Access to Reddit Bot...\n")
    bot = RedditBot()
    bot.connect_to_reddit()
    questionary.print("Access Granted!!!\n...\n")

    # for each url in the list, grab the post and comments
    for url in urls:
        current_post = bot.get_post_and_comments(url)
        # like the post
        current_post.upvote()
        post_text = current_post.selftext
        post_title = current_post.title
        post_author = current_post.author
        comments = bot.grab_comments(current_post)
        # check if there are any comments
        if len(comments) > 0:
            # remove the first comment
            comments.pop(0)
            # for each comment, generate an ai response
            for comment in comments:
                comment_author = comment.author
                response = bot.generate_comment(subreddit_name, post_text, comment.body, post_title, post_author, comment_author, subreddit_description, subreddit_summary)
                # reply to the comment
                bot.reply_to_comment(comment, response)
        else:
            # if there are no comments, generate an ai response
            response = bot.generate_comment(subreddit_name, post_text, "There are no comments", post_title, post_author, "no author", subreddit_description, subreddit_summary)
            # reply to the post
            bot.make_comment(current_post, response)

   

if __name__ == '__main__':
    main()
