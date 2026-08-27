"""Quick contract check for frontend API shape."""
import json
import urllib.request
from pathlib import Path

img = Path(__file__).resolve().parents[2] / "sample_images" / "acceptable" / "acceptable_01.jpg"
raw = img.read_bytes()
boundary = "----bound"
body = (
    f"--{boundary}\r\n"
    'Content-Disposition: form-data; name="file"; filename="a.jpg"\r\n'
    "Content-Type: image/jpeg\r\n\r\n"
).encode() + raw + f"\r\n--{boundary}--\r\n".encode()

req = urllib.request.Request(
    "http://localhost:8000/analyze",
    data=body,
    method="POST",
    headers={
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Origin": "http://localhost:3000",
    },
)
data = json.loads(urllib.request.urlopen(req).read())
assert {"id", "quality_score", "quality_label", "issues", "image_stats"} <= set(data)
assert isinstance(data["id"], int)

hist = json.loads(
    urllib.request.urlopen(
        urllib.request.Request(
            "http://localhost:8000/history",
            headers={"Origin": "http://localhost:3000"},
        )
    ).read()
)
assert isinstance(hist, list) and hist
assert {"id", "quality_label", "quality_score", "created_at", "thumbnail_url"} <= set(hist[0])

one = json.loads(urllib.request.urlopen(f"http://localhost:8000/results/{data['id']}").read())
assert one["id"] == data["id"]
print("contract OK", data["quality_label"], data["quality_score"], "history", len(hist))
