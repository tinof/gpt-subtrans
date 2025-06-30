import logging
import os
import sys

from PySubtitle.cli.common import CreateArgParser, CreateOptions, CreateProject, CreateTranslator, InitLogger
from PySubtitle.Options import Options
from PySubtitle.SubtitleProject import SubtitleProject
from PySubtitle.SubtitleTranslator import SubtitleTranslator


def main():
    """Main entry point for mistral-subtrans command"""
    provider = "Mistral"
    default_model = os.getenv("MISTRAL_MODEL") or "open-mistral-nemo"

    parser = CreateArgParser("Translates an SRT file using an Mistral model")
    parser.add_argument(
        "-k", "--apikey", type=str, default=None, help="Your Mistral API Key (https://console.mistral.ai/api-keys/)"
    )
    parser.add_argument("-m", "--model", type=str, default=None, help="The model to use for translation")
    parser.add_argument("--server_url", type=str, default=None, help="Server URL (leave blank for default).")
    args = parser.parse_args()

    InitLogger("mistral-subtrans", args.debug)

    try:
        options: Options = CreateOptions(args, provider, model=args.model or default_model, server_url=args.server_url)

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
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
