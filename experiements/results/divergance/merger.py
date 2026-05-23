import pandas as pd
import glob

def merge_csv(files, output_file):
    # Read and collect all dataframes
    df_list = [pd.read_csv(file) for file in files]
    
    # Concatenate them into one
    merged_df = pd.concat(df_list, ignore_index=True)
    
    # Save to a new CSV
    merged_df.to_csv(output_file, index=False)
    print(f"Merged {len(files)} files into '{output_file}'")

if __name__ == "__main__":

    # Example: get all CSV files in current directory
    files = glob.glob("*.csv")
    print("Files to merge:", files)
    # Or specify manually:
    # files = ["file1.csv", "file2.csv", "file3.csv"]
    
    merge_csv(files, "merged_output.csv")
