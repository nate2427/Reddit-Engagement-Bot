import streamlit as st
from reddit_bot import redditBot as bot
from gpt_prompts import get_prompt, update_persona_prompt_template
from config import subreddit_configs

reddit_personas = {
    "General Coding Tutor": "r_ProgrammerBasicTemplate",
    "Mindfulness Practitioner": "r_mindfulnessaudiencetemplate",
}

def home_page():
    col1, col2 = st.columns([1, 2])

    # Check if 'post_url' exists in session state
    if 'post_url' not in st.session_state:
        st.session_state.post_url = ""

    # Initialize AI comments in session state if not present
    if 'ai_comments' not in st.session_state:
        st.session_state.ai_comments = {}

    if 'comments' not in st.session_state:
        st.session_state.comments = []

    if 'post' not in st.session_state:
        st.session_state.post = ""
    
    if 'subreddit' not in st.session_state:
        st.session_state.subreddit = ""
    
    if 'subreddit_description' not in st.session_state:
        st.session_state.subreddit_description = ""
    
    if 'subreddit_summary' not in st.session_state:
        st.session_state.subreddit_summary = ""
    

    post_url = col1.text_input("Reddit post URL", st.session_state.post_url)
    search_button = col1.button("search")

    if search_button:
        st.session_state.post_url = post_url
        with st.spinner("Loading..."):
            bot.connect_to_reddit()
            st.session_state.post = bot.get_post_and_comments(post_url)
        st.session_state.comments = bot.grab_comments(st.session_state.post)
        st.session_state.selected_persona = col2.selectbox("Choose A Persona", reddit_personas.keys(), index=0 if 'selected_persona' not in st.session_state else list(reddit_personas.keys()).index(st.session_state.selected_persona))
    elif 'selected_persona' in st.session_state:
        st.session_state.selected_persona = col2.selectbox("Choose A Persona", reddit_personas.keys(), index=list(reddit_personas.keys()).index(st.session_state.selected_persona))

    if 'post_url' in st.session_state and st.session_state.post_url:
        # sidebar configuration section
        st.sidebar.title("Reddit Post")
        st.sidebar.text_area(st.session_state.post.title, f"{st.session_state.post.selftext}", height=250)
        st.sidebar.text(f"Author: {st.session_state.post.author}")

        # show selected persona prompt template in sidebar
        persona_prompt = get_prompt(reddit_personas[st.session_state.selected_persona])
        persona_prompt_text_area = st.sidebar.text_area("Persona: 🧑🏾‍🦱", persona_prompt, height=250)
        if st.sidebar.button("Update Persona"):
            st.sidebar.info(f"{reddit_personas[st.session_state.selected_persona]} \n\n {persona_prompt_text_area}")
            if update_persona_prompt_template(reddit_personas[st.session_state.selected_persona], persona_prompt_text_area):
                st.sidebar.success("Updated!")
            else:
                st.sidebar.error("Failed Upating Persona!")

        # subreddit configuration section
        st.header("Subreddit Configuration")
        selected_subreddit = st.selectbox("Choose a subreddit", subreddit_configs.keys())
        st.session_state.subreddit = selected_subreddit
        st.session_state.subreddit_description = subreddit_configs[selected_subreddit]['subreddit_desc']
        st.session_state.subreddit_summary = subreddit_configs[selected_subreddit]['subreddit_summary']
        desc_col, summary_col = st.columns(2)
        subr_desc = desc_col.text_area("Subreddit Description", f"{st.session_state.subreddit_description}", height=150)
        subr_summary = summary_col.text_area("Subreddit Summary", f"{st.session_state.subreddit_summary}", height=150)


        # comments section
        st.header("Top Level Comments")
        for i, comment in enumerate(st.session_state.comments):
            comment_author = comment.author
            comment_body = comment.body
            st.text_area("Comment", f"{comment_body}", height=50, label_visibility="hidden", key="comment_{}".format(str(i)), disabled=True)
            st.text(f"Author: {comment_author}")
            container = st.empty()
            # Buttons to interact with comment
            but_col1, but_col2, but_col3 = st.columns(3)
            generate_ai_comment_button = but_col1.button("Generate AI\nResponse", key=f'generate_ai_comment_{i}')
            regenerate_button = but_col2.button("Regenerate Response", key=f'regenerate_{i}', disabled=i not in st.session_state.ai_comments)
            post_reply_button = but_col3.button("Reply to Comment", key=f'post_comment_{i}', disabled=i not in st.session_state.ai_comments)

            # Generate Button Click Handler
            
            if generate_ai_comment_button:
                with st.spinner("Regenerating..."):
                    ai_comment = bot.generate_comment(selected_subreddit, st.session_state.post.selftext, comment_body, st.session_state.post.title, st.session_state.post.author, comment_author, subr_desc, subr_summary, persona_prompt_text_area)

                st.session_state.ai_comments[i] = container.text_area("🤖 AI Generated Comment 📝:", f"{ai_comment}", height=200, key="ai_comment_{}".format(str(i)))


            elif i in st.session_state.ai_comments:
                st.session_state.ai_comments[i] = container.text_area("🤖 AI Generated Comment 📝:", f"{st.session_state.ai_comments[i]}", height=200, key="ai_comment_{}".format(str(i)))


            # Regenerate Button Click Handler
            if regenerate_button:
                container.empty()
                with st.spinner("Generating..."):
                    ai_comment = bot.regenerate_comment(selected_subreddit, st.session_state.post.selftext, comment_body, st.session_state.post.title, st.session_state.post.author, comment_author, subr_desc, subr_summary, persona_prompt_text_area, st.session_state.ai_comments[i])

                st.session_state.ai_comments[i] = container.text_area("🤖 AI Generated Comment 📝:", f"{ai_comment}", height=200, key="ai_regen_comment_{}".format(str(i)))


            # Post Comment Button Click Handler
            if post_reply_button:
                with st.spinner("Replying..."):
                    if bot.reply_to_comment(comment, st.session_state.ai_comments[i]):
                        container.empty()
                        st.success("Successfully replied to comment!")
                    else:
                        st.error("Failed to reply to comment!")


def about_page():
    st.write("This is the About Page!")

def contact_page():
    st.write("Feel free to contact us!")

# Set up sidebar
pages = ["Generate Comments", "About", "Contact"]
st.title("🤖 Reddit Buzz Builder 🤖")
selected_page = st.selectbox("", pages)

# Display selected page
if selected_page == "Generate Comments":
    home_page()
elif selected_page == "About":
    about_page()
else:
    contact_page()
