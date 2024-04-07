import streamlit as st
import google.generativeai as genai
import os

# Set your API key
os.environ['GOOGLE_API_KEY'] = "Enter your gemini api key here"

# Configure GenerativeAI library with the API key
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

def generate_content(topics, content_length, language):
    # Generate content using the Gemini LLM API
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"Generate content related to {topics} with a length of {content_length} words in {language} language."
    response = model.generate_content(prompt)
    generated_content = response.parts[0].text
    return generated_content

def main():
    st.title('Gemini Blog Assistant')

    topics = st.text_input('Enter a topic:')
    content_length = st.number_input('Enter the content length (words):', min_value=1)

    language_options = {
        'en': 'English',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'ja': 'Japanese',
        'ko': 'Korean',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'zh-CN': 'Chinese (Simplified)',
        'zh-TW': 'Chinese (Traditional)',
        'ar': 'Arabic',
        'hi': 'Hindi',
        'id': 'Indonesian',
        'tr': 'Turkish',
        'th': 'Thai',
        'nl': 'Dutch',
        'sv': 'Swedish',
        'fi': 'Finnish',
        'da': 'Danish',
        'no': 'Norwegian',
        'pl': 'Polish',
        'cs': 'Czech',
        'hu': 'Hungarian',
        'el': 'Greek',
        'iw': 'Hebrew',
        'ro': 'Romanian',
        'sr': 'Serbian',
        'sk': 'Slovak',
        'sl': 'Slovenian',
        'es': 'Spanish',
        'sw': 'Swahili',
        'sv': 'Swedish',
        'th': 'Thai',
        'tr': 'Turkish',
        'uk': 'Ukrainian',
        'vi': 'Vietnamese',
    }

    language = st.selectbox('Select language:', list(language_options.values()))

    if st.button('Generate Content'):
        if not topics:
            st.warning("Please enter a topic.")
        else:
            generated_content = generate_content(topics, content_length, next((code for code, name in language_options.items() if name == language), 'en'))
            st.subheader('Generated Content:')
            st.markdown(generated_content, unsafe_allow_html=True)  # Display the generated content as markdown

if __name__ == '__main__':
    main()
