import logging
import sys

from PySubtitle.cli.common import CreateArgParser, CreateOptions, CreateProject, CreateTranslator, InitLogger
from PySubtitle.Options import Options
from PySubtitle.SubtitleProject import SubtitleProject
from PySubtitle.SubtitleTranslator import SubtitleTranslator


def main():
    """Main entry point for llm-subtrans command"""
    provider = "Custom Server"

    # Parse command line arguments
    parser = CreateArgParser("Translates an SRT file using an AI model running on a local server")
    parser.add_argument(
        "-s", "--server", type=str, default=None, help="Address of the server including port (e.g. http://localhost:1234)"
    )
    parser.add_argument(
        "-e", "--endpoint", type=str, default=None, help="Endpoint to call on  the server (e.g. /v1/completions)"
    )
    parser.add_argument("-k", "--apikey", type=str, default=None, help="API Key, if required")
    parser.add_argument("-m", "--model", type=str, default=None, help="Model to use if the server allows it to be specified")
    parser.add_argument("--chat", action="store_true", help="Use chat format requests for the endpoint")
    parser.add_argument(
        "--systemmessages", action="store_true", help="Indicates that the endpoint supports system messages in chat requests"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=None,
        help="Request timeout in seconds for server calls (defaults to 300)",
    )
    args = parser.parse_args()

    InitLogger("llm-subtrans", args.debug)

    try:
        options: Options = CreateOptions(
            args,
            provider,
            server_address=args.server,
            endpoint=args.endpoint,
            model=args.model,
            supports_conversation=args.chat,
            supports_system_messages=args.systemmessages,
            timeout=args.timeout,
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
