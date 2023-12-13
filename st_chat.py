import time
import os
import streamlit as st
import google.generativeai as genai

GOOGLE_API_KEY=os.environ.get('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')


st.write('# Chat with AI')

# Chat history (allows to ask multiple questions)
if 'messages' not in st.session_state:
    st.session_state.messages = []
    st.session_state.gemini_history = []
    print('new_cache made')

chat = model.start_chat(
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
    response = chat.send_message(
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
            print(chunk.parts)
            if chunk.parts:
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
            role=chat.history[-1].role,
            content=chat.history[-1].parts[0].text,
        )
    )
    # Save chat history to ask multiple questions
    st.session_state.gemini_history = chat.history