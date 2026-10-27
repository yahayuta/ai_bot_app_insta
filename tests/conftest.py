"""Stub the AI SDKs so the Flask app imports without API keys or network."""
import os
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _stub(name, **attrs):
    module = sys.modules.get(name) or types.ModuleType(name)
    for key, value in attrs.items():
        setattr(module, key, value)
    sys.modules[name] = module
    return module


class _Anything:
    def __init__(self, *args, **kwargs):
        pass

    def __getattr__(self, name):
        return _Anything()

    def __call__(self, *args, **kwargs):
        return _Anything()


_stub("PIL", Image=_Anything())
_stub("PIL.Image")
_stub("stability_sdk", client=_Anything())
_stub("stability_sdk.interfaces")
_stub("stability_sdk.interfaces.gooseai")
_stub("stability_sdk.interfaces.gooseai.generation")
_stub("stability_sdk.interfaces.gooseai.generation.generation_pb2")
_stub("openai", OpenAI=_Anything)
_stub("google.cloud.storage")
_stub("google.genai", types=_Anything())
_stub("google.genai.types")
