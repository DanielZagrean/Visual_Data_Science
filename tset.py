import pandas as pd
import matplotlib.pyplot as plt
df = pd.read_csv("fishing_fleet.csv")

df.drop(['STRUCTURE', 'STRUCTURE_ID', 'STRUCTURE_NAME', 'freq', 'Time frequency','Time','Observation value', 'OBS_FLAG','gear','Engine power','Observation status (Flag) V2 structure','CONF_STATUS', 'Confidentiality status (flag)'], axis=1, inplace = True)
df = df.rename(columns={
    "Geopolitical entity (reporting)": "geo_entity",
    "Fishing gears": "gear",
    "TIME_PERIOD": "year",
    "OBS_VALUE": "value"
})
df_1 = df[
    (df["geo"] == "EU") & #instance EU
    (df["gear"] == "Total") & #all gears
    (df["unit"] == "NR") & #Displays Number
    (df["eng_pow"] == "TOTAL") #For all engine powers
]

df_1 = df_1.sort_values("year")
print(df_1.shape)
# Plot
plt.figure(figsize=(10,6))
plt.plot(df_1["year"], df_1["value"], color='darkblue')
plt.xlabel("Year")
plt.ylabel("Number of Ships")
plt.title("Number of Ships in EU Over Time")
plt.grid(False)
plt.show()


df_NO = df[
    (df["geo"] == "NO") &
    (df["gear"] == "Total") &
    (df["unit"] == "GT") &
    (df["eng_pow"] == "TOTAL")
]
#print(df_country.head())
# Sort by year
df_NO = df_NO.sort_values("year")

# Plot
plt.figure(figsize=(10,6))
plt.bar(df_NO["year"], df_NO["value"], color='darkblue')
plt.xlabel("Year")
plt.ylabel("Total Kilowatt")
plt.title("Kilowatts in NO Over Time")
plt.grid(False)
plt.show()

import pandas as pd
import matplotlib.pyplot as plt

# Filter
df_filtered = df[
    (df["gear"] == "Total") &
    (df["unit"] == "NR") &
    (df["eng_pow"] == "TOTAL")
]

# Percent change per country
percentage_changes = []
for country in df_filtered["geo"].unique():
    df_country = df_filtered[df_filtered["geo"] == country].sort_values("year")
    if len(df_country) >= 6:
        first_3 = df_country["value"].iloc[:3].mean()
        last_3 = df_country["value"].iloc[-3:].mean()
        pct_change = ((last_3 - first_3) / first_3) * 100
        percentage_changes.append({"Country": country, "Percent Change": pct_change})

df_changes = pd.DataFrame(percentage_changes)

# Remove EU row from bar plot
df_no_eu = df_changes[df_changes["Country"] != "EU"].copy()
df_no_eu = df_no_eu.sort_values("Percent Change", ascending=False)
avg_value = df_no_eu["Percent Change"].mean()

# Color logic (EU removed, so only pos/neg)
colors = ["red" if p > 0 else "green" for p in df_no_eu["Percent Change"]]

# Plot
plt.figure(figsize=(12, 6))
plt.bar(df_no_eu["Country"], df_no_eu["Percent Change"], color=colors)
plt.axhline(y=avg_value, linewidth=4, linestyle="-", label="EU Average")
plt.ylabel("% Change in Gross-Tonage")
plt.xlabel("Country")
plt.title("Percentage Change in Gross-Tonage Between First 3 and Last 3 Years")
plt.xticks(rotation=45)
plt.grid(axis="y")
plt.grid(False)
plt.legend()
plt.tight_layout()
plt.show()
df_IE_gears = df[
    (df["geo"] == "IE") &
    (df["unit"] == "NR") &
    (df["gear"] != "Total")
]

# year as index, gear as columns and values
df_pivot = df_IE_gears.pivot_table(
    index="year",
    columns="gear",
    values="value",
    aggfunc="sum"
).fillna(0)

# LinePlot
plt.figure(figsize=(12,6))
for gear in df_pivot.columns:
    plt.plot(df_pivot.index, df_pivot[gear], marker='o',markersize = 4, label=gear)

plt.xlabel("Year")
plt.ylabel("Number of Fishing Gears")
plt.title("Evolution of Fishing Gears in Ireland Over Time")
plt.legend(title="Fishing Gears", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True, alpha = 0.2)
plt.tight_layout()
plt.show()
import matplotlib.pyplot as plt

# Filter für Irland, Gesamtfanggeräte, ohne Total
df_IE_num = df[
    (df["geo"] == "NO") &
    (df["gear"] == "Total") &
    (df["unit"] == "NR") &
    (df["eng_pow"] == "TOTAL")
].sort_values("year")

df_IE_kw = df[
    (df["geo"] == "NO") &
    (df["gear"] == "Total") &
    (df["unit"] == "GT") &
    (df["eng_pow"] == "TOTAL")
].sort_values("year")
#
# Plot
# fig, ax1 = plt.subplots(figsize=(12,6))
#
# # Linie für Anzahl der Schiffe
# ax1.plot(df_IE_num["year"], df_IE_num["value"], color='blue', marker='o', label="Number of Ships")
# ax1.set_xlabel("Year")
# ax1.set_ylabel("Number of Ships", color='blue')
# ax1.tick_params(axis='y', labelcolor='blue')
#
# # Zweite Achse für Kilowatt
# ax2 = ax1.twinx()
# ax2.plot(df_IE_kw["year"], df_IE_kw["value"], color='red', marker='*', label="Kilowatts")
# ax2.set_ylabel("Total Kilowatts", color='red')
# ax2.tick_params(axis='y', labelcolor='red')
#
# # Titel und Legende
# fig.suptitle("Number of Ships and Total Kilowatts in Norway Over Time")
# fig.tight_layout()
# fig.legend(loc="upper left", bbox_to_anchor=(0.15,0.85))
# plt.show()
df_num_norm = df_IE_num["value"] / df_IE_num["value"].iloc[0]
df_kw_norm = df_IE_kw["value"] / df_IE_kw["value"].iloc[0]

plt.figure(figsize=(12,6))
plt.plot(df_IE_num["year"], df_num_norm, label="Number of Ships (normalized)", marker='o')
plt.plot(df_IE_kw["year"], df_kw_norm, label="Gross-Tonage (normalized)", marker='*')
plt.xlabel("Year")
plt.ylabel("Normalized Value")
plt.title("Norways Trend in Number of Ships and Gross-Tonage from whole Fleet (normalized)")
plt.legend()
plt.grid(True, alpha = 0.2)
plt.show()

import matplotlib.pyplot as plt

# Filter für Irland, Gesamtfanggeräte, ohne Total
df_IE_num = df[
    (df["geo"] == "NO") &
    (df["gear"] == "Total") &
    (df["unit"] == "NR") &
    (df["eng_pow"] == "TOTAL")
].sort_values("year")

df_IE_kw = df[
    (df["geo"] == "NO") &
    (df["gear"] == "Total") &
    (df["unit"] == "KW") &
    (df["eng_pow"] == "TOTAL")
].sort_values("year")
#
# Plot
fig, ax1 = plt.subplots(figsize=(12,6))

# Linie für Anzahl der Schiffe
ax1.plot(df_IE_num["year"], df_IE_num["value"], color='blue', marker='o', label="Number of Ships")
ax1.set_xlabel("Year")
ax1.set_ylabel("Number of Ships", color='blue')
ax1.tick_params(axis='y', labelcolor='blue')

# Zweite Achse für Kilowatt
ax2 = ax1.twinx()
ax2.plot(df_IE_kw["year"], df_IE_kw["value"], color='red', marker='*', label="Kilowatts")
ax2.set_ylabel("Total Kilowatts", color='red')
ax2.tick_params(axis='y', labelcolor='red')

# Titel und Legende
fig.suptitle("Number of Ships and Total Kilowatts in Norway Over Time")
fig.tight_layout()
fig.legend(loc="upper left", bbox_to_anchor=(0.15,0.85))
plt.show()

