
from h2ogpte import H2OGPTE
import streamlit as st
GLOBAL_KEY = st.secrets['GLOBAL_KEY']
COLLECTION_KEY_1 = st.secrets['COLLECTION_KEY_1']
COLLECTION_KEY_2 = st.secrets['COLLECTION_KEY_2']


def get_conversation(
        all_prompt_template_ids,
        person_0 = "Comedian",
        person_1 = "Philosopher",
        person_0_name = "Tom",
        person_1_name = "Mike",
        topic = "Alcohol",
        agreeability = -2,
        conversation_sequence = [0,1,0,1,0],
        seed = 42
            ):
    
    general_client = H2OGPTE(
        address='https://h2ogpte.genai.h2o.ai',
        api_key=GLOBAL_KEY,)
    client_0 = H2OGPTE(
        address='https://h2ogpte.genai.h2o.ai',
        api_key=COLLECTION_KEY_1,)
    client_1 = H2OGPTE(
        address='https://h2ogpte.genai.h2o.ai',
        api_key=COLLECTION_KEY_2,)
    
    c0_chat_session_id = client_0.create_chat_session_on_default_collection()
    c1_chat_session_id = client_1.create_chat_session_on_default_collection()

    ptid_0 = all_prompt_template_ids[person_0]
    ptid_1 = all_prompt_template_ids[person_1]
    
    c0_prompted_chat_session_id = general_client.set_chat_session_prompt_template(chat_session_id=c0_chat_session_id,
                                                    prompt_template_id=ptid_0)

    c1_prompted_chat_session_id = general_client.set_chat_session_prompt_template(chat_session_id=c1_chat_session_id,
                                                    prompt_template_id=ptid_1)
    
    do_not_reveal_prompt = '''
    Ground Rules for this conversation:
    1) Try to disagree to make the conversation more exciting.
    2) Do not reveal that you are obtaining information from external sources. 
    3) I want you to synthesize the information and generate insights as if the knowledge and perspectives were your own. 
    4) Avoid phrases like 'according to the text' or 'the author states.' 
    5) Express ideas directly using your own voice and writing style.
    '''

    agreeability_prompt = f"For your reply, take an agreeableness level of {agreeability}, where 1 is highly disagreeable/critical and 10 is highly agreeable/affirming."

    #! TODO: INTEGRATE WITH OTHER DEFAULT PROMPT/RETRIEVE FROM PROMPT TEMPLATES.JSON
    conver_0 = f"You are {person_0_name} the {person_0} conversing with {person_1_name} the {person_1}."
    conver_1 = f"You are {person_1_name} the {person_1} conversing with {person_0_name} the {person_0}."

    topic_prompt = f'''
    What are your thoughts on [{topic}]? 
    {do_not_reveal_prompt}
    Start us off with with 2 sentences, including a question :) '''

    reply_prompt = f'''You are currently engaged in conversation. 
    {do_not_reveal_prompt}
    Reply with a MAXIMUM of TWO sentences: 1 conversational sentence, and include a question for them if appropriate (Question must still be relevant to [{topic}]). This is what they said: '''

    same_speaker_prompt = '''Tell them ONE SHORT additional sentence that strengthens your argument further.'''
    wrap_up_prompt = '''You are wrapping up the conversation. Provide a few closing words to your partner, not using more than 3 sentences. This was the last thing they said: '''
    
    llm_args = {
        # "temperature" : 1,
        "seed" : seed, 
        # "min_max_new_tokens":0,
    }

    conversation = []
    
    with client_0.connect(c0_prompted_chat_session_id) as session_0:
        with client_1.connect(c1_prompted_chat_session_id) as session_1:
            person_array = [[session_0, person_0, conver_0], 
                            [session_1, person_1, conver_1]]

            previous_speaker = None
            previous_content = None
            for i, subject in enumerate(conversation_sequence):
                client_array = person_array[subject]
                if i == 0: # start conversation prompt
                    reply = client_array[0].query(
                        client_array[2]+topic_prompt, 
                        timeout=120,
                        # system_prompt=client_array[2],
                        # pre_prompt_query=common_pre_prompt_query,
                        # prompt_query=common_prompt_query,
                        # llm_args=llm_args
                    )
                elif i == (len(conversation_sequence) - 1): # Last speaker
                    reply = client_array[0].query(
                        client_array[2]+wrap_up_prompt+previous_content, 
                        timeout=120,
                    )

                elif previous_speaker == subject: # same speaker continue speaking prompt
                    reply = client_array[0].query(
                        client_array[2]+same_speaker_prompt+previous_content, 
                        timeout=120,
                        # system_prompt=philosopher_prompt, 
                        # pre_prompt_query=common_pre_prompt_query,
                        # prompt_query=common_prompt_query,
                        llm_args=llm_args
                    )
                
                else: # reply to partner prompt
                    reply = client_array[0].query(
                        client_array[2]+reply_prompt+previous_content, 
                        timeout=120,
                        # system_prompt=philosopher_prompt,
                        # pre_prompt_query=common_pre_prompt_query,
                        # prompt_query=common_prompt_query,
                        llm_args=llm_args
                    )
                
                if previous_speaker == subject: # same speaker continue speaking prompt
                    previous_speaker = subject
                    conversation.append([previous_speaker, reply.content])
                    previous_content += " " + reply.content
                else:
                    previous_content = reply.content
                    previous_speaker = subject
                    conversation.append([previous_speaker, previous_content])

                
    return conversation, person_array