from openai import OpenAI
from utils.config_loader import load_config
from utils.env_loader import load_env
import os
import base64
import json
import re

class ImageContentAnalysisAgent:
    def __init__(self):
        """
        Initializes the Image Content Analysis Agent using configurations and environment variables.
        """
        # Load configurations and environment variables
        self.config = load_config()
        load_env()
        self.api_key = os.getenv("OPENAI_API_KEY")

        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        self.model = self.config["openai"]["model"]

    def encode_image(self, image_path):
        """
        Encodes a local image into a base64 string.
        :param image_path: Path to the local image file.
        :return: Base64 encoded string of the image.
        """
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except Exception as e:
            print(f"Error encoding image: {e}")
            return None

    def analyze_images(self, images):
        """
        Analyzes crime scene images and extracts forensic insights.
        :param images: List of image paths (local) or URLs (remote) to analyze.
        :return: Tuple containing findings (dict) and evidence data (list of dicts).
        """
        # Prepare the content payload
        content_list = [
            {
                "type": "text",
                "text": self.config["agents"]["image_analysis"]["description_prompt"]
            }
        ]

        # Append each image as base64 (local) or URL (remote)
        for image in images:
            if os.path.isfile(image):  # Local image
                base64_image = self.encode_image(image)
                if base64_image:
                    content_list.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    })
            else:  # Remote image URL
                content_list.append({
                    "type": "image_url",
                    "image_url": {
                        "url": image
                    }
                })

        # Define the messages payload
        messages = [
            {
                "role": "user",
                "content": content_list
            }
        ]

        # Call OpenAI's chat completion API
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.config["openai"]["max_tokens"],
                temperature=self.config["openai"]["temperature"]
            )

            # Extract content and process it
            response_content = response.choices[0].message.content
            findings, evidence_data = self._process_response(response_content)

            return findings, evidence_data
        except Exception as e:
            print(f"Error analyzing images: {e}")
            return None, None


    def _process_response(self, response_content):
        """
        Processes the OpenAI API response to extract findings and evidence.
        :param response_content: Raw response content from OpenAI API.
        :return: Tuple (findings, evidence_data).
        """
        try:
            # Extract JSON content from the first '{' to the last '}'
            json_content = re.search(r"\{.*\}", response_content, re.DOTALL)
            if not json_content:
                raise ValueError("No valid JSON found in the response content.")

            # Parse the extracted JSON string
            response_data = json.loads(json_content.group(0))

            # Extract findings and evidence data
            findings = {
                "Scene Description": response_data.get("scene_description", "No description provided."),
                "Key Observations": response_data.get("key_observations", "No observations provided."),
                "Environmental Conditions": response_data.get("environmental_conditions", "No conditions provided.")
            }

            evidence_data = response_data.get("evidence", [])
            for evidence in evidence_data:
                evidence["status"] = "unprocessed"  # Add default status

            return findings, evidence_data

        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error processing response content: {e}")
            print("Raw response content:")
            print(response_content)

            # Provide fallback outputs
            findings = {
                "Scene Description": "Could not extract scene description.",
                "Key Observations": "Could not extract observations.",
                "Environmental Conditions": "Could not extract environmental conditions."
            }
            evidence_data = []

            return findings, evidence_data

