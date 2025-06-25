import os
import logging

# Use relative imports now that this is part of a package
from .subtrans_common import InitLogger, CreateArgParser, CreateOptions, CreateTranslator, CreateProject

from PySubtitle.Options import Options
from PySubtitle.SubtitleProject import SubtitleProject
from PySubtitle.SubtitleTranslator import SubtitleTranslator

def main():
    provider = "Claude"
    default_model = os.getenv('CLAUDE_MODEL') or "claude-3-haiku-20240307"

    parser = CreateArgParser(f"Translates an SRT file using Anthropic's Claude AI")
    parser.add_argument('-k', '--apikey', type=str, default=None, help=f"Your Anthropic API Key (https://console.anthropic.com/settings/keys)")
    parser.add_argument('-m', '--model', type=str, default=None, help="The model to use for translation")
    parser.add_argument('--proxy', type=str, default=None, help="SOCKS proxy URL (e.g., socks://127.0.0.1:1089)")
    args = parser.parse_args()

    logger_options = InitLogger("claude-subtrans", args.debug)

    try:
        options : Options = CreateOptions(args, provider, model=args.model or default_model, proxy=args.proxy)

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
        logging.error(f"Translation failed: {e}", exc_info=True)
        print(f"Error: {e}")
        # import sys
        # sys.exit(1)

if __name__ == '__main__':
    main()
