"""
app.py — Milestone 5b: Gradio Interface

Run with:
    python app.py

Then open:
    http://localhost:7860
"""

import gradio as gr
from query import ask

# ── Example questions shown in the UI ────────────────────────────────────────

EXAMPLES = [
    "What was NVIDIA's total revenue for fiscal year 2025?",
    "What does Intel's 2025 10-K identify as its primary competitive risks?",
    "How did Apple's iPhone revenue change between its 2024 and 2025 10-K filings?",
    "According to SpaceX's S-1, what is the intended use of proceeds from the offering?",
    "What was Amazon's AWS segment operating income for fiscal year 2025?",
]


# ── Handler ───────────────────────────────────────────────────────────────────

def handle_query(question: str):
    """Called by Gradio on every button click or Enter keypress."""
    question = question.strip()
    if not question:
        return "Please enter a question.", ""

    result  = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources or "No sources retrieved."


# ── UI layout ─────────────────────────────────────────────────────────────────

with gr.Blocks(title="SEC Filings Q&A") as demo:
    gr.Markdown(
        """
        # SEC Filings Q&A
        Ask questions about 10-K and S-1 filings from Apple, Amazon, NVIDIA, Tesla,
        SpaceX, and more. Answers are grounded — the model only uses the retrieved
        document excerpts and will not guess from outside knowledge.
        """
    )

    with gr.Row():
        with gr.Column(scale=3):
            question_box = gr.Textbox(
                label="Your question",
                placeholder="e.g. What was NVIDIA's total revenue for fiscal year 2025?",
                lines=2,
            )
            ask_btn = gr.Button("Ask", variant="primary")

    with gr.Row():
        answer_box = gr.Textbox(label="Answer", lines=10, interactive=False)

    with gr.Row():
        sources_box = gr.Textbox(label="Retrieved from", lines=4, interactive=False)

    gr.Examples(
        examples=EXAMPLES,
        inputs=question_box,
        label="Example questions",
    )

    # wire button click and Enter key
    ask_btn.click(handle_query, inputs=question_box, outputs=[answer_box, sources_box])
    question_box.submit(handle_query, inputs=question_box, outputs=[answer_box, sources_box])


if __name__ == "__main__":
    demo.launch()
