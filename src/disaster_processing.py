import pandas as pd
import numpy as np
import json
import ast
import os
from config import ALL_DISTRICTS

def load_emdat_data(file_path='data/processed/emdat_malawi.csv'):
    """
    Load and process EM-DAT disaster data (CSV format).
    Extracts district-level events from 'GADM Admin Units' or 'Location'.
    """
    if not os.path.exists(file_path):
        # Return empty DataFrame if file missing
        return pd.DataFrame(columns=['district', 'year', 'type', 'total_affected'])

    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading EM-DAT file: {e}")
        return pd.DataFrame()

    # Relevant columns
    # 'Disaster Type' (e.g. Flood, Storm)
    # 'Start Year'
    # 'GADM Admin Units' (JSON list of district dicts)
    # 'Location' (Fallback text)
    # 'Total Affected'
    
    processed_events = []

    for idx, row in df.iterrows():
        d_type = row.get('Disaster Type', 'Unknown')
        year = row.get('Start Year', np.nan)
        gadm_json = row.get('GADM Admin Units', np.nan)
        affected = row.get('Total Affected', 0)  # Aggregated for the whole event
        
        # Identify districts involved in this event
        districts_found = set()

        # Strategy 1: GADM JSON parsing (e.g. [{"adm2_name":"Karonga"}, ...])
        if pd.notna(gadm_json):
            try:
                # It might be a string representation of a list
                if isinstance(gadm_json, str):
                    units = json.loads(gadm_json)
                else:
                    units = gadm_json # Already a list?
                
                if isinstance(units, list):
                    for unit in units:
                        if 'adm2_name' in unit:
                            dist_name = unit['adm2_name']
                            # Normalize name (e.g. "Nkhata Bay" vs "Nkhata_Bay")
                            dist_name_clean = dist_name.strip()
                            if dist_name_clean in ALL_DISTRICTS:
                                districts_found.add(dist_name_clean)
            except Exception as e:
                # JSON parse error, ignore
                pass

        # Strategy 2: Fallback to 'Location' text search if JSON failed or was empty
        if not districts_found and pd.notna(row.get('Location')):
            loc_text = str(row['Location'])
            for clean_dist in ALL_DISTRICTS.keys():
                if clean_dist in loc_text:
                    districts_found.add(clean_dist)
        
        # If still no districts found, mark as 'Unknown' or 'National' (skip for district map)
        if not districts_found:
            continue

        # Distribute the event to all found districts
        # Note: 'Total Affected' is usually for the whole event, hard to split.
        # We will just record the event occurrence.
        for dist in districts_found:
            processed_events.append({
                'district': dist,
                'year': int(year) if pd.notna(year) else 0,
                'type': d_type,
                'affected': affected # Keeping raw total, knowing it's duplicated across districts
            })

    result_df = pd.DataFrame(processed_events)
    return result_df
