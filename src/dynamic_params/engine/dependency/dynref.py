# DynRef implementation for parameter references

from typing import Any, Union

from ...errors import DynRefError

class DynRef:
    """Class for referencing other parameters in parameterization"""
    
    def __init__(self, name: str):
        """Initialize a DynRef instance
        
        Args:
            name: The name of the parameter to reference
        """
        self.name = name
    
    def resolve(self, context: dict) -> Any:
        """Resolve the referenced parameter value from the context
        
        Args:
            context: Dictionary containing parameter values
            
        Returns:
            The resolved parameter value
            
        Raises:
            DynRefError: If the referenced parameter is not found in the context
        """
        if self.name not in context:
            raise DynRefError(f"Referenced parameter '{self.name}' not found in context")
        return context[self.name]
    
    # Operator overloading methods
    def __add__(self, other: Union[Any, 'DynRef']) -> 'DynRefExpression':
        """Addition operator overload"""
        return DynRefExpression('+', self, other)
    
    def __sub__(self, other: Union[Any, 'DynRef']) -> 'DynRefExpression':
        """Subtraction operator overload"""
        return DynRefExpression('-', self, other)
    
    def __mul__(self, other: Union[Any, 'DynRef']) -> 'DynRefExpression':
        """Multiplication operator overload"""
        return DynRefExpression('*', self, other)
    
    def __truediv__(self, other: Union[Any, 'DynRef']) -> 'DynRefExpression':
        """Division operator overload"""
        return DynRefExpression('/', self, other)
    
    def __str__(self) -> str:
        """String representation"""
        return f"DynRef('{self.name}')"

class DynRefExpression:
    """Class for representing expressions involving DynRef"""
    
    def __init__(self, op: str, left: Union[Any, DynRef, 'DynRefExpression'], 
                 right: Union[Any, DynRef, 'DynRefExpression']):
        """Initialize a DynRefExpression instance
        
        Args:
            op: The operator
            left: The left operand
            right: The right operand
        """
        self.op = op
        self.left = left
        self.right = right
    
    def resolve(self, context: dict) -> Any:
        """Resolve the expression value from the context
        
        Args:
            context: Dictionary containing parameter values
            
        Returns:
            The resolved expression value
        """
        # Resolve left operand
        left_val = self._resolve_operand(self.left, context)
        # Resolve right operand
        right_val = self._resolve_operand(self.right, context)
        
        # Apply the operator
        if self.op == '+':
            return left_val + right_val
        elif self.op == '-':
            return left_val - right_val
        elif self.op == '*':
            return left_val * right_val
        elif self.op == '/':
            return left_val / right_val
        else:
            raise DynRefError(f"Unsupported operator: {self.op}")
    
    def _resolve_operand(self, operand: Union[Any, DynRef, 'DynRefExpression'], 
                        context: dict) -> Any:
        """Resolve an operand
        
        Args:
            operand: The operand to resolve
            context: Dictionary containing parameter values
            
        Returns:
            The resolved operand value
        """
        if isinstance(operand, (DynRef, DynRefExpression)):
            return operand.resolve(context)
        return operand
    
    def __str__(self) -> str:
        """String representation"""
        return f"({self.left} {self.op} {self.right})"
    
    # Operator overloading methods for chaining
    def __add__(self, other: Union[Any, DynRef, 'DynRefExpression']) -> 'DynRefExpression':
        """Addition operator overload for chaining"""
        return DynRefExpression('+', self, other)
    
    def __sub__(self, other: Union[Any, DynRef, 'DynRefExpression']) -> 'DynRefExpression':
        """Subtraction operator overload for chaining"""
        return DynRefExpression('-', self, other)
    
    def __mul__(self, other: Union[Any, DynRef, 'DynRefExpression']) -> 'DynRefExpression':
        """Multiplication operator overload for chaining"""
        return DynRefExpression('*', self, other)
    
    def __truediv__(self, other: Union[Any, DynRef, 'DynRefExpression']) -> 'DynRefExpression':
        """Division operator overload for chaining"""
        return DynRefExpression('/', self, other)
