import streamlit as st
import google.generativeai as genai
import os
from datetime import datetime
import json
from io import StringIO
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="Gemini Blog Assistant Pro",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        margin-top: 10px;
        height: 3em;
        border-radius: 8px;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .output-container {
        background-color: #ffffff;
        border: 1px solid #e6e6e6;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    .settings-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .stSelectbox, .stSlider {
        margin-bottom: 15px;
    }
    .export-section {
        margin-top: 20px;
        padding: 15px;
        border-top: 1px solid #e6e6e6;
    }
    .history-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    h1, h2, h3 {
        color: #1f1f1f;
    }
    .stAlert {
        padding: 10px;
        border-radius: 8px;
    }
    .download-buttons {
        display: flex;
        gap: 10px;
        margin-top: 15px;
    }
    </style>
""", unsafe_allow_html=True)

class BlogAssistant:
    def __init__(self):
        # Initialize API key from .env
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            st.error("Please set your GOOGLE_API_KEY in the .env file")
            st.stop()
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.history = self.load_history()
        
        # Initialize session state for generated content
        if 'generated_content' not in st.session_state:
            st.session_state.generated_content = None
        
        # Comprehensive list of languages supported by Gemini
        self.languages = {
            'af': 'Afrikaans', 'sq': 'Albanian', 'am': 'Amharic', 'ar': 'Arabic', 'hy': 'Armenian',
            'az': 'Azerbaijani', 'eu': 'Basque', 'be': 'Belarusian', 'bn': 'Bengali', 'bs': 'Bosnian',
            'bg': 'Bulgarian', 'ca': 'Catalan', 'ceb': 'Cebuano', 'zh': 'Chinese', 'co': 'Corsican',
            'hr': 'Croatian', 'cs': 'Czech', 'da': 'Danish', 'nl': 'Dutch', 'en': 'English',
            'eo': 'Esperanto', 'et': 'Estonian', 'fi': 'Finnish', 'fr': 'French', 'fy': 'Frisian',
            'gl': 'Galician', 'ka': 'Georgian', 'de': 'German', 'el': 'Greek', 'gu': 'Gujarati',
            'ht': 'Haitian Creole', 'ha': 'Hausa', 'haw': 'Hawaiian', 'he': 'Hebrew', 'hi': 'Hindi',
            'hmn': 'Hmong', 'hu': 'Hungarian', 'is': 'Icelandic', 'ig': 'Igbo', 'id': 'Indonesian',
            'ga': 'Irish', 'it': 'Italian', 'ja': 'Japanese', 'jv': 'Javanese', 'kn': 'Kannada',
            'kk': 'Kazakh', 'km': 'Khmer', 'ko': 'Korean', 'ku': 'Kurdish', 'ky': 'Kyrgyz',
            'lo': 'Lao', 'la': 'Latin', 'lv': 'Latvian', 'lt': 'Lithuanian', 'lb': 'Luxembourgish',
            'mk': 'Macedonian', 'mg': 'Malagasy', 'ms': 'Malay', 'ml': 'Malayalam', 'mt': 'Maltese',
            'mi': 'Maori', 'mr': 'Marathi', 'mn': 'Mongolian', 'my': 'Myanmar (Burmese)',
            'ne': 'Nepali', 'no': 'Norwegian', 'ny': 'Nyanja (Chichewa)', 'or': 'Odia (Oriya)',
            'ps': 'Pashto', 'fa': 'Persian', 'pl': 'Polish', 'pt': 'Portuguese', 'pa': 'Punjabi',
            'ro': 'Romanian', 'ru': 'Russian', 'sm': 'Samoan', 'gd': 'Scots Gaelic', 'sr': 'Serbian',
            'st': 'Sesotho', 'sn': 'Shona', 'sd': 'Sindhi', 'si': 'Sinhala', 'sk': 'Slovak',
            'sl': 'Slovenian', 'so': 'Somali', 'es': 'Spanish', 'su': 'Sundanese', 'sw': 'Swahili',
            'sv': 'Swedish', 'tl': 'Tagalog (Filipino)', 'tg': 'Tajik', 'ta': 'Tamil', 'tt': 'Tatar',
            'te': 'Telugu', 'th': 'Thai', 'tr': 'Turkish', 'tk': 'Turkmen', 'uk': 'Ukrainian',
            'ur': 'Urdu', 'ug': 'Uyghur', 'uz': 'Uzbek', 'vi': 'Vietnamese', 'cy': 'Welsh',
            'xh': 'Xhosa', 'yi': 'Yiddish', 'yo': 'Yoruba', 'zu': 'Zulu'
        }

    def load_history(self):
        if 'generation_history' not in st.session_state:
            st.session_state.generation_history = []
        return st.session_state.generation_history

    def save_to_history(self, topic, content, language, tone, length):
        entry = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'topic': topic,
            'content': content,
            'language': language,
            'tone': tone,
            'length': length
        }
        st.session_state.generation_history.append(entry)

    def generate_content(self, topic, length, language, tone, structure):
        prompt = f"""
        Create a {tone} blog post about {topic} in {language}.
        Length: approximately {length} words
        Structure: {structure}
        
        Please ensure the content is:
        - Well-structured with clear sections
        - Engaging and appropriate for the chosen tone
        - Optimized for readability
        - Including relevant subheadings
        - Written naturally in the target language
        """
        
        try:
            response = self.model.generate_content(prompt)
            content = response.text
            self.save_to_history(topic, content, language, tone, length)
            st.session_state.generated_content = content
            return content
        except Exception as e:
            st.error(f"Error generating content: {str(e)}")
            return None

    def export_history(self, format_type):
        if not self.history:
            return None
        
        if format_type == 'json':
            return json.dumps(self.history, indent=2)
        elif format_type == 'markdown':
            markdown_content = ""
            for entry in self.history:
                markdown_content += f"# {entry['topic']}\n\n"
                markdown_content += f"**Language:** {entry['language']}\n\n"
                markdown_content += f"**Tone:** {entry['tone']}\n\n"
                markdown_content += f"**Length:** {entry['length']} words\n\n"
                markdown_content += f"**Generated on:** {entry['timestamp']}\n\n"
                markdown_content += f"{entry['content']}\n\n---\n\n"
            return markdown_content
        return None

    def clean_markdown(self, text):
        """Remove markdown syntax and clean the text for plain text copy"""
        # Remove bold markers
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        # Remove italic markers
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        # Remove markdown headers
        text = re.sub(r'#+\s*', '', text)
        return text


def main():
    st.title('✍️ Gemini Blog Assistant Pro')
    
    assistant = BlogAssistant()
    
    # Create two columns for layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        with st.container():
            st.subheader("Content Settings")
            
            topic = st.text_area(
                "Enter your blog topic:",
                height=100,
                key="topic_input",
                help="Describe your blog topic in detail"
            )
            
            length = st.slider(
                "Content length (words):",
                min_value=100,
                max_value=5000,
                value=1000,
                step=100,
                help="Choose the approximate length of your content"
            )
            
            language = st.selectbox(
                'Select language:',
                options=list(assistant.languages.values()),
                index=list(assistant.languages.values()).index('English'),
                key='language_select'
            )
            
            tone = st.select_slider(
                'Content tone:',
                options=['Professional', 'Casual', 'Academic', 'Conversational', 'Technical'],
                value='Professional'
            )
            
            structure = st.multiselect(
                'Content structure elements:',
                ['Introduction', 'Body Paragraphs', 'Conclusion', 'Call to Action', 'References'],
                default=['Introduction', 'Body Paragraphs', 'Conclusion']
            )
            
            generate_button = st.button('Generate Content', type='primary', key='generate')
    
    with col2:
        if generate_button:
            if not topic:
                st.warning("Please enter a topic.")
            else:
                with st.spinner('Generating content...'):
                    content = assistant.generate_content(
                        topic,
                        length,
                        language,
                        tone,
                        ', '.join(structure)
                    )
        
        # Display generated content if available
        if st.session_state.generated_content:
            st.subheader("Generated Content")
            with st.container():
                st.markdown(st.session_state.generated_content)
                
                # Copy button with icon
                plain_text = assistant.clean_markdown(st.session_state.generated_content)
                copy_button = st.button("📋 Copy Plain Text")

                if copy_button:
                    st.components.v1.html(
                        f"""
                        <form>
                        <input type="text" value="{plain_text}" id="copy-text" style="opacity:0;position:absolute;z-index:-1;">
                        </form>
                        <script>
                        var copyText = document.getElementById("copy-text");
                        copyText.select();
                        document.execCommand("copy");
                        console.log("text copied");
                        </script>
                        """,
                        height=0
                    )
                    st.success("Plain text copied to clipboard!")
    
    # History and Export Section
    if assistant.history:
        st.header("Generation History")
        
        # Collapsible history section
        with st.expander("View History", expanded=False):
            for entry in reversed(assistant.history):
                with st.container():
                    st.write(f"**Topic:** {entry['topic']}")
                    st.write(f"**Language:** {entry['language']}")
                    st.write(f"**Tone:** {entry['tone']}")
                    st.write(f"**Length:** {entry['length']} words")
                    st.write(f"**Generated on:** {entry['timestamp']}")
                    st.markdown("---")
                    st.markdown(entry['content'])
        
        # Export options
        st.subheader("Export History")
        export_format = st.radio("Export format:", ['json', 'markdown'])
        export_data = assistant.export_history(export_format)
        if export_data:
            st.download_button(
                label=f"Export History as {export_format.upper()}",
                data=export_data,
                file_name=f"generation_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{export_format}",
                mime=f"application/{export_format}" if export_format == 'json' else "text/markdown"
            )

if __name__ == '__main__':
    main()

