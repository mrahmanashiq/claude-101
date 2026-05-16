# Files, PDFs, and Vision

Claude isn't text-only. You can hand it images and PDFs and ask it to look at them. The API handles each as a content block alongside your text, and the model treats them as part of the conversation.

## Sending an image

Two ways to pass an image: base64-encoded inline, or a URL the model fetches.

Base64 (best for local files, anything sensitive):

```python
import base64
from pathlib import Path

img_data = base64.standard_b64encode(Path("chart.png").read_bytes()).decode()

resp = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": img_data,
                },
            },
            {"type": "text", "text": "What's the takeaway from this chart?"},
        ],
    }],
)
```

URL (best for public images):

```python
{"type": "image", "source": {"type": "url", "url": "https://example.com/a.jpg"}}
```

Supported formats: PNG, JPEG, GIF, WebP. Keep file sizes reasonable — images are tokenized by area, and a 4K photo eats more context than you'd think.

## What vision is good at

Strong cases:

- **Charts and graphs.** Read values, summarize trends, spot anomalies.
- **Screenshots.** Describe a UI, find an error message, transcribe table content.
- **Diagrams.** Architecture diagrams, flow charts, whiteboard sketches.
- **Documents.** Read printed or hand-written text (OCR-like, though not perfect).
- **Photographs.** Identify objects, infer context, count items.

Less strong:

- **Pixel-perfect reading.** Tiny labels, dense legal text, blurry photos.
- **Spatial reasoning at high precision.** "Exactly how far apart are these dots?"
- **Identifying specific people.** Won't, and you shouldn't ask.

## Sending a PDF

PDFs come in as their own content block type. Claude can read both the text and the images inside.

```python
import base64
from pathlib import Path

pdf_data = base64.standard_b64encode(Path("report.pdf").read_bytes()).decode()

resp = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=2048,
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "document",
                "source": {
                    "type": "base64",
                    "media_type": "application/pdf",
                    "data": pdf_data,
                },
            },
            {"type": "text", "text": "Summarize the recommendations section."},
        ],
    }],
)
```

There's also a Files API for storing larger PDFs once and referencing them across many calls — useful when the same document gets asked about repeatedly. You upload it once, get back a `file_id`, and reference that ID instead of re-sending the bytes every time.

## Combining text and image (and PDF) in one turn

You can mix any number of blocks in a single user message. A common pattern:

```python
{"role": "user", "content": [
    {"type": "image", "source": {...}},          # screenshot
    {"type": "image", "source": {...}},          # before/after
    {"type": "document", "source": {...}},       # the design spec
    {"type": "text", "text": "Compare the implementation in these "
                              "screenshots against the spec. List "
                              "discrepancies."}
]}
```

This is how you build "review my work" features. The model reads all of it as one coherent message.

## Output is still just text

The model takes images and PDFs as *input* but only produces *text* (or tool calls). It doesn't generate images. If you need image generation, you'd combine Claude with an image model.

## Token math

Images and PDFs cost real tokens. Rough rules:

- An image is sized by resolution and complexity. Expect roughly 1,000–3,000 tokens for a typical screenshot.
- A PDF charges per page; complex layouts cost more than plain text.

If you're processing high volumes — every customer's invoice, every support ticket screenshot — measure cost per item early. The economics can shift fast.

## A practical tip

When asking about an image, frame the question first, *then* the image. "Look at this screenshot and find the error message" puts the model in the right mode before it parses pixels. Bare image with no prompt makes it guess what you want.
