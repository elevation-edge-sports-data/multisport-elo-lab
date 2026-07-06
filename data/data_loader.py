def load_schedule(path):
    df = pd.read_csv(path)
    required = [...]
    assert all(col in df.columns for col in required)
    return df.sort_values(["season", "week"]).reset_index(drop=True)