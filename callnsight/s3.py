import boto3
import uuid
import time
import os
import json

class AudioTranscriptionService:
    def __init__(self, bucket_name='my-trial12'):
        """
        Initialize AWS services for S3 and Transcribe
        
        Args:
            bucket_name (str): S3 bucket name for audio uploads
        """
        self.s3_client = boto3.client('s3',aws_access_key_id="paste_your_api_key",aws_secret_access_key="paste_your_api_key",region_name='ap-south-1')
        self.transcribe_client = boto3.client('transcribe',aws_access_key_id="paste_your_api_key",aws_secret_access_key="paste_your_api_key",region_name='ap-south-1')
        self.bucket_name = bucket_name

    def upload_audio_to_s3(self, audio_file):
        """
        Upload audio file to S3 bucket
        
        Args:
            file_path (str): Local path of audio file to upload
        
        Returns:
            str: S3 URI of uploaded file
        """
        # Generate unique filename
        file_name = f"audio_{uuid.uuid4()}_{os.path.basename(audio_file) if isinstance(audio_file, str) else 'uploaded_audio'}"
        
        # Upload file to S3
        s3_uri = f"s3://{self.bucket_name}/{file_name}"
        self.s3_client.upload_fileobj(audio_file, self.bucket_name, file_name)
        
        return s3_uri

    def transcribe_audio(self, s3_uri,file_extension):
        """
        Transcribe audio file from S3 using AWS Transcribe
        
        Args:
            s3_uri (str): S3 URI of audio file to transcribe
        
        Returns:
            str: Transcribed text
        """
        # Generate unique job name
        job_name = f"transcription_{uuid.uuid4()}"
        
        # Start transcription job
        self.transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': s3_uri},
            MediaFormat=file_extension,
            LanguageCode='en-US',
            OutputBucketName=self.bucket_name
        )
        
        # Wait for job to complete
        while True:
            status = self.transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
            if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
                break
            time.sleep(5)
        
        # Check job status
        if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
            # Get transcription file from S3
            transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
            transcript_file = os.path.basename(transcript_uri)
            
            # Download and read transcript
            self.s3_client.download_file(self.bucket_name, transcript_file, 'transcript.json')
            
            # Extract transcription text
            with open('transcript.json', 'r') as f:
                transcript_data = json.load(f)
            
            return transcript_data['results']['transcripts'][0]['transcript']
        else:
            raise Exception("Transcription job failed")

    def process_audio_file(self, audio_file,file_extension):
        """
        Complete workflow: upload audio and transcribe
        
        Args:
            audio_file (str or file-like obj): audio file to process
        
        Returns:
            str: Transcribed text
        """
        s3_uri = self.upload_audio_to_s3(audio_file)
        transcription = self.transcribe_audio(s3_uri,file_extension)
        return transcription
    
if __name__ == '__main__':
    transcript_server = AudioTranscriptionService()
    transcript = transcript_server.process_audio_file("/Users/shreeganeshnayak/Downloads/audio-wav-16khz_1006849_normalized.wav")
    print(transcript)
