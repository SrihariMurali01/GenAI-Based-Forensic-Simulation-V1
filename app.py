from flask import Flask, request, render_template, redirect, send_from_directory, url_for, jsonify
import os
import logging
from agents.image_analysis_agent import ImageContentAnalysisAgent
from agents.summarizer_agent import SummarizerAgent
from agents.encryption_agent import EncryptionAgent
from agents.narrative_generation_agent import NarrativeGenerationAgent
from agents.luma_simulation_agent import LumaSimulationAgent

# Initialize Flask app
app = Flask(__name__)

# Set up logging
log_directory = "logs/"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

log_file = os.path.join(log_directory, "pipeline_logs.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),  # Log to a file
        logging.StreamHandler()         # Also log to console
    ]
)

def get_absolute_path(relative_path):
    """Convert a relative path to an absolute path."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, relative_path)

def clean_decrypted_directory():
    """Deletes all files in the decrypted directory."""
    decrypted_dir = "data/evidence/decrypted/"
    if os.path.exists(decrypted_dir):
        try:
            for file_name in os.listdir(decrypted_dir):
                file_path = os.path.join(decrypted_dir, file_name)
                os.remove(file_path)
            logging.info(f"Decrypted directory cleaned: {decrypted_dir}")
        except Exception as e:
            logging.error(f"Error cleaning decrypted directory: {e}")


class MainAgent:
    def __init__(self):
        self.image_agent = ImageContentAnalysisAgent()
        self.summarizer = SummarizerAgent()
        self.encryption_agent = EncryptionAgent()
        self.narrative_agent = NarrativeGenerationAgent()
        self.luma_agent = LumaSimulationAgent()

    def analyze_image(self, image_path):
        logging.info(f"Analyzing image: {image_path}")
        return self.image_agent.analyze_images([image_path])

    def summarize_findings(self, findings, evidence_data):
        logging.info("Summarizing findings...")
        return self.summarizer.summarize(findings, evidence_data)

    def encrypt_file(self, file_path):
        logging.info(f"Encrypting file: {file_path}")
        return self.encryption_agent.encrypt_file(file_path)

    def decrypt_file(self, encrypted_file_path):
        logging.info(f"Decrypting file: {encrypted_file_path}")
        return self.encryption_agent.decrypt_file(encrypted_file_path)
    

    def delete_file(self, file_path):
        """Deletes a specified file."""
        try:
            os.remove(file_path)
            logging.info(f"File deleted: {file_path}")
        except Exception as e:
            logging.error(f"Error deleting file {file_path}: {e}")

    def generate_2d_prompt(self, findings, evidence_data):
        """Generates a narrative-based 2D prompt for visualization."""
        try:
            narrative = self.narrative_agent.generate_narrative(findings, evidence_data)
            prompt_folder = "data/prompts/"
            if not os.path.exists(prompt_folder):
                os.makedirs(prompt_folder)

            prompt_path = os.path.join(prompt_folder, "2D_Prompt.txt")
            with open(prompt_path, "w") as prompt_file:
                prompt_file.write("=== 2D Prompt for Visualization ===\n")
                prompt_file.write(f"Reconstructed Narrative:\n{narrative}\n")

            logging.info(f"2D Prompt generated at: {prompt_path}")
            return narrative
        except Exception as e:
            logging.error(f"Error generating 2D prompt: {e}")
            raise

    def simulate_video(self, narrative):
        logging.info("Simulating video from narrative...")
        return self.luma_agent.generate_video(prompt=narrative)


main_agent = MainAgent()

# Flask routes

@app.route('/')
def index():
    """Main Index Route"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and redirect to menu."""
    file = request.files.get('file')
    if not file:
        return "No file uploaded", 400
    file_path = os.path.join("data/input/", file.filename)
    file.save(file_path)

    # Trigger analysis (this happens in the backend; user doesn't see it immediately)
    main_agent.analyze_image(file_path)

    # Redirect to the navigation menu
    return redirect(url_for('menu'))

@app.route('/menu')
def menu():
    """Display the navigation menu."""
    return render_template('navigation.html')

@app.route('/analyze-image')
def analyze_image():
    """Display the results of image analysis."""
    # Fetch pre-analyzed data (assume it's stored after backend processing)
    try:
        analysis_results = main_agent.analyze_image("data/input/example.jpg")
        if isinstance(analysis_results, tuple):
            findings, evidence_data = analysis_results
        else:
            findings = analysis_results.get('findings', {})
            evidence_data = analysis_results.get('evidence_data', [])
    except Exception as e:
        findings = {}
        evidence_data = []
        logging.error(f"Error fetching image analysis results: {e}")

    return render_template(
        'image_analysis.html',
        findings=findings,
        evidence_data=evidence_data
    )

@app.route('/summarize', methods=['GET'])
def summarize():
    """Fetch and display the analysis report and graphs."""
    try:
        # Encrypted report and graph paths
        encrypted_report_path = "data/reports/crime_scene_report.txt.enc"
        encrypted_graph_path = "data/reports/evidence_distribution.png.enc"

        # Decrypt files using the Encryption Agent
        encryption_agent = main_agent.encryption_agent
        report_path = encryption_agent.decrypt_file(encrypted_report_path)
        graph_path = encryption_agent.decrypt_file(encrypted_graph_path)

        # Ensure files are decrypted successfully
        if not report_path or not graph_path:
            return jsonify({"error": "Failed to decrypt the report or graph."}), 500

        # Render the report and graph in the template
        return render_template(
            'analysed_report.html',
            report=report_path,
            graphs=[graph_path]
        )

    except Exception as e:
        logging.error(f"Error fetching analysis report: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/simulate-video', methods=['POST'])
def simulate_video():
    """Simulate Video Route"""
    narrative = request.json.get("narrative", "")
    if not narrative:
        return "No narrative provided", 400

    video_path = main_agent.simulate_video(narrative)

    return render_template(
        'video_simulation.html',
        video_path=video_path
    )

@app.route('/evidenceCollected', methods=['GET'])
def evidence_collected():
    """Evidence Collection Route"""
    decrypted_evidence = []
    evidence_dir = "data/evidence/encrypted/"
    for filename in os.listdir(evidence_dir):
        if filename.endswith('.enc'):
            decrypted_file = main_agent.decrypt_file(os.path.join(evidence_dir, filename))
            decrypted_evidence.append(decrypted_file)

    return render_template(
        'evidence_collected.html',
        evidence=decrypted_evidence
    )

@app.route('/encrypt-reports', methods=['POST'])
def encrypt_reports():
    """Encrypt all files in the reports directory."""
    try:
        report_dir = "data/reports/"
        encryption_agent = main_agent.encryption_agent

        # Encrypt each file in the reports directory
        encrypted_files = []
        for file_name in os.listdir(report_dir):
            file_path = os.path.join(report_dir, file_name)
            if os.path.isfile(file_path):  # Ensure it's a file
                encrypted_file_path = encryption_agent.encrypt_file(file_path)
                encrypted_files.append(encrypted_file_path)

        return jsonify({"encrypted_files": encrypted_files})
    
    except Exception as e:
        logging.error(f"Error encrypting reports: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/load-section/<string:section>', methods=['GET'])
def load_section(section):
    """Dynamically load the content for a specific section."""
    clean_decrypted_directory()  # Clean decrypted files before processing
    try:
        if section == "analyze-image":
            # Dynamically fetch evidence file for analysis
            input_dir = get_absolute_path("data/input/")
            file_path = next((os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith(('.jpg', '.png'))), None)
            if not file_path:
                return jsonify({"error": "No image file found for analysis."}), 404

            # Analyze the image
            analysis_results = main_agent.analyze_image(file_path)
            if isinstance(analysis_results, tuple):
                findings, evidence_data = analysis_results
            else:
                findings = analysis_results.get('findings', {})
                evidence_data = analysis_results.get('evidence_data', [])

            # Encrypt the evidence file after analysis
            encryption_agent = main_agent.encryption_agent
            encrypted_file_path = encryption_agent.encrypt_file(file_path)
            if not encrypted_file_path:
                logging.error(f"Failed to encrypt evidence file: {file_path}")
                return jsonify({"error": "Failed to encrypt evidence file."}), 500

            logging.info(f"Evidence file encrypted and saved: {encrypted_file_path}")

            # Render analysis results
            return render_template('image_analysis.html', findings=findings, evidence_data=evidence_data)

        elif section == "summarize":

            # Dynamically fetch input file for simulation
            input_dir = get_absolute_path("data/input/")
            file_path = next((os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith(('.jpg', '.png'))), None)
            if not file_path:
                return jsonify({"error": "No image file found for simulation."}), 404

            # Analyze the image
            analysis_results = main_agent.analyze_image(file_path)
            if isinstance(analysis_results, tuple):
                findings, evidence_data = analysis_results
            else:
                findings = analysis_results.get('findings', {})
                evidence_data = analysis_results.get('evidence_data', [])

            # Summarize the findings and generate a report
            report_path = main_agent.summarize_findings(findings, evidence_data)["report"]
            graph_path = main_agent.summarize_findings(findings, evidence_data)["graphs"]

            # Encrypt the report
            encryption_agent = main_agent.encryption_agent
            encrypted_report_path = encryption_agent.encrypt_file(report_path)
            encrypted_graph_path = encryption_agent.encrypt_file(graph_path)

            if not encrypted_report_path:
                logging.error(f"Failed to encrypt the report: {report_path}")
                return jsonify({"error": "Failed to encrypt the report."}), 500

            # Delete the original report after encryption
            try:
                os.remove(report_path)
                os.remove(graph_path)
                logging.info(f"Deleted original report: {report_path}")
            except Exception as e:
                logging.error(f"Failed to delete the original report: {report_path}. Error: {e}")


            encrypted_report_path = get_absolute_path("data/evidence/encrypted/crime_scene_report.txt.enc")
            encrypted_graph_path = get_absolute_path("data/evidence/encrypted/evidence_distribution.png.enc")

            # Decrypt files using the Encryption Agent
            encryption_agent = main_agent.encryption_agent
            report_path = encryption_agent.decrypt_file(encrypted_report_path)
            graph_path = encryption_agent.decrypt_file(encrypted_graph_path)

            if not report_path or not graph_path:
                logging.error("Decryption failed for report or graph.")
                return jsonify({"error": "Failed to decrypt the report or graph."}), 500

            # Generate accessible URLs for the frontend
            report_url = f"/decrypted/{os.path.basename(report_path)}"
            graph_url = f"/decrypted/{os.path.basename(graph_path)}"

            logging.info(f"Report URL: {report_url}")
            logging.info(f"Graph URL: {graph_url}")

            # Render the Analysis Report page
            return render_template(
                'analysed_report.html',
                report=report_url,
                graphs=[graph_url]
            )

        elif section == "simulate-video":
            # Clean decrypted directory before processing
            clean_decrypted_directory()

            # Dynamically fetch input file for simulation
            input_dir = get_absolute_path("data/input/")
            file_path = next((os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith(('.jpg', '.png'))), None)
            if not file_path:
                return jsonify({"error": "No image file found for simulation."}), 404

            # Perform analysis
            analysis_results = main_agent.analyze_image(file_path)
            if isinstance(analysis_results, tuple):
                findings, evidence_data = analysis_results
            else:
                findings = analysis_results.get('findings', {})
                evidence_data = analysis_results.get('evidence_data', [])

            # Generate narrative
            narrative = main_agent.generate_2d_prompt(findings, evidence_data)
            if not narrative:
                error_message = "Failed to generate narrative for simulation."
                return render_template('video_simulation.html', error=error_message)

            # Simulate video
            video_path = main_agent.simulate_video(narrative)
            if not video_path:
                error_message = "Failed to generate video simulation. Please check your inputs or try again later."
                return render_template('video_simulation.html', error=error_message)
            # Generate accessible URL for the video stored in `data/simulations`
            video_url = f"/simulations/{os.path.basename(video_path)}"

            # Render the video simulation template
            return render_template('video_simulation.html', video_path=video_url)


        elif section == "evidence-collected":
            # Decrypt and display evidence
            evidence_dir = get_absolute_path("data/evidence/encrypted/")
            decrypted_evidence = []

            for filename in os.listdir(evidence_dir):
                if filename.endswith('.enc'):
                    decrypted_file = main_agent.decrypt_file(os.path.join(evidence_dir, filename))
                    if decrypted_file:
                        # Generate accessible URL for the decrypted file
                        evidence_url = f"/decrypted/{os.path.basename(decrypted_file)}"
                        decrypted_evidence.append(evidence_url)

            if not decrypted_evidence:
                logging.error("No evidence files found after decryption.")
                return jsonify({"error": "No decrypted evidence available."}), 404

            # Render the Evidence Collected page
            return render_template('evidence_collected.html', evidence=decrypted_evidence)
        
        elif section == "previous-generations":
            # Fetch all video files from the simulations directory
            simulations_dir = get_absolute_path("data/simulations/")
            video_files = [
                f"/simulations/{filename}"
                for filename in os.listdir(simulations_dir)
                if filename.endswith('.mp4')
            ]

            if not video_files:
                logging.warning("No previously generated videos found.")
                return render_template('previous_generations.html', videos=None)

            # Render the Previous Generations page
            return render_template('previous_generations.html', videos=video_files)



        else:
            return jsonify({"error": "Invalid section requested"}), 400
    except Exception as e:
        logging.error(f"Error loading section {section}: {e}")
        return jsonify({"error": str(e)}), 500
    
# File Servers
    
@app.route('/decrypted/<path:filename>')
def serve_decrypted_file(filename):
    """Serve decrypted files from the decrypted directory."""
    decrypted_dir = get_absolute_path("data/evidence/decrypted")
    return send_from_directory(decrypted_dir, filename)

@app.route('/simulations/<path:filename>')
def serve_simulation_file(filename):
    """Serve simulation files from the simulations directory."""
    simulations_dir = get_absolute_path("data/simulations")
    return send_from_directory(simulations_dir, filename)

@app.route('/clear-encrypted-data', methods=['POST', 'GET'])
def clear_all_data():
    """Clear all encrypted, input, and decrypted data and redirect to the main page."""
    # Define directories to clear
    directories_to_clear = [
        get_absolute_path("data/evidence/encrypted"),  # Encrypted files
        get_absolute_path("data/evidence/decrypted"),  # Decrypted files
        get_absolute_path("data/input")               # Input files
    ]

    try:
        for directory in directories_to_clear:
            if os.path.exists(directory):
                for file in os.listdir(directory):
                    file_path = os.path.join(directory, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                logging.info(f"Cleared all files in directory: {directory}")
    except Exception as e:
        logging.error(f"Error clearing data: {e}")
        return jsonify({"error": "Failed to clear all data"}), 500

    return redirect('/')




if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
