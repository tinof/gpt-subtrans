import os
import logging
import sys # Import sys for exit

# Use absolute imports from the package root
from PySubtitle.Helpers.cli_utils import InitLogger, CreateArgParser, CreateOptions, CreateTranslator, CreateProject
from PySubtitle.Options import Options
from PySubtitle.SubtitleProject import SubtitleProject
from PySubtitle.SubtitleTranslator import SubtitleTranslator

def gemini_main():
    """ Entry point for the gemini-subtrans command """
    provider = "Gemini"
    # Default model name might need adjustment based on Gemini's current offerings
    default_model = os.getenv('GEMINI_MODEL') # Removed fallback to "Gemini 2.0 Flash" to rely on provider defaults if env var not set

    parser = CreateArgParser(f"Translates an SRT file using Google Gemini")
    # Add provider-specific arguments
    parser.add_argument('-k', '--apikey', type=str, default=os.getenv('GEMINI_API_KEY'), help=f"Your Gemini API Key (or set GEMINI_API_KEY env var)")
    parser.add_argument('-m', '--model', type=str, default=default_model, help="The Gemini model to use for translation (e.g., gemini-1.5-flash-latest)")
    args = parser.parse_args()

    # Use the command name for the log filename
    logger_options = InitLogger("gemini-subtrans", args.debug)

    try:
        # Pass model explicitly to CreateOptions
        options : Options = CreateOptions(args, provider, model=args.model)

        # Validate API key presence using the get method
        if not options.get('api_key'):
            raise ValueError("Gemini API Key is required. Provide via -k argument or GEMINI_API_KEY environment variable.")

        translator : SubtitleTranslator = CreateTranslator(options)
        project : SubtitleProject = CreateProject(options, args)

        project.TranslateSubtitles(translator)

        if project.write_project:
            logging.info(f"Writing project data to {str(project.projectfile)}")
            project.WriteProjectFile()

        logging.info("Gemini translation process completed.")

    except Exception as e:
        logging.error(f"Translation failed: {e}", exc_info=True)
        print(f"\nError: {e}\n", file=sys.stderr) # Print errors to stderr
        sys.exit(1) # Exit with a non-zero code on error

# Add other main functions here as needed, e.g.:
# def openai_main(): ...
# def claude_main(): ...

# Note: The if __name__ == '__main__': block is not needed here
# as these functions are intended to be called via the entry points.
