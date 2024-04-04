import streamlit as st
import openai

# Set your OpenAI API key
openai.api_key = "your-api-key"


def translate_text(text, source_language, target_language):
    """
    Translate text from the source language to the target language.
    """
    try:
        response = openai.Completion.create(
            model="text-davinci-003",  # or the latest available model
            prompt=f"Translate this text from {source_language} to {target_language}: {text}",
            temperature=0.7,
            max_tokens=100,
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error in translation: {str(e)}"


def generate_customer_support_response(query):
    """
    Generate a customer support response to the query.
    """
    try:
        response = openai.Completion.create(
            model="text-davinci-003",  # or the latest available model
            prompt=f"Respond to this customer support query: {query}",
            temperature=0.7,
            max_tokens=150,
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error in generating response: {str(e)}"


def main():
    st.title("Multilingual Customer Support Demo")

    # User inputs
    customer_query = st.text_area(
        "Enter Customer Query (Non-English)", "Example: ¿Cuándo llegará mi pedido?"
    )
    source_language = st.text_input("Source Language", "Spanish")

    if st.button("Generate Support Response"):
        with st.spinner("Processing..."):
            # Translate query to English
            translated_query = translate_text(
                customer_query, source_language, "English"
            )
            st.text("Translated Query (English):")
            st.write(translated_query)

            # Generate response in English
            response_english = generate_customer_support_response(translated_query)
            st.text("Response in English:")
            st.write(response_english)

            # Translate response back to the original language
            translated_response = translate_text(
                response_english, "English", source_language
            )
            st.text(f"Response in {source_language}:")
            st.write(translated_response)


if __name__ == "__main__":
    main()

import streamlit as st
import openai

# Set your OpenAI API key
openai.api_key = "your-api-key"


def generate_personalized_email(customer_segment):
    """
    Generate personalized email content based on the customer segment.
    """
    try:
        response = openai.Completion.create(
            model="text-davinci-003",  # or the latest available model
            prompt=f"Create a personalized email for the customer segment: {customer_segment}.",
            temperature=0.7,
            max_tokens=150,
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error in generating email: {str(e)}"


def main():
    st.title("Email Marketing Personalization Demo")

    # User input for customer segment details
    customer_segment = st.text_area(
        "Enter Customer Segment Details",
        "Example: Frequent buyers, age 30-40, interested in outdoor sports.",
    )

    if st.button("Generate Personalized Email"):
        with st.spinner("Generating personalized email..."):
            personalized_email = generate_personalized_email(customer_segment)
            st.text_area("Generated Email", personalized_email, height=300)


if __name__ == "__main__":
    main()

import streamlit as st
import openai

# Set your OpenAI API key
openai.api_key = "your-api-key"


def generate_social_media_content(prompt, type_of_content):
    """
    Generate social media content based on the provided prompt and content type.
    """
    try:
        response = openai.Completion.create(
            model="text-davinci-003",  # or the latest available model
            prompt=f"Generate a {type_of_content} for the following social media prompt: {prompt}",
            temperature=0.7,
            max_tokens=150,
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error in generating content: {str(e)}"


def main():
    st.title("Social Media Management Automation Demo")

    # User input for the social media prompt
    social_media_prompt = st.text_area(
        "Enter Social Media Prompt", "Example: Announcing a new product launch."
    )

    content_type = st.selectbox("Select Content Type", ["Post", "Response"])

    if st.button("Generate Social Media Content"):
        with st.spinner("Generating content..."):
            social_media_content = generate_social_media_content(
                social_media_prompt, content_type
            )
            st.text_area("Generated Content", social_media_content, height=300)


if __name__ == "__main__":
    main()
