from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import textwrap
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont, ImageOps
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "replicalab" / "outputs" / "demo_video"
SCREENS_DIR = OUTPUT_DIR / "screens"
SLIDES_DIR = OUTPUT_DIR / "slides"
AUDIO_DIR = OUTPUT_DIR / "audio"
TEXT_DIR = OUTPUT_DIR / "text"
CHROME_PATH = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
BASE_URL = "http://127.0.0.1:7860"
ONBOARDING_KEY = "replicalab-onboarded"
THEME_KEY = "replicalab-theme"
VIDEO_SIZE = (1920, 1080)
NARRATION = (
    "ReplicaLab starts from a research paper and turns it into a seeded replication benchmark. "
    "The Scientist proposes a protocol, the Lab Manager enforces budget, tools, and scheduling, "
    "and a deterministic Judge scores rigor, feasibility, and fidelity. In our first scenario, "
    "the agents agree immediately, so the paper looks replicable in this lab. In the second scenario, "
    "they negotiate across all six rounds, which creates a rich reinforcement learning signal. "
    "In the third, they never resolve the blockers, so the system rejects the paper for the current setup. "
    "Because every outcome is scored deterministically, we can train the Scientist with Unsloth and TRL, "
    "compare baseline versus trained runs, inspect real logs, and see exactly where more learning is still needed. "
    "The training page is intentionally honest: the live run reached positive rewards, but the held-out compare still "
    "shows that the trained Scientist has not beaten the deterministic baseline yet."
)


@dataclass(frozen=True)
class Scene:
    id: str
    url: str
    title: str
    subtitle: str
    duration: float
    expected_text: str | None = None


SCENES: tuple[Scene, ...] = (
    Scene(
        id="dashboard",
        url=f"{BASE_URL}/",
        title="Paper to benchmark",
        subtitle="ReplicaLab turns a paper into a seeded replication benchmark.",
        duration=8.0,
        expected_text="ReplicaLab",
    ),
    Scene(
        id="fast_agreement",
        url=f"{BASE_URL}/episode?template=ml_benchmark&difficulty=medium&seed=101&demo=1&autoplay=1&demoCase=fast-agreement",
        title="Scenario 1: first-round agreement",
        subtitle="The agents converge quickly and the paper scores as a strong replication candidate.",
        duration=11.0,
        expected_text="Completed: First-round agreement",
    ),
    Scene(
        id="learning_opportunity",
        url=f"{BASE_URL}/episode?template=ml_benchmark&difficulty=medium&seed=202&demo=1&autoplay=1&demoCase=learning-opportunity",
        title="Scenario 2: multi-round learning",
        subtitle="Six rounds of disagreement create a rich RL signal before the final acceptance.",
        duration=13.0,
        expected_text="Completed: Multi-round learning opportunity",
    ),
    Scene(
        id="no_agreement",
        url=f"{BASE_URL}/episode?template=ml_benchmark&difficulty=medium&seed=303&demo=1&autoplay=1&demoCase=no-agreement",
        title="Scenario 3: no agreement",
        subtitle="The blockers remain unresolved, so the system rejects replication for this setup.",
        duration=12.0,
        expected_text="Completed: No agreement reached",
    ),
    Scene(
        id="training",
        url=f"{BASE_URL}/training",
        title="Artifact-backed training review",
        subtitle="The training page shows real checkpoints, real compare metrics, and what still needs improvement.",
        duration=16.0,
        expected_text="Training Logs And Analysis",
    ),
)


def load_env_value(key: str) -> str | None:
    if os.getenv(key):
        return os.getenv(key)

    for path in (ROOT / ".env", ROOT / ".env.local", ROOT / "frontend" / ".env"):
        if not path.exists():
            continue
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            env_key, env_value = line.split("=", 1)
            if env_key.strip() == key:
                return env_value.strip().strip('"').strip("'")
    return None


def ensure_backend() -> None:
    try:
        with urllib.request.urlopen(f"{BASE_URL}/health", timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception as exc:  # pragma: no cover - user-facing failure
        raise RuntimeError(
            f"Backend unavailable at {BASE_URL}. Start it with "
            "\"python -m uvicorn server.app:app --host 127.0.0.1 --port 7860\"."
        ) from exc
    if data.get("status") != "ok":
        raise RuntimeError(f"Unexpected backend health payload: {data}")


def ensure_output_dirs() -> None:
    for directory in (OUTPUT_DIR, SCREENS_DIR, SLIDES_DIR, AUDIO_DIR, TEXT_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path(r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf"),
        Path(r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def pick_voice(api_key: str, preferred_voice_id: str | None) -> str:
    if preferred_voice_id:
        return preferred_voice_id

    request = urllib.request.Request(
        "https://api.elevenlabs.io/v1/voices",
        headers={"xi-api-key": api_key, "Accept": "application/json"},
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))

    voices = payload.get("voices", [])
    if not voices:
        raise RuntimeError("ElevenLabs returned no voices for the current API key.")

    preferred_names = ("Rachel", "Aria", "Sarah", "Charlie", "George")
    for name in preferred_names:
        for voice in voices:
            if voice.get("name") == name and voice.get("voice_id"):
                return voice["voice_id"]
    for voice in voices:
        if voice.get("voice_id"):
            return voice["voice_id"]
    raise RuntimeError("No usable ElevenLabs voice_id found.")


def synthesize_voiceover(api_key: str, voice_id: str, text: str, output_path: Path) -> None:
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.4,
            "similarity_boost": 0.8,
            "style": 0.25,
            "use_speaker_boost": True,
        },
    }
    body = json.dumps(payload).encode("utf-8")
    urls = (
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_44100_128",
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
    )

    last_error: Exception | None = None
    for url in urls:
        request = urllib.request.Request(
            url,
            data=body,
            headers={
                "xi-api-key": api_key,
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                audio = response.read()
            if not audio:
                raise RuntimeError("ElevenLabs returned an empty audio payload.")
            output_path.write_bytes(audio)
            return
        except Exception as exc:  # pragma: no cover - fallback path
            last_error = exc
    raise RuntimeError(f"Failed to synthesize ElevenLabs audio: {last_error}")


def build_driver() -> webdriver.Chrome:
    options = Options()
    options.binary_location = str(CHROME_PATH)
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1600,1200")
    options.add_argument("--force-device-scale-factor=1")
    options.add_argument("--hide-scrollbars")
    options.add_argument("--mute-audio")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument(f"--user-data-dir={OUTPUT_DIR / 'chrome_profile'}")
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1600, 1200)
    return driver


def capture_screens() -> list[Path]:
    driver = build_driver()
    files: list[Path] = []
    try:
        driver.get(BASE_URL)
        WebDriverWait(driver, 20).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        driver.execute_script(
            "window.localStorage.setItem(arguments[0], '1');"
            "window.localStorage.setItem(arguments[1], 'light');",
            ONBOARDING_KEY,
            THEME_KEY,
        )

        for scene in SCENES:
            driver.get(scene.url)
            WebDriverWait(driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            if scene.expected_text:
                try:
                    WebDriverWait(driver, 35).until(
                        lambda d: scene.expected_text in d.page_source
                    )
                except TimeoutException:
                    pass
            time.sleep(1.5)
            output = SCREENS_DIR / f"{scene.id}.png"
            driver.save_screenshot(str(output))
            files.append(output)
    finally:
        driver.quit()
    return files


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=font) <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def create_slides() -> list[Path]:
    title_font = get_font(46, bold=True)
    subtitle_font = get_font(28)
    badge_font = get_font(24, bold=True)
    output_paths: list[Path] = []

    for scene in SCENES:
        raw_image = Image.open(SCREENS_DIR / f"{scene.id}.png").convert("RGB")
        canvas = ImageOps.fit(raw_image, VIDEO_SIZE, method=Image.Resampling.LANCZOS)
        overlay = Image.new("RGBA", VIDEO_SIZE, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        draw.rounded_rectangle((60, 780, 1860, 1020), radius=36, fill=(7, 13, 36, 190))
        draw.rounded_rectangle((60, 56, 520, 116), radius=30, fill=(99, 102, 241, 220))
        draw.text((92, 72), "ReplicaLab - 60 second demo", font=badge_font, fill=(255, 255, 255))
        draw.text((96, 820), scene.title, font=title_font, fill=(255, 255, 255))
        subtitle_lines = wrap_text(draw, scene.subtitle, subtitle_font, width=1620)
        y = 888
        for line in subtitle_lines:
            draw.text((96, y), line, font=subtitle_font, fill=(226, 232, 240))
            y += 40

        final = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
        slide_path = SLIDES_DIR / f"{scene.id}.png"
        final.save(slide_path, quality=95)
        output_paths.append(slide_path)
    return output_paths


def write_concat_file(paths: Iterable[Path]) -> Path:
    concat_path = TEXT_DIR / "slides.txt"
    lines: list[str] = []
    ordered = list(paths)
    for scene, path in zip(SCENES, ordered):
        lines.append(f"file '{path.as_posix()}'")
        lines.append(f"duration {scene.duration:.2f}")
    lines.append(f"file '{ordered[-1].as_posix()}'")
    concat_path.write_text("\n".join(lines), encoding="utf-8")
    return concat_path


def write_script_assets() -> None:
    (TEXT_DIR / "voiceover.txt").write_text(NARRATION, encoding="utf-8")
    (TEXT_DIR / "shot_list.json").write_text(
        json.dumps(
            [
                {
                    "id": scene.id,
                    "title": scene.title,
                    "subtitle": scene.subtitle,
                    "url": scene.url,
                    "duration_seconds": scene.duration,
                }
                for scene in SCENES
            ],
            indent=2,
        ),
        encoding="utf-8",
    )


def seconds_to_srt(value: float) -> str:
    millis = int(round(value * 1000))
    hours, millis = divmod(millis, 3_600_000)
    minutes, millis = divmod(millis, 60_000)
    seconds, millis = divmod(millis, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{millis:03}"


def write_srt() -> None:
    lines = wrap_text(ImageDraw.Draw(Image.new("RGB", (1, 1))), NARRATION, get_font(30), 72 * 18)
    segment_count = max(1, len(lines))
    total_duration = sum(scene.duration for scene in SCENES)
    step = total_duration / segment_count
    chunks = []
    start = 0.0
    for index, line in enumerate(lines, start=1):
        end = min(total_duration, start + step)
        chunks.append(f"{index}\n{seconds_to_srt(start)} --> {seconds_to_srt(end)}\n{line}\n")
        start = end
    (TEXT_DIR / "voiceover.srt").write_text("\n".join(chunks), encoding="utf-8")


def ffprobe_duration(path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(result.stdout.strip())


def run_ffmpeg(audio_path: Path, concat_path: Path) -> Path:
    silent_video = OUTPUT_DIR / "replicalab_demo_60s_silent.mp4"
    final_video = OUTPUT_DIR / "replicalab_demo_60s.mp4"

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_path),
            "-vf",
            "fps=30,format=yuv420p",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(silent_video),
        ],
        check=True,
    )
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(silent_video),
            "-i",
            str(audio_path),
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            str(final_video),
        ],
        check=True,
    )
    return final_video


def main() -> int:
    ensure_backend()
    ensure_output_dirs()
    write_script_assets()
    write_srt()

    api_key = load_env_value("ELEVENLABS_API_KEY")
    if not api_key:
        raise RuntimeError("ELEVENLABS_API_KEY was not found in the environment or .env file.")

    voice_id = pick_voice(api_key, load_env_value("ELEVENLABS_VOICE_ID"))
    audio_path = AUDIO_DIR / "voiceover.mp3"
    synthesize_voiceover(api_key, voice_id, NARRATION, audio_path)

    capture_screens()
    slides = create_slides()
    concat_path = write_concat_file(slides)
    final_video = run_ffmpeg(audio_path, concat_path)

    metadata = {
        "voice_id": voice_id,
        "audio_duration_seconds": round(ffprobe_duration(audio_path), 3),
        "video_path": str(final_video),
        "slides": [str(path) for path in slides],
    }
    (TEXT_DIR / "build_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(textwrap.dedent(f"""
    Built demo assets:
      audio: {audio_path}
      video: {final_video}
      script: {TEXT_DIR / 'voiceover.txt'}
      subtitles: {TEXT_DIR / 'voiceover.srt'}
    """).strip())
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - CLI path
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
