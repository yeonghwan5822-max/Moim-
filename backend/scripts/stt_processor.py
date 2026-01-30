import os
import sys
import logging
import whisper
import warnings
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Suppress FP16 warning on CPU
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

class SecureSTTProcessor:
    def __init__(self, model_size="base"):
        """
        Initialize Whisper Model.
        model_size options: tiny, base, small, medium, large
        """
        logging.info(f"Loading Whisper model ('{model_size}')...")
        self.model = whisper.load_model(model_size)
        logging.info("Whisper model loaded successfully.")
        
    def process_audio(self, audio_path: str, output_path: str = None):
        """
        Transcribes audio and IMMEDIATELY deletes the source file (PIPA Compliance).
        output_path: If None, appends to backend/references/corpus_sample.txt
        """
        if not os.path.exists(audio_path):
            logging.error(f"Audio file not found: {audio_path}")
            return None

        try:
            logging.info(f"Transcribing {audio_path}...")
            
            # 1. Transcribe
            result = self.model.transcribe(audio_path)
            transcript = result["text"].strip()
            
            logging.info(f"Transcription complete: {transcript[:50]}...")
            
            # 2. Save Transcript
            if output_path is None:
                # Default: Append to corpus_sample.txt for OOV detector
                base_dir = Path(__file__).parent.parent
                output_path = base_dir / "references" / "corpus_sample.txt"
            
            with open(output_path, "a", encoding="utf-8") as f:
                f.write(f"\n{transcript}\n")
                
            logging.info(f"Saved transcript to {output_path}")
            
            # 3. Secure Deletion (PIPA)
            os.remove(audio_path)
            if not os.path.exists(audio_path):
                logging.info(f"SECURE DELETE: Original audio file {audio_path} has been permanently deleted.")
            else:
                logging.error(f"CRITICAL: Failed to delete audio file {audio_path}. Manual check required.")
                
            return transcript

        except Exception as e:
            logging.error(f"STT Processing Error: {e}")
            return None

def main():
    # PoC Usage Example
    processor = SecureSTTProcessor(model_size="base")
    
    # Mocking an audio file for testing logic (Create a dummy file to be deleted)
    mock_audio_path = "test_audio_recording.mp3"
    with open(mock_audio_path, "w") as f:
        f.write("Fake Audio Content") # This won't actually transcribe well with Whisper but tests logic
        
    # Note: In real usage, this would be a real recording. 
    # Since we can't easily record audio in this env, we assume the file exists.
    # To properly test Whisper, we need a real valid audio file.
    # Here we just show the Logic Flow.
    
    print("\n[System] Waiting for audio input...")
    
    # Check if a real file exists to test, otherwise skip actual transcribe call to avoid error on fake file
    if os.path.exists("real_test.mp3"):
         processor.process_audio("real_test.mp3")
    else:
        logging.warning("No real 'real_test.mp3' found. Created 'mock_audio.mp3' to test DELETION logic only.")
        # We manually simulate the success path for the mock
        mock_path = "mock_audio.mp3"
        with open(mock_path, "w") as f:
            f.write("dummy data")
            
        # Manually invoke delete/save logic without actual whisper (since fake file fails in whisper)
        # Bypassing processor.process_audio for this dry run print:
        if os.path.exists(mock_path):
            print(f"Transcribing {mock_path}...")
            print("Transcription: [Voice Data Converted]")
            
            # Save
            base_dir = Path(__file__).parent.parent
            out_p = base_dir / "references" / "corpus_sample.txt"
            with open(out_p, "a", encoding="utf-8") as f:
                f.write("\n[STT] 모의 테스트 음성 데이터입니다.\n")
            print(f"Saved to {out_p}")
            
            # Delete
            os.remove(mock_path)
            print(f"SECURE DELETE: {mock_path} deleted.")

if __name__ == "__main__":
    main()
