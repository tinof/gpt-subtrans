# GPT-Subtrans
GPT-Subtrans is an open source subtitle translator that uses LLMs as a translation service. It can translate subtitles between any language pairs supported by the language model.

Note: GPT-Subtrans requires an active internet connection. Subtitles are sent to the provider's servers for translation, so their privacy policy applies.

## About This Fork

This is a **command-line focused fork** of the original [gpt-subtrans project](https://github.com/machinewrapped/gpt-subtrans), specifically designed for server environments, automation workflows, and users who prefer lightweight, CLI-only tools.

### Key Changes Made

- **🏗️ Modern Python Packaging**: Completely refactored from script-based architecture to a standard Python package using `pyproject.toml` and `src/` layout
- **🖥️ GUI Removal**: Removed all GUI components and dependencies (PySide6, events, darkdetect) for a lean, headless-friendly package
- **🚀 Multiple CLI Entry Points**: Created dedicated command-line tools for each AI provider:
  - `gpt-subtrans` (OpenAI GPT)
  - `claude-subtrans` (Anthropic Claude)
  - `gemini-subtrans` (Google Gemini)
  - `deepseek-subtrans` (DeepSeek)
  - `mistral-subtrans` (Mistral AI)
  - `azure-subtrans` (Azure OpenAI)
  - `bedrock-subtrans` (Amazon Bedrock)
  - `llm-subtrans` (Custom LLM servers)
- **📦 pipx Optimization**: Designed specifically for `pipx` installation with minimal dependencies and isolated environments
- **🔧 Better Maintainability**: Follows standard Python packaging practices for easier development and distribution

### Goals

- **Lean & Fast**: Provide a lightweight subtitle translation tool without GUI bloat
- **Server-Friendly**: Perfect for headless servers, Docker containers, and automation scripts
- **Easy Installation**: Simple `pipx` installation with optional provider dependencies
- **Developer-Focused**: Standard packaging practices make it easier to contribute and maintain

### Differences from Original

- **No GUI**: This fork is command-line only - no graphical interface
- **Package-Based**: Installable as a proper Python package rather than standalone scripts
- **Provider-Specific Commands**: Each AI provider has its own dedicated CLI command
- **Minimal Dependencies**: Significantly reduced dependency footprint

This fork maintains full compatibility with the original project's core translation functionality while providing a more streamlined experience for command-line users and automated workflows.

## Installation

This project is designed to be installed using `pipx`, which installs Python command-line tools in isolated environments.

1. First, install `pipx`:
   ```sh
   python3 -m pip install --user pipx
   python3 -m pipx ensurepath
   ```

2. Install `gpt-subtrans` from this repository:
   ```sh
   pipx install git+https://github.com/tinof/gpt-subtrans.git
   ```

### Installing Provider Dependencies

By default, only the core dependencies are installed. You need to install the specific SDK for the AI provider you want to use. You can do this by injecting the dependency into the `gpt-subtrans` environment.

For example, to use **OpenAI**:
```sh
pipx inject gpt-subtrans openai
```

To use **Google Gemini**:
```sh
pipx inject gpt-subtrans google-genai google-api-core
```

You can find the required package for each provider in the `pyproject.toml` file under `[project.optional-dependencies]`.

To install all provider SDKs at once:
```sh
pipx install 'git+https://github.com/tinof/gpt-subtrans.git[all]'
```

### OpenAI
https://openai.com/policies/privacy-policy

You will need an OpenAI API key from https://platform.openai.com/account/api-keys to use OpenAI's GPT models as a translator.

If the API key is associated with a free trial account the translation speed will be severely restricted.

You can use the custom api_base parameter to access a custom OpenAI instance or other providers with an OpenAI compatible API (which is most of them).

You can use an **OpenAI Azure** installation as a translation provider, but this is only advisable if you know what you're doing - in which case hopefully it will be clear how to configure the Azure provider settings.

### Google Gemini
https://ai.google.dev/terms

**Please note that regions restrictions may apply: https://ai.google.dev/available_regions**

You will need a Google Gemini API key from https://ai.google.dev/ or from a project created on https://console.cloud.google.com/. You must ensure that Generative AI is enabled for the api key and project.

The Gemini 2.0 Flash Experimental model is perhaps the leading model for translation speed and fluency at time of writing, and is currently free to use.

### Anthropic Claude
https://support.anthropic.com/en/collections/4078534-privacy-legal

You will need an Anthropic API key from https://console.anthropic.com/settings/keys to use Claude as a provider. The Anthropic SDK does not provide a way to retrieve available models, so the latest Claude 3 model names are currently hardcoded.

The API has very strict [rate limits](https://docs.anthropic.com/claude/reference/rate-limits) based on your credit tier, both on requests per minutes and tokens per day. The free credit tier should be sufficient to translate approximately one full movie per day.

### DeepSeek
https://platform.deepseek.com/downloads/DeepSeek%20Open%20Platform%20Terms%20of%20Service.html

You will need a DeepSeek API key from https://platform.deepseek.com/api_keys to use this provider.

- **API Base**: You can optionally specify a custom URL, e.g. if you are hosting your own DeepSeek instance. If this is not set, the official DeepSeek API endpoint will be used.

- **Model**: The default model is `deepseek-chat`, which is recommended for translation tasks. `deepseek-reasoner` may produce better results for source subtitles with OCR or transcription errors as it will spend longer trying to guess what the error is.

DeepSeek is quite simple to set up and offers reasonable performance at a very low price, though translation does not seem to be its strongest point.

### Mistral AI
https://mistral.ai/terms/

You will need a Mistral API key from https://console.mistral.ai/api-keys/ to use this provider.

- **Server URL**: If you are using a custom deployment of the Mistral API, you can specify the server URL using the `--server_url` argument.

- **Model**: `mistral-large-latest` is recommended for translation. Smaller models tend to perform poorly and may not follow the system instructions well.

Mistral AI is straightforward to set up, but its performance as a translator is not particularly good.

### Custom Server
GPT-Subtrans can interface directly with any server that supports an OpenAI compatible API, including locally hosted models e.g. [LM Studio](https://lmstudio.ai/).

This is mainly for research and you should not expect particularly good results. LLMs derive much of their power from their size, so the small, quantized models you can run on a GPU are likely to produce poor translations, fail to generate valid responses or get stuck in endless loops. If you find a model that reliably producess good results, please post about it in the Discussions area!

Chat and completion endpoints are supported, you should configure the settings and endpoint based on the model the server is running (e.g. instruction tuned models will probably produce better results using the completions endpoint rather than chat/conversation).

### Amazon Bedrock
https://aws.amazon.com/service-terms/

**Bedrock is not recommended for most users**: The setup process is complex, requiring AWS credentials, proper IAM permissions, and region configuration. Additionally, not all models on Bedrock support translation tasks or offer reliable results. Bedrock support will not be included in pre-packaged versions - if you can handle setting up AWS, you can handle installing gpt-subtrans from source!

To use Bedrock, you must:
  1. Create an **IAM user** or **role** with appropriate permissions (e.g., `bedrock:InvokeModel`, `bedrock:ListFoundationModels`).
  2. Ensure the model you wish to use is accessible in your selected AWS region and [enabled for the IAM user](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access-modify.html).

### MacOS
Building MacOS universal binaries with PyInstaller has not worked for some time so releases are only provided for Apple Silicon. If you have an Intel Mac you will need to install from source. If anybody would like to volunteer to maintain Intel releases, please get in touch.

### Linux
Prebuilt Linux packages are not provided so you will need to install from source.

## Development Installation

If you want to modify the program or contribute to development, you can install it in development mode:

1. Clone the repository:
   ```sh
   git clone https://github.com/machinewrapped/gpt-subtrans.git
   cd gpt-subtrans
   ```

2. Install in development mode:
   ```sh
   pip install -e .
   ```

3. Install provider dependencies as needed:
   ```sh
   pip install -e .[all]  # Install all providers
   # OR install specific providers:
   pip install openai google-genai anthropic mistralai boto3
   ```

### Configuration

Create a `.env` file in your working directory with your API keys:

```sh
OPENAI_API_KEY=<your_openai_api_key>
GEMINI_API_KEY=<your_gemini_api_key>
AZURE_API_KEY=<your_azure_api_key>
CLAUDE_API_KEY=<your_claude_api_key>
DEEPSEEK_API_KEY=<your_deepseek_api_key>
MISTRAL_API_KEY=<your_mistral_api_key>
```

For Azure:
```sh
AZURE_API_BASE=<your api_base, such as https://something.openai.azure.com>
AZURE_DEPLOYMENT_NAME=<deployment_name>
```

For Bedrock:
```sh
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_REGION=your-region
```

## Usage
The program works by dividing the subtitles up into small batches and sending each one to the translation service in turn. It is likely to take time to complete, and can potentially make many API calls for each subtitle file.

By default The translated subtitles will be written to a new SRT file in the same directory with the target langugage appended to the original filename.

Subtitle Edit's (https://www.nikse.dk/subtitleedit) "Fix Common Errors" can help to clean up the translated subtitles, though some of its functionality is now covered by the post-process option (`--postprocess`) in GPT-Subtrans.

### Command Line Usage

GPT-Subtrans is a command-line tool with multiple entry points for different AI providers.

The most basic usage is:
```sh
gpt-subtrans <path_to_srt_file> --target_language <target_language>
gemini-subtrans <path_to_srt_file> --target_language <target_language>
claude-subtrans <path_to_srt_file> --target_language <target_language>
deepseek-subtrans <path_to_srt_file> --target_language <target_language>
mistral-subtrans <path_to_srt_file> --target_language <target_language>
azure-subtrans <path_to_srt_file> --target_language <target_language>
bedrock-subtrans <path_to_srt_file> --target_language <target_language>
llm-subtrans -s <server_address> -e <endpoint> -l <language> <path_to_srt_file>
```
If the target language is not specified the default is English. Other options that can be specified on the command line are detailed below.

## Advanced usage

There are a number of command-line arguments that offer more control over the translation process.

Default values for many settings can be set in the .env file, using a NAME_IN_CAPS with format. See Options.py for the full list.

To use any of these arguments, add them to the command-line after the path to the SRT file. For example:

```sh
gpt-subtrans path/to/my/subtitles.srt --moviename "My Awesome Movie" --ratelimit 10 --substitution cat::dog
```

- `-l`, `--target_language`:
  The language to translate the subtitles to.

- `-o`, `--output`:
  Specify a filename for the translated subtitles.

- `--project`:
  Read or Write a project file for the subtitles being translated. More on this below.

- `--ratelimit`:
  Maximum number of requests to the translation service per minute (mainly relevant if you are using an OpenAI free trial account).

- `--moviename`:
  Optionally identify the source material to give context to the translator.

- `--description`:
  A brief description of the source material to give further context. Less is generally more here, or the AI can start improvising.

- `--name`, `--names`:
  Optionally provide (a list of) names to use in the translation (more powerful AI models are more likely to actually use them).

- `--substitution`:
  A pair of strings separated by `::`, to substitute in either source or translation, or the name of a file containing a list of such pairs.

- `--scenethreshold`:
  Number of seconds between lines to consider it a new scene.

- `--minbatchsize`:
  Minimum number of lines to consider starting a new batch to send to the translator.
  Higher values typically result in faster and cheaper translations but increase the risk of desyncs.

- `--maxbatchsize`:
  Maximum number of lines before starting a new batch is compulsory.
  This needs to take into account the token limit for the model being used, but the "optimal" value depends on many factors, so experimentation is encouraged.
  Larger batches are more cost-effective but increase the risk of the AI desynchronising, triggering expensive retries.

- `--preprocess`:
  Preprocess the subtitles prior to batching.
  This performs various actions to prepare the subtitles for more efficient translation, e.g. splitting long (duration) lines into multiple lines.
  Mainly intended for subtitles that have been automatically transcribed with e.g. Whisper.

- `--postprocess`:
  Post-process translated subtitles.
  Performs various actions like adding line breaks to long lines and normalising dialogue tags after a translation request.

- `--instruction`:
  An additional instruction for the AI indicating how it should approach the translation.

- `--instructionfile`:
  Name/path of a file to load AI system instructions from (otherwise the default instructions.txt is used).

- `--maxlines`:
  Maximum number of batches to process. To end the translation after a certain number of lines, e.g. to check the results.

- `--temperature`:
  A higher temperature increases the random variance of translations. Default 0.

### Provider-specific arguments
Some additional arguments are available for specific providers.

#### OpenAI
- `-k`, `--apikey`:
  Your [OpenAI API Key](https://platform.openai.com/account/api-keys).

- `-b`, `--apibase`:
  API base URL if you are using a custom instance. if it is not set, the default URL will be used.

- '--httpx':
  Use the [HTTPX library](https://github.com/projectdiscovery/httpx) for requests (only supported if apibase is specified)

- `-m`, `--model`:
  Specify the [AI model](https://platform.openai.com/docs/models) to use for translation

#### Gemini
- `-k`, `--apikey`:
  Your [Google Gemini API Key](https://aistudio.google.com/app/apikey). Not required if it is set in the .env file.

- `-m`, `--model`:
  Specify the [AI model](https://ai.google.dev/models/gemini) to use for translation

#### Claude
- `-k`, `--apikey`:
  Your [Anthropic API Key](https://console.anthropic.com/settings/keys). Not required if it is set in the .env file.

- `-m`, `--model`:
  Specify the [AI model](https://docs.anthropic.com/claude/docs/models-overview#model-comparison) to use for translation. This should be the full model name, e.g. `claude-3-haiku-20240307`

#### OpenAI Azure
- `--deploymentname`:
  Azure deployment name

- `-k`, `--apikey`:
  API key [for your deployment](https://learn.microsoft.com/en-us/azure/ai-services/openai/).

- `-b`, `--apibase`:
  API backend base address.

- `-a`, `--apiversion`:
  Azure API version.

#### DeepSeek
  - `-k`, `--apikey`:
  Your [DeepSeek API Key](https://platform.deepseek.com/api_keys).

- `-b`, `--apibase`:
  Base URL if you are using a custom deployment of DeepSeek. if it is not set, the official URL will be used.

- `-m`, `--model`:
  Specify the [model](https://api-docs.deepseek.com/quick_start/pricing) to use for translation. **deepseek-chat** is probably the only sensible choice (and default).

#### Mistral AI
  - `-k`, `--apikey`:
  Your [DeepSeek API Key](https://console.mistral.ai/api-keys/).

- `--server_url`:
  URL if you are using a custom deployment of Mistral. if unset, the official URL will be used.

- `-m`, `--model`:
  Specify the [model](https://docs.mistral.ai/getting-started/models/models_overview/) to use for translation. **mistral-large-latest** is recommended, the small models are not very reliable.

#### Amazon Bedrock
- `-k`, `--accesskey`:
  Your [AWS Access Key ID](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html). Not required if it is set in the `.env` file.

- `-s`, `--secretkey`:
  Your [AWS Secret Access Key](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html). Not required if it is set in the `.env` file.

- `-r`, `--region`:
  AWS Region where Bedrock is available. You can check the list of regions [here](https://aws.amazon.com/about-aws/global-infrastructure/regions_az/). For example: `us-east-1` or `eu-west-1`.

- `-m`, `--model`:
  The ID of the [Bedrock model](https://docs.aws.amazon.com/bedrock/latest/userguide/foundation-models.html) to use for translation. Examples include `amazon.titan-text-lite-v1` or `amazon.titan-text-express-v1`.

#### Custom Server specific arguments
- `-s`, `--server`:
  The address the server is running on, including port (e.g. http://localhost:1234). Should be provided by the server

- `-e`, `--endpoint`:
  The API function to call on the server, e.g. `/v1/completions`. Choose an appropriate endpoint for the model running on the server.

- `--chat`:
  Specify this argument if the endpoint expects requests in a conversation format - otherwise it is assumed to be a completion endpoint.

- `--systemmessages`:
  If using a conversation endpoint, translation instructions will be sent as the "system" user if this flag is specified.

- `-k`, `--apikey`:
  Local servers shouldn't need an api key, but the option is provided in case it is needed for your setup.

- `-m`, `--model`:
  The model will usually be determined by the server, but the option is provided in case you need to specify it.

### Proxy

If you need to use proxy in your location, you can use socks proxy by using command line

```sh
python3 gpt-subtrans.py <path_to_srt_file> --target_language <target_language> --proxy socks://127.0.0.1:1089
```
Remember to change the local port to yours and turn on your proxy tools such as v2ray, naiveproxy and clash.

### batch process

you can process files with the following struct：

      #   -SRT
      #   --fold1
      #   ---1.srt
      #   ---2.srt
      #   ...
      #   --fold2
      #   ---1.srt
      #   ---2.srt
      #   ...

```sh
python3 batch_process.py  # process files in different folders
```
You need to modify the command line in batch_process.py accordingly.

### Developers
It is recommended to use an IDE such as Visual Studio Code to run the program when installed from source, and set up a launch.json file to specify the arguments.

Note: Remember to activate the virtual environment every time you work on the project.

## Project File

**Note** A project file can be created automatically by using the `--project` argument.

The `--project` argument or `PROJECT` .env setting can take a number of values, which control whether and when an intermediate file will be written to disc.

The default setting is `None`, which means the project file is neither written nor read, the only output of the program is the final translation.

If the argument is set to `True` then a project file will be created with the `.subtrans` extension, containing details of the translation process,
and it will be updated as the translation progresses. Writing a project file allows, amongst other things, resuming a translation that was interrupted.

Other valid options include `preview`, `resume`, `reparse` and `retranslate`. These are probably only useful if you're modifying the code, in which case
you should be able to see what they do.

## Version History

Version 1.0 is (ironically) a minor update, updating the major version to 1.0 because the project has been stable for some time.

Version 0.7 introduced optional post-processing of translated subtitles to try to fix some of the common issues with LLM-translated subtitles (e.g. adding line breaks), along with new default instructions that tend to produce fewer errors.

Version 0.6 changes the architecture to a provider-based system, allowing multiple AI services to be used as translators.
Settings are compartmentalised for each provider. For the intial release the only supported provider is **OpenAI**.

Version 0.5 adds support for gpt-instruct models and a refactored code base to support different translation engines. For most users, the recommendation is still to use the **gpt-3.5-turbo-16k** model with batch sizes of between (10,100) lines, for the best combination of performance/cost and translation quality.

Version 0.4 features significant optimisations and numerous bug fixes.

Version 0.3 featured many bug fixes and improvements.

Version 0.2 employs a new prompting approach that greatly reduces desyncs caused by GPT merging together source lines in the translation. This can reduce the naturalness of the translation when the source and target languages have very different grammar, but it provides a better base for a human to polish the output.

The instructions have also been made more detailed, with multiple examples of correct output for GPT to reference, and the generation of summaries has been improved so that GPT is better able to understand the context of the batch it is translating. Additionally, double-clicking a scene or batch now allows the summary to be edited by hand, which can greatly improve the results of a retranslation and of subsequent batches or scenes. Individually lines can also be edited by double-clicking them.

## Contributing
Contributions from the community are welcome! To contribute, follow these steps:

Fork the repository onto your own GitHub account.

Clone the repository onto your local machine using the following command:

```sh
git clone https://github.com/your_username/GPT-Subtrans.git
```

Create a new branch for your changes using the following command:

```sh
git checkout -b feature/your-new-feature
```

Make your changes to the code and commit them with a descriptive commit message.

Push your changes to your forked repository.

Submit a pull request to the main GPT-Subtrans repository.

## Acknowledgements
This project uses several useful libraries:

- srt (https://github.com/cdown/srt)
- requests (https://github.com/psf/requests)
- regex (https://github.com/mrabarnett/mrab-regex)
- httpx (https://github.com/projectdiscovery/httpx)

Translation providers:
- openai (https://platform.openai.com/docs/libraries/python-bindings)
- google-genai (https://github.com/googleapis/python-genai)
- anthropic (https://github.com/anthropics/anthropic-sdk-python)
- mistralai (https://github.com/mistralai/client-python)
- boto3 (Amazon Bedrock) (https://github.com/boto/boto3)

For configuration:
- appdirs (https://github.com/ActiveState/appdirs)

## License
GPT-Subtrans is licensed under the MIT License. See LICENSE for the 3rd party library licenses.
