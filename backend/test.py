from websocket_llm.functions import *
from websocket_llm.model import *
from database.database import *

if __name__ == "__main__":
    # text = "Tôi muốn biết về món khoái khẩu của Nguyễn Xuân Son."
    # docs = relevant_documents(text=text, top_k=3, threshold=0.7, db=Session())

    # role_system = """Bạn là một trợ lý AI hữu ích. Chỉ sử dụng thông tin trong tài liệu để trả lời câu hỏi. Nếu không tìm thấy thông tin cần thiết, hãy trả lời: "Tôi không biết!". Không được tự suy đoán hoặc sử dụng kiến thức bên ngoài.\n"""
    # prompt = build_prompt(documents=docs, question=text, system_msg=role_system)

    # print(generate_answer(prompt=prompt))

    text = "Sự khác biệt về cách điều hành đất nước giữa Joe Biden và Donald Trump?"
    print(decompose_prompt(query=text))

