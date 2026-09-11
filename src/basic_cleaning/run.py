#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""
import argparse
import logging
import wandb
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    ######################
    # YOUR CODE HERE     #
    ######################

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    logger.info(f"Getting artifact: {args.input_artifact}")

    artifact_local_path = run.use_artifact(args.input_artifact).file()
    df = pd.read_csv(artifact_local_path)

    logger.info("Input Artifact has %s rows and %s columns", *df.shape)

    logger.info(f"remove duplicate rows")
    df.drop_duplicates(inplace=True)

    logger.info(f"remove rows with missing prices")
    df.dropna(subset=['price'], inplace=True)

    logger.info(f"Filtering data between {args.min_price} and {args.max_price}")
    min_price = args.min_price
    max_price = args.max_price
    idx = df['price'].between(min_price, max_price)
    df = df[idx].copy()

    logger.info(f"Filtering data outside NYC boundaries")
    idx = df["longitude"].between(-74.25, -73.50) & df["latitude"].between(40.5, 41.2)
    df = df[idx].copy()

    logger.info("Cleaned data has %s rows and %s columns", *df.shape)

    # Save the cleaned data to a new CSV file
    output_artifact_path = f"{args.output_artifact}"

    logger.info(f"Saving cleaned data to {output_artifact_path}")
    df.to_csv(output_artifact_path, index=False)

    # Log the output artifact to W&B
    artifact = wandb.Artifact(
        name=args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )
    artifact.add_file(output_artifact_path)
    run.log_artifact(artifact)

    logger.info(f"Uploaded cleaned data to W&B as artifact: {args.output_artifact}")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")


    ## For each parameter, update the type and description
    ## INSERT TYPE HERE: str, float or int,
    ## INSERT DESCRIPTION HERE,

    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="Input data file name",
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str,
        help="Output file name",
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help="Output artifact type",
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help="Description of the output artifact",
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help="Minimum price for filtering",
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type=float,
        help="Maximum price for filtering",
        required=True
    )


    args = parser.parse_args()

    go(args)
