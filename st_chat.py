import time
import os
import joblib
import streamlit as st
import google.generativeai as genai

GOOGLE_API_KEY=os.environ.get('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)


st.write('# Chat with AI')

# Chat history (allows to ask multiple questions)
if 'messages' not in st.session_state:
    try:
        st.session_state.messages = joblib.load('temp_st_messages')
        st.session_state.gemini_history = joblib.load('temp_gemini_messages')
        print('old cache')
    except:
        st.session_state.messages = []
        st.session_state.gemini_history = []
        print('new_cache made')
    st.session_state.model = genai.GenerativeModel('gemini-pro')
    st.session_state.chat = st.session_state.model.start_chat(
        history=st.session_state.gemini_history,
    )

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])


# React to user input
if prompt := st.chat_input('Your message here...'):
    # Display user message in chat message container
    with st.chat_message('user'):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append(
        dict(
            role='user',
            content=prompt,
        )
    )

    ## Send message to AI
    response = st.session_state.chat.send_message(
        prompt,
        stream=True,
    )
    # Display assistant response in chat message container
    with st.chat_message(
        name='ai',
        # avatar='✨',
    ):
        message_placeholder = st.empty()
        full_response = ''
        assistant_response = response
        # Streams in a chunk at a time
        for chunk in response:
            # Simulate stream of chunk
            # TODO: Chunk missing `text` if API stops mid-stream ("safety"?)
            for ch in chunk.text.split(' '):
                full_response += ch + ' '
                time.sleep(0.05)
                # Rewrites with a cursor at end
                message_placeholder.write(full_response + '▌')
        # Write full message with placeholder
        message_placeholder.write(full_response)

    # Add assistant response to chat history
    st.session_state.messages.append(
        dict(
            role=st.session_state.chat.history[-1].role,
            content=st.session_state.chat.history[-1].parts[0].text,
        )
    )
    st.session_state.gemini_history = st.session_state.chat.history
    # Save to file
    joblib.dump(st.session_state.messages, 'temp_st_messages')
    joblib.dump(st.session_state.gemini_history, 'temp_gemini_messages')