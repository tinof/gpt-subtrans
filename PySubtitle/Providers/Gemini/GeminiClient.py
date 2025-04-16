import logging
import time

from google import genai
from google.api_core import exceptions as google_exceptions
from google.genai.types import (
    AutomaticFunctionCallingConfig,
    FinishReason,
    Model,
    GenerateContentConfig,
    GenerateContentResponse,
    GenerateContentResponseUsageMetadata,
    HarmBlockMethod,
    HarmBlockThreshold,
    HarmCategory,
    Part,
    SafetySetting
)

from PySubtitle.Helpers import FormatMessages
from PySubtitle.SubtitleError import TranslationError, TranslationImpossibleError, TranslationResponseError
from PySubtitle.Translation import Translation
from PySubtitle.TranslationClient import TranslationClient

from PySubtitle.TranslationPrompt import TranslationPrompt

class GeminiContextLimitError(TranslationError):
    """ Custom exception for context limit errors """
    pass

class GeminiClient(TranslationClient):
    """
    Handles communication with Google Gemini to request translations
    """
    _model_info_cache = {} # Cache Model info objects

    def __init__(self, settings : dict):
        super().__init__(settings)

        logging.info(f"Initializing GeminiClient for model {self.model_name or 'default'}")
        # Create the client once
        try:
            # Explicitly use v1beta as recommended for features like system_instruction
            # Although default might be beta, let's be explicit for stability based on docs
            # http_options = types.HttpOptions(api_version='v1beta') # Requires importing types
            # For now, let's stick to SDK default as 'v1beta' might need 'types' import
            self.gemini_client = genai.Client(api_key=self.api_key)
            # Pre-fetch model info during initialization if model_name is known
            if self.model_name:
                self._get_model_info(self.model_name) # Changed back to _get_model_info
        except Exception as e:
            logging.error(f"Failed to initialize Gemini client: {e}")
            self.gemini_client = None # Ensure client is None if init fails

        logging.info(f"Translating with Gemini {self.model_name or 'default'} model")


        self.safety_settings = [
            SafetySetting(category=HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=HarmBlockThreshold.BLOCK_NONE),
            SafetySetting(category=HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=HarmBlockThreshold.BLOCK_NONE),
            SafetySetting(category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=HarmBlockThreshold.BLOCK_NONE),
            SafetySetting(category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=HarmBlockThreshold.BLOCK_NONE),
            SafetySetting(category=HarmCategory.HARM_CATEGORY_CIVIC_INTEGRITY, threshold=HarmBlockThreshold.BLOCK_NONE)
        ]

        self.automatic_function_calling = AutomaticFunctionCallingConfig(disable=True, maximum_remote_calls=None)

    @property
    def api_key(self):
        return self.settings.get('api_key')

    @property
    def model(self):
        return self.settings.get('model')

    @property
    def model_name(self):
        return self.settings.get('model')

    @property
    def rate_limit(self):
        return self.settings.get('rate_limit')

    def _request_translation(self, prompt : TranslationPrompt, temperature : float = None) -> Translation:
        """
        Request a translation based on the provided prompt
        """
        logging.debug(f"Messages:\n{FormatMessages(prompt.messages)}")

        temperature = temperature or self.temperature
        try:
            response = self._send_messages(prompt.system_prompt, prompt.content, temperature)
            return Translation(response) if response else None
        except GeminiContextLimitError as e:
            # Re-raise context limit errors so the batcher can potentially handle them
            raise e
        except TranslationError as e:
            logging.error(f"Translation error: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error during Gemini translation: {e}")
            # Let higher levels handle unexpected errors or re-raise if necessary
            raise TranslationImpossibleError(f"Unexpected error: {e}") from e

    def _abort(self):
        # TODO cancel any ongoing requests
        return super()._abort()

    def _send_messages(self, system_instruction : str, completion : str, temperature):
        """
        Make a request to the Gemini API to provide a translation.
        Checks token limits before sending.
        """
        response = {}
        model_name = self.model_name
        if not self.gemini_client:
             raise TranslationImpossibleError("Gemini client was not initialized successfully.")

        try:
            # Check token limits before sending
            model_info : Model | None = self._get_model_info(model_name) # Use Model type hint if available, else object
            input_token_limit = model_info.input_token_limit if model_info and hasattr(model_info, 'input_token_limit') else None

            if input_token_limit:
                # Use the client's count_tokens method
                prompt_tokens = self._count_tokens(model_name, system_instruction, completion)
                if prompt_tokens >= input_token_limit: # Use >= for safety
                    raise GeminiContextLimitError(f"Estimated prompt tokens ({prompt_tokens}) exceed model limit ({input_token_limit}) for {model_name}")
                logging.debug(f"Estimated prompt tokens: {prompt_tokens} / {input_token_limit}")
            # else: # Warning is handled in _get_model_info now
            #    logging.warning(f"Could not determine input token limit for {model_name}. Proceeding without check.")

        except GeminiContextLimitError:
            raise # Re-raise context limit errors immediately
        except Exception as e:
            logging.error(f"Error during token pre-check for {model_name}: {e}")
            # Decide if we should proceed or raise an error - for now, let's proceed cautiously
            # raise TranslationImpossibleError(f"Failed token pre-check: {e}") from e

        for retry in range(1 + self.max_retries):
            try:
                # Use the stored client instance
                config = GenerateContentConfig(
                    candidate_count=1,
                    temperature=temperature,
                    system_instruction=system_instruction,
                    automatic_function_calling=self.automatic_function_calling,
                    safety_settings=self.safety_settings, # Move safety_settings into the config
                    max_output_tokens=None,
                    response_modalities=[]
                )
                # Use client.models.generate_content as per docs
                gcr : GenerateContentResponse = self.gemini_client.models.generate_content(
                    model=model_name,
                    contents=Part.from_text(text=completion),
                    config=config # Correct keyword argument is 'config'
                    # safety_settings=self.safety_settings # Correctly moved into config object earlier
                )

                if self.aborted:
                    return None

                if not gcr:
                    raise TranslationImpossibleError("No response from Gemini")

                if gcr.prompt_feedback and gcr.prompt_feedback.block_reason:
                    raise TranslationResponseError(f"Request was blocked by Gemini: {str(gcr.prompt_feedback.block_reason)}", response=gcr)

                # Try to find a validate candidate
                candidates = [candidate for candidate in gcr.candidates if candidate.content]
                candidates = [candidate for candidate in candidates if candidate.finish_reason == FinishReason.STOP] or candidates

                if not candidates:
                    raise TranslationResponseError("No valid candidates returned in the response", response=gcr)

                candidate = candidates[0]
                response['token_count'] = candidate.token_count

                finish_reason = candidate.finish_reason
                if finish_reason == "STOP" or finish_reason == FinishReason.STOP:
                    response['finish_reason'] = "complete"
                elif finish_reason == "MAX_TOKENS" or finish_reason == FinishReason.MAX_TOKENS:
                    response['finish_reason'] = "length"
                    raise TranslationResponseError("Gemini response exceeded token limit", response=candidate)
                elif finish_reason == "SAFETY" or finish_reason == FinishReason.SAFETY:
                    response['finish_reason'] = "blocked"
                    raise TranslationResponseError("Gemini response was blocked for safety reasons", response=candidate)
                elif finish_reason == "RECITATION" or finish_reason == FinishReason.RECITATION:
                    response['finish_reason'] = "recitation"
                    raise TranslationResponseError("Gemini response was blocked for recitation", response=candidate)
                elif finish_reason == "FINISH_REASON_UNSPECIFIED" or finish_reason == FinishReason.FINISH_REASON_UNSPECIFIED:
                    response['finish_reason'] = "unspecified"
                    raise TranslationResponseError("Gemini response was incomplete", response=candidate)
                else:
                    # Probably a failure
                    response['finish_reason'] = finish_reason

                usage_metadata : GenerateContentResponseUsageMetadata = gcr.usage_metadata
                if usage_metadata:
                    response['prompt_tokens'] = usage_metadata.prompt_token_count
                    response['output_tokens'] = usage_metadata.candidates_token_count
                    response['total_tokens'] = usage_metadata.total_token_count

                if not candidate.content.parts:
                    raise TranslationResponseError("Gemini response has no valid content parts", response=candidate)

                response_text = "\n".join(part.text for part in candidate.content.parts)

                if not response_text:
                    raise TranslationResponseError("Gemini response is empty", response=candidate)

                response['text'] = response_text

                thoughts = "\n".join(part.thought for part in candidate.content.parts if part.thought)
                if thoughts:
                    response['reasoning'] = thoughts

                return response

            except Exception as e:
                if retry == self.max_retries:
                    # Re-raise context limit errors without retry
                    if isinstance(e, GeminiContextLimitError):
                        raise e
                    # Re-raise specific Google API errors if needed for more granular handling
                    if isinstance(e, google_exceptions.GoogleAPIError):
                         logging.error(f"Google API Error: {e}")
                         # Potentially check e.code or e.message for specific conditions like quota exceeded

                    if retry == self.max_retries:
                        raise TranslationImpossibleError(f"Failed to communicate with provider after {self.max_retries} retries: {e}") from e

                    if not self.aborted:
                        sleep_time = self.backoff_time * 2.0**retry
                        logging.warning(f"Gemini request failure {str(e)}, retrying in {sleep_time} seconds...")
                        time.sleep(sleep_time)
                    else:
                        # Aborted during sleep/retry logic
                        return None # Or raise an aborted exception

            except GeminiContextLimitError:
                raise # Propagate context limit errors immediately without retry

    def _get_model_info(self, model_name: str) -> Model | None:
        """ Get model information using client.models.get(), using a cache """
        if not model_name:
            logging.error("Model name is required to get model info.")
            return None

        if model_name in self._model_info_cache:
            return self._model_info_cache[model_name]

        if not self.gemini_client:
            logging.error("Gemini client not initialized, cannot get model info.")
            return None

        try:
            logging.debug(f"Fetching model info for {model_name}")
            # Use client.models.get(model=model_name)
            model_info = self.gemini_client.models.get(model=model_name)

            if model_info:
                self._model_info_cache[model_name] = model_info
                input_limit = getattr(model_info, 'input_token_limit', 'N/A')
                output_limit = getattr(model_info, 'output_token_limit', 'N/A')
                logging.info(f"Model {model_name}: Input Limit={input_limit}, Output Limit={output_limit}")
                return model_info
            else:
                # This case might not happen if get() raises an error on failure
                logging.warning(f"Could not retrieve info for model {model_name} (returned None)")
                self._model_info_cache[model_name] = None # Cache failure
                return None
        except google_exceptions.NotFound:
             logging.error(f"Model not found: {model_name}")
             self._model_info_cache[model_name] = None
             return None
        except Exception as e:
            # Catch other potential errors like permission issues, API errors
            logging.error(f"Failed to get model info for {model_name}: {e}")
            self._model_info_cache[model_name] = None # Cache failure
            return None

    def _count_tokens(self, model_name: str, system_prompt: str, user_prompt: str) -> int:
        """ Estimate the token count for the prompt using client.models.count_tokens """
        if not model_name:
            raise ValueError("Model name is required to count tokens")

        if not self.gemini_client:
             raise TranslationImpossibleError("Gemini client not initialized, cannot count tokens.")

        try:
            # Construct the content structure Gemini expects for counting.
            # System prompt needs to be included explicitly for counting,
            # even though it's passed separately in generate_content's config.
            # Combine system and user prompt for counting purposes
            full_prompt_text = f"{system_prompt}\n\n{user_prompt}" if system_prompt else user_prompt

            # Use the client.models.count_tokens method, passing contents as a list
            count_response = self.gemini_client.models.count_tokens(
                model=model_name,
                contents=[full_prompt_text] # Pass the string inside a list
            )
            return count_response.total_tokens

        except Exception as e:
            logging.error(f"Failed to count tokens for model {model_name}: {e}")
            # Re-raising is safer to prevent overruns if counting fails
            raise TranslationImpossibleError(f"Failed to count tokens for model {model_name}: {e}") from e
