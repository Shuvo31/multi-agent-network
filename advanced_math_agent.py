from python_a2a import A2AServer, skill, agent, run_server, TaskStatus, TaskState
import math
import re
import numpy as np

@agent(
    name="Advanced Math Agent",
    description="Specialized in trigonometric and advanced mathematical operations",
    version="1.0.0"
)
class AdvancedMathAgent(A2AServer):
    
    @skill(
        name="Trigonometric Calculator",
        description="Calculate sine, cosine, tangent with high precision",
        tags=["trig", "sin", "cos", "tan", "mathematics"]
    )
    def calculate_trig(self, number, function):
        """Calculate trigonometric functions with error handling."""
        try:
            if function.lower() in ['sin', 'sine']:
                result = math.sin(number)
            elif function.lower() in ['cos', 'cosine']:
                result = math.cos(number)
            elif function.lower() in ['tan', 'tangent']:
                result = math.tan(number)
            else:
                return f"Unsupported function: {function}"
            
            return {
                "input": number,
                "function": function,
                "result": result,
                "formatted": f"The {function} of {number} is {result:.10f}"
            }
        except Exception as e:
            return f"Error calculating {function}({number}): {str(e)}"
    
    def handle_task(self, task):
        input_message = task.message["content"]["text"].lower()
        
        # Enhanced pattern matching
        trig_functions = ['sin', 'sine', 'cos', 'cosine', 'tan', 'tangent']
        function_found = None
        
        for func in trig_functions:
            if func in input_message:
                function_found = func
                break
        
        if not function_found:
            task.artifacts = [{
                "parts": [{"type": "text", "text": "Please specify a trigonometric function (sin, cos, or tan)"}]
            }]
            task.status = TaskStatus(state=TaskState.FAILED)
            return task
        
        # Extract number with improved regex
        match = re.search(r"([-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)", input_message)
        
        if not match:
            task.artifacts = [{
                "parts": [{"type": "text", "text": "Could not extract a valid number from the input"}]
            }]
            task.status = TaskStatus(state=TaskState.FAILED)
            return task
        
        number = float(match.group(1))
        result = self.calculate_trig(number, function_found)
        
        task.artifacts = [{
            "parts": [{"type": "text", "text": result["formatted"] if isinstance(result, dict) else result}]
        }]
        task.status = TaskStatus(state=TaskState.COMPLETED)
        
        return task

if __name__ == "__main__":
    agent = AdvancedMathAgent()
    run_server(agent, port=4737)