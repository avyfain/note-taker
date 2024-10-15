
from llm.model import load_llm_model

def process_with_llm(query, context):
    # Load the LLM model
    model = load_llm_model()
        
    # Generate the response
    response = model.generate_response(query)
    
    return response