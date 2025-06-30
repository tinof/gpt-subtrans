import logging
import os
import sys

from PySubtitle.cli.common import CreateArgParser, CreateOptions, CreateProject, CreateTranslator, InitLogger
from PySubtitle.Options import Options
from PySubtitle.SubtitleProject import SubtitleProject
from PySubtitle.SubtitleTranslator import SubtitleTranslator


def main():
    """Main entry point for azure-subtrans command"""
    # latest_azure_api_version = "2024-02-01"  # Reserved for future use

    provider = "Azure"
    deployment_name = os.getenv("AZURE_DEPLOYMENT_NAME")
    api_base = os.getenv("AZURE_API_BASE")
    api_version = os.getenv("AZURE_API_VERSION", "2024-02-01")

    parser = CreateArgParser("Translates an SRT file using a model on an OpenAI Azure deployment")
    parser.add_argument("-k", "--apikey", type=str, default=None, help="API key for your deployment")
    parser.add_argument("-b", "--apibase", type=str, default=None, help="API backend base address.")
    parser.add_argument("-a", "--apiversion", type=str, default=None, help="Azure API version")
    parser.add_argument("--deploymentname", type=str, default=None, help="Azure deployment name")
    args = parser.parse_args()

    InitLogger("azure-subtrans", args.debug)

    try:
        options: Options = CreateOptions(
            args,
            provider,
            api_base=args.apibase or api_base,
            api_version=args.apiversion or api_version,
            deployment_name=args.deploymentname or deployment_name,
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
