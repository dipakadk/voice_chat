import os
import time  # To measure time
import streamlit as st
import tempfile
from audio_recorder_streamlit import audio_recorder
import base64
from openai import OpenAI
import datetime

# load_dotenv()

# openai_api_key = os.getenv("OPENAI_API_KEY")  # Get the API key stored in the .env file

def speech_to_text_conversion(file_path):
    """Converts audio format message to text using OpenAI's Whisper model."""
    audio_file = open(file_path, "rb")  # Open the audio file in binary read mode
    transcription = client.audio.transcriptions.create(
        model="whisper-1",  # Model to use for transcription
        file=audio_file  # Audio file to transcribe
    )
    return transcription.text

def text_chat(text):
    """Generates response using OpenAI and streams the output in real-time."""
    answer = ""
    response_chunks = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"You are a helpful assistant that provides the response to the user about Nepal in at most 50 words. The user text is {text}"},
        ],
        # stream=True  # Enable streaming
    )

    first_chunk_received = False
     # Measure the time before receiving the first chunk
    return response_chunks.choices[0].message.content

    # for chunk in response_chunks:
    #     start_time = time.time() 

    #     # Accessing the content directly from delta
    #     if (text_chunk := chunk.choices[0].delta.content):
    #         if not first_chunk_received:
    #             first_chunk_received = True
    #             first_char_time = time.time() - start_time  # Time taken to get the first character
    #             st.write(f"Time to receive first character: {first_char_time:.2f} seconds")  # Display in UI
    #         answer += text_chunk
    #         yield text_chunk  # Yield each text chunk as it arrives
    
    # return answer

def text_to_speech_conversion(text):
    """Converts text to audio format message using OpenAI's text-to-speech model - tts-1."""
    if text:  # Check if converted_text is not empty
        speech_file_path = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + "_speech.webm"
        response = client.audio.speech.create(
            model="tts-1",  # Model to use for text-to-speech conversion
            voice="fable",  # Voice to use for speech synthesis
            input=text  # Text to convert to speech
        )
        response.stream_to_file(speech_file_path)  # Streaming synthesized speech to file
        # Read the audio file as binary data
        with open(speech_file_path, "rb") as audio_file:
            audio_data = audio_file.read()
        os.remove(speech_file_path)
        return audio_data


st.title('🎙️🤖Voice ChatBot🤖🎙️')  # Set the title for the Streamlit web application



user_input = st.text_input("Enter some text:")
client = OpenAI(api_key=user_input)

# Create a submit button
if st.button("Submit"):
    if user_input:


        # Use the audio_recorder function to record audio input
        audio_bytes = audio_recorder(
            text="Click to record",
            recording_color="#e8b62c",
            neutral_color="#6aa36f",
            icon_name="microphone",
            icon_size="3x",
        )

        if audio_bytes:
            # Save audio to a temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                temp_audio.write(audio_bytes)
                temp_audio_path = temp_audio.name

            # Track the time for speech-to-text processing
            start_time_stt = time.time()
            
            # 1. Convert speech to text
            converted_text_openai = speech_to_text_conversion(temp_audio_path)
            
            time_stt = time.time() - start_time_stt  # Time taken for speech-to-text
            st.write(f"Time taken for speech-to-text: {time_stt:.2f} seconds")

            # 2. Get the chatbot's response in streaming format
            response_placeholder = st.empty()  # Placeholder for streaming response
            full_response = ""

            # Measure the time taken to get the first character from LLM
            full_response=text_chat(converted_text_openai)
            response_placeholder.write(full_response)
            
            # for response_chunk in text_chat(converted_text_openai):
            #     full_response += response_chunk  # Append each chunk to the full response
            #     response_placeholder.write(full_response)  # Update UI with the current response

            # 3. Convert the full text response to audio (text-to-speech)
            start_time_tts = time.time()
            
            audio_data = text_to_speech_conversion(full_response)  # Convert the text response to audio format
            
            time_tts = time.time() - start_time_tts  # Time taken for text-to-speech
            st.write(f"Time taken for text-to-speech: {time_tts:.2f} seconds")
            st.write(f"complete time: {time.time()-start_time_stt} seconds")

            # Save the audio response to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile: 
                tmpfile.write(audio_data)
                tmpfile_path = tmpfile.name

            audio_placeholder = st.empty()  # Create a placeholder for the audio

            # Encode audio_data to base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            audio_str = f"""
                <audio autoplay>
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                </audio>
            """
            audio_placeholder.markdown(audio_str, unsafe_allow_html=True)  # Inject the audio element with autoplay
            
    else:
        st.write("Invalid")
