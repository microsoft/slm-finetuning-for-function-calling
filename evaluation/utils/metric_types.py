from typing import Any, NewType

from pydantic import BaseModel, ConfigDict, model_validator

Parameters = NewType("Parameters", dict[str, object])


class ImmutableModel(BaseModel):
    """
    Immutable base model that prevents modifications after creation.

    This ensures data integrity for evaluation metrics.

    Attributes
    ----------
    model_config : ConfigDict
        Configuration setting that makes the model immutable (frozen).
    """
    model_config = ConfigDict(frozen=True)


class BaseInput(ImmutableModel):
    """
    Base class for all input schemas.

    Attributes
    ----------
    input : str
        The raw input text or query.
    """
    input: str


class BaseOutput(ImmutableModel):
    """
    Base class for all output schemas.

    This is a placeholder class that can be extended for specific outputs.
    """
    pass


class BaseMetric(ImmutableModel):
    """
    Base class for all metric schemas.

    Ensures that all metric field values are numerical (float or int).

    Methods
    -------
    accept_only_floats(data: dict[str, Any]) -> dict[str, Any]
        Validates that all metric values are floats or integers.
    """

    @model_validator(mode="before")
    @classmethod
    def accept_only_floats(cls, data: dict[str, Any]) -> dict[str, Any]:
        """
        Validates that all provided values are either floats or integers.

        Parameters
        ----------
        data : dict[str, Any]
            The dictionary containing metric values.

        Returns
        -------
        dict[str, Any]
            The validated dictionary with only numeric values.

        Raises
        ------
        ValueError
            If any value is not a float or an int.
        """
        for key, value in data.items():
            if (type_ := type(value)) is not float and type_ is not int:  # pyright: ignore [reportUnknownVariableType]
                raise ValueError(
                    f"Key '{key}' has value <{repr(value)}> of type '{type_}' that is neither a float nor an int"
                )
        return data


class Function(BaseModel):
    """
    Represents a function call with its parameters.

    Attributes
    ----------
    name : str
        The name of the function.
    parameters : Parameters
        A dictionary of parameter names and values.
    """
    name: str
    parameters: Parameters


class Input(BaseInput):
    """
    Input schema containing function expectations.

    Attributes
    ----------
    expected : Function
        The expected function call and parameters.
    use_case : str
        Description of the specific use case for evaluation.
    """
    expected: Function
    use_case: str


class Output(BaseOutput):
    """
    Output schema representing model-generated function calls.

    Attributes
    ----------
    answer : str | None
        The textual response from the model (if any).
    functions : list[Function]
        List of functions extracted from the model's response.
    model_reviewed : bool
        Whether the model's response has been manually reviewed.
    revised_functions : list[Function]
        Adjusted functions after human revision.
    """

    answer: str | None
    functions: list[Function]
    model_reviewed: bool
    revised_functions: list[Function]


class Metric(BaseMetric):
    """
    Stores evaluation metrics for function calling.

    Attributes
    ----------
    passed : float
        Indicates whether the model successfully passed the evaluation (1.0 or 0.0).
    correct_function_called : float
        Whether the model selected the correct function (1.0 or 0.0).
    function_exists : float
        Whether the function exists in the predefined specification (1.0 or 0.0).
    function_name_specified : float
        Whether the function name was explicitly stated (1.0 or 0.0).
    correctly_generated_arguments : float
        Precision: Correct arguments returned by the model / total arguments returned.
    correctly_retrieved_arguments : float
        Recall: Correct arguments returned by the model / total expected arguments.
    extra_argument : float
        Number of unexpected arguments (hallucinated or non-expected).
    secs_to_first_token : float
        Time taken to generate the first token (in seconds).
    secs_to_last_token : float
        Time taken to complete response generation (in seconds).
    tokens_per_second : float
        Rate of token generation (tokens per second).
    """

    # TOP LEVEL METRICS

    passed: float  # !failed

    # DETAILED METRICS

    correct_function_called: float

    function_exists: float

    function_name_specified: float  #!no function called

    # Precision: Number of correct arguments returned by the SLM / number of arguments returned by the SLM
    correctly_generated_arguments: float

    # Recall: Number of correct arguments returned by the SLM / number of arguments expected
    correctly_retrieved_arguments: float

    extra_argument: float  # non-expected existing args or/and hallucinated args

    # NON-FUNCTIONAL METRICS

    secs_to_first_token: float

    secs_to_last_token: float

    tokens_per_second: float
