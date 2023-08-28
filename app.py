import streamlit as st
from reddit_bot import redditBot as bot
from gpt_prompts import get_prompt, update_persona_prompt_template
from db import get_all_persona_configs, get_all_subreddit_configs, add_new_persona_config, add_new_subreddit_config

reddit_personas = get_all_persona_configs()
subreddit_configs = get_all_subreddit_configs()

def generate_comments_page():
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

        # write a comment on post section
        st.header("Generate a Comment on the Post")
        comment_container = st.empty()
        comment_but_col1, comment_but_col2, comment_but_col3 = st.columns(3)
        generate_comment_button = comment_but_col1.button("Generate Comment", key="generate_comment")
        regenerate_comment_button = comment_but_col2.button("Regenerate Comment", key="regenerate_comment", disabled="generated_comment" not in st.session_state)
        post_comment_button = comment_but_col3.button("Post Comment", key="post_comment", disabled="generated_comment" not in st.session_state)
        if generate_comment_button:
            with st.spinner("Generating..."):
                ai_generated_comment = bot.generate_comment_to_post(selected_subreddit, st.session_state.post.selftext, "", st.session_state.post.title, st.session_state.post.author, "", subr_desc, subr_summary, persona_prompt_text_area)
                comment_container.empty()
            st.session_state.generated_comment = comment_container.text_area("🤖 AI Generated Comment 📝:", f"{ai_generated_comment}", height=200, key="ngenerated_comment_0")
            st.experimental_rerun()
        elif "generated_comment" in st.session_state:
            st.session_state.generated_comment = comment_container.text_area("🤖 AI Generated Comment 📝:", f"{st.session_state.generated_comment}", height=200, key="generated_comment_0")

        if regenerate_comment_button:
            with st.spinner("Regenerating..."):
                ai_regenerated_comment = bot.regenerate_comment_to_post(selected_subreddit, st.session_state.post.selftext, "", st.session_state.post.title, st.session_state.post.author, "", subr_desc, subr_summary, persona_prompt_text_area, st.session_state.generated_comment)
                comment_container.empty()
            st.session_state.generated_comment = comment_container.text_area("🤖 AI Generated Comment 📝:", f"{ai_regenerated_comment}", height=200, key="regenerated_comment_0")

        if post_comment_button:
            with st.spinner("Posting..."):
                if bot.make_comment(st.session_state.post, st.session_state.generated_comment):
                    st.success("Comment Posted!")
                else:
                    st.error("Failed to post comment!")

        # comments section
        st.header("Top Level Comments")
        for i, comment in enumerate(st.session_state.comments):
            comment_author = comment.author
            comment_body = comment.body
            st.text_area("Comment", f"{comment_body}", height=50, label_visibility="hidden", key="comment_{}".format(str(i)), disabled=True)
            container = st.empty()
            st.text(f"Author: {comment_author}")
            # Buttons to interact with comment
            but_col1, but_col2, but_col3 = st.columns(3)
            generate_ai_comment_button = but_col1.button("Generate AI\nResponse", key=f'generate_ai_comment_{i}')
            regenerate_button = but_col2.button("Regenerate Response", key=f'regenerate_{i}', disabled=i not in st.session_state.ai_comments)
            post_reply_button = but_col3.button("Reply to Comment", key=f'post_comment_{i}', disabled=i not in st.session_state.ai_comments)

            # Generate Button Click Handler
            
            if generate_ai_comment_button:
                with st.spinner("Generating..."):
                    ai_comment = bot.generate_comment(selected_subreddit, st.session_state.post.selftext, comment_body, st.session_state.post.title, st.session_state.post.author, comment_author, subr_desc, subr_summary, st.session_state.generated_comment, persona_prompt_text_area)

                st.session_state.ai_comments[i] = container.text_area("🤖 AI Generated Comment 📝:", f"{ai_comment}", height=200, key="ai_comment_{}".format(str(i)))
                st.experimental_rerun()
            elif i in st.session_state.ai_comments:
                st.session_state.ai_comments[i] = container.text_area("🤖 AI Generated Comment 📝:", f"{st.session_state.ai_comments[i]}", height=200, key="ai_comment_{}".format(str(i)))


            # Regenerate Button Click Handler
            if regenerate_button:
                container.empty()
                with st.spinner("Regenerating..."):
                    ai_comment = bot.regenerate_comment(selected_subreddit, st.session_state.post.selftext, comment_body, st.session_state.post.title, st.session_state.post.author, comment_author, subr_desc, subr_summary, st.session_state.generated_comment, persona_prompt_text_area, st.session_state.ai_comments[i])

                st.session_state.ai_comments[i] = container.text_area("🤖 AI Generated Comment 📝:", f"{ai_comment}", height=200, key="ai_regen_comment_{}".format(str(i)))


            # Post Comment Button Click Handler
            if post_reply_button:
                with st.spinner("Replying..."):
                    if bot.reply_to_comment(comment, st.session_state.ai_comments[i]):
                        container.empty()
                        st.success("Successfully replied to comment!")
                    else:
                        st.error("Failed to reply to comment!")


def add_persona_config():
    persona_name = st.text_input("New Persona Title", placeholder="GPT Instructor")
    persona_prompt_id = st.text_input("Persona Prompt ID", placeholder="gpt_instructor")
    button = st.button("Add Persona")
    # add this persona to the db
    if button:
        if add_new_persona_config(persona_name, persona_prompt_id):
            st.success("Successfully added new persona!")
        else:
            st.error("Failed to add new persona!")

def add_subreddit_config():
    subreddit_name = st.text_input("New Subreddit Title", placeholder="learnpython")
    subreddit_desc = st.text_area("Subreddit Description", placeholder="Get this from Gummy Search")
    subreddit_summary = st.text_area("Subreddit Summary", placeholder="Get this from Gummy Search")
    button = st.button("Add Subreddit")
    # add this subreddit to the db
    if button:
        if add_new_subreddit_config(subreddit_name, subreddit_desc, subreddit_summary):
            st.success("Successfully added new subreddit!")
        else:
            st.error("Failed to add new subreddit!")

# Set up sidebar
pages = ["Generate Comments", "Add New Persona", "Add New Subreddit"]
st.title("🤖 Reddit Buzz Builder 🤖")
selected_page = st.selectbox("Pages", pages, label_visibility="hidden")

# Display selected page
if selected_page == "Generate Comments":
    generate_comments_page()
elif selected_page == "Add New Persona":
    add_persona_config()
elif selected_page == "Add New Subreddit":
    add_subreddit_config()
