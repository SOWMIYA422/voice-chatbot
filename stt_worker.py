import queue
import sounddevice as sd
import json
import time
import os
import wave
from vosk import Model, KaldiRecognizer
from config import VOSK_MODEL_PATH, SAMPLE_RATE

# Make sure transcriptdata folder exists
os.makedirs("transcriptdata", exist_ok=True)

# Timestamp for this recording session
timestamp = int(time.time())
audio_file = os.path.join("transcriptdata", f"audio_{timestamp}.wav")
transcript_file = os.path.join("transcriptdata", f"transcript_{timestamp}.txt")

# Save raw audio to .wav
wf = wave.open(audio_file, "wb")
wf.setnchannels(1)
wf.setsampwidth(2)  # 16-bit PCM
wf.setframerate(SAMPLE_RATE)

# Load vosk
print("[vosk] Loading model...")
model = Model(VOSK_MODEL_PATH)
rec = KaldiRecognizer(model, SAMPLE_RATE)
rec.SetWords(True)

q = queue.Queue()


def callback(indata, frames, time_, status):
    if status:
        print(status, flush=True)
    q.put(bytes(indata))
    wf.writeframes(bytes(indata))  # write raw audio to file


def save_text(text):
    with open(transcript_file, "a", encoding="utf-8") as f:
        f.write(text + "\n")
    print(f"[FILE] {text}")


def main():
    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=8000,
        dtype="int16",
        channels=1,
        callback=callback,
    ):
        print("🎙️ Listening... Ctrl+C to stop.")
        try:
            while True:
                data = q.get()
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    if result.get("text"):
                        save_text(result["text"])
                else:
                    partial = json.loads(rec.PartialResult()).get("partial", "")
                    if partial:
                        print(f"[partial] {partial}", end="\r")
        except KeyboardInterrupt:
            print("\n🛑 Stopping...")
        finally:
            wf.close()


if __name__ == "__main__":
    main()
