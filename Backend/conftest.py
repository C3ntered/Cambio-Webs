import sys
from unittest.mock import MagicMock

# Mock fastapi and its submodules
mock_fastapi = MagicMock()
sys.modules["fastapi"] = mock_fastapi
sys.modules["fastapi.middleware.cors"] = MagicMock()
sys.modules["fastapi.staticfiles"] = MagicMock()
sys.modules["fastapi.responses"] = MagicMock()

# Mock pydantic
class MockBaseModel:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def model_dump(self, **kwargs):
        # Return only public attributes
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

    @classmethod
    def model_validate(cls, obj):
        if isinstance(obj, dict):
            return cls(**obj)
        return obj

def mock_config_dict(**kwargs):
    return kwargs

mock_pydantic = MagicMock()
mock_pydantic.BaseModel = MockBaseModel
mock_pydantic.ConfigDict = mock_config_dict
sys.modules["pydantic"] = mock_pydantic
