import tensorflow as tf
tf.get_logger().setLevel('ERROR')
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
from sentence_transformers import SentenceTransformer
from langchain_huggingface import HuggingFacePipeline

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model_path = "phamhai/Llama-3.2-1B-Instruct-Frog"
tokenizer = AutoTokenizer.from_pretrained(model_path)

eos_token_id = tokenizer.convert_tokens_to_ids("<|eot_id|>")

embedder = SentenceTransformer('all-MiniLM-L6-v2').to(device)

def convert_text_to_tokenizer(text: str) -> list:
    vector_data = embedder.encode([text])
    return vector_data.flatten().tolist()

model = AutoModelForCausalLM.from_pretrained(
    model_path,
    return_dict=True,
    low_cpu_mem_usage=True,
    torch_dtype=torch.float16,
    trust_remote_code=True,
)

# Sử dụng trọng số đã có sẵn
model.eval()

pipe_chainlang = pipeline(
                "text-generation",
                model=model,
                max_new_tokens=100,
                do_sample=False,
                temperature=None,
                top_p=None,
                num_return_sequences=1,
                no_repeat_ngram_size=2,
                tokenizer=tokenizer,
                torch_dtype=torch.float16,
                device_map="auto",
                eos_token_id=eos_token_id,
                pad_token_id=eos_token_id, 
                return_full_text=False,
                )

def generate_answer(prompt: str, max_tokens: int = 2024) -> str:
    pip = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                torch_dtype=torch.float16,
                device_map="auto",
                eos_token_id=eos_token_id,
                pad_token_id=eos_token_id, 
                )

    return pip(
        prompt,
        max_new_tokens=max_tokens,
        do_sample=False,
        temperature=None,
        top_p=None,
        num_return_sequences=1,
        no_repeat_ngram_size=2,
    )[0]['generated_text']

chainlang = HuggingFacePipeline(pipeline=pipe_chainlang)
