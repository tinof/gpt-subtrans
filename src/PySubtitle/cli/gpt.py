import logging
import os
import sys

from PySubtitle.cli.common import CreateArgParser, CreateOptions, CreateProject, CreateTranslator, InitLogger
from PySubtitle.Options import Options
from PySubtitle.SubtitleProject import SubtitleProject
from PySubtitle.SubtitleTranslator import SubtitleTranslator


def main():
    """Main entry point for gpt-subtrans command"""
    # We'll write separate scripts for other providers
    provider = "OpenAI"
    default_model = os.getenv("OPENAI_MODEL") or "gpt-4o"

    parser = CreateArgParser("Translates an SRT file using an OpenAI model")
    parser.add_argument(
        "-k", "--apikey", type=str, default=None, help="Your OpenAI API Key (https://platform.openai.com/account/api-keys)"
    )
    parser.add_argument("-b", "--apibase", type=str, default="https://api.openai.com/v1", help="API backend base address.")
    parser.add_argument("-m", "--model", type=str, default=None, help="The model to use for translation")
    parser.add_argument(
        "--httpx",
        action="store_true",
        help="Use the httpx library for custom api_base requests. May help if you receive a 307 redirect error.",
    )
    parser.add_argument("--proxy", type=str, default=None, help="SOCKS proxy URL (e.g., socks://127.0.0.1:1089)")
    args = parser.parse_args()

    InitLogger("gpt-subtrans", args.debug)

    try:
        options: Options = CreateOptions(
            args, provider, use_httpx=args.httpx, api_base=args.apibase, proxy=args.proxy, model=args.model or default_model
        )

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
