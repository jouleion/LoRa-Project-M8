import os
import pandas as pd
import matplotlib.pyplot as plt
import folium

# ────────────────────────────────────────────────────────────────────────────────
# CONFIG – adjust paths if your layout differs
# ────────────────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(__file__)
DATA_DIR   = os.path.join(BASE_DIR, "data")
GW_CSV     = os.path.join(DATA_DIR, "gateway_locations.csv")
SENS_CSV   = os.path.join(DATA_DIR, "sensor_locations.csv")
MAP_OUT    = os.path.join(BASE_DIR, "sensor_gateway_map.html")
# ────────────────────────────────────────────────────────────────────────────────

def load_data():
    gateways = pd.read_csv(GW_CSV).rename(columns=str.strip)
    sensors  = pd.read_csv(SENS_CSV).rename(columns=str.strip)
    return gateways, sensors

def summary_stats(gateways, sensors):
    print("\n=== BASIC COUNTS ===")
    print(f"Gateways : {len(gateways)}")
    print(f"Sensors  : {len(sensors)}\n")

    if "Roomname" in sensors:
        sensors["building_code"] = sensors["Roomname"].str[:2]
        print("Sensors per building code:\n",
              sensors["building_code"].value_counts(), "\n")

    if "Mazemap_Floor" in sensors:
        print("Sensors per floor:\n",
              sensors["Mazemap_Floor"].value_counts().sort_index(), "\n")

def plot_eda(gateways, sensors):
    valid_alt = sensors["Altitude_Masl"].notna().sum()
    total_alt = len(sensors)
    print(f"Sensor altitude: {valid_alt}/{total_alt} non-null "
          f"({valid_alt/total_alt:.1%})\n")

    # Gateway altitude
    plt.figure(figsize=(6,4))
    gateways["altitude"].hist(bins=10)
    plt.title("Gateway Altitude Distribution (m a.s.l.)")
    plt.xlabel("Altitude (m)")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.show()

    # Sensors per floor
    if "Mazemap_Floor" in sensors:
        plt.figure(figsize=(6,4))
        sensors["Mazemap_Floor"].value_counts().sort_index().plot.bar()
        plt.title("Sensors per Floor")
        plt.xlabel("Floor")
        plt.ylabel("Count")
        plt.tight_layout()
        plt.show()

    # Top 10 Rooms
    if "Roomname" in sensors:
        plt.figure(figsize=(8,4))
        sensors["Roomname"].value_counts().head(10).plot.bar()
        plt.title("Top 10 Sensor Rooms")
        plt.xlabel("Room Name")
        plt.ylabel("Sensor Count")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.show()

def make_map(gateways, sensors):
    # drop any sensors with missing coords
    sensors_clean = sensors.dropna(subset=["St_Y", "St_X"])

    # compute map center
    avg_lat = (gateways["latitude"].mean() + sensors_clean["St_Y"].mean()) / 2
    avg_lon = (gateways["longitude"].mean() + sensors_clean["St_X"].mean()) / 2
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=15)

    # gateways
    for _, row in gateways.iterrows():
        folium.Marker(
            [row["latitude"], row["longitude"]],
            popup=f"Gateway: {row['name']}",
            icon=folium.Icon(color="blue", icon="wifi")
        ).add_to(m)

    # sensors
    for _, row in sensors_clean.iterrows():
        folium.CircleMarker(
            [row["St_Y"], row["St_X"]],
            radius=4, color="green", fill=True, fill_opacity=0.7,
            popup=f"Sensor: {row['Sensor_Eui']}"
        ).add_to(m)

    m.save(MAP_OUT)
    print(f"Interactive map written to {MAP_OUT}")

if __name__ == "__main__":
    gw_df, sens_df = load_data()
    summary_stats(gw_df, sens_df)
    plot_eda(gw_df, sens_df)
    make_map(gw_df, sens_df)
