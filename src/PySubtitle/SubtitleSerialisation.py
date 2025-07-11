import json

from PySubtitle.SubtitleBatch import SubtitleBatch
from PySubtitle.SubtitleError import TranslationError
from PySubtitle.SubtitleFile import SubtitleFile
from PySubtitle.SubtitleLine import SubtitleLine
from PySubtitle.SubtitleScene import SubtitleScene
from PySubtitle.Translation import Translation
from PySubtitle.TranslationPrompt import TranslationPrompt


# Serialisation helpers
def classname(obj):
    if isinstance(obj, type):
        return obj.__name__
    return type(obj).__name__


# Convert our custom types to JSON
class SubtitleEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, TranslationError):
            # Don't bother trying to serialise all the error types (why not?)
            return {"__class": classname(TranslationError), "type": classname(obj), "problem": str(obj)}

        _class = classname(obj)
        properties = self.serialize_object(obj)
        if isinstance(properties, dict):
            properties = {k: v for k, v in properties.items() if v is not None}
            return {**{"_class": _class}, **properties}
        else:
            return properties

    def serialize_object(self, obj):
        if obj is None:
            return None

        if isinstance(obj, SubtitleFile):
            return {
                "sourcepath": obj.sourcepath,
                "outputpath": obj.outputpath,
                "scenecount": len(obj.scenes),
                "settings": obj.settings or obj.context,
                "scenes": obj.scenes,
            }
        elif isinstance(obj, SubtitleScene):
            return {
                "scene": obj.number,
                "batchcount": obj.size,
                "linecount": obj.linecount,
                "all_translated": obj.all_translated,
                "context": {
                    "summary": obj.context.get("summary"),
                    "history": obj.context.get("history") or obj.context.get("summaries"),
                },
                "batches": obj._batches,
            }
        elif isinstance(obj, SubtitleBatch):
            return {
                "scene": obj.scene,
                "batch": obj.number,
                "size": obj.size,
                "all_translated": obj.all_translated,
                "errors": obj.errors if obj.errors else None,
                "summary": obj.summary,
                "originals": obj._originals,
                "translated": obj._translated,
                "context": {
                    "summary": obj.context.get("summary"),
                    "history": obj.context.get("history") or obj.context.get("summaries"),
                },
                "translation": obj.translation,
                "prompt": obj.prompt,
            }
        elif isinstance(obj, SubtitleLine):
            return {"line": obj.line, "translation": obj.translation, "original": obj.original}
        elif isinstance(obj, Translation):
            return {"content": obj.content}
        elif isinstance(obj, TranslationPrompt):
            return {
                "user_prompt": obj.user_prompt,
                "batch_prompt": obj.batch_prompt,
                "messages": obj.messages,
                "supports_system_messages": obj.supports_system_messages,
                "supports_system_prompt": obj.supports_system_prompt,
                "conversation": obj.conversation,
            }
        elif hasattr(obj, "name"):
            return obj.name

        return super().default(obj)


# Reconstruct our custom types from JSON
class SubtitleDecoder(json.JSONDecoder):
    def __init__(self, **kwargs):
        super().__init__(object_hook=self.object_hook, **kwargs)

    def object_hook(self, dct):
        if "_class" in dct:
            class_name = dct.pop("_class")
            if class_name == classname(SubtitleFile):
                sourcepath = dct.get("sourcepath")
                outpath = dct.get("outputpath") or dct.get("filename")
                obj = SubtitleFile(sourcepath, outpath)
                obj.settings = dct.get("settings", {}) or dct.get("context", {})
                obj.scenes = dct.get("scenes", [])
                obj.UpdateProjectSettings({})  # Force update for legacy files
                return obj
            elif class_name == classname(SubtitleScene):
                obj = SubtitleScene(dct)
                return obj
            elif class_name == classname(SubtitleBatch):
                obj = SubtitleBatch(dct)
                return obj
            elif class_name == classname(SubtitleLine) or class_name == "Subtitle":  # TEMP backward compatibility
                return SubtitleLine(dct.get("line"), translation=dct.get("translation"), original=dct.get("original"))
            elif class_name == classname(Translation) or class_name == "GPTTranslation":
                content = dct.get("content") or {
                    "text": dct.get("text"),
                    "finish_reason": dct.get("finish_reason"),
                    "response_time": dct.get("response_time"),
                    "prompt_tokens": dct.get("prompt_tokens"),
                    "output_tokens": dct.get("completion_tokens"),
                    "reasoning_tokens": dct.get("reasoning_tokens"),
                    "accepted_prediction_tokens": dct.get("accepted_prediction_tokens"),
                    "rejected_prediction_tokens": dct.get("rejected_prediction_tokens"),
                    "total_tokens": dct.get("total_tokens"),
                    "summary": dct.get("summary"),
                    "scene": dct.get("scene"),
                    "synopsis": dct.get("synopsis"),
                    "names": dct.get("names") or dct.get("characters"),
                }

                if isinstance(content["text"], list):
                    # This shouldn't happen, but try to recover if it does
                    content["text"] = "\n".join(content["text"])

                obj = Translation(content)
                return obj
            elif class_name == classname(TranslationPrompt):
                user_prompt = dct.get("user_prompt")
                conversation = dct.get("conversation")
                obj = TranslationPrompt(user_prompt, conversation)
                obj.supports_system_messages = dct.get("supports_system_messages")
                obj.supports_system_prompt = dct.get("supports_system_prompt")
                obj.batch_prompt = dct.get("batch_prompt")
                obj.messages = dct.get("messages")
                return obj
            elif class_name == classname(TranslationError):
                return TranslationError(dct.get("message"))

        return dct
