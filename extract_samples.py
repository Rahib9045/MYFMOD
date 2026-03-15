import pandas as pd
df = pd.read_csv(r'e:\PRTFLIO\ai recrut\archive\dataset.csv')
for name in ['Kara Harvey', 'Brenda Benitez', 'Alec Cunningham']:
    row = df[df['Name'] == name].iloc[0]
    with open(f"{name.replace(' ', '_')}.txt", "w", encoding='utf-8') as f:
        f.write(f"RESUME:\n{row['Resume']}\n\nTRANSCRIPT:\n{row['Transcript']}\n\nJOB:\n{row['Job_Description']}")
    print(f"Extracted {name}")
