from python_a2a import A2AServer, skill, agent, run_server, TaskStatus, TaskState
import statistics
import re
import json

@agent(
    name="Statistical Analysis Agent",
    description="Provides statistical analysis and data processing capabilities",
    version="1.0.0"
)
class StatisticalAgent(A2AServer):
    
    @skill(
        name="Statistical Calculator",
        description="Calculate mean, median, mode, standard deviation",
        tags=["statistics", "mean", "median", "std", "analysis"]
    )
    def calculate_stats(self, numbers):
        """Calculate comprehensive statistics for a list of numbers."""
        try:
            return {
                "count": len(numbers),
                "mean": statistics.mean(numbers),
                "median": statistics.median(numbers),
                "mode": statistics.mode(numbers) if len(set(numbers)) < len(numbers) else "No mode",
                "std_dev": statistics.stdev(numbers) if len(numbers) > 1 else 0,
                "min": min(numbers),
                "max": max(numbers),
                "range": max(numbers) - min(numbers)
            }
        except Exception as e:
            return f"Error calculating statistics: {str(e)}"
    
    def handle_task(self, task):
        input_message = task.message["content"]["text"]
        
        # Extract numbers from the message
        numbers = re.findall(r"[-+]?[0-9]*\.?[0-9]+", input_message)
        
        if len(numbers) < 2:
            task.artifacts = [{
                "parts": [{"type": "text", "text": "Please provide at least 2 numbers for statistical analysis"}]
            }]
            task.status = TaskStatus(state=TaskState.FAILED)
            return task
        
        numbers = [float(n) for n in numbers]
        stats = self.calculate_stats(numbers)
        
        if isinstance(stats, dict):
            response = f"""Statistical Analysis Results:
            
📊 Dataset: {numbers}
📈 Count: {stats['count']}
📊 Mean: {stats['mean']:.4f}
📈 Median: {stats['median']:.4f}
📊 Mode: {stats['mode']}
📈 Standard Deviation: {stats['std_dev']:.4f}
📊 Range: {stats['min']} - {stats['max']} (span: {stats['range']})
            """
        else:
            response = stats
        
        task.artifacts = [{
            "parts": [{"type": "text", "text": response}]
        }]
        task.status = TaskStatus(state=TaskState.COMPLETED)
        
        return task

if __name__ == "__main__":
    agent = StatisticalAgent()
    run_server(agent, port=4738)