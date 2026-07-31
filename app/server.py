"""Serve the text generator through Gradio."""

import branding
import gradio as gr
from generator import TextGenerator

MODEL_DIR = "model"


def build_demo(generator: TextGenerator) -> gr.Interface:
    return gr.Interface(
        fn=generator.generate,
        inputs=gr.Textbox(
            lines=6,
            label="Prompt",
            placeholder="Enter text for the model to continue or answer…",
        ),
        outputs=[
            gr.Textbox(lines=10, label="Generated text"),
            gr.Markdown(),
        ],
        title="Edge Text Generator",
        description="Enter a prompt and click **Generate** to see the model's response.",
        submit_btn="Generate",
        clear_btn=None,
        flagging_mode="never",
    )


def main() -> None:
    demo = build_demo(TextGenerator(MODEL_DIR))
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        theme=branding.theme(),
    )


if __name__ == "__main__":
    main()
