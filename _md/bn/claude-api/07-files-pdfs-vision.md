# File, PDF ও Vision

Claude text-only না। Image ও PDF দিতে পারেন এবং দেখতে বলতে পারেন। API প্রতিটাকে text-এর পাশাপাশি একটা content block হিসেবে handle করে, এবং model এগুলোকে conversation-এর অংশ হিসেবে treat করে।

## Image পাঠানো

দুইভাবে image pass করতে পারেন: base64-encoded inline, বা একটা URL যা model fetch করবে।

Base64 (local file-এর জন্য best, sensitive কিছু-এর জন্য):

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
            {"type": "text", "text": "এই chart থেকে takeaway কী?"},
        ],
    }],
)
```

URL (public image-এর জন্য best):

```python
{"type": "image", "source": {"type": "url", "url": "https://example.com/a.jpg"}}
```

Supported format: PNG, JPEG, GIF, WebP। File size reasonable রাখুন — image area দিয়ে tokenize হয়, একটা 4K photo যা ভাবেন তার চেয়ে বেশি context খায়।

## Vision কীসে ভালো

Strong case:

- **Chart ও graph।** Value পড়া, trend summarize, anomaly spot।
- **Screenshot।** একটা UI describe, একটা error message খোঁজা, table content transcribe।
- **Diagram।** Architecture diagram, flow chart, whiteboard sketch।
- **Document।** Printed বা hand-written text পড়া (OCR-এর মতো, perfect না)।
- **Photograph।** Object identify, context infer, item count।

Less strong:

- **Pixel-perfect reading।** ছোট label, dense legal text, blurry photo।
- **High precision-এ spatial reasoning।** "এই বিন্দু দুটো ঠিক কতদূরে?"
- **Specific মানুষ identify করা।** করবে না, এবং চাইতেও যাবেন না।

## PDF পাঠানো

PDF নিজের content block type হিসেবে আসে। Claude ভেতরের text ও image — দুটোই পড়তে পারে।

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
            {"type": "text", "text": "Recommendation section summarize করো।"},
        ],
    }],
)
```

একটা Files API-ও আছে — larger PDF একবার store করে অনেক call-এ reference করার জন্য — যখন একই document নিয়ে বারবার জিজ্ঞেস করা হয় তখন useful। একবার upload করেন, একটা `file_id` পান, এবং প্রতিবার byte না পাঠিয়ে সেই ID reference করেন।

## এক turn-এ text + image (+ PDF) combine

একটা single user message-এ যেকোনো সংখ্যক block mix করতে পারেন। একটা common pattern:

```python
{"role": "user", "content": [
    {"type": "image", "source": {...}},          # screenshot
    {"type": "image", "source": {...}},          # before/after
    {"type": "document", "source": {...}},       # design spec
    {"type": "text", "text": "এই screenshot-এ implementation-কে "
                              "spec-এর সাথে compare করো। "
                              "Discrepancy list করো।"}
]}
```

"Review my work" feature এভাবে বানাবেন। Model এই সব একটা coherent message হিসেবে পড়ে।

## Output এখনো শুধু text

Model image ও PDF *input* হিসেবে নেয় কিন্তু শুধু *text* (বা tool call) produce করে। Image generate করে না। Image generation দরকার হলে — Claude-কে একটা image model-এর সাথে combine করবেন।

## Token math

Image ও PDF real token খরচ করে। Rough rule:

- একটা image resolution ও complexity দিয়ে sized। একটা typical screenshot-এর জন্য roughly 1,000–3,000 token expect করুন।
- PDF per page charge — complex layout plain text-এর চেয়ে বেশি cost।

High volume process করলে — প্রতি customer-এর invoice, প্রতি support ticket-এর screenshot — early-তে cost per item measure করুন। Economics দ্রুত shift হতে পারে।

## একটা practical tip

একটা image সম্পর্কে জিজ্ঞেস করার সময় — প্রথমে question frame করুন, *তারপর* image। "এই screenshot দেখো এবং error message খুঁজে বের করো" — pixel parse করার আগে model-কে right mode-এ রাখে। Prompt ছাড়া bare image — model guess করে আপনি কী চান।
