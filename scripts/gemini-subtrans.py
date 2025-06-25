import logging
import os

from PySubtitle.Options import Options
from PySubtitle.SubtitleProject import SubtitleProject
from PySubtitle.SubtitleTranslator import SubtitleTranslator

# Use relative imports now that this is part of a package
from .subtrans_common import (
    CreateArgParser,
    CreateOptions,
    CreateProject,
    CreateTranslator,
    InitLogger,
)


def main():
    provider = "Gemini"
    default_model = os.getenv("GEMINI_MODEL") or "Gemini 2.0 Flash"

    parser = CreateArgParser("Translates an SRT file using a Google Gemini model")
    parser.add_argument(
        "-k",
        "--apikey",
        type=str,
        default=None,
        help="Your Gemini API Key (https://makersuite.google.com/app/apikey)",
    )
    parser.add_argument("-m", "--model", type=str, default=None, help="The model to use for translation")
    args = parser.parse_args()

    logger_options = InitLogger("gemini-subtrans", args.debug)

    try:
        options: Options = CreateOptions(args, provider, model=args.model or default_model)

        # Create a project for the translation
        project: SubtitleProject = CreateProject(options, args)

        # Create a translator with the provided options
        translator: SubtitleTranslator = CreateTranslator(options)

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


if __name__ == "__main__":
    main()
