#!/usr/bin/env python3
"""Render the council member portraits from prompts.json.

Reads the 15 prompts and writes one PNG per prompt into --out.
Stdlib only. Bring your own API key.

    export OPENAI_API_KEY=sk-...
    ./generate.py --provider openai

    export GEMINI_API_KEY=...
    ./generate.py --provider gemini

Useful flags:
    --only cto                 # one member, all three states
    --only cto-thinking        # one image
    --dry-run                  # print what would be sent, call nothing
    --force                    # re-render images that already exist
"""

import argparse
import base64
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent

PROVIDERS = {
    # Model ids move fast; override with --model if your account has a different one.
    "openai": {"env": "OPENAI_API_KEY", "model": "gpt-image-1"},
    "gemini": {"env": "GEMINI_API_KEY", "model": "gemini-2.5-flash-image"},
}


def post(url, payload, headers, timeout=180):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def render_openai(prompt, key, model, size, quality=None):
    payload = {"model": model, "prompt": prompt, "size": size, "n": 1}
    if quality:
        payload["quality"] = quality
    body = post(
        "https://api.openai.com/v1/images/generations",
        payload,
        {"Authorization": f"Bearer {key}"},
    )
    datum = body["data"][0]
    # gpt-image-1 always returns base64; the dall-e-* models return a URL by default.
    if "b64_json" in datum:
        return base64.b64decode(datum["b64_json"])
    with urllib.request.urlopen(datum["url"], timeout=120) as resp:
        return resp.read()


def render_gemini(prompt, key, model, size, quality=None):
    body = post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        {"contents": [{"parts": [{"text": prompt}]}]},
        {"x-goog-api-key": key},
    )
    for part in body["candidates"][0]["content"]["parts"]:
        if "inlineData" in part:
            return base64.b64decode(part["inlineData"]["data"])
    raise RuntimeError("no image part in Gemini response")


RENDERERS = {"openai": render_openai, "gemini": render_gemini}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--provider", choices=sorted(PROVIDERS), default="openai")
    ap.add_argument("--model", help="override the provider's default model id")
    ap.add_argument("--out", type=pathlib.Path, default=HERE / "png")
    ap.add_argument("--prompts", type=pathlib.Path, default=HERE / "prompts.json")
    ap.add_argument("--size", default="1024x1024", help="openai only")
    ap.add_argument("--quality", choices=["low", "medium", "high", "auto"],
                    help="openai only; omitted lets the model decide. Drives cost.")
    ap.add_argument("--only", help="member slug or full image id")
    ap.add_argument("--force", action="store_true", help="overwrite existing files")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--retries", type=int, default=3)
    args = ap.parse_args()

    images = json.loads(args.prompts.read_text())["images"]
    if args.only:
        images = [i for i in images
                  if i["id"] == args.only or i["member_slug"] == args.only]
        if not images:
            sys.exit(f"--only {args.only!r} matched nothing")

    spec = PROVIDERS[args.provider]
    model = args.model or spec["model"]

    key = os.environ.get(spec["env"])
    if not key and not args.dry_run:
        sys.exit(f"{spec['env']} is not set")

    args.out.mkdir(parents=True, exist_ok=True)
    render = RENDERERS[args.provider]
    failed = []

    for n, img in enumerate(images, 1):
        dest = args.out / img["filename"]
        tag = f"[{n}/{len(images)}] {img['id']}"

        if dest.exists() and not args.force:
            print(f"{tag}: exists, skipping (--force to redo)")
            continue

        if args.dry_run:
            print(f"{tag} -> {dest}\n  {img['prompt']}\n")
            continue

        for attempt in range(1, args.retries + 1):
            try:
                dest.write_bytes(
                    render(img["prompt"], key, model, args.size, args.quality))
                print(f"{tag}: wrote {dest} ({dest.stat().st_size // 1024} KB)")
                break
            except (urllib.error.URLError, KeyError, IndexError, RuntimeError) as e:
                detail = ""
                if isinstance(e, urllib.error.HTTPError):
                    detail = f" {e.read().decode(errors='replace')[:300]}"
                if attempt == args.retries:
                    print(f"{tag}: FAILED after {attempt} attempts: {e}{detail}",
                          file=sys.stderr)
                    failed.append(img["id"])
                else:
                    backoff = 2 ** attempt
                    print(f"{tag}: attempt {attempt} failed ({e}{detail}); "
                          f"retrying in {backoff}s", file=sys.stderr)
                    time.sleep(backoff)

    if failed:
        sys.exit(f"\n{len(failed)} image(s) failed: {', '.join(failed)}")


if __name__ == "__main__":
    main()
