# one time script to get the gene synonym mapping from the Census_gene_list.csv file
import pandas as pd

df = pd.read_csv("../ref/Census_gene_list.csv", dtype=str).fillna("")

# keep just what you need
df = df[["Gene Symbol", "Synonyms"]].rename(columns={"Gene Symbol": "official"})

# split the comma-separated synonym cell into many rows
df["synonym"] = df["Synonyms"].str.split(",")
df = df.explode("synonym", ignore_index=True)

# clean
df["synonym"] = df["synonym"].str.strip().str.strip('"').str.strip()
df["official"] = df["official"].str.strip()

# optionally also map the official symbol to itself
self_map = df[["official"]].drop_duplicates().assign(synonym=lambda x: x["official"])
df = pd.concat([df[["synonym", "official"]], self_map[["synonym", "official"]]], ignore_index=True)

# drop empties + duplicates
df = df[(df["synonym"] != "") & (df["official"] != "")]
df = df.drop_duplicates()

# write a tiny TSV you can ship/load fast
df.to_csv("../ref/synonym_to_gene_symbol.tsv", sep="\t", index=False, header=False)