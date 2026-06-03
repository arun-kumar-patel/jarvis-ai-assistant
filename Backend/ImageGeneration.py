import os
import httpx
import io
from PIL import Image
from random import randint, choice
from time import sleep, time
from dotenv import load_dotenv
from pathlib import Path
import sys

# ---------------------------------------------------------
# LOAD ENV
# ---------------------------------------------------------

load_dotenv()
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

if not HF_API_KEY:
    print("ERROR: HUGGINGFACE_API_KEY missing")
    sys.exit(1)

# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "Data"
FRONTEND_DIR = BASE_DIR.parent / "Frontend" / "Files"

DATA_DIR.mkdir(exist_ok=True)
FRONTEND_DIR.mkdir(parents=True, exist_ok=True)

print("--- Jarvis Image Generator Started ---\n")

# ---------------------------------------------------------
# USER PROMPT
# ---------------------------------------------------------

prompt = input("Prompt: ").strip()
if not prompt:
    print("ERROR: Prompt empty")
    sys.exit(1)

# ---------------------------------------------------------
# PROMPT ENHANCEMENT (REALISM LOGIC)
# ---------------------------------------------------------

style_variations = [
    "cinematic lighting",
    "dramatic shadows",
    "studio lighting",
    "volumetric lighting",
    "neon rim light",
]

quality_prompt = (
    "Ultra realistic 3D render, "
    "photorealistic, "
    "8k resolution, "
    "sharp focus, "
    "high detail textures, "
    "vibrant colors, "
    "Unreal Engine, "
    "Octane render, "
)

# ---------------------------------------------------------
# API CONFIG
# ---------------------------------------------------------

API_URL = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"

headers = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Content-Type": "application/json"
}

# ---------------------------------------------------------
# GENERATE 2 UNIQUE IMAGES
# ---------------------------------------------------------

for i in range(1, 3):
    seed = int(time()) + randint(1000, 9999)

    final_prompt = (
        f"{prompt}, {quality_prompt}, {choice(style_variations)}"
    )

    payload = {
        "inputs": final_prompt,
        "parameters": {
            "seed": seed,
            "guidance_scale": 8.5,
            "num_inference_steps": 40
        }
    }

    print(f"Generating image {i} with seed {seed}...")
    sleep(1)

    try:
        response = httpx.post(API_URL, headers=headers, json=payload, timeout=200)
    except Exception as e:
        print("API connection failed:", e)
        continue

    if response.status_code != 200:
        print("API error:", response.text)
        continue

    try:
        image = Image.open(io.BytesIO(response.content))
    except Exception:
        print("Invalid image returned")
        continue

    file_name = f"generated_{seed}.png"
    save_path = FRONTEND_DIR / file_name
    image.save(save_path)

    print("Saved:", save_path)

    if os.name == "nt":
        try:
            os.startfile(save_path)
        except:
            pass

print("\n--- Image Generation Completed Successfully ---")
