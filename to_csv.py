import json
import os
import pandas as pd

json_dir = 'customer_stories/results'

all_data = []  # Collect data before creating DataFrame

for filename in os.listdir(json_dir):
    if filename.endswith('.json'):
        try:
            with open(os.path.join(json_dir, filename), 'r') as f:
                data = json.load(f)

            tool_name = filename.rsplit('_', 1)[-1][:-5].capitalize()  # Extract tool name
            for i, entry in enumerate(data, 1):
                entry['toolName'] = tool_name
            all_data.extend(data)  # Add to the list

        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error processing file '{filename}': {e}")

# Create the DataFrame in one step
df = pd.DataFrame(all_data) 
# Rearrange the columns
df = df[['toolName', 'company', 'title', 'url', 'content']]

df.to_csv('customer_stories/results/customer_stories_all.csv', index=True)