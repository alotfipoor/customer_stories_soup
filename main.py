import subprocess
import os
from tqdm import tqdm

# Directory containing the scripts
script_dir = os.path.join('customer_stories', 'spiders')

# Ensure the directory exists
os.makedirs(script_dir, exist_ok=True)

# List of scripts to run
scripts = ['scraper_board.py.py', 'scraper_insight.py', 'scraper_powerbi.py']

# Run each script and save the output
for script in tqdm(scripts):
    script_path = os.path.join(script_dir, script)
    output_file = os.path.join(script_dir, f'{script[:-3]}_output.txt')
    with open(output_file, 'w') as f:
        subprocess.run(['python3', script_path], stdout=f)