import os
import pandas as pd
from sdv.io.local import CSVHandler
from sdv.metadata import Metadata
from sdv.multi_table import HMASynthesizer
from sdv.evaluation.multi_table import evaluate_quality, get_column_plot


def generate(folder_name: str):
    """Generate synthetic data based on real data using SDV Synthesizer."""
    # Check if the data folder exists
    if not os.path.exists(folder_name):
        raise FileNotFoundError(f"The folder {folder_name} does not exist.")

    # Check if metadata file exists
    metadata_file = os.path.join(folder_name, "metadata.json")
    if not os.path.exists(metadata_file):
        raise FileNotFoundError(f"The metadata file {metadata_file} does not exist.")

    try:
        # Load CSV data files from the specified folder
        connector = CSVHandler()
        data = connector.read(folder_name=folder_name)

        # Load metadata
        metadata = Metadata.load_from_json(metadata_file)

        # Create and train synthesizer
        synthesizer = HMASynthesizer(metadata)
        synthesizer.fit(data)

        # Generate synthetic data
        synthetic_data = synthesizer.sample(scale=1)

        # Save synthetic data to CSV files
        os.makedirs("synthetic_data", exist_ok=True)
        for table_name, df in synthetic_data.items():
            output_file = os.path.join("synthetic_data", f"{table_name}.csv")
            df.to_csv(output_file, index=False)

        return f"Data generated successfully and saved in 'synthetic_data' folder with {len(synthetic_data)} tables named as {list(synthetic_data.keys())} CSV files."

    # Handle exceptions during data generation
    except Exception as e:
        raise RuntimeError(f"An error occurred while generating synthetic data: {e}")


def evaluate(folder_name: str):
    """Evaluate the quality of synthetic data compared to real data."""
    # Check if real and synthetic data folders exist
    if not os.path.exists(folder_name):
        raise FileNotFoundError(f"Real data folder not found: {folder_name}")
    if not os.path.exists("synthetic_data"):
        raise FileNotFoundError(
            f"Synthetic data folder not found. Please generate synthetic data first using the SDV generate method."
        )

    # Check if metadata file exists
    metadata_file = os.path.join(folder_name, "metadata.json")
    if not os.path.exists(metadata_file):
        raise FileNotFoundError(f"The metadata file {metadata_file} does not exist.")

    try:
        # Load metadata
        metadata = Metadata.load_from_json(metadata_file)

        # Get list of tables from metadata
        table_names = metadata.tables

        # Create data dictionaries
        real_data_dict = {}
        synthetic_data_dict = {}

        # Load each table from CSV files
        for table_name in table_names:
            real_path = os.path.join(folder_name, f"{table_name}.csv")
            synthetic_path = os.path.join("synthetic_data", f"{table_name}.csv")

            if not os.path.exists(real_path):
                raise FileNotFoundError(f"Real data file not found: {real_path}")
            if not os.path.exists(synthetic_path):
                raise FileNotFoundError(
                    f"Synthetic data file not found: {synthetic_path}"
                )

            real_data_dict[table_name] = pd.read_csv(real_path)
            synthetic_data_dict[table_name] = pd.read_csv(synthetic_path)

        # Run evaluation
        quality_report = evaluate_quality(
            real_data=real_data_dict,
            synthetic_data=synthetic_data_dict,
            metadata=metadata,
            verbose=False,
        )

        # Get overall score and properties
        overall_score = quality_report.get_score()
        properties_df = quality_report.get_properties()
        properties = properties_df.to_dict(orient="records")

        # Return metrics
        return {"Overall Score": overall_score, "Properties": properties}

    # Handle exceptions during evaluation
    except Exception as e:
        raise RuntimeError(f"An error occurred during evaluation: {e}")


def visualize(
    folder_name: str,
    table_name: str,
    column_name: str,
    visualization_folder: str = "evaluation_plots",
):
    """Generate visualization comparing real and synthetic data for a specific column."""
    # Check if real and synthetic data folders exist
    if not os.path.exists(folder_name):
        raise FileNotFoundError(f"Real data folder not found: {folder_name}")
    if not os.path.exists("synthetic_data"):
        raise FileNotFoundError(
            "Synthetic data folder not found. Please generate synthetic data first."
        )

    # Check if metadata file exists
    metadata_file = os.path.join(folder_name, "metadata.json")
    if not os.path.exists(metadata_file):
        raise FileNotFoundError(f"The metadata file {metadata_file} does not exist.")

    try:
        # Load metadata
        metadata = Metadata.load_from_json(metadata_file)

        # Verify table exists
        if table_name not in metadata.tables:
            raise ValueError(f"Table '{table_name}' not found in metadata")

        # Load real and synthetic data for the specified table
        real_path = os.path.join(folder_name, f"{table_name}.csv")
        synthetic_path = os.path.join("synthetic_data", f"{table_name}.csv")

        if not os.path.exists(real_path):
            raise FileNotFoundError(f"Real data file not found: {real_path}")
        if not os.path.exists(synthetic_path):
            raise FileNotFoundError(f"Synthetic data file not found: {synthetic_path}")

        real_data = pd.read_csv(real_path)
        synthetic_data = pd.read_csv(synthetic_path)

        # Verify column exists
        if column_name not in real_data.columns:
            raise ValueError(
                f"Column '{column_name}' not found in table '{table_name}'"
            )

        # Create data dictionaries as required by get_column_plot
        real_data_dict = {table_name: real_data}
        synthetic_data_dict = {table_name: synthetic_data}

        # Create visualization folder if it doesn't exist
        os.makedirs(visualization_folder, exist_ok=True)

        # Generate column plot
        fig = get_column_plot(
            real_data=real_data_dict,
            synthetic_data=synthetic_data_dict,
            metadata=metadata,
            table_name=table_name,
            column_name=column_name,
        )

        if fig is None:
            raise ValueError(
                f"Could not generate visualization for {table_name}.{column_name}"
            )

        # Create filename
        safe_column_name = column_name.replace(" ", "_").replace("/", "_")
        filename = f"{table_name}_{safe_column_name}.png"
        filepath = os.path.join(visualization_folder, filename)

        # Save the figure and return success message
        fig.write_image(filepath)
        return f"Visualization for {table_name}.{column_name} saved successfully at {os.path.abspath(filepath)}"
    
    # Handle exceptions during visualization
    except Exception as e:
        raise RuntimeError(f"An error occurred during visualization: {e}")
