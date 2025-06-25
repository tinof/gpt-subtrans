import logging
import os
import sys

# Use absolute imports from the package root
from PySubtitle.Helpers.cli_utils import (
    CreateArgParser,
    CreateOptions,
    CreateProject,
    CreateTranslator,
    InitLogger,
)
from PySubtitle.Options import Options
from PySubtitle.SubtitleProject import SubtitleProject
from PySubtitle.SubtitleTranslator import SubtitleTranslator


def gpt_subtrans_main():
    """Entry point for the gpt-subtrans command"""
    provider = "OpenAI"
    default_model = os.getenv("OPENAI_MODEL") or "gpt-4o"

    parser = CreateArgParser("Translates an SRT file using an OpenAI model")
    parser.add_argument(
        "-k",
        "--apikey",
        type=str,
        default=None,
        help="Your OpenAI API Key (https://platform.openai.com/account/api-keys)",
    )
    parser.add_argument(
        "-b",
        "--apibase",
        type=str,
        default="https://api.openai.com/v1",
        help="API backend base address.",
    )
    parser.add_argument("-m", "--model", type=str, default=None, help="The model to use for translation")
    parser.add_argument(
        "--httpx",
        action="store_true",
        help="Use the httpx library for custom api_base requests. May help if you receive a 307 redirect error.",
    )
    parser.add_argument(
        "--proxy",
        type=str,
        default=None,
        help="SOCKS proxy URL (e.g., socks://127.0.0.1:1089)",
    )
    args = parser.parse_args()

    logger_options = InitLogger("gpt-subtrans", args.debug)

    try:
        options: Options = CreateOptions(
            args,
            provider,
            use_httpx=args.httpx,
            api_base=args.apibase,
            proxy=args.proxy,
            model=args.model or default_model,
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

        logging.info("OpenAI translation process completed.")

    except Exception as e:
        logging.error(f"Translation failed: {e}", exc_info=True)
        print(f"\nError: {e}\n", file=sys.stderr)
        sys.exit(1)


def azure_subtrans_main():
    """Entry point for the azure-subtrans command"""
    latest_azure_api_version = "2024-02-01"

    provider = "Azure"
    deployment_name = os.getenv("AZURE_DEPLOYMENT_NAME")
    api_base = os.getenv("AZURE_API_BASE")
    api_version = os.getenv("AZURE_API_VERSION", latest_azure_api_version)

    parser = CreateArgParser("Translates an SRT file using a model on an OpenAI Azure deployment")
    parser.add_argument("-k", "--apikey", type=str, default=None, help="API key for your deployment")
    parser.add_argument("-b", "--apibase", type=str, default=None, help="API backend base address.")
    parser.add_argument("-a", "--apiversion", type=str, default=None, help="Azure API version")
    parser.add_argument("--deploymentname", type=str, default=None, help="Azure deployment name")
    args = parser.parse_args()

    logger_options = InitLogger("azure-subtrans", args.debug)

    try:
        options: Options = CreateOptions(
            args,
            provider,
            deployment_name=args.deploymentname or deployment_name,
            api_base=args.apibase or api_base,
            api_version=args.apiversion or api_version,
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

        logging.info("Azure translation process completed.")

    except Exception as e:
        logging.error(f"Translation failed: {e}", exc_info=True)
        print(f"\nError: {e}\n", file=sys.stderr)
        sys.exit(1)


def bedrock_subtrans_main():
    """Entry point for the bedrock-subtrans command"""
    provider = "Bedrock"

    # Fetch Bedrock-specific environment variables
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region = os.getenv("AWS_REGION", "us-east-1")  # Default to a common Bedrock region

    parser = CreateArgParser("Translates an SRT file using a model on Amazon Bedrock")
    parser.add_argument("-k", "--accesskey", type=str, default=None, help="AWS Access Key ID")
    parser.add_argument("-s", "--secretkey", type=str, default=None, help="AWS Secret Access Key")
    parser.add_argument("-r", "--region", type=str, default=None, help="AWS Region (default: us-east-1)")
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        default=None,
        help="Model ID to use (e.g., amazon.titan-text-express-v1)",
    )
    args = parser.parse_args()

    logger_options = InitLogger("bedrock-subtrans", args.debug)

    try:
        options: Options = CreateOptions(
            args,
            provider,
            access_key=args.accesskey or access_key,
            secret_access_key=args.secretkey or secret_access_key,
            aws_region=args.region or aws_region,
            model=args.model,
        )

        # Validate that required Bedrock options are provided
        if (
            not options.get("access_key")
            or not options.get("secret_access_key")
            or not options.get("aws_region")
            or not options.get("model")
        ):
            raise ValueError("AWS Access Key, Secret Key, Region, and Model ID must be specified.")

        # Create a project for the translation
        project: SubtitleProject = CreateProject(options, args)

        # Create a translator with the provided options
        translator: SubtitleTranslator = CreateTranslator(options)

        # Translate the subtitles
        project.TranslateSubtitles(translator)

        if project.write_project:
            logging.info(f"Writing project data to {str(project.projectfile)}")
            project.WriteProjectFile()

        logging.info("Bedrock translation process completed.")

    except Exception as e:
        logging.error(f"Translation failed: {e}", exc_info=True)
        print(f"\nError: {e}\n", file=sys.stderr)
        sys.exit(1)


def claude_subtrans_main():
    """Entry point for the claude-subtrans command"""
    provider = "Claude"
    default_model = os.getenv("CLAUDE_MODEL") or "claude-3-haiku-20240307"

    parser = CreateArgParser("Translates an SRT file using Anthropic's Claude AI")
    parser.add_argument(
        "-k",
        "--apikey",
        type=str,
        default=None,
        help="Your Anthropic API Key (https://console.anthropic.com/settings/keys)",
    )
    parser.add_argument("-m", "--model", type=str, default=None, help="The model to use for translation")
    parser.add_argument(
        "--proxy",
        type=str,
        default=None,
        help="SOCKS proxy URL (e.g., socks://127.0.0.1:1089)",
    )
    args = parser.parse_args()

    logger_options = InitLogger("claude-subtrans", args.debug)

    try:
        options: Options = CreateOptions(args, provider, model=args.model or default_model, proxy=args.proxy)

        # Create a project for the translation
        project: SubtitleProject = CreateProject(options, args)

        # Create a translator with the provided options
        translator: SubtitleTranslator = CreateTranslator(options)

        # Translate the subtitles
        project.TranslateSubtitles(translator)

        if project.write_project:
            logging.info(f"Writing project data to {str(project.projectfile)}")
            project.WriteProjectFile()

        logging.info("Claude translation process completed.")

    except Exception as e:
        logging.error(f"Translation failed: {e}", exc_info=True)
        print(f"\nError: {e}\n", file=sys.stderr)
        sys.exit(1)


def deepseek_subtrans_main():
    """Entry point for the deepseek-subtrans command"""
    provider = "DeepSeek"
    default_model = os.getenv("DEEPSEEK_MODEL") or "deepseek-chat"

    parser = CreateArgParser("Translates an SRT file using an DeepSeek model")
    parser.add_argument(
        "-k",
        "--apikey",
        type=str,
        default=None,
        help="Your DeepSeek API Key (https://platform.deepseek.com/api_keys)",
    )
    parser.add_argument(
        "-b",
        "--apibase",
        type=str,
        default="https://api.deepseek.com",
        help="API backend base address.",
    )
    parser.add_argument("-m", "--model", type=str, default=None, help="The model to use for translation")
    args = parser.parse_args()

    logger_options = InitLogger("deepseek-subtrans", args.debug)

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

        logging.info("DeepSeek translation process completed.")

    except Exception as e:
        logging.error(f"Translation failed: {e}", exc_info=True)
        print(f"\nError: {e}\n", file=sys.stderr)
        sys.exit(1)


def llm_subtrans_main():
    """Entry point for the llm-subtrans command"""
    provider = "Custom Server"

    # Parse command line arguments
    parser = CreateArgParser("Translates an SRT file using an AI model running on a local server")
    parser.add_argument(
        "-s",
        "--server",
        type=str,
        default=None,
        help="Address of the server including port (e.g. http://localhost:1234)",
    )
    parser.add_argument(
        "-e",
        "--endpoint",
        type=str,
        default=None,
        help="Endpoint to call on  the server (e.g. /v1/completions)",
    )
    parser.add_argument("-k", "--apikey", type=str, default=None, help="API Key, if required")
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        default=None,
        help="Model to use if the server allows it to be specified",
    )
    parser.add_argument("--chat", action="store_true", help="Use chat format requests for the endpoint")
    parser.add_argument(
        "--systemmessages",
        action="store_true",
        help="Indicates that the endpoint supports system messages in chat requests",
    )
    args = parser.parse_args()

    logger_options = InitLogger("llm-subtrans", args.debug)

    try:
        options: Options = CreateOptions(
            args,
            provider,
            api_key=args.apikey,
            endpoint=args.endpoint,
            model=args.model,
            server_address=args.server,
            supports_conversation=args.chat,
            supports_system_messages=args.systemmessages,
        )

        # Create a project for the translation
        project: SubtitleProject = CreateProject(options, args)

        # Create a translator with the provided options
        translator: SubtitleTranslator = CreateTranslator(options)

        project.TranslateSubtitles(translator)

        if project.write_project:
            logging.info(f"Writing project data to {str(project.projectfile)}")
            project.WriteProjectFile()

        logging.info("LLM translation process completed.")

    except Exception as e:
        logging.error(f"Translation failed: {e}", exc_info=True)
        print(f"\nError: {e}\n", file=sys.stderr)
        sys.exit(1)


def mistral_subtrans_main():
    """Entry point for the mistral-subtrans command"""
    provider = "Mistral"
    default_model = os.getenv("MISTRAL_MODEL") or "open-mistral-nemo"

    parser = CreateArgParser("Translates an SRT file using an Mistral model")
    parser.add_argument(
        "-k",
        "--apikey",
        type=str,
        default=None,
        help="Your Mistral API Key (https://console.mistral.ai/api-keys/)",
    )
    parser.add_argument("-m", "--model", type=str, default=None, help="The model to use for translation")
    parser.add_argument(
        "--server_url",
        type=str,
        default=None,
        help="Server URL (leave blank for default).",
    )
    args = parser.parse_args()

    logger_options = InitLogger("mistral-subtrans", args.debug)

    try:
        options: Options = CreateOptions(
            args,
            provider,
            server_url=args.server_url,
            model=args.model or default_model,
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

        logging.info("Mistral translation process completed.")

    except Exception as e:
        logging.error(f"Translation failed: {e}", exc_info=True)
        print(f"\nError: {e}\n", file=sys.stderr)
        sys.exit(1)


def batch_process_main():
    """Entry point for the batch-process command"""
    parser = CreateArgParser("Batch process SRT files in subdirectories using a specified gpt-subtrans provider.")
    parser.add_argument("root_dir", help="Root directory containing subfolders with SRT files.")
    parser.add_argument("--target_language", required=True, help="Target language for translation.")
    parser.add_argument(
        "--instructionfile",
        default=None,
        help="Path to the instruction file for the provider.",
    )
    parser.add_argument(
        "--provider_command",
        default="gpt-subtrans",
        help="The provider command to execute (e.g., gpt-subtrans, gemini-subtrans).",
    )
    args, unknown_args = parser.parse_known_args()

    logging.info(f"Starting batch processing in directory: {args.root_dir}")
    logging.info(f"Provider command: {args.provider_command}")
    logging.info(f"Target language: {args.target_language}")
    if args.instructionfile:
        logging.info(f"Using instruction file: {args.instructionfile}")
    if unknown_args:
        logging.info(f"Passing additional arguments to provider: {' '.join(unknown_args)}")

    processed_files = 0
    failed_files = 0

    # Map provider commands to their respective main functions
    provider_functions = {
        "gpt-subtrans": gpt_subtrans_main,
        "azure-subtrans": azure_subtrans_main,
        "bedrock-subtrans": bedrock_subtrans_main,
        "claude-subtrans": claude_subtrans_main,
        "deepseek-subtrans": deepseek_subtrans_main,
        "gemini-subtrans": gemini_main,
        "llm-subtrans": llm_subtrans_main,
        "mistral-subtrans": mistral_subtrans_main,
    }

    provider_func = provider_functions.get(args.provider_command)
    if not provider_func:
        logging.error(f"Unknown provider command: {args.provider_command}")
        sys.exit(1)

    # Traverse all subfolders under the root directory
    for subdir, dirs, files in os.walk(args.root_dir):
        for file in files:
            # Check if the file ends with '.srt'
            if file.lower().endswith(".srt"):
                src_file = os.path.join(subdir, file)
                logging.info(f"Processing file: {src_file}")

                original_argv = None  # Initialize original_argv

                try:
                    # Reconstruct arguments for the provider function
                    provider_args = [
                        src_file,
                        "--target_language",
                        args.target_language,
                    ]
                    if args.instructionfile:
                        if not os.path.isfile(args.instructionfile):
                            logging.warning(
                                f"Instruction file not found: {args.instructionfile}. Skipping for {src_file}."
                            )
                        else:
                            provider_args.extend(["--instructionfile", args.instructionfile])

                    provider_args.extend(unknown_args)

                    # Temporarily save original sys.argv and replace with provider-specific args
                    original_argv = sys.argv
                    sys.argv = [args.provider_command] + provider_args

                    logging.debug(f"Calling provider function with arguments: {' '.join(sys.argv)}")

                    # Call the provider function directly
                    provider_func()

                    logging.info(f"Successfully processed: {src_file}")
                    processed_files += 1

                except Exception as e:
                    logging.error(f"Failed to process {src_file}. Error: {e}", exc_info=True)
                    failed_files += 1
                finally:
                    # Restore original sys.argv if it was set
                    if original_argv is not None:
                        sys.argv = original_argv

    logging.info("Batch processing finished.")
    logging.info(f"Successfully processed: {processed_files} files.")
    logging.info(f"Failed to process: {failed_files} files.")


def gemini_main():
    """Entry point for the gemini-subtrans command"""
    provider = "Gemini"
    # Default model name might need adjustment based on Gemini's current offerings
    default_model = os.getenv(
        "GEMINI_MODEL"
    )  # Removed fallback to "Gemini 2.0 Flash" to rely on provider defaults if env var not set

    parser = CreateArgParser("Translates an SRT file using Google Gemini")
    # Add provider-specific arguments
    parser.add_argument(
        "-k",
        "--apikey",
        type=str,
        default=os.getenv("GEMINI_API_KEY"),
        help="Your Gemini API Key (or set GEMINI_API_KEY env var)",
    )
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        default=default_model,
        help="The Gemini model to use for translation (e.g., gemini-1.5-flash-latest)",
    )
    args = parser.parse_args()

    # Use the command name for the log filename
    logger_options = InitLogger("gemini-subtrans", args.debug)

    try:
        # Pass model explicitly to CreateOptions
        options: Options = CreateOptions(args, provider, model=args.model)

        # Validate API key presence using the get method
        if not options.get("api_key"):
            raise ValueError(
                "Gemini API Key is required. Provide via -k argument or GEMINI_API_KEY environment variable."
            )

        translator: SubtitleTranslator = CreateTranslator(options)
        project: SubtitleProject = CreateProject(options, args)

        project.TranslateSubtitles(translator)

        if project.write_project:
            logging.info(f"Writing project data to {str(project.projectfile)}")
            project.WriteProjectFile()

        logging.info("Gemini translation process completed.")

    except Exception as e:
        logging.error(f"Translation failed: {e}", exc_info=True)
        print(f"\nError: {e}\n", file=sys.stderr)  # Print errors to stderr
        sys.exit(1)  # Exit with a non-zero code on error
