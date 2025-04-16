import os
import logging

# Use relative imports now that this is part of a package
from .subtrans_common import InitLogger, CreateArgParser, CreateOptions, CreateTranslator, CreateProject

from PySubtitle.Options import Options
from PySubtitle.SubtitleProject import SubtitleProject
from PySubtitle.SubtitleTranslator import SubtitleTranslator

def main():
    provider = "Mistral"
    default_model = os.getenv('MISTRAL_MODEL') or "open-mistral-nemo"

    parser = CreateArgParser(f"Translates an SRT file using an Mistral model")
    parser.add_argument('-k', '--apikey', type=str, default=None, help=f"Your Mistral API Key (https://console.mistral.ai/api-keys/)")
    parser.add_argument('-m', '--model', type=str, default=None, help="The model to use for translation")
    parser.add_argument('--server_url', type=str, default=None, help="Server URL (leave blank for default).")
    args = parser.parse_args()

    logger_options = InitLogger("mistral-subtrans", args.debug)

    try:
        options : Options = CreateOptions(
            args,
            provider,
            server_url=args.server_url,
            model=args.model or default_model
        )

        # Create a translator with the provided options
        translator : SubtitleTranslator = CreateTranslator(options)

        # Create a project for the translation
        project : SubtitleProject = CreateProject(options, args)

        # Translate the subtitles
        project.TranslateSubtitles(translator)

        if project.write_project:
            logging.info(f"Writing project data to {str(project.projectfile)}")
            project.WriteProjectFile()

    except Exception as e:
        logging.error(f"Translation failed: {e}", exc_info=True)
        print(f"Error: {e}")
        # import sys
        # sys.exit(1)

if __name__ == '__main__':
    main()
