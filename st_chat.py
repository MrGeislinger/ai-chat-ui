import time
import os
import joblib
import streamlit as st
import google.generativeai as genai

GOOGLE_API_KEY=os.environ.get('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

new_chat_id = f'{time.time()}'

# Sidebar allows a list of past chats
with st.sidebar:
    st.write('# Past Chats')
    past_chats: dict = joblib.load('past_chats.json')
    chat_id = st.selectbox(
        label='Pick a past chat',
        options=[new_chat_id] + list(past_chats.keys()),
        format_func=lambda x: past_chats.get(x, 'New Chat'),
        placeholder='_',
    )
    # Save new chats after a message has been sent to AI
        

st.write('# Chat with AI')

# Chat history (allows to ask multiple questions)
try:
    st.session_state.messages = joblib.load(f'data/{chat_id}-st_messages')
    st.session_state.gemini_history = joblib.load(f'data/{chat_id}-gemini_messages')
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
    # Save this as a chat for later
    if chat_id not in past_chats.keys():
        # TODO: Give user a chance to name chat
        chat_title = f'NEW'
        past_chats[chat_id] = f'{chat_title}-{chat_id}'
    joblib.dump(past_chats, 'past_chats.json')
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
    joblib.dump(st.session_state.messages, f'data/{chat_id}-st_messages')
    joblib.dump(st.session_state.gemini_history, f'data/{chat_id}-gemini_messages')