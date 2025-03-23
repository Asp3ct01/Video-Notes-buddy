import youtube_dl
import torch
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline
from urllib.parse import urlparse, parse_qs

class VideoNotesBot:
    def __init__(self, model_name="facebook/bart-large-cnn"):
        # Available models for summarization
        self.available_models = {
            "bart": "facebook/bart-large-cnn",
            "pegasus": "google/pegasus-xsum",
            "t5": "t5-base",
            "distilbart": "sshleifer/distilbart-cnn-12-6"
        }
        
        # Use provided model or default to bart
        model_name = self.available_models.get(model_name.lower(), model_name)
        self.summarizer = pipeline("summarization", model=model_name)
        
    def get_video_id(self, url):
        """Extract video ID from YouTube URL"""
        parsed_url = urlparse(url)
        if parsed_url.hostname == 'youtu.be':
            return parsed_url.path[1:]
        if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
            if parsed_url.path == '/watch':
                return parse_qs(parsed_url.query)['v'][0]
        return None

    def get_transcript(self, video_id):
        """Get video transcript"""
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return ' '.join([entry['text'] for entry in transcript])
        except Exception as e:
            return f"Error getting transcript: {str(e)}"

    def summarize_text(self, text, max_length=1024, min_length=256):
        """Summarize the transcript"""
        # Split text into chunks if it's too long
        chunks = [text[i:i + 4096] for i in range(0, len(text), 4096)]
        summaries = []
        
        for chunk in chunks:
            summary = self.summarizer(chunk, 
                                    max_length=max_length, 
                                    min_length=min_length, 
                                    do_sample=False)
            summaries.append(summary[0]['summary_text'])
        
        return ' '.join(summaries)

    def process_video(self, url):
        """Main function to process video and return summary"""
        # Get video ID
        video_id = self.get_video_id(url)
        if not video_id:
            return "Invalid YouTube URL"

        # Get transcript
        transcript = self.get_transcript(video_id)
        if transcript.startswith("Error"):
            return transcript

        # Generate summary
        try:
            summary = self.summarize_text(transcript)
            return summary
        except Exception as e:
            return f"Error generating summary: {str(e)}"

    def change_model(self, model_name):
        """Change the summarization model"""
        try:
            if model_name in self.available_models:
                model_name = self.available_models[model_name]
            self.summarizer = pipeline("summarization", model=model_name)
            return f"Successfully switched to {model_name}"
        except Exception as e:
            return f"Error changing model: {str(e)}"

# Usage example
def main():
    bot = VideoNotesBot()
    
    while True:
        url = input("Enter YouTube video URL (or 'quit' to exit): ")
        if url.lower() == 'quit':
            break
            
        summary = bot.process_video(url)
        print("\nSummary:")
        print(summary)
        print("\n" + "="*50 + "\n")

    bot.change_model("distilbart")

if __name__ == "__main__":
    main()
