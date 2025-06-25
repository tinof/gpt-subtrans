import argparse
import logging
import os
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def main():
    # Use parse_known_args to separate batch arguments from provider arguments
    parser = argparse.ArgumentParser(
        description="Batch process SRT files in subdirectories using a specified gpt-subtrans provider.",
        add_help=False,
    )
    parser.add_argument("root_dir", help="Root directory containing subfolders with SRT files.")
    parser.add_argument("--target_language", required=True, help="Target language for translation.")
    parser.add_argument(
        "--instructionfile",
        default=None,
        help="Path to the instruction file for the provider.",
    )
    parser.add_argument(
        "--provider_command",
        default="gpt-subtrans",
        help="The provider command to execute (e.g., gpt-subtrans, gemini-subtrans).",
    )
    parser.add_argument("--help", action="help", help="Show this help message and exit.")

    args, unknown_args = parser.parse_known_args()

    logging.info(f"Starting batch processing in directory: {args.root_dir}")
    logging.info(f"Provider command: {args.provider_command}")
    logging.info(f"Target language: {args.target_language}")
    if args.instructionfile:
        logging.info(f"Using instruction file: {args.instructionfile}")
    if unknown_args:
        logging.info(f"Passing additional arguments to provider: {' '.join(unknown_args)}")

    processed_files = 0
    failed_files = 0

    # Traverse all subfolders under the root directory
    for subdir, dirs, files in os.walk(args.root_dir):
        for file in files:
            # Check if the file ends with '.srt'
            if file.lower().endswith(".srt"):
                src_file = os.path.join(subdir, file)
                logging.info(f"Processing file: {src_file}")

                try:
                    # Build the command for the provider script
                    command = [
                        args.provider_command,
                        src_file,
                        "--target_language",
                        args.target_language,
                    ]
                    if args.instructionfile:
                        # Ensure the instruction file path is valid
                        if not os.path.isfile(args.instructionfile):
                            logging.warning(
                                f"Instruction file not found: {args.instructionfile}. Skipping for {src_file}."
                            )
                            # Decide whether to skip or proceed without it. Let's proceed without.
                            # failed_files += 1
                            # continue
                        else:
                            command.extend(["--instructionfile", args.instructionfile])

                    # Add any unknown arguments captured earlier
                    command.extend(unknown_args)

                    logging.debug(f"Executing command: {' '.join(command)}")

                    # Call the provider command
                    result = subprocess.run(command, check=True, capture_output=True, text=True)
                    logging.info(f"Successfully processed: {src_file}")
                    logging.debug(f"Provider output for {src_file}:\n{result.stdout}")
                    processed_files += 1

                except FileNotFoundError:
                    logging.error(f"Provider command '{args.provider_command}' not found. Is it installed and in PATH?")
                    # Stop processing if the command isn't found
                    return
                except subprocess.CalledProcessError as e:
                    logging.error(f"Failed to process {src_file}. Error: {e}")
                    logging.error(f"Provider stderr:\n{e.stderr}")
                    failed_files += 1
                except Exception as e:
                    logging.error(f"An unexpected error occurred while processing {src_file}: {e}")
                    failed_files += 1

    logging.info("Batch processing finished.")
    logging.info(f"Successfully processed: {processed_files} files.")
    logging.info(f"Failed to process: {failed_files} files.")


if __name__ == "__main__":
    main()
