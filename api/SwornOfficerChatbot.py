from pinecone import Pinecone
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
from pathlib import Path

env_path = "/Users/jameschan/swornprojects/sworn-chat-bot/.env"

# print(f"Checking .env file at: {env_path}")
# print(f"File exists: {os.path.exists(env_path)}")

# with open(env_path, 'r') as f:
#     print("Content of .env file:")
#     print(f.read())

load_dotenv(dotenv_path=env_path, override=True)
# print(f"After loading, OPENAI_API_KEY={os.getenv('OPENAI_API_KEY')}")

# Initialize API clients
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')

# Add this debugging section after load_dotenv()
# print("Current working directory:", os.getcwd())
# print("Environment file loaded:", os.path.exists('.env'))
# print("API Key being used:", OPENAI_API_KEY[:10] + "..." if OPENAI_API_KEY else "None")

if not OPENAI_API_KEY or not PINECONE_API_KEY:
    raise ValueError("Missing required environment variables. Please ensure OPENAI_API_KEY and PINECONE_API_KEY are set in .env")

client = OpenAI(api_key=OPENAI_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("swornvideorecommendationsystem")

class ContentChatbot:
    def __init__(self):
        self.conversation_history = []

    def generate_embedding(self, text):
        """Generate embedding for search query"""
        try:
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Error generating embedding: {str(e)}")

    def search_content(self, query, top_k=3):
        """Search content from the sworn-text-content namespace"""
        query_embedding = self.generate_embedding(query)
        used_sources = []  # We'll collect sources here
        
        try:
            results = index.query(
                namespace="sworn-text-content",
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            # Collect sources from metadata
            if results and hasattr(results, 'matches'):
                for match in results.matches:
                    source = match.metadata.get('text-source', 'Unknown source')
                    if source not in used_sources:
                        used_sources.append(source)
            
            return results, used_sources  # Return both results and sources
        except Exception as e:
            print(f"Error searching content: {str(e)}")
            return None, []

    def safe_get_metadata(self, match):
        """Safely extract metadata from a match"""
        try:
            source = match.metadata.get('text-source', 'Unknown source')
            content = match.metadata.get('content', 'No content available')
            return source, content
        except AttributeError:
            return 'Unknown source', 'No content available'

    def format_context(self, video_results, content_results):
        """Format search results into context for the LLM"""
        context = []

        # Add content from ns2 (educational materials)
        if content_results and hasattr(content_results, 'matches'):
            context.append("Relevant information from educational content:")
            for match in content_results.matches:
                source, content = self.safe_get_metadata(match)
                context.append(f"\nFrom {source}:\n{content}")

        # Add content from ns1 (video transcripts)
        if video_results and hasattr(video_results, 'matches'):
            context.append("\nRelevant information from video transcripts:")
            for match in video_results.matches:
                source, content = self.safe_get_metadata(match)
                context.append(f"\nFrom video {source}:\n{content}")

        if not context:
            context.append("No relevant content found in the knowledge base.")

        return "\n".join(context)

    def generate_response(self, user_query, context):
        """Generate a response using the OpenAI API"""
        try:
            messages = [
                {"role": "system", "content": """You are a helpful assistant with access to a knowledge base of educational
                 content and video transcript, curated specifically to help on duty police officers manage their health.
                 Use the provided context to answer questions accurately. Be conversational but precise.
                 When you reference information, mention if it comes from educational content or video material.
                 If the context doesn't contain relevant information, be honest about it and provide general guidance."""},
                {"role": "user", "content": f"""Context:\n{context}\n\nUser Question: {user_query}
                 Please provide a helpful response using this context. If the context doesn't contain relevant information,
                 let me know and provide general guidance instead."""}
            ]

            messages.extend(self.conversation_history)

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content

        except Exception as e:
            return f"I apologize, but I encountered an error generating a response. Please try asking your question in a different way."

    def chat(self, user_input):
        try:
            video_results, used_sources = self.search_content(user_input)
            context = self.format_context(video_results, None)  # Keep existing context building
            response = self.generate_response(user_input, context)

            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": response})
            if len(self.conversation_history) > 6:
                self.conversation_history = self.conversation_history[-6:]

            return {
                "response": response,
                "sources": used_sources  # Include sources in response
            }

        except Exception as e:
            return {
                "response": f"I apologize, but I encountered an error: {type(e).__name__} - {str(e)}", 
                "sources": []
            }


def main():
    chatbot = ContentChatbot()

    print("Content Chatbot initialized. Type 'quit' to exit.")
    print("Connecting to knowledge base...")

    while True:
        user_input = input("\nYou: ").strip()
        if not user_input:
            continue

        if user_input.lower() == 'quit':
            break

        response = chatbot.chat(user_input)
        print("\nAssistant:", response)


if __name__ == "__main__":
    main()