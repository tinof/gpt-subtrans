import os
import sys
import logging

from PySubtitle.cli.common import InitLogger, CreateArgParser, CreateOptions, CreateTranslator, CreateProject
from PySubtitle.Options import Options
from PySubtitle.SubtitleProject import SubtitleProject
from PySubtitle.SubtitleTranslator import SubtitleTranslator

def main():
    """Main entry point for bedrock-subtrans command"""
    provider = "Bedrock"

    # Fetch Bedrock-specific environment variables
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region = os.getenv('AWS_REGION', 'us-east-1')  # Default to a common Bedrock region

    parser = CreateArgParser(f"Translates an SRT file using a model on Amazon Bedrock")
    parser.add_argument('-k', '--accesskey', type=str, default=None, help="AWS Access Key ID")
    parser.add_argument('-s', '--secretkey', type=str, default=None, help="AWS Secret Access Key")
    parser.add_argument('-r', '--region', type=str, default=None, help="AWS Region (default: us-east-1)")
    parser.add_argument('-m', '--model', type=str, default=None, help="Model ID to use (e.g., amazon.titan-text-express-v1)")
    args = parser.parse_args()

    logger_options = InitLogger("bedrock-subtrans", args.debug)

    try:
        options : Options = CreateOptions(
            args, 
            provider,
            access_key=args.accesskey or access_key,
            secret_access_key=args.secretkey or secret_access_key,
            region=args.region or aws_region,
            model=args.model
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
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
