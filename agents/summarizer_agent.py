import os
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg') 
import json

class SummarizerAgent:
    def __init__(self, report_dir="data/reports/"):
        """
        Initializes the Summarizer Agent.
        :param report_dir: Directory to save generated reports and graphs.
        """
        self.report_dir = report_dir
        os.makedirs(self.report_dir, exist_ok=True)

    def generate_report(self, findings, evidence_summary):
        """
        Generates a structured report based on findings and evidence.
        :param findings: Summarized outputs from other agents.
        :param evidence_summary: Details about the collected evidence.
        :return: Path to the generated report.
        """
        report_path = os.path.join(self.report_dir, "crime_scene_report.txt")
        
        try:
            with open(report_path, "w") as report_file:
                # Title
                report_file.write("Crime Scene Report\n")
                report_file.write("===================\n\n")

                # Findings Section
                report_file.write("Findings:\n")
                for key, value in findings.items():
                    report_file.write(f"- {key}: {value}\n")
                report_file.write("\n")

                # Evidence Summary Section
                report_file.write("Evidence Summary:\n")
                for evidence in evidence_summary:
                    report_file.write(f"- {evidence}\n")

            print(f"Report generated at: {report_path}")
            return report_path
        except Exception as e:
            print(f"Error generating report: {e}")
            return None

    def create_graphs(self, evidence_data):
        """
        Generates graphs based on evidence data.
        :param evidence_data: Data about evidence to visualize.
        :return: List of paths to generated graphs.
        """
        graph_path = ''
        try:
            # Generate Evidence Distribution Graph
            evidence_types = [item["type"] for item in evidence_data]
            evidence_counts = {etype: evidence_types.count(etype) for etype in set(evidence_types)}

            plt.figure()
            plt.bar(evidence_counts.keys(), evidence_counts.values(), color="blue", alpha=0.7)
            plt.title("Evidence Distribution")
            plt.xlabel("Evidence Type")
            plt.ylabel("Count")
            plt.xticks(rotation=45)
            graph_path = os.path.join(self.report_dir, "evidence_distribution.png")
            plt.savefig(graph_path)  # Save the graph to a file
            plt.close()

            print(f"Graph generated at: {graph_path}")
        except Exception as e:
            print(f"Error generating graphs: {e}")

        return graph_path


    def summarize(self, findings, evidence_data):
        """
        Aggregates findings and evidence into a report and graphs.
        :param findings: Summarized outputs from other agents.
        :param evidence_data: Data about evidence.
        :return: Dictionary with paths to the report and graphs.
        """
        try:
            # Prepare Evidence Summary
            evidence_summary = [f"{e['type']} found at {e['location']}" for e in evidence_data]

            # Generate Report
            report_path = self.generate_report(findings, evidence_summary)

            # Generate Graphs
            graph_paths = self.create_graphs(evidence_data)

            return {
                "report": report_path,
                "graphs": graph_paths
            }
        except Exception as e:
            print(f"Error during summarization: {e}")
            return None
