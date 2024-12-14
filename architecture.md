GenAI-Based-Forensic-Simulator/
│
├── agents/
│   ├── encryption_agent.py
│   ├── image_analysis_agent.py
│   ├── luma_simulation_agent.py
│   ├── narrative_generation_agent.py
│   ├── summarizer_agent.py
│   └── __init__.py
│   └── __pycache__/  (compiled Python files)
│
├── config/
│   ├── .env
│   ├── config.yaml
│   ├── encryption.key
│
├── data/
│   ├── evidence/
│   │   ├── decrypted/
│   │   └── encrypted/
│   ├── input/
│   │   └── Evidence_1.jpg
│   ├── prompts/
│   │   └── 2D_Prompt.txt
│   ├── reports/
│   └── simulations/
│       ├── crime_scene_simulation.mp4
│       ├── Evidence_1_simulation.mp4
│       ├── Reconstructed_Narrative_The_scene_unfolds_in_a_modern_room_...
│       └── ____2D_Prompt_for_Visualization____Reconstructed_Narrative_...
│
├── logs/
│   └── pipeline_logs.log
│
├── static/
│   ├── images/
│   │   ├── bg.jpg
│   │   └── bg_.png
│
├── templates/
│   ├── analysed_report.html
│   ├── base.html
│   ├── evidence_collected.html
│   ├── image_analysis.html
│   ├── index.html
│   ├── navigation.html
│   ├── previous_generations.html
│   └── video_simulation.html
│
├── utils/
│   ├── config_loader.py
│   ├── env_loader.py
│   ├── __init__.py
│   └── __pycache__/  (compiled Python files)
│
│
├── README.md
├── requirements.txt
├── app.py
├── main_agent.py
├── test_agent.py
