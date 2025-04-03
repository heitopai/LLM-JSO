from main import optimize
import os
from datetime import datetime

# model_name = "gemini-2.0-flash"
model_name = "gemini-2.0-flash-lite"
# model_name = "gemini-2.0-flash-thinking-exp-1219"
# model_name = "gemini-2.0-flash-thinking-exp-01-21"
# model_name = "gemini-2.0-pro-exp-02-05"
# model_name = "DeepSeek-V3"
# model_name = "qwen-max"

current_time = datetime.now().strftime("%Y%m%d%H%M%S")
output_dir = model_name + "_results_" + current_time
temperature = 1
iterations = 500
dir= "./data1/"
files = os.listdir(dir)
for file in files:
    optimize(dir + file, iterations=iterations, model_name=model_name, temperature = temperature, output_dir=output_dir)

