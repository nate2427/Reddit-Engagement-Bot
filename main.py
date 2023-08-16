import praw
from dotenv import load_dotenv
import os
import questionary
import openai

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

    def grab_comments(self, post):
        # Retrieve the comments from the post
        post.comments.replace_more(limit=None)
        return post.comments.list()

    def generate_comment(self, subreddit, post, comment, isReply=True):
        try:
            # Define the system prompt
            system_prompt = f"You are a user browsing the {subreddit} subreddit. You are reading a post that says '{post.selftext}' and a comment that says '{comment['body']}'. Your goal is to reply to the comment in the most optimized way to keep the conversation going. Engage the user by showing interest, asking questions, or providing relevant information. Be respectful and contribute positively to the discussion.\n\nAt the end of your comment, you can include a call to action or encourage further interaction.\n\nIf you receive 'There are no comments', please write an insightful and engaging comment that encourages the user to continue the conversation.\n\nRules for engaging the user:\nMake sure replies and comments are concise, thoughtful, and relevant. Have an intellectual undertone as you are the GURU/expert in the field (dont say that in your response), but also be a good conversationalist with humor, wit, compassion, and empathy. Make sure WORD COUNT IS LESS THAN 75 WORDS!!! Also, if the poster/replier is looking for help, promote me as a resource that can help by giving them GPT Business Integration Consultations. I will show them how to use GPT technology to various business pain points.\nThis is the tone you need to have the entire message, but be as conversational as possible. Only promote if neccessary, otherwise provide insightful information. If it isnt about running there own business, but about working for others, mention how i can help them with integrating GPT into their everyday workflows, freeing up more time. be conversational and engaging as much as possible. Try to get a response! That's your main goal.\nYou have personalities like Einstein, Steve Jobs, and Elon Musk, Barack Obama, and Jesus Christ, Ganhdi, Buddha. You understand life deeply on a spiritual, quantum, and metaphysical level. You believe in Evolutionary Game Theory and believe that the individuals who understand and use the tech the best will win. You keep this undertone while you speak, but you dont push it. It's more of a conversational tone. \n\n You start typing your reply..."

            # Generate the comment using OpenAI
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-16k",
                temperature=0.76,
                max_tokens=500,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": comment['body']}
                ],
            )
            response_comment = completion.choices[0]["message"]["content"]
            # if the comment is a reply, reply to the comment
            if isReply:
                return self.reply_to_comment(post, response_comment)
            # if no comments, make a comment
            else:
                return self.make_comment(post, response_comment)
            return response_comment
        except Exception as e:
            print(e)
            # Return a default comment if an error occurs
            return "I'm sorry, I couldn't generate a suitable comment at the moment."
        
    # replies to the comment it created an ai response
    def reply_to_comment(self, comment, ai_response):
        return comment.reply(ai_response)

    # make a comment on the post it created an ai response
    def make_comment(self, post, ai_response):
        return post.reply(ai_response)


def main():
    # Prompt user for subreddit and comment
    subreddit_name = questionary.text("Enter the subreddit name:").ask()

    bot = RedditBot()
    bot.connect_to_reddit()

    subreddit = bot.grab_subreddit(subreddit_name)
    post = bot.grab_post(subreddit)
    comments = bot.grab_comments(post)

    # say found a post and show the link
    questionary.print(f"Found a post in {subreddit_name}!\n")
    questionary.print(f"Link: {post.url}\n")

    # Display the post text
    questionary.print(f"\nCurrent Post Text:\n{post.selftext}\n")


    first_comment = None
    ai_response = None
    # if there are comments, respond to them
    if len(comments) > 2:
        comment = comments[0]
        questionary.print(f"Current Comment Text:\n{comment.body}\n")
         # Get the AI response
        ai_response = bot.generate_comment(subreddit, post, comment)
        questionary.print(f"AI Response:\n{ai_response}\n")
    # if no comments, respond with insightful ai response
    else:
        comment = {
            "body": "There are no comments",
        }
        questionary.print("No comments found...Creating an AI response...\n")
        ai_response = bot.generate_comment(subreddit, post, comment, isReply=False)
    questionary.print(f"AI Response:\n{post.url}/{ai_response}\n")

   

if __name__ == '__main__':
    main()
