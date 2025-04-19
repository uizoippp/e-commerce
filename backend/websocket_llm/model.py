import tensorflow as tf
tf.get_logger().setLevel('ERROR')
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
from sentence_transformers import SentenceTransformer

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

def generate_answer(prompt: str, max_tokens: int = 4048) -> str:
    pipe = pipeline(
                    "text-generation",
                    model=model,
                    tokenizer=tokenizer,
                    torch_dtype=torch.float16,
                    device_map="auto",
                    eos_token_id=eos_token_id,
                    pad_token_id=eos_token_id, 
                    )
    return pipe(
        prompt,
        max_new_tokens=max_tokens,
        do_sample=False,
        num_return_sequences=1,
        no_repeat_ngram_size=2,
    )[0]['generated_text']#.split("### Assistant:")[-1].strip()