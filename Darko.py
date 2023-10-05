import pandas as pd

user = input("User: ")
csv = '/Users/{}/Downloads/DARKO.csv'.format(user)
df = pd.read_csv(csv)
print(df)
