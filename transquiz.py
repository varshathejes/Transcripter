#!/usr/bin/env python
# coding: utf-8

# # Youtube Transcription

# In[1]:


#for summarization
from youtube_transcript_api import YouTubeTranscriptApi
import re
from transformers import pipeline

def extract_video_id(url):
    # Extract video ID from the YouTube URL
    match = re.search(r"(?:v=|\/)([a-zA-Z0-9_-]{11}).*", url)
    if match:
        return match.group(1)
    else:
        return None

def get_auto_captions(youtube_url):
    video_id = extract_video_id(youtube_url)
    transcript_text = ""
    
    if video_id:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_text = " ".join([entry['text'] for entry in transcript])
            transcript_length = len(transcript_text)
            return transcript_text, transcript_length
        except Exception as e:
            print(f"Error fetching auto-generated captions: {e}")
            return None, None
    else:
        print("Invalid YouTube URL. Please provide a valid video URL.")
        return None, None



# # Summarization

# In[2]:


summarizer = pipeline('summarization',max_length=56)


# In[3]:


def summarize(youtube_url, summarizer, max_length=56):
    # Call get_auto_captions to retrieve transcript text and length
    transcript, transcript_length = get_auto_captions(youtube_url)
    
    if transcript:
        num_iters = int(transcript_length / 1000)
        summarized_text = []

        for i in range(0, num_iters + 1):
            start = i * 1000
            end = (i + 1) * 1000
            input_text = transcript[start:end]
            #print("Input text:\n", input_text)

            out = summarizer(input_text, max_length=max_length)
            out = out[0]
            out = out['summary_text']

            #print("Summarized text:\n", out)
            summarized_text.append(out)
        
        return str(summarized_text)
    else:
        print("Failed to retrieve transcript from the YouTube video.")
        return None




# In[4]:


#youtube_url = "https://www.youtube.com/watch?v=A4OmtyaBHFE"

# Call summarize_video function
#summarized_text = summarize(youtube_url, summarizer)


# # Translation

# ## 1.Import necessary Libraries

# In[6]:


from transformers import pipeline
import warnings


# In[7]:


# Suppress warnings
warnings.filterwarnings("ignore")


# ## 2.Load the Pipeline

# In[8]:


from huggingface_hub import notebook_login

notebook_login()


# In[9]:


from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline


# In[10]:


model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-600M")
tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-600M")


# In[11]:


translator = pipeline('translation', model=model, tokenizer=tokenizer, src_lang="eng_Latn", tgt_lang='tam_Taml', max_length = 400)


# # Generating MCQs

# In[12]:


import spacy 
import random
from collections import Counter


# In[13]:


nlp = spacy.load('en_core_web_sm')


# In[29]:


def generate_mcqs(text, num_questions=5):
    # text = clean_text(text)
    if text is None:
        return []

    # Process the text with spaCy
    doc = nlp(text)

    # Extract sentences from the text
    sentences = [sent.text for sent in doc.sents]

    # Ensure that the number of questions does not exceed the number of sentences
    num_questions = min(num_questions, len(sentences))

    # Randomly select sentences to form questions
    selected_sentences = random.sample(sentences, num_questions)

    # Initialize list to store generated MCQs
    mcqs = []

    # Generate MCQs for each selected sentence
    for sentence in selected_sentences:
        # Process the sentence with spaCy
        sent_doc = nlp(sentence)

        # Extract entities (nouns) from the sentence
        nouns = [token.text for token in sent_doc if token.pos_ == "NOUN"]

        # Ensure there are enough nouns to generate MCQs
        if len(nouns) < 2:
            continue

        # Count the occurrence of each noun
        noun_counts = Counter(nouns)

        # Select the most common noun as the subject of the question
        if noun_counts:
            subject = noun_counts.most_common(1)[0][0]

            # Generate the question stem
            question_stem = sentence.replace(subject, "______")

            # Generate answer choices
            answer_choices = [subject]

            # Add some random words from the text as distractors
            distractors = list(set(nouns) - {subject})

            # Ensure there are at least three distractors
            while len(distractors) < 3:
                distractors.append("[Distractor]")  # Placeholder for missing distractors

            random.shuffle(distractors)
            for distractor in distractors[:3]:
                answer_choices.append(distractor)

            # Shuffle the answer choices
            random.shuffle(answer_choices)

            # Append the generated MCQ to the list
            correct_answer = chr(64 + answer_choices.index(subject) + 1)  # Convert index to letter
            mcqs.append((question_stem, answer_choices, correct_answer))

    return mcqs


# # Gradio User Interface

# In[33]:


def translate(text, tgt_lang):
    translator = pipeline('translation', model=model, tokenizer=tokenizer, src_lang="eng_Latn", tgt_lang=tgt_lang)
    translated_text = translator(text[:1024])[0]['translation_text']
    return translated_text


# In[32]:


def summarize_video(youtube_url):
    # Define the summarizer
    summarizer = pipeline('summarization', max_length=56)
    
    # Call summarize_video function to retrieve transcript and summarize
    summarized_text = summarize(youtube_url, summarizer)
    
    if summarized_text:
        return str(summarized_text)
    else:
        return "Failed to retrieve or summarize the video captions."


# In[43]:


def url_mcqs(youtube_url, num_questions):
    summarized_text = summarize_video(youtube_url)
    mcqs = generate_mcqs(summarized_text, num_questions)
    mcqs_with_index = [(i + 1, mcq) for i, mcq in enumerate(mcqs)]
    formatted_mcqs = []
    for question in mcqs_with_index:
        formatted_question = f"Question {question[0]}: {question[1][0]}\nOptions:\n"
        options = question[1][1]
        for i, option in enumerate(options):
            formatted_question += f"{chr(97 + i)}) {option}\n"
        formatted_question += f"Correct Answer: {question[1][2]}\n\n"
        formatted_mcqs.append(formatted_question)
    return "\n".join(formatted_mcqs)


# In[68]:


#import gradio as gr
#with gr.Blocks(theme='abidlabs/banana') as demo:
#    with gr.Row():
#        heading = gr.HTML("<h1 style='text-align:center; margin-top: 50px; margin-bottom: 20px; font-family:Bebas Neue; font-size: 40px; color:#126180;'>LANGUAGE SHUFFLE</h1>" + "<br>")

 #   with gr.Tabs():
   #     with gr.TabItem("Translation"):
  #          with gr.Row():
    #            with gr.Column():
     #               youtube_url = gr.components.Textbox(lines=1,label="Enter the URL:")
      #              submit_btn = gr.components.Button("Submit")
       #             output = gr.components.Textbox(lines=2, label='Captions')
        #
         #           submit_btn.click(fn=summarize_video, inputs=youtube_url, outputs=output)
        
        #        with gr.Column():
         #           tgt_lang = gr.components.Dropdown(choices=[('hindi', 'hin_Deva'), ('telugu', 'tel_Telu'), ('kanada', 'kan_Knda'), ('tamil', 'tam_Taml'), ('malayalam', 'mal_Mlym')], label='Target Language', visible=True)
          #          trans= gr.components.Textbox(lines=2, label='Translated Text')
           #        
           #         translate_btn = gr.Button('Translate')
        #
         #           translate_btn.click(translate, inputs=[output, tgt_lang], outputs=trans)
       # with gr.TabItem("MCQ Generator"):
        #    gr.Interface(
         #       fn=url_mcqs,
          #      inputs=[
           #         gr.Textbox(lines=1,label="Enter the URL:"),
             #       gr.Number(minimum=3, label="Number of Questions")
            #    ],
              #  allow_flagging="never",
               # outputs=gr.Textbox(label="Generated MCQs"),
                #title="Multiple Choice Question Generator",
            #)


# In[69]:


#iface = demo.launch(allowed_paths=[absolute_path], share=True, inbrowser=True)


# In[ ]:




