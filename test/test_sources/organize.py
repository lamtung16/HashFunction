import glob
import pandas as pd


def organize_csv_files(directory="."):
  """Reads all CSV files in the specified directory, removes duplicates,

  sorts them by exp_date and max_connections ascending, and overwrites the files.
  """
  # Find all CSV files in the folder
  csv_files = glob.glob(f"{directory}/*.csv")

  if not csv_files:
    print("No CSV files found in the directory.")
    return

  for file_path in csv_files:
    print(f"Processing: {file_path}")
    try:
      # Read the CSV file
      df = pd.read_csv(file_path)

      # Define expected columns
      expected_cols = [
          "host",
          "username",
          "password",
          "status",
          "created_at",
          "exp_date",
          "active_cons",
          "max_connections",
      ]

      # Check if all required columns are present
      if not all(col in df.columns for col in expected_cols):
        print(
            f"Skipping {file_path}: Missing one or more required columns."
        )
        continue

      # Step 1: Remove duplicates based on host, username, and password
      df = df.drop_duplicates(subset=["host", "username", "password"])

      # Step 2: Sort by priority ascending: exp_date, then max_connections
      df = df.sort_values(by=["exp_date", "max_connections"], ascending=False)

      # Overwrite the original CSV file with the organized data
      df.to_csv(file_path, index=False)
      print(f"Successfully organized and replaced: {file_path}\n")

    except Exception as e:
      print(f"Error processing {file_path}: {e}")


if __name__ == "__main__":
  # Runs on the current working directory. Change '.' if your files are elsewhere.
  organize_csv_files(".")