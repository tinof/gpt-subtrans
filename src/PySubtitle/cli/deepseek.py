import logging
import os
import sys

from PySubtitle.cli.common import CreateArgParser, CreateOptions, CreateProject, CreateTranslator, InitLogger
from PySubtitle.Options import Options
from PySubtitle.SubtitleProject import SubtitleProject
from PySubtitle.SubtitleTranslator import SubtitleTranslator


def main():
    """Main entry point for deepseek-subtrans command"""
    provider = "DeepSeek"
    default_model = os.getenv("DEEPSEEK_MODEL") or "deepseek-chat"

    parser = CreateArgParser("Translates an SRT file using an DeepSeek model")
    parser.add_argument(
        "-k", "--apikey", type=str, default=None, help="Your DeepSeek API Key (https://platform.deepseek.com/api_keys)"
    )
    parser.add_argument("-b", "--apibase", type=str, default="https://api.deepseek.com", help="API backend base address.")
    parser.add_argument("-m", "--model", type=str, default=None, help="The model to use for translation")
    args = parser.parse_args()

    InitLogger("deepseek-subtrans", args.debug)

    try:
        options: Options = CreateOptions(args, provider, api_base=args.apibase, model=args.model or default_model)

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
