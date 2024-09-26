import gradio as gr
from transquiz import summarize_video, translate, url_mcqs

with gr.Blocks(theme='abidlabs/banana') as demo:
    with gr.Row():
        heading = gr.HTML("<h1 style='text-align:center; margin-top: 50px; margin-bottom: 20px; font-family:Bebas Neue; font-size: 40px; color:#126180;'>U-TRANSQUIZITOR</h1>" + "<br>")

    with gr.Tabs():
        with gr.TabItem("Translation"):
            with gr.Row():
                with gr.Column():
                    youtube_url = gr.components.Textbox(lines=1, label="Enter the URL:")
                    submit_btn = gr.components.Button("Submit")
                    output = gr.components.Textbox(lines=2, label='Captions')
        
                    submit_btn.click(fn=summarize_video, inputs=youtube_url, outputs=output)
        
                with gr.Column():
                    tgt_lang = gr.components.Dropdown(choices=[('hindi', 'hin_Deva'), ('telugu', 'tel_Telu'), ('kanada', 'kan_Knda'), ('tamil', 'tam_Taml'), ('malayalam', 'mal_Mlym')], label='Target Language', visible=True)
                    trans= gr.components.Textbox(lines=2, label='Translated Text')
                   
                    translate_btn = gr.Button('Translate')
        
                    translate_btn.click(translate, inputs=[output, tgt_lang], outputs=trans)
        with gr.TabItem("MCQ Generator"):
            gr.Interface(
                fn=url_mcqs,
                inputs=[
                    gr.Textbox(lines=1, label="Enter the URL:"),
                    gr.Number(minimum=3, label="Number of Questions")
                ],
                allow_flagging="never",
                outputs=gr.Textbox(label="Generated MCQs"),
                title="Multiple Choice Question Generator",
            )

if __name__ == "__main__":
    demo.launch(share=True, inbrowser=True)
