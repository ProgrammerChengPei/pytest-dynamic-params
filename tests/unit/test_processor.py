# Test ParametrizeProcessor functionality
import pytest
from unittest.mock import Mock, MagicMock, patch
from dynamic_params.engine.parametrize.processor import ParametrizeProcessor
from dynamic_params.engine.dependency.dynref import
from dynamic_params.engine.generator.registry import registry as generator_registry
from dynamic_params.engine.generator.base import GeneratorBase
from dynamic_params.errors import ParametrizeError
class TestParametrizeProcessor:
    """Test ParametrizeProcessor class"""
    def test_processor_init(self):
        """Test ParametrizeProcessor initialization"""
        processor = ParametrizeProcessor()
        assert processor.resolver is not None
        assert processor.combinator is not None
    def test_process_no_parametrizations(self):
        """Test process with no parametrizations"""
        processor = ParametrizeProcessor()
        metafunc = Mock()
        metafunc.definition.iter_markers.return_value = []
        processor.process(metafunc)
        # Should not call parametrize if no parametrizations
        metafunc.parametrize.assert_not_called()
    def test_get_parametrizations_with_marker(self):
        """Test _get_parametrizations with marker"""
        processor = ParametrizeProcessor()
        # 使用 spec_set 确保 function 没有_dynamic_parametrize 属性
        metafunc = Mock(spec_set=['definition', 'function'])
        metafunc.function = Mock(spec_set=[])
        metafunc.definition = Mock()
        marker = Mock()
        marker.name = "dynamic_parametrize"
        marker.kwargs = {"argnames": "a,b", "argvalues": [[1, 2]]}
        metafunc.definition.iter_markers.return_value = [marker]
        result = processor._get_parametrizations(metafunc)
        assert len(result) == 1
        assert result[0]["argnames"] == "a,b"
        assert result[0]["argvalues"] == [[1, 2]]
    def test_get_parametrizations_no_marker(self):
        """Test _get_parametrizations with no marker"""
        processor = ParametrizeProcessor()
        metafunc = Mock()
        metafunc.definition.iter_markers.return_value = []
        result = processor._get_parametrizations(metafunc)
        assert len(result) == 0
    def test_resolve_parameters_basic(self):
        """Test resolve_parameters with basic parameters"""
        processor = ParametrizeProcessor()
        parametrization = {
            "argnames": "a,b",
            "argvalues": [1, 2]
        }
        result = processor.resolve_parameters(parametrization)
        assert "a" in result
        assert "b" in result
    def test_resolve_parameters_with_context(self):
        """Test resolve_parameters with context"""
        processor = ParametrizeProcessor()
        parametrization = {
            "argnames": "a",
            "argvalues": [("existing")]
        }
        context = {"existing": 42}
        result = processor.resolve_parameters(parametrization, context)
        assert result["a"] == 42
    def test_resolve_parameters_with_dynref(self):
        """Test resolve_parameters with"""
        processor = ParametrizeProcessor()
        parametrization = {
            "argnames": "a,b",
            "argvalues": [10("a")]
        }
        context = {"a": 10}
        result = processor.resolve_parameters(parametrization, context)
        assert result["a"] == 10
        assert result["b"] == 10
    def test_resolve_parameters_with_expression(self):
        """Test resolve_parameters with expression"""
        processor = ParametrizeProcessor()
        parametrization = {
            "argnames": "a,b,sum",
            "argvalues": [10, 20("a") +("b")]
        }
        context = {"a": 10, "b": 20}
        result = processor.resolve_parameters(parametrization, context)
        assert result["a"] == 10
        assert result["b"] == 20
        assert result["sum"] == 30
    def test_generate_param_combinations_single(self):
        """Test generate_param_combinations with single parametrization"""
        processor = ParametrizeProcessor()
        parametrizations = [
            {
                "argnames": "a",
                "argvalues": [[1], [2], [3]]
            }
        ]
        result = processor.generate_param_combinations(parametrizations)
        # The combinator creates Cartesian product, so with single parametrization
        # it should return the values wrapped in lists
        assert len(result) >= 1
    def test_generate_param_combinations_multiple(self):
        """Test generate_param_combinations with multiple parametrizations"""
        processor = ParametrizeProcessor()
        parametrizations = [
            {
                "argnames": "a",
                "argvalues": [[1], [2]]
            },
            {
                "argnames": "b",
                "argvalues": [[3], [4]]
            }
        ]
        result = processor.generate_param_combinations(parametrizations)
        # Should create Cartesian product
        assert len(result) >= 1
        assert len(result[0]) == 2  # Each combination should have 2 elements
    def test_resolve_value_with_generator(self):
        """Test _resolve_value with generator"""
        processor = ParametrizeProcessor()
        def test_gen():
            yield 1
            yield 2
        # Test with direct function passing
        result = processor._resolve_value(test_gen, {})
        assert result == [1, 2]
    def test_resolve_value_with_dynref(self):
        """Test _resolve_value with"""
        processor = ParametrizeProcessor()
        context = {"a": 42}
        result = processor._resolve_value(("a"), context)
        assert result == 42
    def test_resolve_value_with_list(self):
        """Test _resolve_value with list"""
        processor = ParametrizeProcessor()
        context = {"a": 10}
        result = processor._resolve_value([1("a"), 3], context)
        assert result == [1, 10, 3]
    def test_resolve_value_with_dict(self):
        """Test _resolve_value with dict"""
        processor = ParametrizeProcessor()
        context = {"a": 20}
        result = processor._resolve_value({"x":("a"), "y": 5}, context)
        assert result == {"x": 20, "y": 5}
    def test_resolve_value_with_tuple(self):
        """Test _resolve_value with tuple"""
        processor = ParametrizeProcessor()
        context = {"a": 30}
        result = processor._resolve_value((("a"), 2), context)
        assert result == (30, 2)
    def test_resolve_value_simple(self):
        """Test _resolve_value with simple value"""
        processor = ParametrizeProcessor()
        result = processor._resolve_value(42, {})
        assert result == 42
    def test_apply_parametrization(self):
        """Test _apply_parametrization"""
        processor = ParametrizeProcessor()
        # 使用 spec_set 确保 function 没有_dynamic_parametrize 属性
        metafunc = Mock(spec_set=['definition', 'function', 'parametrize'])
        metafunc.function = Mock(spec_set=[])
        metafunc.definition = Mock()
        marker = Mock()
        marker.name = "dynamic_parametrize"
        marker.kwargs = {"argnames": "a,b", "argvalues": [[1, 2]]}
        metafunc.definition.iter_markers.return_value = [marker]
        param_combinations = [[1, 2], [3, 4]]
        processor._apply_parametrization(metafunc, param_combinations)
        metafunc.parametrize.assert_called_once()
    def test_process_with_parametrizations(self):
        """Test process with parametrizations"""
        processor = ParametrizeProcessor()
        # 使用 spec_set 确保 function 没有_dynamic_parametrize 属性
        metafunc = Mock(spec_set=['definition', 'function', 'parametrize'])
        metafunc.function = Mock(spec_set=[])
        metafunc.definition = Mock()
        marker = Mock()
        marker.name = "dynamic_parametrize"
        marker.kwargs = {"argnames": "a", "argvalues": [[1], [2]]}
        metafunc.definition.iter_markers.return_value = [marker]
        processor.process(metafunc)
        metafunc.parametrize.assert_called_once()
    def test_resolve_parameters_empty_argnames(self):
        """Test resolve_parameters with empty argnames"""
        processor = ParametrizeProcessor()
        parametrization = {
            "argnames": "",
            "argvalues": []
        }
        result = processor.resolve_parameters(parametrization)
        assert result == {}
    def test_resolve_parameters_mismatched_argnames_argvalues(self):
        """Test resolve_parameters with mismatched argnames and argvalues"""
        processor = ParametrizeProcessor()
        parametrization = {
            "argnames": "a,b,c",
            "argvalues": [1]
        }
        result = processor.resolve_parameters(parametrization)
        # Should only resolve parameters that have values
        assert len(result) <= 1
