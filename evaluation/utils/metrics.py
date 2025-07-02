import json
from collections.abc import Iterator, Mapping
from datetime import datetime
from math import isnan, nan
from pathlib import Path
from typing import Final, TypedDict, cast

from utils.metric_types import Function, Metric


class FunctionParameterSpec(TypedDict):
    """
    Represents a function parameter specification.

    Attributes
    ----------
    description : str
        Description of the parameter.
    type : str
        Data type of the parameter.
    """
    description: str
    type: str


class FunctionParametersSpec(TypedDict):
    """
    Represents the structure of function parameters.

    Attributes
    ----------
    type : str
        The type of parameter structure (e.g., "object").
    properties : dict[str, object]
        Dictionary defining parameter names and their properties.
    required : list[str]
        List of required parameter names.
    """
    type: str
    properties: dict[str, object]
    required: list[str]


class FunctionSpec(TypedDict):
    """
    Represents a function specification.

    Attributes
    ----------
    name : str
        The name of the function.
    parameters : FunctionParametersSpec
        The parameter structure of the function.
    """
    name: str
    parameters: FunctionParametersSpec


def load_function_specs(dir_path: Path) -> Iterator[FunctionSpec]:
    """
    Loads function specifications from JSON files in a directory.

    Parameters
    ----------
    dir_path : Path
        Path to the directory containing function specification JSON files.

    Returns
    -------
    Iterator[FunctionSpec]
        An iterator over loaded function specifications.
    """
    return (
        cast(FunctionSpec, json.loads(fp.read_text()))
        for fp in dir_path.glob("**/*.json")
    )


FAIL_METRIC: Final = Metric(
    passed=0,
    correct_function_called=nan,
    function_exists=nan,
    function_name_specified=nan,
    correctly_generated_arguments=nan,
    correctly_retrieved_arguments=nan,
    extra_argument=nan,
    secs_to_first_token=nan,
    secs_to_last_token=nan,
    tokens_per_second=nan,
)


def calculate_metric(
    function_specs: Mapping[str, FunctionSpec],
    expected: Function,
    functions_from_slm: list[Function],
    tokens_count: float,
    start_timestamp: datetime | None,
    first_token_timestamp: datetime | None,
    last_token_timestamp: datetime | None
) -> Metric:
    """
    Evaluates the model-generated function calls against expected outputs.

    Parameters
    ----------
    function_specs : Mapping[str, FunctionSpec]
        Dictionary of function specifications.
    expected : Function
        The expected function call and parameters.
    functions_from_slm : list[Function]
        List of function calls predicted by the model.
    tokens_count : float
        Total number of tokens generated in the response.
    start_timestamp : datetime | None
        Timestamp when generation started.
    first_token_timestamp : datetime | None
        Timestamp when the first token was generated.
    last_token_timestamp : datetime | None
        Timestamp when generation completed.

    Returns
    -------
    Metric
        Evaluation results including accuracy, recall, precision, and response efficiency.
    """
    match functions_from_slm:
        case [output]:
            output_args_names = output.parameters.keys()
            expected_args_names = expected.parameters.keys()

            common_args = {
                name: (expected.parameters[name], output.parameters[name])
                for name in output_args_names & expected_args_names
            }

            args_nb_in_output_that_are_in_expected = sum(
                int(output_value == expected_value)
                for (expected_value, output_value) in common_args.values()
            )

            extra_args_name = output_args_names - expected_args_names

            func_spec = function_specs.get(output.name)

            match func_spec:
                case {"parameters": {"properties": props, "required": required}}:
                    (parameters, required_parameters) = (props, required)
                case None:
                    (parameters, required_parameters) = ({}, [])
                case other:
                    raise ValueError(f"Unexpected function spec: {other}")

            non_existing_extra_args = [
                arg for arg in extra_args_name if arg not in parameters
            ]

            # extra arguments that are part of the function specification, but not part of the ground truth
            existing_extra_args = [arg for arg in extra_args_name if arg in parameters]

            required_extra_args = [
                arg for arg in existing_extra_args if arg in required_parameters
            ]

            not_required_existing_extra_args = {
                name: (
                    cast(FunctionParameterSpec, parameters[name]).get(
                        "type", "undefined"
                    ),
                    output.parameters[name],
                )
                for name in existing_extra_args
                if name not in required_parameters and name in parameters
            }

            def is_default_string_or_array(arg_type: str, value: object) -> bool:
                return (arg_type == "string" and value in (None, "")) or (
                    arg_type == "array" and value == []
                )

            not_required_existing_extra_args_with_default_value = [
                name
                for name, (arg_type, value) in not_required_existing_extra_args.items()
                if is_default_string_or_array(arg_type, value)
            ]

            missing_args_name = expected_args_names - output_args_names

            not_required_missing_args = {
                name: (
                    cast(FunctionParameterSpec, parameters[name]).get(
                        "type", "undefined"
                    ),
                    expected.parameters[name],
                )
                for name in missing_args_name
                if name not in required_parameters and name in parameters
            }

            not_required_missing_args_with_default_value = [
                name
                for name, (arg_type, value) in not_required_missing_args.items()
                if is_default_string_or_array(arg_type, value)
            ]

            adjusted_output_parameters_length = len(output.parameters) - len(
                not_required_existing_extra_args_with_default_value
            )
            correctly_generated_arguments = (
                args_nb_in_output_that_are_in_expected
                / adjusted_output_parameters_length
                if adjusted_output_parameters_length > 0
                else nan
            )

            adjusted_expected_parameters_lenght = len(expected.parameters) - len(
                not_required_missing_args_with_default_value
            )
            correctly_retrieved_arguments = (
                args_nb_in_output_that_are_in_expected
                / adjusted_expected_parameters_lenght
                if adjusted_expected_parameters_lenght > 0
                else nan
            )

            passed = int(
                expected.name == output.name
                and (correctly_retrieved_arguments == 1.0 or isnan(correctly_retrieved_arguments))
                and (
                    correctly_generated_arguments == 1.0
                    or isnan(correctly_generated_arguments)
                )
                and len(non_existing_extra_args) == 0
                and len(required_extra_args) == 0
            )

            secs_to_first_token = nan
            secs_to_last_token = nan
            tokens_per_second = nan
            if (
                start_timestamp is not None
                and first_token_timestamp is not None
                and last_token_timestamp is not None
            ):
                secs_to_first_token = round(
                    (first_token_timestamp - start_timestamp).total_seconds(), 2
                )
                secs_to_last_token = round(
                    (last_token_timestamp - start_timestamp).total_seconds(), 2
                )
                tokens_per_second = round(
                    tokens_count
                    / (last_token_timestamp - first_token_timestamp).total_seconds(),
                    2,
                )

            return Metric(
                passed=passed,
                correct_function_called=int(expected.name == output.name),
                function_exists=int(func_spec is not None),
                function_name_specified=int(bool(output.name)),
                correctly_generated_arguments=correctly_generated_arguments,
                correctly_retrieved_arguments=correctly_retrieved_arguments,
                extra_argument=len(extra_args_name)
                - len(not_required_existing_extra_args_with_default_value),
                secs_to_first_token=secs_to_first_token,
                secs_to_last_token=secs_to_last_token,
                tokens_per_second=tokens_per_second,
            )

        case _:  # zero or multiple functions
            return FAIL_METRIC
