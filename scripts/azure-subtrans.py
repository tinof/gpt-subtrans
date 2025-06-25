import os
import logging

# Use relative imports now that this is part of a package
from .subtrans_common import InitLogger, CreateArgParser, CreateOptions, CreateTranslator, CreateProject
from PySubtitle.Options import Options
from PySubtitle.SubtitleProject import SubtitleProject
from PySubtitle.SubtitleTranslator import SubtitleTranslator

def main():
    # Update when newer ones are available - https://learn.microsoft.com/en-us/azure/ai-services/openai/reference
    latest_azure_api_version = "2024-02-01"

    provider = "Azure"
    deployment_name = os.getenv('AZURE_DEPLOYMENT_NAME')
    api_base = os.getenv('AZURE_API_BASE')
    api_version = os.getenv('AZURE_API_VERSION', latest_azure_api_version)

    parser = CreateArgParser(f"Translates an SRT file using a model on an OpenAI Azure deployment")
    parser.add_argument('-k', '--apikey', type=str, default=None, help=f"API key for your deployment")
    parser.add_argument('-b', '--apibase', type=str, default=None, help="API backend base address.")
    parser.add_argument('-a', '--apiversion', type=str, default=None, help="Azure API version")
    parser.add_argument('--deploymentname', type=str, default=None, help="Azure deployment name")
    args = parser.parse_args()

    logger_options = InitLogger("azure-subtrans", args.debug)

    try:
        options : Options = CreateOptions(
            args,
            provider,
            deployment_name=args.deploymentname or deployment_name,
            api_base=args.apibase or api_base,
            api_version=args.apiversion or api_version,
        )

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
