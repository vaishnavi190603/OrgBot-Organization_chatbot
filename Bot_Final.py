import json
import textsim2  # Import the text similarity module

class UltraChatBot:
    def __init__(self, user_type):
        """Initialize chatbot with the appropriate dataset based on user type (admin/user)."""
        self.user_type = user_type  # Store user type
        self.dataset = self.load_dataset()
        self.last_question = None  # Store the last unknown question for admin training

    def load_dataset(self):
        """Load dataset based on user type and ensure correct structure."""
        json_file = 'Employee_Chatbot.json' if self.user_type == "employees" else 'User_Chatbot.json'
        try:
            with open(json_file, 'r', encoding="utf8") as file:
                data = json.load(file)
                if isinstance(data, list) and all(isinstance(i, list) and len(i) == 2 for i in data):
                    print(f"✅ Loaded dataset from {json_file}: {len(data)} entries")  # Debugging print
                    return data  # ✅ Ensure dataset is a list of [question, answer]
                else:
                    print(f"❌ Error: {json_file} has an incorrect structure. Expected [['question', 'answer']].")
                    return []
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"❌ Error loading {json_file}: {e}")
            return []  # Return empty list if the file is missing or corrupted

    def process_incoming_message(self, incoming_message):
        """Process user message and return chatbot response."""
        return self.text_similarity(incoming_message)

    def text_similarity(self, user_input):
        """Find best matching response from dataset using word similarity and synonyms."""
        self.last_question = user_input  # Store last question for admin training
        best_match = None
        highest_match_score = 0  # Track the best match score

        # ✅ Handle admin training input
        if self.user_type == "employees" and user_input.lower().startswith("yes:"):
            return self.train_chatbot(user_input.replace("yes:", "").strip())

        # ✅ Ensure dataset is valid before iterating
        if not self.dataset:
            return "⚠️ Sorry, no knowledge base is loaded."

        # ✅ Search for a matching response in the dataset
        for input_text, response_text in self.dataset:
            match_score = textsim2.count_matching_words(input_text, user_input)
            print(f"🔍 Comparing: '{input_text}' | User: '{user_input}' | Score: {match_score}")  # Debugging print

            if match_score > highest_match_score:
                highest_match_score = match_score
                best_match = response_text

        # ✅ If a good match is found, return it
        if highest_match_score > 0:
            return best_match

        # ✅ If no match found, store question for admin training
        if self.user_type == "employees":
            return f"🤖 I don't know this. You can train me by typing 'yes: your answer'. Your question: {self.last_question}"
        else:
            return "🚫 You have no authority to see this data."

    def train_chatbot(self, new_answer):
        """Train chatbot with a new answer for the last unknown question."""
        if self.last_question:
            entry = [self.last_question, new_answer]
            self.dataset.append(entry)

            # ✅ Update dataset file
            json_file = 'Employee_Chatbot.json'
            try:
                with open(json_file, 'w', encoding="utf8") as file:
                    json.dump(self.dataset, file, ensure_ascii=False, indent=4)
                self.last_question = None  # Clear stored question
                return "✅ Thank you! Your input has been added in the correct format (question-answer)."
            except Exception as e:
                return f"❌ Error saving new data: {e}"
        else:
            return "⚠️ There's no previous question to train."

# Example Usage
if __name__ == "__main__":
    user_type = input("Enter user type (employees/user): ").strip().lower()
    chatbot = UltraChatBot(user_type)

    while True:
        user_message = input("You: ")
        if user_message.lower() == "exit":
            print("Chatbot: Goodbye! 👋")
            break
        response = chatbot.process_incoming_message(user_message)
        print(f"Chatbot: {response}")
