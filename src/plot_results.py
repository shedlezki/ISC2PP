import pandas as pd
import matplotlib.pyplot as plt
import argparse
import ast
import numpy as np

def parse_args():
    parser = argparse.ArgumentParser(description='Plot CSV data columns')
    parser.add_argument('csv_file', type=str, help='Path to the CSV file')
    parser.add_argument('--exclude', nargs='+', default=['EID'], 
                      help='Columns to exclude from plotting')
    return parser.parse_args()

def clean_data(df):
    # Convert string representations of lists/tuples to actual Python objects
    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                df[col] = df[col].apply(ast.literal_eval)
            except:
                continue
    return df

def plot_column(data, column, output_dir='plots'):
    plt.figure(figsize=(10, 6))
    
    if isinstance(data[column].iloc[0], (list, tuple)):
        # For columns containing lists/tuples
        if isinstance(data[column].iloc[0][0], tuple):
            # Handle Potential column specifically
            x_vals = [point[0] for row in data[column] for point in row]
            y_vals = [point[1] for row in data[column] for point in row]
            plt.scatter(x_vals, y_vals, alpha=0.5)
            plt.xlabel('Player 1')
            plt.ylabel('Player 2')
        else:
            # For other list/tuple columns
            for i, row in enumerate(data[column]):
                if isinstance(row, (list, tuple)):
                    plt.plot(range(len(row)), row, 'o-', alpha=0.5, label=f'Row {i}')
    else:
        # For numeric columns
        if data[column].dtype in ['float64', 'int64']:
            plt.hist(data[column], bins=30, alpha=0.7)
            plt.axvline(data[column].mean(), color='red', linestyle='dashed', linewidth=1)
            plt.axvline(data[column].median(), color='green', linestyle='dashed', linewidth=1)
        # For boolean columns
        elif data[column].dtype == 'bool':
            counts = data[column].value_counts()
            plt.bar(counts.index.astype(str), counts.values)
    
    plt.title(f'{column} Distribution')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Save plot
    plt.savefig(f'{output_dir}/{column.replace("/", "_")}.png')
    plt.close()

def main():
    args = parse_args()
    
    # Read CSV file
    df = pd.read_csv(args.csv_file)
    
    # Clean the data
    df = clean_data(df)
    
    # Create output directory if it doesn't exist
    import os
    os.makedirs('plots', exist_ok=True)
    
    # Plot each column except excluded ones
    for column in df.columns:
        if column not in args.exclude:
            try:
                print(f"Plotting {column}...")
                plot_column(df, column)
            except Exception as e:
                print(f"Error plotting {column}: {str(e)}")

if __name__ == "__main__":
    main() 