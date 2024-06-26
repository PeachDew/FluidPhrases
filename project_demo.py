import streamlit as st
import time
import json
from h2oconvo_PUBLIC import get_conversation
from random import randint as rint

st.set_page_config("Fluid Phrases",
                   "💧",)

with open("prompt_template_ids.json", "r") as file:
    all_prompt_template_ids = json.load(file)

user_emojis = "🐶 🐱 🐭 🐹 🐰 🦊 🐻 🐼 🐻‍❄️ 🐨 🐯 🦁 🐮 🐷 🐸 🐵 🐔 🐧 🐦 🐤 "

un_text_input_container = st.empty()
user = un_text_input_container.text_input("Hi there! What's your name?")
if user != "":
    st.session_state['user_name'] = user
    un_text_input_container.empty()

if 'user_name' in st.session_state:
    un_icon_input_container = st.empty()
    user_icon = un_icon_input_container.selectbox("Select your icon!",
                                        [e for e in user_emojis],
                                        None)
    if user_icon:
        st.session_state['user_icon'] = user_icon
        un_icon_input_container.empty()



personalities = [
    "Comedian 🤡",
    "Educator 🎓",
    "Lawyer ⚖️",
    "Philosopher 🤔",
    "Politician 🎤",
    "Rapper 🔥",
]

MODEL_ID_TO_MODEL = {}
SPINNER_TEXTS = [
"Working feverishly... 🔥",
"Crunching computations... 🧮",
"Extracting the archives of ancient wisdom... 🏛️",
"Awakening the elder scripts... 📜",
"Harnessing graphics power... 🖥️",
"Communing with the machine spirits... 💻",
"Reticulating splines... ⚙️",
"Quantum decrypting... 🔐",
"Bending the laws of physics... 🌌",
"Brewing hot codez... ☕",
"Flushing the interwebz buffer... 🌐",
"Asking the online magic 8-ball... 🎱",
"Activating temporal displacement field... ⌛",
"Waiting for the hair of the dog to bark... 🐶"
]

affirming_messages = [
"You got it!",
"Affirmative!",
"Roger that!",
"Loud and clear!",
"Understood!",
"Copy that!",
"Wilco!",
"No problemo!",
"Consider it done!",
"Aye aye, captain!"
]

def stream_str(sent):
    for word in sent.split(" "):
        if len(word) > 5:
            time.sleep(0.02)
        else: 
            time.sleep(0.01)
        yield word + " "

if 'text_history' not in st.session_state:
    st.session_state['text_history']=[]

def reset_convo():
    if 'conversation' in st.session_state:
        if 'past_conversations' not in st.session_state:
            st.session_state['past_conversations'] = []
        st.session_state.past_conversations.append(dict(conversation=st.session_state['conversation'], 
                                                        person_array=st.session_state['person_array']))
        del st.session_state['conversation']
        del st.session_state['person_array']
CHAT_ORDER = [0,1,0,1,0]
if ('user_name' in st.session_state) and ('user_icon' in st.session_state):
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Tom's Personality")
        personality_1 = st.selectbox("Tom's Personality:",
                                    personalities,
                                    label_visibility="hidden",
                                    on_change=reset_convo)
        MODEL_ID_TO_MODEL[0] = personality_1.split()

    with c2:
        st.markdown("### Mike's Personality")
        personality_2 = st.selectbox("Mike's Personality:",
                                    personalities,
                                    label_visibility="hidden",
                                    index=1,
                                    on_change=reset_convo)
        MODEL_ID_TO_MODEL[1] = personality_2.split()

    with st.sidebar:
        st.info(f"Hi {st.session_state.user_name}{st.session_state.user_icon}!")
        topic_prompt = st.chat_input("Enter a conversation topic.")

    if topic_prompt:
        st.session_state['topic'] = topic_prompt
        reset_convo()
    
    if 'topic' not in st.session_state:
        st.markdown(":orange[Topic not set, enter one on the right!]")

    SEED = 42
    CHAT_ORDER = [0,1,0,1,0]
    if 'topic' in st.session_state:
        st.markdown("##### Current Topic: ")
        st.markdown(f"#### :orange[{st.session_state.topic}]")

        with st.expander("Optional Settings"):
            os1, os2 = st.columns(2)
            with os1:
                chat_order_input = st.text_input("Conversation sequence, 0 for Tom, 1 for Mike.",
                                                placeholder="01010")
                if chat_order_input:
                    reset_convo()
                    if "," in chat_order_input:
                        chat_order = [int(co.strip()) if co.strip().isdigit() else co.strip() for co in chat_order_input.split(",") ]
                        valid_co = all((i==0 or i==1) for i in chat_order)
                    else:
                        valid_co = True
                        chat_order = []
                        for ch in chat_order_input:
                            if ch == "0":
                                chat_order.append(0)
                            elif ch == "1":
                                chat_order.append(1)
                            else: 
                                valid_co = False
                                break
                        
                    if not valid_co: 
                        st.markdown(":red[Invalid Chat Order is entered, using default: 01010]")
                        CHAT_ORDER = [0,1,0,1,0]
                    else: 
                        CHAT_ORDER = chat_order
                        st.markdown(f":green[{affirming_messages[rint(0,len(affirming_messages)-1)]} Current order: {CHAT_ORDER}]")
            with os2:
                seed_input = st.text_input("Seed", placeholder="42")
                if seed_input:
                    reset_convo()
                    if seed_input.isdigit():
                        SEED = int(seed_input)
                        st.markdown(f":green[{affirming_messages[rint(0,len(affirming_messages)-1)]} Seed set to: {SEED}]")
                    else: 
                        SEED = 42
                        st.markdown(":red[Invalid seed entered, using default: 42]")

                

        if st.button("Generate Conversation"):
            with st.spinner(SPINNER_TEXTS[rint(0,len(SPINNER_TEXTS)-1)]):
                reset_convo()
                conversation, person_array = get_conversation(all_prompt_template_ids=all_prompt_template_ids,
                                                              topic=st.session_state.topic,
                                                              conversation_sequence=CHAT_ORDER,
                                                              person_0 = MODEL_ID_TO_MODEL[0][0],
                                                              person_1 = MODEL_ID_TO_MODEL[1][0],
                                                              seed = SEED
                                                              )
                st.session_state['conversation'] = conversation
                st.session_state['person_array'] = person_array

        curr_convo, past_convo = st.tabs(["Current Chat", "Past Chats"],)
        with past_convo:
            if "past_conversations" in st.session_state:
                for i, convopa in enumerate(st.session_state.past_conversations):
                    convo = convopa['conversation']
                    pa = convopa['person_array']
                    with st.expander(f"Conversation {i}"):
                        for j, c in enumerate(convo):
                            speaker_id, content = c
                            speaker = pa[speaker_id][1]
                            m = MODEL_ID_TO_MODEL[speaker_id]
                            if speaker_id == 0:
                                with st.container(border=True):
                                    with st.chat_message(m[1]):
                                        st.markdown(content)
                            else:
                                with st.chat_message(m[1]):
                                    st.markdown(content)

        with curr_convo:
            if "conversation" in st.session_state:
                for i, c in enumerate(st.session_state.conversation):
                    speaker_id, content = c
                    speaker = st.session_state.person_array[speaker_id][1]
                    m = MODEL_ID_TO_MODEL[speaker_id]

                    if speaker_id == 0:
                        with st.container(border=True):
                            with st.chat_message(m[1]):
                                # st.write(m[0])
                                st.write_stream(stream_str(content))
                    else:
                        with st.chat_message(m[1]):
                            # st.write(m[0])
                            st.write_stream(stream_str(content))
        


        

    

