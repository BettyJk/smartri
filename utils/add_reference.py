import json
import os

def add_reference(new_entry, json_path="data/Planning_Inventaire_Integral_clean.json"):
    # Load existing data
    if not os.path.exists(json_path):
        data = []
    else:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    # Add new entry
    data.append(new_entry)

    # Custom serializer for non-serializable objects
    def default_serializer(obj):
        try:
            import pandas as pd
            import numpy as np
            if isinstance(obj, (pd.Timestamp, np.datetime64)):
                return str(obj)
        except ImportError:
            pass
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        return str(obj)

    # Write back to file
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=default_serializer)
    return True
