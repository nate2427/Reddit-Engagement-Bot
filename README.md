# Reddit Comment Dashboard/Bot

This project is a dashboard and bot that helps with commenting and replying on targeted posts from Reddit.

## Installation

1. Clone the repository:

`git clone https://github.com/nate2427/Reddit-Engagement-Bot`

2. Install the required dependencies:

`pip install -r requirements.txt`

3. Rename the `._.env` file to `.env`:

`mv _.env .env`

4.  Update the `.env` file with the appropriate values for your Reddit API credentials and other settings.

    Example `.env` file:

         REDDIT_CLIENT_ID=your-reddit-client-id
         REDDIT_CLIENT_SECRET=your-reddit-client-secret
         REDDIT_USERNAME=your-reddit-username
         REDDIT_PASSWORD=your-reddit-password

## Usage

1. Go to the project directory:

`cd Reddit-Engagement-Bot`

2. Start the Streamlit app:

`streamlit run app.py`

3. Open your web browser and visit `http://localhost:8501` to access the Reddit Comment Dashboard.

4. In the dashboard, enter the Reddit post URL you want to target in the "Reddit post URL" field.

5. Choose a persona from the "Choose A Persona" dropdown.

6. Interact with the dashboard to comment and reply on the targeted Reddit post.

## Project Structure

The project structure is as follows:

reddit-comment-dashboard/

├── app.py # Entry point of the Streamlit app

├── requirements.txt # List of required dependencies

└── …

# Other project files and directories

- `app.py`: This is the main entry point of the Streamlit app. It contains the dashboard functionality for commenting and replying on Reddit posts.
- `requirements.txt`: This file lists all the required dependencies for the project.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
