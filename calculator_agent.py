from python_a2a import A2AServer, skill, agent, run_server, TaskStatus, TaskState
import re
import math
import operator

@agent(
    name="Advanced Calculator Agent",
    description="Performs general arithmetic operations, algebraic calculations, and mathematical expressions",
    version="1.0.0"
)
class CalculatorAgent(A2AServer):
    
    def __init__(self):
        super().__init__()
        # Safe operators for evaluation
        self.operators = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv,
            '//': operator.floordiv,
            '%': operator.mod,
            '**': operator.pow,
            '^': operator.pow,  # Alternative power notation
        }
        
        # Safe mathematical functions
        self.math_functions = {
            'sqrt': math.sqrt,
            'abs': abs,
            'pow': pow,
            'round': round,
            'ceil': math.ceil,
            'floor': math.floor,
            'log': math.log,
            'log10': math.log10,
            'exp': math.exp,
            'factorial': math.factorial,
        }
    
    @skill(
        name="Basic Arithmetic",
        description="Perform basic arithmetic operations: addition, subtraction, multiplication, division",
        tags=["arithmetic", "add", "subtract", "multiply", "divide", "calculator"]
    )
    def basic_arithmetic(self, expression):
        """Perform basic arithmetic calculations."""
        try:
            # Clean and prepare expression
            expression = expression.replace("x", "*").replace("×", "*").replace("÷", "/")
            expression = expression.replace("^", "**")  # Handle power notation
            
            # Use eval with restricted scope for safety
            allowed_names = {
                "__builtins__": {},
                "sqrt": math.sqrt,
                "abs": abs,
                "pow": pow,
                "round": round,
                "pi": math.pi,
                "e": math.e,
            }
            
            result = eval(expression, allowed_names)
            
            return {
                "expression": expression,
                "result": result,
                "formatted": f"{expression} = {result}"
            }
        except Exception as e:
            return f"Error calculating '{expression}': {str(e)}"
    
    @skill(
        name="Advanced Calculator",
        description="Handle complex mathematical expressions with functions",
        tags=["advanced", "functions", "expressions", "math"]
    )
    def advanced_calculation(self, expression):
        """Handle more complex mathematical expressions."""
        try:
            # Prepare expression with mathematical functions
            expression = self.prepare_expression(expression)
            
            # Safe evaluation environment
            safe_dict = {
                "__builtins__": {},
                **self.math_functions,
                "pi": math.pi,
                "e": math.e,
            }
            
            result = eval(expression, safe_dict)
            
            return {
                "original": expression,
                "result": result,
                "formatted": f"Result: {result}",
                "scientific": f"Scientific notation: {result:.2e}" if abs(result) > 1000 or abs(result) < 0.001 else None
            }
        except Exception as e:
            return f"Error in advanced calculation: {str(e)}"
    
    def prepare_expression(self, expr):
        """Prepare mathematical expression for safe evaluation."""
        # Replace common mathematical notations
        replacements = {
            "^": "**",
            "×": "*",
            "÷": "/",
            "√": "sqrt",
        }
        
        for old, new in replacements.items():
            expr = expr.replace(old, new)
        
        return expr
    
    def extract_calculation(self, text):
        """Extract mathematical expressions from natural language."""
        # Common calculation patterns
        patterns = [
            r"calculate\s+(.+)",
            r"compute\s+(.+)",
            r"what\s+is\s+(.+)",
            r"solve\s+(.+)",
            r"(.+)\s*=\s*\?",
            r"(.+)"  # Fallback: treat entire text as expression
        ]
        
        text = text.lower().strip()
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                expression = match.group(1).strip()
                # Clean up common words
                words_to_remove = ["please", "can you", "help me", "find", "the value of"]
                for word in words_to_remove:
                    expression = expression.replace(word, "").strip()
                return expression
        
        return text
    
    def handle_task(self, task):
        input_message = task.message["content"]["text"]
        
        # Extract mathematical expression
        expression = self.extract_calculation(input_message)
        
        if not expression:
            task.artifacts = [{
                "parts": [{"type": "text", "text": "Please provide a mathematical expression to calculate"}]
            }]
            task.status = TaskStatus(state=TaskState.FAILED)
            return task
        
        # Try basic arithmetic first, then advanced if needed
        result = self.basic_arithmetic(expression)
        
        # If basic arithmetic fails, try advanced calculation
        if isinstance(result, str) and result.startswith("Error"):
            result = self.advanced_calculation(expression)
        
        # Format response
        if isinstance(result, dict):
            if "formatted" in result:
                response = result["formatted"]
                if result.get("scientific"):
                    response += f"\n{result['scientific']}"
            else:
                response = f"Calculation result: {result['result']}"
        else:
            response = str(result)
        
        task.artifacts = [{
            "parts": [{"type": "text", "text": response}]
        }]
        task.status = TaskStatus(state=TaskState.COMPLETED)
        
        return task

if __name__ == "__main__":
    agent = CalculatorAgent()
    run_server(agent, port=4739)