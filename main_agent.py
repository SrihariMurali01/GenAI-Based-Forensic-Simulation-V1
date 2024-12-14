import logging
import os
from crewai import Agent, Task
from agents.image_analysis_agent import ImageContentAnalysisAgent
from agents.summarizer_agent import SummarizerAgent
from agents.encryption_agent import EncryptionAgent
from agents.narrative_generation_agent import NarrativeGenerationAgent
from agents.luma_simulation_agent import LumaSimulationAgent

# Set up logging to both console and file
log_directory = "logs/"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

log_file = os.path.join(log_directory, "pipeline_logs.log")

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(log_file),  # Log to a file
                        logging.StreamHandler()         # Also log to console
                    ])

class MainAgent:
    def __init__(self):
        # Initialize agents
        self.image_agent = ImageContentAnalysisAgent()
        self.summarizer = SummarizerAgent()
        self.encryption_agent = EncryptionAgent()
        self.narrative_agent = NarrativeGenerationAgent()
        self.luma_agent = LumaSimulationAgent()

        # Setup CrewAI agents for orchestration
        self.agent = Agent(
            name="MainAgent",  # Name of the agent
            role="Orchestrator",  # Role of the agent
            goal="Process images, summarize findings, and encrypt reports.",  # Goal of the agent
            backstory="This agent handles the forensic analysis of crime scene images, summarizes findings, generate stunnign visualisations and ensures secure encryption of reports."  # Backstory for context
        )

    def image_analysis_task(self, image_path):
        """Task for image analysis."""
        logging.info(f"Processing image: {image_path}")
        results = self.image_agent.analyze_images([image_path])
        return results

    def summarization_task(self, findings, evidence_data):
        """Task for summarizing the findings."""
        logging.info("Summarizing findings...")
        summarized_results = self.summarizer.summarize(findings, evidence_data)
        return summarized_results

    def encryption_task(self, file_path):
        """Task for encrypting the file."""
        logging.info(f"Encrypting file: {file_path}")
        encrypted_files = self.encryption_agent.encrypt_file(file_path)
        
        # Check if the encryption was successful
        if not encrypted_files:
            logging.error(f"Encryption failed for file: {file_path}")
            return None
        
        return encrypted_files

    def decrypt_file(self, encrypted_file_path):
        """Decrypt a file when it needs to be accessed."""
        logging.info(f"Decrypting file: {encrypted_file_path}")
        decrypted_file = self.encryption_agent.decrypt_file(encrypted_file_path)
        return decrypted_file

    def delete_file(self, file_path):
        """Delete a file after use."""
        try:
            os.remove(file_path)
            logging.info(f"File deleted: {file_path}")
        except Exception as e:
            logging.error(f"Error deleting file {file_path}: {e}")
    
    def generate_2d_prompt(self, findings, evidence_data):
        """Generate a predictive 2D prompt based on findings and summarized results."""
        try:
            # Call the narrative generation agent to generate the story-like prediction
            narrative = self.narrative_agent.generate_narrative(findings, evidence_data,)

            prompt_folder = "data/prompts/"
            if not os.path.exists(prompt_folder):
                os.makedirs(prompt_folder)

            prompt_path = os.path.join(prompt_folder, "2D_Prompt.txt")
            with open(prompt_path, "w") as prompt_file:
                prompt_file.write("=== 2D Prompt for Visualization ===\n")
                prompt_file.write(f"Reconstructed Narrative:\n{narrative}\n")

            logging.info(f"2D Prompt with predictive narrative generated at: {prompt_path}")

            return narrative
        except Exception as e:
            logging.error(f"Error generating 2D prompt: {e}")
            raise
    
    def simulation_task(self, narrative):
        """Task to generate a video simulation using the narrative."""
        logging.info("Starting video simulation task...")
        video_path = self.luma_agent.generate_video(prompt=narrative)
        if video_path:
            logging.info(f"Video simulation generated at: {video_path}")
        else:
            logging.error("Video simulation task failed.")
        return video_path


    def run_pipeline(self):
        try:
            # Step 1: Process images in 'data/input/' folder
            images_directory = "data/input/"
            image_files = [f for f in os.listdir(images_directory) if f.endswith(('.jpg', '.png', '.jpeg'))]
            logging.info(f"Found image files: {image_files}")
            findings, evidence_data = '', ''
            for image in image_files:
                image_path = os.path.join(images_directory, image)
                results = self.image_analysis_task(image_path)
                # Image Analysis Task
                if isinstance(results, tuple):
                # If it's a tuple, unpack it
                    findings, evidence_data = results
                else:    
                    findings = results.get('findings', {})
                    evidence_data = results.get('evidence_data', [])

                logging.info(f"Findings: {findings}")
                logging.info(f"Evidence Data: {evidence_data}")

                # Summarization Task
                summarized_results = self.summarization_task(findings, evidence_data)

                # Step 2: Encrypt the image files directly from data/input/
                encrypted_files = self.encryption_task(image_path)

                if encrypted_files is None:
                    logging.error(f"Encryption failed for {image_path}. Skipping.")
                    continue

                # Delete the original image file after encryption
                self.delete_file(image_path)

                # Encrypt the report files directly from data/reports/
                 # Step 3: Encrypt all files in 'data/reports/'
            reports_directory = "data/reports/"
            report_files = [f for f in os.listdir(reports_directory) if f.endswith(('.txt', '.pdf', '.png'))]
            logging.info(f"Found report files: {report_files}")

            for report in report_files:
                report_path = os.path.join(reports_directory, report)

                # Encrypt the report file
                encrypted_files = self.encryption_task(report_path)

                if encrypted_files is None:
                    logging.error(f"Encryption failed for {report_path}. Skipping.")
                    continue

                # Delete the original report file after encryption
                self.delete_file(report_path)

                # Step 3: Decrypt the encrypted report when needed
                decrypted_report = self.decrypt_file(encrypted_files)

                if decrypted_report is None:
                    logging.error("Decryption failed. Skipping this file.")
                    continue  # Skip this file if decryption fails

                # Generate 2D Prompt
                narrative = self.generate_2d_prompt(findings, evidence_data)

                # Generate Simulation
                self.simulation_task(narrative)

        except Exception as e:
            logging.error(f"Error during pipeline execution: {e}")
            raise


if __name__ == "__main__":
    main_agent = MainAgent()
    main_agent.run_pipeline()