from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
from sklearn.model_selection import train_test_split
import numpy as np
from nltk.corpus import wordnet
import random
import time
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import os
import gc
import torch
from transformers import BertForSequenceClassification, Trainer, TrainingArguments
import torch.nn as nn
from sklearn.utils import class_weight
import numpy as np

def synonym_replacement(text): 
    words = text.split()
    new_words = words.copy()
    random_word_list = list(set([word for word in words if wordnet.synsets(word)]))
    random.shuffle(random_word_list)
    replaced_words = set()  # Track already replaced words
    num_replacements = max(1, int(0.1 * len(words)))

    for random_word in random_word_list:
        if random_word in replaced_words:
            continue  # Skip already replaced words

        synonyms = wordnet.synsets(random_word)
        if synonyms:
            synonym = synonyms[0].lemmas()[0].name()  # Get first synonym
            # Avoid multiple replacements of the same word
            new_words = [synonym if word == random_word else word for word in new_words]
            replaced_words.add(random_word)  # Mark this word as replaced
        if len(replaced_words) >= num_replacements:
            break  # Stop once the required number of replacements is reached
    return ' '.join(new_words)


# Function for back translation (dummy function, you need an API or library for actual implementation)
def back_translation(text):
    # Translate to another language and back to original language
    # This is a placeholder. You can use services like Google Translate API for actual implementation.
    return text

def random_insertion(text):
    words = text.split()
    new_words = words.copy()
    random_word_list = list(set([word for word in words if wordnet.synsets(word)]))

    # Check if random_word_list is empty before proceeding
    if not random_word_list:
        return text  # Return original text if no words with synonyms are found

    num_insertions = max(1, int(0.1 * len(words)))
    
    for _ in range(num_insertions):
        random_word = random.choice(random_word_list)
        synonyms = wordnet.synsets(random_word)
        if synonyms:
            synonym = synonyms[0].lemmas()[0].name()
            insert_position = random.randint(0, len(new_words))  # Insert at random position
            new_words.insert(insert_position, synonym)
    return ' '.join(new_words)


# Original text samples and labels
texts = [
    # Threat Prevention Policy (Includes Browser Extension Policy) - 10 samples
    #Threat Prevention Policy SafeBrowsingProtectionLevel
    "Enable Safe browsing protection level to protect against dangers", #SafeBrowsingProtectionLevel
    "Block websites that display excessive ads.", #BlockExcessiveAds
    "Block excessive ads",
    "block ads",
    "block web abs",
    "cert errors",
    "allow cam",
    "Override certificate errors for trusted websites.", #SSLCertificateProtection
    "Block third-party websites that inject code.", #BlockInjectedCode
    "Block permissions.", #SetPermissions
    "Whitelist only essential extensions.", #WhitelistExtensions
    "Blacklist suspicious extensions.", #BlacklistExtensions
    "Allow Camera Permission", #camera
    "Allow Camera", #camera
    "Block Camera permission", #camera
    "Block Camera", #camera
    "Set Permissions",#camera
    "Set location permission", #geolocation
    "Allow Motion Sensors", #MotionSensor
    "Block Motion Sensors", #MotionSensor
    "Allow notification", #Notifications
    "Block notifications", #Notifications
    "Block Javascript", #JavaScript
    "Allow javascript", #Notifications
    "Block pop ups", 
    "Allow pop ups",
    "Allow web usb access",
    "block web usb access"
    "Enable Safe browsing strictly protection level to protect online against dangers.",
    "Block suspicious websites that display excessive ads.",
    "Whitelist only essential extensions for browsing.",
    "Allow device Camera Permission.",
    "Block unauthorized third-party websites that inject code.", 
    "Activate Safe browsing protection level to shield from threats."
    "Prevent websites that show too many ads.",
    "Whitelist only critical extensions.",
    "Allow Camera Access.",
    "Stop third-party websites from injecting scripts.",

    # Data Leakage Policy (Includes Download Filter Policy) - 20 samples
    "Print webpage",
    "browser sync",
    "Save browser history",
    "Autofill",
    "screenshots",
    "Remember passwords",
    "Site per process",
    "search suggest",
    "suggesting search",
    "Metrics reporting",
    "download location",
    "history deletion",
    "network prediction",
    "third party cookies",
    "restrict downloads",
    "Permit downloads",
    "Block downloads",
    "browsing data lifetime",
    "set browsing data lifetime",
    "Restrict printing of web pages.",
    "Disable browser sync for personal data.",
    "Prevent saving browser history.",
    "Disallow autofill of forms in the browser.",
    "Block file uploads to external websites.",
    "Disable screenshots in the browser.",
    "Prevent the browser from remembering passwords.",
    "Restrict site per process settings.",
    "Disable search suggestions in the browser.",
    "Block metrics reporting to Google.",
    "Prompt for download location every time.",
    "Prevent browser history deletion.",
    "Disable background processing in the browser.",
    "Disable network predictions.",
    "Block third-party cookies.",
    "Restrict downloads from specific web domains.",
    "Block all downloads from social media sites.",
    "Allow file downloads only from trusted sources.",
    "Block downloads of executable files.",
    "Permit downloads of PDF and TXT files.",
    "Configure the browser to delete browsing history older than 7 days.",
    "Set the browser to automatically clear cookies and site data after 24 hours.",
    "Ensure cached images and files are removed after one week to free up space.",
    "Remove saved passwords after 30 days to enhance security.",
    "Automatically delete autofill data that is more than 48 hours old.",  # <-- Comma added here
    "Purge site settings and hosted app data every 72 hours.",
    "Implement a policy to delete all browsing data every 12 hours to comply with company security standards.",
    "Set the browser to clear download history daily to maintain user privacy.",
    "Ensure that cookies and other site data are deleted every 6 hours to prevent unauthorized tracking.",
    "Schedule the browser to delete all browsing data older than 1 hour after every 15 minutes of activity.",
    "Enable a policy that clears cached images and files after 2 days while keeping cookies for 48 hours.",
    "Configure the browser to delete specific types of data, like browsing history and cookies, after 12 hours.",
    "Turn off browser sync for personal information.",
    "Stop the browser from saving history.",
    "Forbid file uploads to external platforms.",
    "Prohibit form autofill in the browser.",
    "Ask for download location every time.",
    "Disable browser completely sync for any personal data.",
    "Prevent the browser from saving any history.",
    "Block all file uploads to unknown external websites.",
    "Disallow automatic autofill of forms on any website in the browser.",
    "Prompt user for download location each time.",

    "Restrict users from saving browser history.",
    "Disable the browser's ability to sync personal information.",
    "Do not allow form autofill to function.",
    "Stop saving passwords in the browser to protect sensitive information.",
    "Ensure that browser suggestions are disabled for privacy reasons.",
    "Block all metrics reporting to third-party services.",
    "Restrict file downloads from untrusted sources.",
    "Limit printing of sensitive web content.",
    "Automatically clear browser cookies after 6 hours.",
    "Disallow screenshots to prevent information capture."
    


    "Block third party cookies", #this is DLP now
    "block websites",# this is TPP now
    "allow websites", ## this is TPP now
    "prevent websites"# this is TPP now
] 
# Additional text samples to address misclassifications
additional_texts = [
    "Block access to sites", # this is TPP now
    "Allow access only to educational websites.",  # this is TPP now
    "Enable filtering of adult content.",  # this is TPP now
    "Disable automatic form filling.",  # Data Leakage Policy
    "Allow only secure connections for browsing."  # Data Leakage Policy
]

# Correct the labels for TPP (0) and DLP (1)
labels = [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0,0,0, 0, 0, # TPP samples
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1 # DLP samples
]


# Corresponding labels
additional_labels = [
    0,  # Threat Prevention Policy
    0,  # Threat Prevention Policy
  # Data Leakage Policy
      # Data Leakage Policy
    1,
    1,
    1,  # Data Leakage Policy
]
# Corrected labels (Adding the missing two labels for Data Leakage Policy)

# Update the lengths of texts and labels
print(f"Length of texts: {len(texts)}")
print(f"Length of labels: {len(labels)}")

# Combine original and additional texts and labels
texts += additional_texts
labels += additional_labels

# Debugging step to print the lengths
print(f"Length of texts after combining: {len(texts)}")
print(f"Length of labels after combining: {len(labels)}")

# Data augmentation
augmented_texts = []
augmented_labels = []

for text, label in zip(texts + additional_texts, labels + additional_labels):
    augmented_texts.append(synonym_replacement(text))
    augmented_texts.append(random_insertion(text))
    augmented_texts.append(back_translation(text))
    
    augmented_labels.extend([label] * 3)  # Duplicate label for each augmentation

# Combine original and augmented data
all_texts = texts + additional_texts + augmented_texts
all_labels = labels + additional_labels + augmented_labels

# Debugging step: Print lengths of combined lists
print(f"Length of all_texts after augmentation: {len(all_texts)}")
print(f"Length of all_labels after augmentation: {len(all_labels)}")

# Ensure the lengths match
assert len(all_texts) == len(all_labels), "Lengths of texts and labels do not match!"

# Split the data into training and validation sets
train_texts, val_texts, train_labels, val_labels = train_test_split(all_texts, all_labels, test_size=0.2, random_state=42)

# Check class distribution in training set
unique, counts = np.unique(train_labels, return_counts=True)
print(f"Class distribution in training set: {dict(zip(unique, counts))}")

# Load the BERT tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

# Tokenize the texts
train_encodings = tokenizer(train_texts, truncation=True, padding=True)
val_encodings = tokenizer(val_texts, truncation=True, padding=True)

# Create a PyTorch dataset class
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

# Create training and validation datasets
train_dataset = CustomDataset(train_encodings, train_labels)
val_dataset = CustomDataset(val_encodings, val_labels)




# Define class weights (adjust based on your class distribution)
#class_weights = torch.tensor([0.5, 2.0], dtype=torch.float32).to('cuda' if torch.cuda.is_available() else 'cpu')
# Assuming train_labels is a list of your labels
label_set = list(set(train_labels))  # Get the unique labels
total_samples = len(train_labels)  # Total number of samples
label_counts = {label: 0 for label in label_set}  # Initialize counts for each label

# Count occurrences of each label
for label in train_labels:
    label_counts[label] += 1

# Calculate class weights as: total_samples / (num_classes * count_per_class)
class_weights = {label: total_samples / (len(label_set) * count) for label, count in label_counts.items()}
print("Class Weights:", class_weights)



# Custom Trainer class to apply class weights
class WeightedTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False):
        labels = inputs.get("labels")
        outputs = model(**inputs)
        logits = outputs.get("logits")
        
        # Use weighted cross-entropy loss
        loss_fct = nn.CrossEntropyLoss(weight=class_weights)
        loss = loss_fct(logits, labels)
        
        return (loss, outputs) if return_outputs else loss

# Update TrainingArguments without class_weights
# Re-train with adjusted weights and epochs



training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=7,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    warmup_steps=100,
    weight_decay=0.02,  # Slightly higher weight decay
    logging_dir='./logs',
    logging_steps=10,
    evaluation_strategy="epoch",  # Use 'epoch' for both evaluation and saving
    save_strategy="epoch",        # Ensure the saving strategy matches
    load_best_model_at_end=True,  # Early stopping related
    metric_for_best_model="f1",   # You can change this metric
    greater_is_better=True,       # Higher F1 is better
    save_total_limit=2,           # Limit the number of saved models
    learning_rate=1e-4  # Lower learning rate for better fine-tuning

)


# Define the model name, e.g., 'bert-base-uncased' or a custom model
model_name = 'bert-base-uncased'

# Load pre-trained model and tokenizer
model = BertForSequenceClassification.from_pretrained(model_name, num_labels=2)
tokenizer = BertTokenizer.from_pretrained(model_name)


# Function to compute evaluation metrics
def compute_metrics(p):
    preds = np.argmax(p.predictions, axis=1)
    precision, recall, f1, _ = precision_recall_fscore_support(p.label_ids, preds, average='weighted')
    acc = accuracy_score(p.label_ids, preds)
    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall
    }

# Create a Trainer instance with evaluation metrics
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics
)

# Re-train and test with better data handling for WFP cases
start_time = time.time()
trainer.train()
end_time = time.time()
print(f"Training time: {end_time - start_time:.2f} seconds")



# Manually clear any potential GPU or memory allocations
def clear_model_cache():
    torch.cuda.empty_cache()  # Clears GPU cache if using CUDA
    gc.collect()  # Forces Python garbage collection to release memory

# Before saving, ensure the model is not being mapped to memory
clear_model_cache()
# Save the fine-tuned model with torch.save as a fallback
try:
    model.save_pretrained('./saved_models', safe_serialization=False)
except Exception as e:
    print(f"Error during save_pretrained: {e}")
    # Fallback method
    torch.save(model.state_dict(), './saved_models/model_state.pth')

# Disable safetensors serialization and use default torch save

model.save_pretrained('./saved_models', safe_serialization=False)

def save_model_and_tokenizer(model, tokenizer, save_dir='./saved_models'):
    # Ensure the directory exists
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # Try to save the model with safe serialization disabled
    try:
        model.save_pretrained(save_dir, safe_serialization=False)  # Turn off safe serialization
        tokenizer.save_pretrained(save_dir)
    except Exception as e:
        print(f"Error while saving using save_pretrained: {e}")
        # Fallback to torch.save if safetensors fails
        torch.save(model.state_dict(), os.path.join(save_dir, 'model_state.pth'))
        print("Model saved using torch.save as a fallback.")

# Call the save function
save_model_and_tokenizer(model, tokenizer)



def classify_text(text, threshold=0.8):  # Adjusted threshold to 0.5
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True)
    outputs = model(**inputs)
    logits = outputs.logits
    probabilities = torch.softmax(logits, dim=-1)
    predicted_class_id = torch.argmax(probabilities).item()

    # Print probabilities for debugging
    print(f"Probabilities: {probabilities}")

    if probabilities[0][predicted_class_id] < threshold:
        return "Uncertain"

    return predicted_class_id

class FocalLoss(nn.Module):
    def __init__(self, gamma=2.0, alpha=None):
        super(FocalLoss, self).__init__()
        self.gamma = gamma
        self.alpha = alpha

    def forward(self, logits, targets):
        ce_loss = nn.CrossEntropyLoss()(logits, targets)
        p_t = torch.exp(-ce_loss)
        focal_loss = (1 - p_t) ** self.gamma * ce_loss
        return focal_loss

# In your WeightedTrainer class, replace CrossEntropyLoss with FocalLoss:
class WeightedTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False):
        labels = inputs.get("labels")
        outputs = model(**inputs)
        logits = outputs.get("logits")
        loss_fct = FocalLoss(gamma=2.0)
        loss = loss_fct(logits, labels)
        return (loss, outputs) if return_outputs else loss

# Convert class weights to a tensor
class_weights_tensor = torch.tensor([class_weights[label] for label in sorted(class_weights.keys())], dtype=torch.float)

# Define the loss function with class weights
criterion = nn.CrossEntropyLoss(weight=class_weights_tensor)


# Test the model with new samples
test_samples = [
    "Enable Safe browsing protection level to protect against dangers", #SafeBrowsingProtectionLevel
    "Block websites that display excessive ads.", #BlockExcessiveAds
    "Block excessive ads",
    "block ads",
    "block web abs",
    "cert errors",
    "allow cam",
    "Override certificate errors for trusted websites.", #SSLCertificateProtection
    "Block third-party websites that inject code.", #BlockInjectedCode
    "Block permissions.", #SetPermissions
    "Whitelist only essential extensions.", #WhitelistExtensions
    "Blacklist suspicious extensions.", #BlacklistExtensions
    "Allow Camera Permission", #camera
    "Allow Camera", #camera
    "Block Camera permission", #camera
    "Block Camera", #camera
    "Set Permissions",#camera
    "Set location permission", #geolocation
    "Allow Motion Sensors", #MotionSensor
    "Block Motion Sensors", #MotionSensor
    "Allow notification", #Notifications
    "Block notifications", #Notifications
    "Block Javascript", #JavaScript
    "Allow javascript", #Notifications
    "Block pop ups", 
    "Allow pop ups",
    "Allow web usb access",
    "block web usb access"
    "Enable Safe browsing strictly protection level to protect online against dangers.",
    "Block suspicious websites that display excessive ads.",
    "Whitelist only essential extensions for browsing.",
    "Allow device Camera Permission.",
    "Block unauthorized third-party websites that inject code.", 
    "Activate Safe browsing protection level to shield from threats."
    "Prevent websites that show too many ads.",
    "Whitelist only critical extensions.",
    "Allow Camera Access.",
    "Stop third-party websites from injecting scripts.",
    "Whitelist extensions",

    # Data Leakage Policy (Includes Download Filter Policy) - 20 samples
    "Print webpage",
    "browser sync",
    "Save browser history",
    "Autofill",
    "screenshots",
    "Remember passwords",
    "Site per process",
    "search suggest",
    "suggesting search",
    "Metrics reporting",
    "download location",
    "history deletion",
    "network prediction",
    "third party cookies",
    "restrict downloads",
    "Permit downloads",
    "Block downloads",
    "browsing data lifetime",
    "set browsing data lifetime",
    "Restrict printing of web pages.",
    "Disable browser sync for personal data.",
    "Prevent saving browser history.",
    "Disallow autofill of forms in the browser.",
    "Block file uploads to external websites.",
    "Disable screenshots in the browser.",
    "Prevent the browser from remembering passwords.",
    "Restrict site per process settings.",
    "Disable search suggestions in the browser.",
    "Block metrics reporting to Google.",
    "Prompt for download location every time.",
    "Prevent browser history deletion.",
    "Disable background processing in the browser.",
    "Disable network predictions.",
    "Block third-party cookies.",
    "Restrict downloads from specific web domains.",
    "Block all downloads from social media sites.",
    "Allow file downloads only from trusted sources.",
    "Block downloads of executable files.",
    "Permit downloads of PDF and TXT files.",
    "Configure the browser to delete browsing history older than 7 days.",
    "Set the browser to automatically clear cookies and site data after 24 hours.",
    "Ensure cached images and files are removed after one week to free up space.",
    "Remove saved passwords after 30 days to enhance security.",
    "Automatically delete autofill data that is more than 48 hours old.",  # <-- Comma added here
    "Purge site settings and hosted app data every 72 hours.",
    "Implement a policy to delete all browsing data every 12 hours to comply with company security standards.",
    "Set the browser to clear download history daily to maintain user privacy.",
    "Ensure that cookies and other site data are deleted every 6 hours to prevent unauthorized tracking.",
    "Schedule the browser to delete all browsing data older than 1 hour after every 15 minutes of activity.",
    "Enable a policy that clears cached images and files after 2 days while keeping cookies for 48 hours.",
    "Configure the browser to delete specific types of data, like browsing history and cookies, after 12 hours.",
    "Turn off browser sync for personal information.",
    "Stop the browser from saving history.",
    "Forbid file uploads to external platforms.",
    "Prohibit form autofill in the browser.",
    "Ask for download location every time.",
    "Disable browser completely sync for any personal data.",
    "Prevent the browser from saving any history.",
    "Block all file uploads to unknown external websites.",
    "Disallow automatic autofill of forms on any website in the browser.",
    "Prompt user for download location each time.",
    


    "Block third party cookies", #this is DLP now
    "block websites",# this is TPP now
    "allow websites", ## this is TPP now
    "prevent websites"# this is TPP now

    "Restrict users from saving browser history.",
    "Disable the browser's ability to sync personal information.",
    "Do not allow form autofill to function.",
    "Stop saving passwords in the browser to protect sensitive information.",
    "Ensure that browser suggestions are disabled for privacy reasons.",
    "Block all metrics reporting to third-party services.",
    "Restrict file downloads from untrusted sources.",
    "Limit printing of sensitive web content.",
    "Automatically clear browser cookies after 6 hours.",
    "Disallow screenshots to prevent information capture."
]


categories = ["Threat Prevention Policy", "Data Leakage Policy"]

expected_categories = [
    0,  # "Enable Safe browsing protection level to protect against dangers" (TPP)
    0,  # "Block websites that display excessive ads." (TPP)
    0,  # "Block excessive ads" (TPP)
    0,  # "block ads" (TPP)
    0,  # "block web abs" (TPP)
    0,  # "cert errors" (TPP)
    0,  # "allow cam" (TPP)
    0,  # "Override certificate errors for trusted websites." (TPP)
    0,  # "Block third-party websites that inject code." (TPP)
    0,  # "Block permissions." (TPP)
    0,  # "Whitelist only essential extensions." (TPP)
    0,  # "Blacklist suspicious extensions." (TPP)
    0,  # "Allow Camera Permission" (TPP)
    0,  # "Allow Camera" (TPP)
    0,  # "Block Camera permission" (TPP)
    0,  # "Block Camera" (TPP)
    0,  # "Set Permissions" (TPP)
    0,  # "Set location permission" (TPP)
    0,  # "Allow Motion Sensors" (TPP)
    0,  # "Block Motion Sensors" (TPP)
    0,  # "Allow notification" (TPP)
    0,  # "Block notifications" (TPP)
    0,  # "Block Javascript" (TPP)
    0,  # "Allow javascript" (TPP)
    0,  # "Block pop ups" (TPP)
    0,  # "Allow pop ups" (TPP)
    0,  # "Allow web usb access" (TPP)
    0,  # "block web usb access" (TPP)
    0,  # "Enable Safe browsing strictly protection level to protect online against dangers." (TPP)
    0,  # "Block suspicious websites that display excessive ads." (TPP)
    0,  # "Whitelist only essential extensions for browsing." (TPP)
    0,  # "Allow device Camera Permission." (TPP)
    0,  # "Block unauthorized third-party websites that inject code." (TPP)
    0,  # "Activate Safe browsing protection level to shield from threats." (TPP)
    0,  # "Prevent websites that show too many ads." (TPP)
    0,  # "Whitelist only critical extensions." (TPP)
    0,  # "Allow Camera Access." (TPP)
    0,  # "Stop third-party websites from injecting scripts." (TPP)

    # Data Leakage Policy (DLP)
    1,  # "Print webpage" (DLP)
    1,  # "browser sync" (DLP)
    1,  # "Save browser history" (DLP)
    1,  # "Autofill" (DLP)
    1,  # "screenshots" (DLP)
    1,  # "Remember passwords" (DLP)
    1,  # "Site per process" (DLP)
    1,  # "search suggest" (DLP)
    1,  # "suggesting search" (DLP)
    1,  # "Metrics reporting" (DLP)
    1,  # "download location" (DLP)
    1,  # "history deletion" (DLP)
    1,  # "network prediction" (DLP)
    1,  # "third party cookies" (DLP)
    1,  # "restrict downloads" (DLP)
    1,  # "Permit downloads" (DLP)
    1,  # "Block downloads" (DLP)
    1,  # "browsing data lifetime" (DLP)
    1,  # "set browsing data lifetime" (DLP)
    1,  # "Restrict printing of web pages." (DLP)
    1,  # "Disable browser sync for personal data." (DLP)
    1,  # "Prevent saving browser history." (DLP)
    1,  # "Disallow autofill of forms in the browser." (DLP)
    1,  # "Block file uploads to external websites." (DLP)
    1,  # "Disable screenshots in the browser." (DLP)
    1,  # "Prevent the browser from remembering passwords." (DLP)
    1,  # "Restrict site per process settings." (DLP)
    1,  # "Disable search suggestions in the browser." (DLP)
    1,  # "Block metrics reporting to Google." (DLP)
    1,  # "Prompt for download location every time." (DLP)
    1,  # "Prevent browser history deletion." (DLP)
    1,  # "Disable background processing in the browser." (DLP)
    1,  # "Disable network predictions." (DLP)
    1,  # "Block third-party cookies." (DLP)
    1,  # "Restrict downloads from specific web domains." (DLP)
    1,  # "Block all downloads from social media sites." (DLP)
    1,  # "Allow file downloads only from trusted sources." (DLP)
    1,  # "Block downloads of executable files." (DLP)
    1,  # "Permit downloads of PDF and TXT files." (DLP)
    1,  # "Configure the browser to delete browsing history older than 7 days." (DLP)
    1,  # "Set the browser to automatically clear cookies and site data after 24 hours." (DLP)
    1,  # "Ensure cached images and files are removed after one week to free up space." (DLP)
    1,  # "Remove saved passwords after 30 days to enhance security." (DLP)
    1,  # "Automatically delete autofill data that is more than 48 hours old." (DLP)
    1,  # "Purge site settings and hosted app data every 72 hours." (DLP)
    1,  # "Implement a policy to delete all browsing data every 12 hours to comply with company security standards." (DLP)
    1,  # "Set the browser to clear download history daily to maintain user privacy." (DLP)
    1,  # "Ensure that cookies and other site data are deleted every 6 hours to prevent unauthorized tracking." (DLP)
    1,  # "Schedule the browser to delete all browsing data older than 1 hour after every 15 minutes of activity." (DLP)
    1,  # "Enable a policy that clears cached images and files after 2 days while keeping cookies for 48 hours." (DLP)
    1,  # "Configure the browser to delete specific types of data, like browsing history and cookies, after 12 hours." (DLP)
    1,  # "Turn off browser sync for personal information." (DLP)
    1,  # "Stop the browser from saving history." (DLP)
    1,  # "Forbid file uploads to external platforms." (DLP)
    1,  # "Prohibit form autofill in the browser." (DLP)
    1,  # "Ask for download location every time." (DLP)
    1,  # "Disable browser completely sync for any personal data." (DLP)
    1,  # "Prevent the browser from saving any history." (DLP)
    1,  # "Block all file uploads to unknown external websites." (DLP)
    1,  # "Disallow automatic autofill of forms on any website in the browser." (DLP)
    1,  # "Prompt user for download location each time." (DLP)

    # These are classified based on your notes
    1,  # "Block third party cookies" (DLP)
    0,  # "block websites" (TPP)
    0,  # "allow websites" (TPP)
    0,  # "prevent websites" (TPP)

    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
]
misclassified_policies = []

# Track misclassified policies
for sample, expected_category in zip(test_samples, expected_categories):
    category = classify_text(sample)
    
    # Check if the predicted category matches the expected category
    if category == "Uncertain" or category != expected_category:
        misclassified_policies.append(sample)

# Display results
for sample in test_samples:
    category = classify_text(sample)
    
    # Check if the result is 'Uncertain' before using it as an index
    if category == "Uncertain":
        print(f"Input: {sample}\nPredicted Category: {category}\n")
    else:
        print(f"Input: {sample}\nPredicted Category: {categories[category]}\n")

print(model)
