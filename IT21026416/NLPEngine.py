from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments, EarlyStoppingCallback
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import numpy as np
from nltk.corpus import wordnet
import torch
import torch.nn as nn
import os
import gc
import random
import openai  # To integrate OpenAI GPT-4 for justifications
from dotenv import load_dotenv
from sklearn.utils.class_weight import compute_class_weight

# Global model, tokenizer, and OpenAI API key variables
model = None
tokenizer = None

# Load the environment variables from the .env file
load_dotenv(dotenv_path=r'D:\NLP\NLPFinal\Main\nlp-browser-security\.env')

# Retrieve the OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Test if the key is loaded correctly
print(f"OpenAI API Key: {openai.api_key}")

def load_model():
    global model, tokenizer
    model_name = 'bert-base-uncased'

    # Check if model and tokenizer are already loaded
    if model is None:
        print("Loading BERT model...")
        try:
            # Load pre-trained BERT model
            model = BertForSequenceClassification.from_pretrained(model_name, num_labels=3)
            
            # Apply dropout configuration
            model.config.hidden_dropout_prob = 0.2  # Apply dropout to the BERT model
            model.config.attention_probs_dropout_prob = 0.2
            print("Model loaded and dropout configuration applied.")
        
        except Exception as e:
            print(f"Error loading BERT model: {e}")
    
    else:
        print("BERT model is already loaded.")

    if tokenizer is None:
        print("Loading BERT tokenizer...")
        try:
            # Load the tokenizer
            tokenizer = BertTokenizer.from_pretrained(model_name)
            print("Tokenizer loaded successfully.")
        
        except Exception as e:
            print(f"Error loading BERT tokenizer: {e}")
    
    else:
        print("BERT tokenizer is already loaded.")


# Data augmentation methods (for training purposes)
def synonym_replacement(text):
    words = text.split()
    new_words = words.copy()
    random_word_list = list(set([word for word in words if wordnet.synsets(word)]))
    random.shuffle(random_word_list)
    replaced_words = set()
    num_replacements = max(1, int(0.1 * len(words)))

    for random_word in random_word_list:
        if random_word in replaced_words:
            continue

        synonyms = wordnet.synsets(random_word)
        if synonyms:
            synonym = synonyms[0].lemmas()[0].name()
            new_words = [synonym if word == random_word else word for word in new_words]
            replaced_words.add(random_word)
        if len(replaced_words) >= num_replacements:
            break
    return ' '.join(new_words)


def back_translation(text):
    # Dummy function for back translation (replace with actual implementation)
    return text

def augment_data(texts, labels):
    augmented_texts = []
    augmented_labels = []

    for text, label in zip(texts, labels):
        augmented_texts.append(synonym_replacement(text))
        augmented_texts.append(back_translation(text))
        augmented_labels.extend([label] * 2)  # Duplicate the label for each augmentation

    return augmented_texts, augmented_labels


def random_insertion(text):
    words = text.split()
    new_words = words.copy()
    random_word_list = list(set([word for word in words if wordnet.synsets(word)]))

    if not random_word_list:
        return text

    num_insertions = max(1, int(0.1 * len(words)))
    
    for _ in range(num_insertions):
        random_word = random.choice(random_word_list)
        synonyms = wordnet.synsets(random_word)
        if synonyms:
            synonym = synonyms[0].lemmas()[0].name()
            insert_position = random.randint(0, len(new_words))
            new_words.insert(insert_position, synonym)
    return ' '.join(new_words)



def ensemble_classification(models, input_text):
    votes = []
    for model in models:
        result = classify_text_with_context(input_text)
        votes.append(result["label"])

    # Majority vote for final prediction
    final_prediction = max(set(votes), key=votes.count)
    return final_prediction


# Function to compute metrics for evaluation
def compute_metrics(p):
    preds = np.argmax(p.predictions, axis=1)
    precision, recall, f1, _ = precision_recall_fscore_support(
        p.label_ids, preds, average='weighted', zero_division=1
    )
    acc = accuracy_score(p.label_ids, preds)
    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall
    }


# Function to clear model cache
def clear_model_cache():
    torch.cuda.empty_cache()
    gc.collect()


# Function to save the model and tokenizer
def save_model_and_tokenizer(model, tokenizer, save_dir='./saved_models'):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    try:
        model.save_pretrained(save_dir, safe_serialization=False)
        tokenizer.save_pretrained(save_dir)
    except Exception as e:
        print(f"Error while saving using save_pretrained: {e}")
        torch.save(model.state_dict(), os.path.join(save_dir, 'model_state.pth'))
        print("Model saved using torch.save as a fallback.")


texts = [
    # Threat Prevention Policy (TPP)
    "How do I ensure secure browsing for users?", # TPP
    "What’s the best way to block risky websites?", # TPP
    "I need to protect the browser against malware.", # TPP
    "Is there a way to disable extensions that could cause threats?", # TPP
    "How do I allow only company-approved browser plugins?", # TPP
    "Ensure users don’t access untrusted sites.", # TPP
    "I want to block websites with excessive ads.", # TPP
    "Can we prevent unauthorized code injection through the browser?", # TPP
    "How do we restrict browser permissions for external content?", # TPP
    "What’s the safest way to handle browser certificates?", # TPP
    "I need to block third-party website scripts.", # TPP
    "Is there a way to enforce strict security settings in the browser?", # TPP
    "Allow only necessary permissions on the browser.", # TPP
    "Can we disable notifications from untrusted sites?", # TPP
    "How do we control browser extension installation?", # TPP
        # Threat Prevention Policy (TPP) samples
    "Block all attempts to use the browser camera", # TPP
    "Restrict access to camera in browser", # TPP
    "Disable any requests for camera access", # TPP
    "Prevent any site from accessing camera or microphone", # TPP
    "Block external websites from accessing system camera", # TPP
    "Enable strict security policy for camera access", # TPP
    
    # Data Leakage Policy (DLP)
    "How can we prevent sensitive data from being printed?", # DLP
    "Can we restrict file downloads to company-approved domains?", # DLP
    "What’s the policy to prevent browser sync of personal information?", # DLP
    "I need to ensure browsing history isn’t saved.", # DLP
    "How do I prevent users from downloading files from unauthorized sites?", # DLP
    "Disable browser autofill for all users.", # DLP
    "Is there a way to block third-party cookies to protect privacy?", # DLP
    "Ensure that all browser cookies are deleted after each session.", # DLP
    "How do I enforce the deletion of browser history after 7 days?", # DLP
    "We need to block users from uploading files to external websites.", # DLP
    "How can I ensure that no screenshots are taken in the browser?", # DLP
    "Block downloads from unapproved websites.", # DLP
    "Can we restrict browser metrics from being reported?", # DLP
    "Ensure that password saving is disabled.", # DLP
    "Limit file uploads to trusted services only.", # DLP,
        # Data Leakage Prevention (DLP) samples
    "Disable autofill for all forms", # DLP
    "Do not allow passwords to be saved in the browser", # DLP
    "Restrict download access to company files", # DLP
    "How do I disable the browser's ability to sync passwords?", # DLP
    "Block the browser from storing browsing history", # DLP
    "How do I prevent users from sharing confidential data on social media?",
    "Ensure that browser data is deleted after closing the session.",
    "Limit the ability to copy or paste sensitive information.",
    "How do I block uploads of confidential documents?",
    "Ensure that password fields are not auto-filled for security reasons.",
    "Limit downloads to only company-approved files.",
    "Restrict clipboard access for browser sessions.",
    "Ensure no sensitive data is retained after session expiration.",
    "How do I ensure secure browsing for users?",
    "Block websites with risky content",


    # Compliance Queries
    "I need the browser to comply with the latest NIST standards.", # Compliance
    "How do I ensure that we’re compliant with CM-1 of NIST?", # Compliance
    "What’s the best way to handle cookies to stay compliant with GDPR?", # Compliance
    "What settings should be enforced for HIPAA compliance in the browser?", # Compliance
    "What’s the policy for handling PII in browsers?", # Compliance
    "Enforce policies to minimize the risk of data leaks.", # Compliance
    "Ensure all browser activities are compliant with ISO 27001.", # Compliance
    "Block features that may lead to unauthorized data sharing.", # Compliance
    "Can we ensure the browser is aligned with SOC 2 compliance?", # Compliance
    "How do I disable features that could violate privacy regulations?" # Compliance

        # Ambiguous samples that may require clarification or additional context
    "Block websites that may track user data", # Could be TPP or DLP
    "How do I protect browser data from being stolen?", # Uncertain (requires clarification)
    "Prevent the use of unauthorized browser extensions", # TPP
    "Allow only certain websites to access system files", # Could be TPP or DLP
    "Restrict permissions on sensitive data", # Uncertain (requires clarification)
]


labels = [
    # TPP (0) and DLP (1) labels
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, # TPP labels
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  1,1,1,1,1,1, 1, 1, 1, 1, 1, 1, 1, 1, # DLP labels
    2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 1, 1, 1, 1,  # Compliance/Vague labels (could map to "Uncertain")
    0, 1, 
]
print(f"Initial number of texts: {len(texts)}")
print(f"Initial number of labels: {len(labels)}")


# Ensure the initial assertion holds
assert len(texts) == len(labels), "Mismatch between number of texts and labels before augmentation"


# Augment the data
augmented_texts, augmented_labels = augment_data(texts, labels)
assert len(augmented_texts) == len(augmented_labels), "Mismatch after data augmentation"


print(f"Number of texts after augmentation: {len(texts)}")
print(f"Number of labels after augmentation: {len(labels)}")

# Combine with original dataset
train_texts = texts + augmented_texts
train_labels = labels + augmented_labels

def classify_text_with_context(input_text, threshold=0.3):  # Lowering the threshold to 0.3
    load_model()
    inputs = tokenizer(input_text, return_tensors='pt', truncation=True, padding=True)
    outputs = model(**inputs)
    logits = outputs.logits
    probabilities = torch.softmax(logits, dim=-1)

    predicted_class_id = torch.argmax(probabilities).item()
    confidence = probabilities[0][predicted_class_id]

    if confidence < threshold:
        clarification_needed = f"The model's confidence is below the threshold. Can you provide more details?"
        return {
            "label": "Uncertain",
            "confidence": confidence.item(),
            "justification": clarification_needed
        }

    classification_label = map_class_id_to_label(predicted_class_id)
    print(f"Classified: {input_text} as {classification_label} with confidence {confidence}")  # Add this line
    explanation = get_openai_justification(input_text, classification_label)

    return {
        "label": classification_label,
        "confidence": confidence.item(),
        "justification": explanation
    }


# Function to map class IDs to security categories
def map_class_id_to_label(class_id):
    class_map = {0: "Threat Prevention", 1: "Data Leakage", 2: "Uncertain"}
    return class_map.get(class_id, "Uncertain")


# Function to integrate OpenAI GPT-4 for generating justifications
def get_openai_justification(input_text, classification_label):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a cybersecurity expert. You will help non technical users."},
                {"role": "user", "content": f"Explain why the following policy is classified under {classification_label}: {input_text}"}
            ],
            max_tokens=100,
            temperature=0.7,
        )
        explanation = response['choices'][0]['message']['content'].strip()
        return explanation
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return "Explanation could not be generated."

print(f"Number of texts before split: {len(texts)}")
print(f"Number of labels before split: {len(labels)}")
assert len(texts) == len(labels), "Mismatch between texts and labels before split"

def train_model():
    print("Training the model...")
    load_model()

    train_texts, val_texts, train_labels, val_labels = train_test_split(
        texts, labels, test_size=0.2, random_state=42
    )
    print(f"Train texts: {len(train_texts)}")
    print(f"Validation texts: {len(val_texts)}")
    print(f"Train labels: {len(train_labels)}")
    print(f"Validation labels: {len(val_labels)}")
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    train_encodings = tokenizer(train_texts, truncation=True, padding=True)
    val_encodings = tokenizer(val_texts, truncation=True, padding=True)

    class CustomDataset(torch.utils.data.Dataset):
        def __init__(self, encodings, labels):
            self.encodings = encodings
            self.labels = labels

        def __getitem__(self, idx):
            item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
            item['labels'] = torch.tensor(self.labels[idx])
            return item

        def __len__(self):
            return len(self.labels)

    train_dataset = CustomDataset(train_encodings, train_labels)
    val_dataset = CustomDataset(val_encodings, val_labels)

    # Define the training arguments
    training_args = TrainingArguments(
        output_dir='./results',
        num_train_epochs=20,  # More epochs may help fine-tune the model better
        per_device_train_batch_size=64,  # Increase batch size for broader data exposure
        per_device_eval_batch_size=64,
        warmup_steps=100,
        weight_decay=0.01,
        learning_rate=5e-6,  # Lower learning rate for more fine-tuning # to 
        logging_dir='./logs',
        logging_steps=50,  # Log every 50 steps
        save_steps=500,  # Save checkpoint every 500 steps
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        save_total_limit=2,
        lr_scheduler_type="linear",  # Gradual learning rate decay
    )


    # Early stopping callback
    early_stopping = EarlyStoppingCallback(
        early_stopping_patience=5,  # Stop training if the evaluation metric doesn't improve after 3 epochs
        early_stopping_threshold=0.01  # Consider the training to have improved if the metric changes by at least 1%
    )

    # Define the Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
        callbacks=[early_stopping],  # Add the early stopping callback
    )

    # Start training
    trainer.train()

    # Save model and tokenizer after training
    save_model_and_tokenizer(model, tokenizer)

    # Clear the model cache
    clear_model_cache()


class_weights = compute_class_weight('balanced', classes=np.unique(labels), y=labels)
class_weights = torch.tensor(class_weights, dtype=torch.float)
loss_fn = nn.CrossEntropyLoss(weight=class_weights)


# Compute weighted loss (this can be integrated into Trainer's loss function)
def compute_loss(preds, labels):
    loss = loss_fn(preds, labels)
    return loss

from collections import Counter
print(Counter(labels))  # Check the distribution of labels

if __name__ == "__main__":
    # Train the model if necessary
    train_model()

    # Automate classification of text samples and track misclassifications
    print("\n--- Automated Text Classification ---\n")
    misclassified = []

    for text, true_label in zip(texts, labels):
        result = classify_text_with_context(text)
        predicted_label = result['label']
        confidence = result['confidence']

        if predicted_label != map_class_id_to_label(true_label):
            misclassified.append((text, predicted_label, true_label, confidence))

        print(f"Input: {text}")
        print(f"Prediction: {predicted_label}")
        print(f"Confidence: {confidence:.4f}")
        print("-" * 80)

    # Display misclassified examples
    print("\n--- Misclassified Examples ---\n")
    for item in misclassified:
        print(f"Text: {item[0]}")
        print(f"Predicted: {item[1]}, True: {item[2]}, Confidence: {item[3]:.4f}")
        print("-" * 80)

    print("\n--- Classification Complete ---")
