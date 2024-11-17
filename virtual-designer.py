import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import openai
import base64
import io
from github import Github
from googletrans import Translator
import requests  # For fetching the image from the URL

# Initialize Session State for Version Control
if "design_versions" not in st.session_state:
    st.session_state["design_versions"] = []
    st.session_state["current_version"] = None
if "components" not in st.session_state:
    st.session_state["components"] = []

# Multi-Language Support
translator = Translator()

# App Title
st.title("Enhanced Virtual Design Mentor")
st.subheader("An AI-powered platform for interactive design feedback and enhancement!")

# Language selection
lang = st.selectbox('Select language', ['en', 'es', 'fr', 'de'])
lang_dict = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
}

# Translate to selected language
def translate_text(text, lang_code):
    return translator.translate(text, dest=lang_code).text

# Custom Components Library
components_library = {
    "Header": {"html": "<header><h1>App Header</h1></header>", "css": "header { background-color: #333; color: white; padding: 10px;}"},
    "Product Card": {"html": "<div class='product-card'><h3>Product Title</h3><img src='product.jpg' alt='Product'><p>Price: $99.99</p><button>Add to Cart</button></div>", "css": ".product-card {border: 1px solid #ddd; padding: 10px;}"},
    "Footer": {"html": "<footer><p>Footer Content</p></footer>", "css": "footer { background-color: #222; color: white; padding: 20px; text-align: center;}"},
    "Landing Page": {"html": "<div class='landing-page'><h1>Welcome to Our Website</h1><p>Explore our services and products</p></div>", "css": ".landing-page {text-align: center; padding: 50px; background-color: #f4f4f4;}"},
}

# Helper to generate code from components
def generate_code_from_components(selected_components):
    html_code = ""
    css_code = ""
    for component in selected_components:
        html_code += components_library[component]["html"]
        css_code += components_library[component]["css"]
    return html_code, css_code


# --- App Interface ---
st.sidebar.title("Options")
mode = st.sidebar.radio("Select Mode", ["Upload Image", "Generate AI Wireframe"])

# --- OpenAI Key Input ---
openai_key = st.sidebar.text_input("Enter OpenAI API Key:", type="password")

if openai_key:
    openai.api_key = openai_key  # Set OpenAI API key from the input field

# --- Upload Image Mode ---
if mode == "Upload Image":
    uploaded_file = st.file_uploader("Upload your wireframe/sketch (JPG, PNG)", type=["jpg", "png"])

    if uploaded_file:
        # Display Uploaded Image
        image = Image.open(uploaded_file)
        st.image(image, caption=translate_text("Uploaded Design", lang), use_column_width=True)

        # Drawable Canvas for Interactive Editing
        st.markdown("### Interactive Editing")
        st.markdown(translate_text("Draw directly on your design or annotate detected components.", lang))

        image_width, image_height = image.size
        canvas_result = st_canvas(
            fill_color="rgba(255, 0, 0, 0.3)",  # Highlight color
            stroke_width=3,
            stroke_color="red",
            background_image=image,
            update_streamlit=True,
            height=image_height,
            width=image_width,
            drawing_mode="freedraw",
            key="canvas",
        )

        # Save Edited Design as a Version
        if st.button(translate_text("Save Design Version", lang)):
            if canvas_result.image_data is not None:
                edited_image = Image.fromarray(canvas_result.image_data.astype("uint8"))
                st.session_state["design_versions"].append(edited_image)
                st.session_state["current_version"] = len(st.session_state["design_versions"]) - 1
                st.success(f"Saved version {len(st.session_state['design_versions'])}!")

        # Version Control
        if st.session_state["design_versions"]:
            st.markdown(translate_text("### Version Control", lang))
            version_index = st.selectbox(
                translate_text("Select a version to view or compare:", lang),
                options=list(range(len(st.session_state["design_versions"]))),
                format_func=lambda x: f"Version {x + 1}",
            )
            if version_index is not None:
                st.image(
                    st.session_state["design_versions"][version_index],
                    caption=f"Version {version_index + 1}",
                    use_column_width=True,
                )

        # AI Suggestions
        st.markdown("### AI Feedback & Suggestions")
        feedback_type = st.selectbox(
            translate_text("What type of feedback would you like?", lang),
            options=[translate_text("Usability", lang), translate_text("Accessibility", lang), translate_text("Aesthetics", lang), translate_text("All", lang)],
        )

        design_context = st.text_area(translate_text("Describe the design goal or context:", lang))

        if st.button(translate_text("Get AI Feedback", lang)):
            with st.spinner(translate_text("Generating feedback...", lang)):
                feedback_prompt = (
                    f"You are a virtual design mentor. Based on the design goal: '{design_context}', provide "
                    f"{feedback_type.lower()} feedback for the uploaded design."
                )
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[ 
                            {"role": "system", "content": "You are a professional design mentor."},
                            {"role": "user", "content": feedback_prompt},
                        ],
                        temperature=0.7,
                        max_tokens=300,
                    )
                    feedback = response["choices"][0]["message"]["content"].strip()
                    st.success(translate_text("AI Feedback:", lang))
                    st.write(feedback)
                except Exception as e:
                    st.error(f"Error generating feedback: {str(e)}")

        # AI Suggestions for Design Enhancements
        st.markdown(translate_text("### AI Suggestions for Enhancement", lang))
        enhancement_type = st.selectbox(
            translate_text("Select the type of enhancement you are looking for:", lang),
            options=[translate_text("Layout Improvement", lang), translate_text("Color Scheme", lang), translate_text("Typography", lang), translate_text("All", lang)],
        )

        if st.button(translate_text("Get Enhancement Suggestions", lang)):
            with st.spinner(translate_text("Generating enhancement suggestions...", lang)):
                enhancement_prompt = (
                    f"You are a design expert. Based on the uploaded image, provide suggestions for "
                    f"{enhancement_type.lower()} in the design."
                )
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[ 
                            {"role": "system", "content": "You are a design expert providing enhancement suggestions."},
                            {"role": "user", "content": enhancement_prompt},
                        ],
                        temperature=0.7,
                        max_tokens=300,
                    )
                    enhancement_suggestions = response["choices"][0]["message"]["content"].strip()
                    st.success(translate_text("AI Enhancement Suggestions:", lang))
                    st.write(enhancement_suggestions)
                except Exception as e:
                    st.error(f"Error generating enhancement suggestions: {str(e)}")

        # Select components to generate code
        st.markdown(translate_text("### Generate Code from Selected Components", lang))
        selected_components = st.multiselect(
            translate_text("Choose components to include in your design:", lang),
            options=list(components_library.keys())
        )

        if selected_components:
            html_code, css_code = generate_code_from_components(selected_components)
            st.markdown(translate_text("### Generated HTML Code", lang))
            st.code(html_code, language="html")
            st.markdown(translate_text("### Generated CSS Code", lang))
            st.code(css_code, language="css")

# --- Generate AI Wireframe Mode ---
elif mode == "Generate AI Wireframe":
    st.markdown("### AI Wireframe Generation")
    
    # Allow users to select fidelity level
    fidelity_option = st.selectbox("Select Wireframe Fidelity", ["Low Fidelity", "High Fidelity"])

    # User prompt to describe the wireframe
    user_prompt = st.text_area("Describe the type of wireframe you want:", "e.g., 'A simple mobile app for e-commerce with product listings'")

    if st.button(translate_text("Generate Wireframe", lang)):
        with st.spinner(translate_text("Generating wireframe...", lang)):
            try:
                # Modify the prompt based on the selected fidelity
                fidelity_description = "simple and low-fidelity wireframe with basic shapes" if fidelity_option == "Low Fidelity" else "detailed and high-fidelity wireframe with realistic elements and styles"

                full_prompt = f"Generate a {fidelity_description} based on the following description: '{user_prompt}'"
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[ 
                        {"role": "system", "content": "You are an expert wireframe designer."},
                        {"role": "user", "content": full_prompt},
                    ],
                    temperature=0.7,
                    max_tokens=500,
                )
                wireframe_code = response["choices"][0]["message"]["content"].strip()
                st.success(translate_text("Generated Wireframe Code:", lang))
                st.code(wireframe_code)
            except Exception as e:
                st.error(f"Error generating wireframe: {str(e)}")
# --- GitHub Integration (Save Design to GitHub) ---
st.markdown("### Save Design to GitHub")
github_token = st.text_input(translate_text("Enter GitHub Token (Personal Access Token):", lang))
repo_name = st.text_input(translate_text("Enter GitHub Repository Name:", lang))

if github_token and repo_name:
    g = Github(github_token)
    repo = g.get_user().get_repo(repo_name)
    design_file = io.BytesIO()
    image.save(design_file, format='PNG')
    design_file.seek(0)

    try:
        repo.create_file(f"design_{repo_name}.png", "Upload design", design_file.read())
        st.success(translate_text("Design saved to GitHub successfully!", lang))
    except Exception as e:
        st.error(f"Error saving design: {str(e)}")
