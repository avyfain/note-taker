import sounddevice as sd
import numpy as np
import threading
import queue
import time
import resampy
import wave
from textual import log

def print_audio_devices():
    log.info("Available audio devices:")
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        log.info(
            f"{i}: {device['name']} (Max channels: In={device['max_input_channels']}, Out={device['max_output_channels']})"
        )

from typing import Callable

# Define a callable type with input types and return type
AudioDataCallback = Callable[[np.ndarray], None]

class AudioCapture:
    def __init__(
        self, audio_data_callback: AudioDataCallback, 
        target_sample_rate=16000, block_duration=0.05
    ):
        self.target_sample_rate = target_sample_rate
        self.block_duration = block_duration
        self.recording = False
        self.audio_queue = queue.Queue()
        self.audio_data_callback = audio_data_callback
        self.last_mic_data = None
        self.last_desktop_data = None
        self.new_mic_data = True
        self.new_desktop_data = True

    def get_desktop_device(self):
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if device["max_input_channels"] > 0:  # Check if it's an input device
                if "Stereo Mix" in device["name"] or "What U Hear" in device["name"]:
                    return i
        return sd.default.device[0]  # Default input device if no specific one found

    def start_recording(self):
        self.recording = True

        try:
            # Get default device sample rates
            default_input_device = sd.query_devices(sd.default.device[0], "input")

            self.mic_sample_rate = int(default_input_device["default_samplerate"])
            mic_block_size = int(self.mic_sample_rate * self.block_duration)

            # Start microphone stream
            self.mic_stream = sd.InputStream(
                samplerate=self.mic_sample_rate,
                blocksize=mic_block_size,
                channels=1,
                device=sd.default.device[0],
                callback=self.mic_callback,
            )

            # Find and configure desktop audio stream
            desktop_device = self.get_desktop_device()
            self.desktop_sample_rate = sd.query_devices(desktop_device, "input")[
                "default_samplerate"
            ]
            device_info = sd.query_devices(desktop_device, "input")
            desktop_channels = min(
                device_info["max_input_channels"], 2
            )  # Use max 2 channels
            desktop_block_size = int(self.desktop_sample_rate * self.block_duration)

            self.desktop_stream = sd.InputStream(
                samplerate=self.desktop_sample_rate,
                blocksize=desktop_block_size,
                channels=desktop_channels,
                device=desktop_device,
                callback=self.desktop_callback,
            )

            self.mic_stream.start()
            self.desktop_stream.start()

            # Start processing thread
            self.processing_thread = threading.Thread(target=self.process_audio)
            self.processing_thread.start()

            log.info(
                f"Recording started. Mic: {self.mic_stream.channels} channel(s) at {self.mic_sample_rate}Hz, Desktop: {self.desktop_stream.channels} channel(s) at {self.desktop_sample_rate}Hz"
            )
        except sd.PortAudioError as e:
            log.info(f"Error starting audio streams: {e}")
            log.info("Available devices:")
            print_audio_devices()
            raise

    def stop_recording(self):
        self.recording = False
        if self.mic_stream:
            self.mic_stream.stop()
            self.mic_stream.close()
        if self.desktop_stream:
            self.desktop_stream.stop()
            self.desktop_stream.close()
        if hasattr(self, "processing_thread"):
            self.processing_thread.join()
        log.info("Recording stopped.")

    def mic_callback(self, indata, frames, time, status):
        if status:
            log.info(f"Microphone stream error: {status}")
        if self.recording:
            self.audio_queue.put(("mic", indata.copy()))

    def desktop_callback(self, indata, frames, time, status):
        if status:
            log.info(f"Desktop stream error: {status}")
        if self.recording:
            self.audio_queue.put(("desktop", indata.copy()))

    def normalize_audio(self, audio, target_level=-3):
        """
        Normalize the audio to a target RMS level in dB.
        """
        rms = np.sqrt(np.mean(audio**2))
        target_rms = 10**(target_level / 20)
        gain = target_rms / (rms + 1e-9)  # Add small value to avoid division by zero
        return audio * gain

    def resample(self, audio, original_sample_rate):
        # make sure audio is 2D array with shape (channels, samples)
        if audio.ndim == 1:
            audio = audio.reshape(1, -1)
        if audio.shape[0] > audio.shape[1]:
            audio = audio.T

        # If stereo, downmix to mono
        if audio.shape[1] >= 2:
            audio = np.mean(audio, axis=0)

        resampled_audio = resampy.resample(
            audio, original_sample_rate, self.target_sample_rate
        )

        # Normalize audio shape to (samples, 1)
        return resampled_audio.reshape(-1, 1)

    def process_audio(self):
        while self.recording or not self.audio_queue.empty():
            try:
                source, data = self.audio_queue.get(timeout=1)

                # Resample to target sample rate
                if source == "mic":
                    data = self.resample(data, self.mic_sample_rate)
                    self.last_mic_data = data
                    self.new_mic_data = True
                else:
                    data = self.resample(data, self.desktop_sample_rate)
                    self.last_desktop_data = data
                    self.new_desktop_data = True

                # Blend mic and desktop audio if both are available
                if (
                    self.last_mic_data is not None
                    and self.last_desktop_data is not None
                    and self.new_mic_data and self.new_desktop_data
                ):
                    # Normalize audio levels
                    normalized_mic = self.last_mic_data
                    normalized_desktop = self.last_desktop_data

                    # Ensure both arrays have the same shape
                    max_length = max(
                        normalized_mic.shape[0], self.last_desktop_data.shape[0]
                    )
                    mic_padded = np.pad(
                        normalized_mic,
                        ((0, max_length - normalized_mic.shape[0]), (0, 0)),
                    )
                    desktop_padded = np.pad(
                        normalized_desktop,
                        ((0, max_length - normalized_desktop.shape[0]), (0, 0)),
                    )

                    # Blend the audio (you can adjust the weights as needed)
                    blended_audio = 0.5 * mic_padded + 0.5 * desktop_padded

                    if self.audio_data_callback:
                        self.audio_data_callback(blended_audio)

                    self.new_mic_data = False
                    self.new_desktop_data = False

            except queue.Empty:
                continue



# Global variable to hold the WAV file object
wav_file = None

def example_callback(audio_data):
    global wav_file
    if wav_file is not None:
        # Convert float32 audio data to int16
        audio_data_int = (audio_data * 32767).astype(np.int16)
        
        # Write the audio data to the WAV file
        wav_file.writeframes(audio_data_int.tobytes())

def main():
    global wav_file
    log.info("Available audio devices:")
    print_audio_devices()

    # Open the WAV file for writing
    wav_file = wave.open("streaming_recording.wav", "wb")
    wav_file.setnchannels(1)  # Mono
    wav_file.setsampwidth(2)  # 2 bytes per sample (16-bit)
    wav_file.setframerate(16000)  # Sample rate

    audio_capture = AudioCapture(audio_data_callback=example_callback)
    try:
        audio_capture.start_recording()
        log.info("Recording... Press Ctrl+C to stop.")
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        log.info("Stopping recording...")
    finally:
        if hasattr(audio_capture, 'stop_recording'):
            audio_capture.stop_recording()
        
        # Close the WAV file
        if wav_file is not None:
            wav_file.close()
            log.info("Recording saved to streaming_recording.wav")

if __name__ == "__main__":
    main()
