import pandas as pd
df = pd.read_csv(r'e:\\PRTFLIO\\ai recrut\\archive\\dataset.csv')
s = df[df['Name'] == 'Jose Morrison'].iloc[0]
with open('jose_morrison.txt', 'w', encoding='utf-8') as f:
    f.write("RESUME:\n" + s['Resume'] + "\n\n")
    f.write("TRANSCRIPT:\n" + s['Transcript'] + "\n\n")
    f.write("JOB:\n" + s['Job_Description'] + "\n")
