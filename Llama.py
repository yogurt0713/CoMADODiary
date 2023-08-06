from llama_index import SimpleDirectoryReader, GPTVectorStoreIndex, load_index_from_storage, StorageContext, QuestionAnswerPrompt
from llama_index import PromptHelper, LLMPredictor, ServiceContext
from llama_index import download_loader
import openai
import json
import os
from langchain.chat_models import ChatOpenAI
# ConversationBufferMemoryをチェーン内で使う
from langchain.agents import AgentType, Tool, initialize_agent
# ConversationSummaryBufferMemory: 過去会話の要約と，直近の会話（トークン数で指定）を保持
# ConversationBufferWindowMemory; 直近k個の会話履歴のみ保持．古い会話が削除されるのでプロンプトが膨大にならない．
from langchain.memory import ConversationSummaryBufferMemory, ConversationBufferWindowMemory
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from sys import argv

# load .env file
from dotenv import load_dotenv
load_dotenv()

# summarize用


class Llama:
    def __init__(self):

        openai.api_key = os.getenv["OPENAI_API_KEY"]

        # define LLM
        max_input_size = 4096
        num_output = 2048
        max_chunk_overlap = 20

        prompt_helper = PromptHelper(
            max_input_size, num_output, max_chunk_overlap)
        llm_predictor = LLMPredictor(llm=ChatOpenAI(
            temperature=0.2, model_name="gpt-4"))
        self.service_context = ServiceContext.from_defaults(
            llm_predictor=llm_predictor, prompt_helper=prompt_helper)
        # create index (for CoMADO load json and additional data)

    def loadJson(self, filename):
        JSONReader = download_loader("JSONReader")
        loader = JSONReader()
        document = loader.load_data(file=filename)
        self.index = GPTVectorStoreIndex.from_documents(
            document, service_context=self.service_context)

    # JSONをloadした後に追加でテキストファイルを読み込む(directory指定）
    def load_additional_txt_from_directory(self, directory_path):

        documents = SimpleDirectoryReader(directory_path).load_data()
        for document in documents:
            self.index.insert(document)

    # JSONを追加で読み込む（ファイル指定）
    def load_additional_json_from_directory(self, filename):

        JSONReader = download_loader("JSONReader")
        loader = JSONReader()
        document = loader.load_data(file=filename)
        self.index.insert(document)

    def save_index(self):
        self.index.set_index_id("vector_index")
        self.index.storage_context.persist('./storage')

    def search_custom_prompt(self, query, prompt):
        with open(prompt, 'r') as f:
            custom = f.read()
        qa_prompt = QuestionAnswerPrompt(custom)
        query_engine = self.index.as_query_engine(
            text_qa_templage=qa_prompt, response_mode="tree_summarize")
        response = query_engine.query(query)
        return response

# rebuild storage context


class RetriveLlama:
    def __init__(self):
        pass

    def load_index(self, storage_dir):
        storage_context = StorageContext.from_defaults(persist_dir=storage_dir)
        self.index = load_index_from_storage(storage_context)

        tools = [
            Tool(
                name="llamaIndex",
                func=lambda q: str(self.index.as_query_engine().query(q)),
                description="CoMADOデータの体験記録を調べる際に使います．東京大学の博物館見学の体験記録が保存されているのでその検索に利用できます．",
                return_direct=True,
            ),
        ]

        llm = ChatOpenAI(temperature=0.2, client=openai, model_name="gpt-4")

        prefix = """次の質問にtoolを使って答えてください．"""
        suffix = """日本語で回答よろしくお願いします"""

        self.agent_chain = initialize_agent(
            tools,
            llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=memory,
            prefix=prefix,
            suffix=suffix,
            verbose=True,
        )

    def chat(self):
        while True:
            user_input = input("You: ")
            if user_input == "exit":
                print("Bye!")
                break

            response = self.agent_chain.run(input=user_input)
            print("Agent: " + response)


# chatbot用


class ChatLlama:
    def __init__(self):

        openai.api_key = os.getenv["OPENAI_API_KEY"]

    def loadJson(self, filename):
        JSONReader = download_loader("JSONReader")
        loader = JSONReader()
        document = loader.load_data(file=filename)
        self.index = GPTVectorStoreIndex.from_documents(
            document)

        # プロンプトを定義
        with open("prompt-CoMADO.txt", 'r') as f:
            self.QA_PROMPT_TMPL = f.read()

        tools = [
            Tool(
                name="llamaIndex",
                func=lambda q: str(self.index.as_query_engine().query(q)),
                description="CoMADOデータの体験記録を調べる際に使います．東京大学の博物館見学の体験記録が保存されているのでその検索に利用できます．",
                return_direct=True,
            ),
        ]

        llm = ChatOpenAI(temperature=0.2, client=openai, model_name="gpt-4")
        """llm = ChatOpenAI(streaming=True,callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]), client=openai,temperature=0.2)"""

        memory = ConversationSummaryBufferMemory(
            llm=llm,
            memory_key="chat_history",
            max_token_limit=1000,
        )

        prefix = """次の質問にtoolを使って答えてください．"""
        suffix = """日本語で回答よろしくお願いします"""

        self.agent_chain = initialize_agent(
            tools,
            llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=memory,
            prefix=prefix,
            suffix=suffix,
            verbose=True,
        )

    def save_index(self):
        self.index.set_index_id("vector_index")
        self.index.storage_context.persist('./storage')

    def chat(self):
        while True:
            user_input = input("You: ")
            if user_input == "exit":
                print("Bye!")
                break

            response = self.agent_chain.run(input=user_input)
            print("Agent: " + response)


# comado dataのjsonファイルを読み込む
# option data がある場合読み込むようにする（テキストファイル）


# chat形式でQAを作成する
# 　前の会話は記憶する(langchain memoryクラスをつかう）
""" https://zenn.dev/t_kakei/articles/94d2c3bfdb839d
https://book.st-hakky.com/docs/memory-of-langchain/


# 作ったモデルは保存する（あとからよびだせるように）
https://zenn.dev/fusic/articles/try-llamaindex

# 参照：プロプトテンプレート例　llama hubsにapiある
https://qiita.com/DeepTama/items/ffb7425cefe97bb5408a
 """

if __name__ == '__main__':

    if argv[1] == "1":
        # chatbot用
        cl = ChatLlama()

        cl.loadJson('./0712.json')
        cl.save_index()

        cl.chat()

    else:
        rt = RetriveLlama()
        rt.load_index("./storage")
        rt.chat()

"""'''
    ll = Llama()
    ll.loadJson('./0712.json')

    while True:
        # 質問を入力
        query = input('質問を入力してください（終了は「終了」:')
        if query == '終了':
            break
        else:
            response = ll.search_custom_prompt(query, 'prompt-CoMADO.txt')
            print(response) 
"""
