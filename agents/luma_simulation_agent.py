import os
import time
import logging
from lumaai import LumaAI
import requests
from utils.env_loader import load_env

class LumaSimulationAgent:
    def __init__(self, output_dir="data/simulations/"):
        """
        Initializes the Luma Simulation Agent.
        :param api_key: Luma API Key.
        :param output_dir: Directory to save generated simulations.
        """
        load_env()
        self.api_key = os.getenv("LUMAAI_API_KEY")
        print(self.api_key)
        self.client = LumaAI(auth_token=self.api_key)
        print(self.client)
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_video(self, prompt, video_name="crime_scene_simulation.mp4"):
        """
        Generates a video based on the provided prompt using Luma Dream Machine API.
        :param prompt: Textual prompt describing the crime scene.
        :param video_name: Name of the output video file.
        :return: Path to the generated video or None if failed.
        """
        try:
            logging.info("Sending request to generate video...")
            generation = self.client.generations.create(prompt=prompt)
            logging.info(f"Generation initiated with ID: {generation.id}")

            # Polling for status
            while True:
                generation = self.client.generations.get(id=generation.id)
                if generation.state == "completed":
                    video_url = generation.assets.video
                    logging.info(f"Video generation completed. Downloading from {video_url}")
                    return self._download_video(video_url, video_name)
                elif generation.state == "failed":
                    logging.error(f"Generation failed: {generation.failure_reason}")
                    return None
                else:
                    logging.info("Generation in progress...")
                    time.sleep(5)
        except Exception as e:
            logging.error(f"An error occurred while generating video: {e}")
            return None

    def _download_video(self, url, file_name):
        """
        Downloads and saves the generated video.
        :param url: URL of the video.
        :param file_name: Name of the file to save.
        :return: Path to the saved video.
        """
        try:
            video_response = requests.get(url, stream=True)
            video_path = os.path.join(self.output_dir, file_name)
            with open(video_path, 'wb') as file:
                for chunk in video_response.iter_content(chunk_size=8192):
                    file.write(chunk)
            logging.info(f"Video saved at: {video_path}")
            return video_path
        except Exception as e:
            logging.error(f"Error downloading video: {e}")
            return None
