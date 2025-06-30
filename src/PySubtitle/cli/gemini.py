import os
import sys
import logging

from PySubtitle.cli.common import InitLogger, CreateArgParser, CreateOptions, CreateTranslator, CreateProject
from PySubtitle.Options import Options
from PySubtitle.SubtitleProject import SubtitleProject
from PySubtitle.SubtitleTranslator import SubtitleTranslator

def main():
    """Main entry point for gemini-subtrans command"""
    provider = "Gemini"
    default_model = os.getenv('GEMINI_MODEL') or "Gemini 2.0 Flash"

    parser = CreateArgParser(f"Translates an SRT file using a Google Gemini model")
    parser.add_argument('-k', '--apikey', type=str, default=None, help=f"Your Gemini API Key (https://makersuite.google.com/app/apikey)")
    parser.add_argument('-m', '--model', type=str, default=None, help="The model to use for translation")
    args = parser.parse_args()

    logger_options = InitLogger("gemini-subtrans", args.debug)

    try:
        options : Options = CreateOptions(args, provider, model=args.model or default_model)

        # Create a project for the translation
        project : SubtitleProject = CreateProject(options, args)

        # Create a translator with the provided options
        translator : SubtitleTranslator = CreateTranslator(options)

        # Translate the subtitles
        project.TranslateSubtitles(translator)

        if project.write_project:
            logging.info(f"Writing project data to {str(project.projectfile)}")
            project.WriteProjectFile()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
