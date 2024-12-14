from openai import OpenAI
import logging
import os
from utils.config_loader import load_config
from utils.env_loader import load_env

class NarrativeGenerationAgent:
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

    def generate_narrative(self, findings, evidence_data):
        """
        Generate a predictive narrative for the crime scene based on findings and evidence.
        :param findings: Crime scene findings (descriptions, observations)
        :param evidence_data: Collected evidence data (location, type, etc.)
        :param environmental_conditions: Conditions in the crime scene (lighting, weather, etc.)
        :return: A generated narrative of what might have happened at the crime scene.
        """
        # Construct a prompt to send to GPT
        prompt = self.create_prompt(findings, evidence_data)
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        try:
            # Use the OpenAI API to generate a narrative
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.config["openai"]["max_tokens"],
                temperature=self.config["openai"]["temperature"]
            )

            narrative = response.choices[0].message.content
            logging.info("Generated narrative: " + narrative)
            return narrative
        except Exception as e:
            logging.error(f"Error generating narrative: {e}")
            return None

    def create_prompt(self, findings, evidence_data):
        """
        Create a prompt string for the GPT model to generate the narrative.
        :param findings: The findings from the crime scene analysis
        :param evidence_data: Evidence collected from the crime scene
        :return: A formatted prompt string
        """
        prompt = f"Given the following crime scene information, predict the sequence of events leading up to and following the incident:\n"
        prompt += f"Findings: {findings}\n"
        prompt += f"Evidence: {evidence_data}\n"
        prompt += "I need you Generate a very real story-like prediction about what might have happened during the crime. Limit yourself to 250 words or less only. It should be just in the form of paragraphs, no headings, nothing. I want just the prediction. I need to give this prompt to a 2D simulation model, to create a simulation. Rephrase it and use a very neutral language. DO NOT INCLUDE ANY KIND OF RESTRICTIVE WORDS SUCH AS BLOOD, BLOODSTAIN, KILLER, etc."

        return prompt
